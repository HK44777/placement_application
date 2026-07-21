"""
routes/student.py
─────────────────
All student-facing endpoints. Every route requires student authentication.
"""

from fastapi import APIRouter, Request, Depends, HTTPException, status, UploadFile
from pydantic import ValidationError
from datetime import datetime, date
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db, User, Student, PlacementDrive, Application, Company, StudentResume
from schemas import StudentProfileUpdateSchema
from utils.auth import require_student
from utils.helpers import allowed_pdf, check_eligibility, format_pydantic_errors
from tasks import process_resume_skills
from utils.scoring import calculate_match_score
import json

student_bp = APIRouter(prefix="/api/student", tags=["student"])


# ─────────────────────────────────────────────────────────────────────────────
# Serializers
# ─────────────────────────────────────────────────────────────────────────────

def student_to_dict(student):
    return {
        'id':              student.id,
        'name':            student.name,
        'email':           student.user.email,
        'usn':             student.usn,
        'branch':          student.branch,
        'cgpa':            student.cgpa,
        'graduation_year': student.graduation_year,
        'backlog_history': student.backlog_history,
        'active_backlog':  student.active_backlog,
        'skills':          student.skills,
        'resume_filename': student.resume_path
    }


def drive_to_dict(drive, is_eligible=None, reasons=None):
    return {
        'id':                      drive.id,
        'title':                   drive.title,
        'company_name':            drive.company.company_name,
        'ctc':                     drive.ctc,
        'deadline':                drive.deadline.strftime('%Y-%m-%d'),
        'min_cgpa':                drive.min_cgpa,
        'history_backlog_allowed': drive.history_backlog_allowed,
        'allowed_active_backlogs': drive.allowed_active_backlogs,
        'allowed_branches':        drive.allowed_branches.split(','),
        'allowed_grad_years':      [int(y) for y in drive.allowed_grad_years.split(',') if y.strip()],
        'skills_required':         drive.skills_required,
        'rounds':                  drive.rounds.split(',') if drive.rounds else [],
        'round_dates':             drive.round_dates.split(',') if drive.round_dates else [],
        'jd_filename':             drive.jd_path,
        'status':                  drive.status,
        'approval_status':         drive.approval_status,
        'is_eligible':             is_eligible,
        'reasons':                 reasons or []
    }


def application_to_dict(application):
    drive = application.drive
    return {
        'id':                  application.id,
        'drive_id':            drive.id,
        'drive_title':         drive.title,
        'company_name':        drive.company.company_name,
        'drive_status':        drive.status,
        'status':              application.status,
        'applied_date':        application.applied_date.isoformat() if application.applied_date else None,
        'current_round_index': application.current_round_index,
        'rounds':              drive.rounds.split(',') if drive.rounds else [],
        'round_dates':         drive.round_dates.split(',') if drive.round_dates else [],
        'round_statuses':      application.round_statuses.split(',') if application.round_statuses else [],
        'round_result_dates':  application.round_result_dates.split(',') if application.round_result_dates else [],
        'resume_filename':     application.custom_resume_path
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/student/profile
# ─────────────────────────────────────────────────────────────────────────────

@student_bp.get('/profile', status_code=status.HTTP_200_OK)
def get_profile(user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student_to_dict(student)


# ─────────────────────────────────────────────────────────────────────────────
# Resumes Management
# ─────────────────────────────────────────────────────────────────────────────

@student_bp.get('/resumes', status_code=status.HTTP_200_OK)
def get_resumes(user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    resumes = db.query(StudentResume).filter_by(student_id=student.id).order_by(StudentResume.created_at.desc()).all()
    return [{'id': r.id, 'name': r.name, 'file_path': r.file_path, 'created_at': r.created_at} for r in resumes]

@student_bp.post('/resumes', status_code=status.HTTP_201_CREATED)
async def upload_resume(request: Request, user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        form = await request.form()
        name = form.get('name', 'My Resume')
        resume_key = form.get('resume_key')
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid form data")
        
    if not resume_key:
        raise HTTPException(status_code=400, detail={'error': 'A resume key is required'})
        
    resume_filename = resume_key
    
    new_resume = StudentResume(
        student_id=student.id,
        name=name,
        file_path=resume_filename
    )
    try:
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Upload failed', 'details': str(e)})
        
    # Trigger background AI skill extraction
    try:
        from tasks import process_resume_skills
        process_resume_skills.delay(str(new_resume.id))
    except Exception as e:
        print(f"Error triggering background task: {e}")
        
    return {'message': 'Resume uploaded successfully', 'id': new_resume.id, 'name': new_resume.name}

@student_bp.delete('/resumes/{resume_id}', status_code=status.HTTP_200_OK)
def delete_resume(resume_id: str, user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    resume = db.query(StudentResume).filter_by(id=resume_id, student_id=student.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Optional: We could prevent deleting if it's the only resume, or if it's currently used in an active application.
    # We will just let them delete it. The file stays on disk, but the DB record is removed.
    try:
        db.delete(resume)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Delete failed', 'details': str(e)})
        
    return {'message': 'Resume deleted successfully'}


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/student/profile
# ─────────────────────────────────────────────────────────────────────────────

@student_bp.put('/profile', status_code=status.HTTP_200_OK)
async def update_profile(request: Request, user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    details = []
    form = await request.form()
    data = dict(form)

    new_resume = form.get('resume_key')
    if new_resume:
        data.pop('resume_key', None)

    try:
        validated = StudentProfileUpdateSchema(**data)
        validated_data = validated.dict()
    except ValidationError as e:
        details.extend(format_pydantic_errors(e.errors()))
        validated_data = data

    if details:
        raise HTTPException(status_code=400, detail={'error': 'Validation failed', 'details': details})

    student.name            = validated_data['name']
    student.cgpa            = validated_data['cgpa']
    student.backlog_history = validated_data['backlog_history']
    student.active_backlog  = validated_data['active_backlog']
    student.skills          = validated_data.get('skills')

    if new_resume:
        student.resume_path = new_resume

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Update failed', 'details': str(e)})

    # Trigger background AI skill extraction if a resume or skills were updated
    if new_resume or data.get('skills'):
        try:
            latest_resume = db.query(StudentResume).filter_by(student_id=student.id).order_by(StudentResume.created_at.desc()).first()
            if latest_resume:
                from tasks import process_resume_skills
                process_resume_skills.delay(str(latest_resume.id))
        except Exception as e:
            print(f"Error triggering background task: {e}")

    return {
        'message': 'Profile updated successfully',
        'profile': student_to_dict(student)
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/student/jobs
# ─────────────────────────────────────────────────────────────────────────────

@student_bp.get('/jobs', status_code=status.HTTP_200_OK)
def get_jobs(search: Optional[str] = None, sort_by: Optional[str] = None, resume_id: Optional[str] = None, user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    today_start = datetime.combine(date.today(), datetime.min.time())

    query = (
        db.query(PlacementDrive)
        .join(Company)
        .filter(
            PlacementDrive.approval_status == 'Approved',
            PlacementDrive.status          == 'Open',
            PlacementDrive.deadline        >= today_start
        )
    )

    if search:
        search = search.strip()
        query = query.filter(or_(
            PlacementDrive.title.ilike(f'%{search}%'),
            Company.company_name.ilike(f'%{search}%'),
            PlacementDrive.skills_required.ilike(f'%{search}%')
        ))

    all_drives = query.all()

    applied_ids = {
        app.drive_id
        for app in db.query(Application).filter_by(student_id=student.id).all()
    }

    eligible_drives   = []
    ineligible_drives = []

    selected_skills_dict = student.extracted_skills_dict
    if resume_id:
        resume = db.query(StudentResume).filter_by(id=resume_id, student_id=student.id).first()
        if resume and resume.extracted_skills_dict:
            selected_skills_dict = resume.extracted_skills_dict

    for drive in all_drives:
        if drive.id in applied_ids:
            continue

        result, reasons = check_eligibility(student, drive)

        if result is None:
            continue   # wrong branch/year — don't show at all

        drive_dict = drive_to_dict(drive, is_eligible=result, reasons=reasons)
        
        # Calculate match score
        match_score = 0
        if selected_skills_dict and drive.extracted_must_haves:
            try:
                student_weighted = json.loads(selected_skills_dict)
                jd_must = json.loads(drive.extracted_must_haves)
                jd_nice = json.loads(drive.extracted_nice_to_haves) if drive.extracted_nice_to_haves else []
                match_score = calculate_match_score(jd_must, jd_nice, student_weighted)
            except Exception as e:
                print(f"Error calculating match score: {e}")
        
        drive_dict['match_score'] = match_score

        if result:
            eligible_drives.append(drive_dict)
        else:
            ineligible_drives.append(drive_dict)

    if sort_by == 'match_score':
        eligible_drives.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        ineligible_drives.sort(key=lambda x: x.get('match_score', 0), reverse=True)

    return {
        'eligible_drives':   eligible_drives,
        'ineligible_drives': ineligible_drives,
        'applied_drive_ids': list(applied_ids)
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/student/jobs/<drive_id>
# ─────────────────────────────────────────────────────────────────────────────

@student_bp.get('/jobs/{drive_id}', status_code=status.HTTP_200_OK)
def get_job_detail(drive_id: str, user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    drive = db.query(PlacementDrive).get(drive_id)
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    result, reasons = check_eligibility(student, drive)

    return drive_to_dict(drive, is_eligible=result, reasons=reasons)


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/student/jobs/<drive_id>/apply
# ─────────────────────────────────────────────────────────────────────────────

@student_bp.post('/jobs/{drive_id}/apply', status_code=status.HTTP_201_CREATED)
async def apply_to_drive(drive_id: str, request: Request, user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    drive = db.query(PlacementDrive).get(drive_id)
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    if drive.approval_status != 'Approved' or drive.status != 'Open':
        raise HTTPException(status_code=400, detail={'error': 'This drive is not accepting applications'})

    if drive.deadline.date() < date.today():
        raise HTTPException(status_code=400, detail={'error': 'Application deadline has passed'})

    existing = db.query(Application).filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing:
        raise HTTPException(status_code=400, detail={'error': 'You have already applied for this drive'})

    # Try to parse json data
    try:
        data = await request.json()
        resume_id = data.get('resume_id')
    except Exception:
        resume_id = None

    if not resume_id:
        raise HTTPException(status_code=400, detail={'error': 'Please select a resume to apply with'})
        
    selected_resume = db.query(StudentResume).filter_by(id=resume_id, student_id=student.id).first()
    if not selected_resume:
        raise HTTPException(status_code=404, detail={'error': 'Selected resume not found'})

    resume_filename = selected_resume.file_path

    rounds         = drive.rounds.split(',') if drive.rounds else []
    round_statuses = ['Pending'] * len(rounds)
    result_dates   = [''] * len(rounds)

    application = Application(
        student_id          = student.id,
        drive_id            = drive.id,
        current_round_index = 0,
        round_statuses      = ','.join(round_statuses),
        round_result_dates  = ','.join(result_dates),
        status              = 'Applied',
        custom_resume_path  = resume_filename
    )

    try:
        db.add(application)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Application failed', 'details': str(e)})

    return {
        'message':        'Application submitted successfully',
        'application_id': application.id
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/student/applications
# ─────────────────────────────────────────────────────────────────────────────

@student_bp.get('/applications', status_code=status.HTTP_200_OK)
def get_applications(search: Optional[str] = None, sort_by: Optional[str] = None, resume_id: Optional[str] = None, user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    apps = (
        db.query(Application)
        .join(PlacementDrive)
        .join(Company)
        .filter(Application.student_id == student.id)
        .all()
    )

    if search:
        search = search.strip().lower()
        apps = [
            a for a in apps
            if search in a.drive.title.lower()
            or search in a.drive.company.company_name.lower()
            or (a.drive.skills_required and search in a.drive.skills_required.lower())
        ]

    status_counts = {}
    for app in apps:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1

    selected_skills_dict = student.extracted_skills_dict
    if resume_id:
        resume = db.query(StudentResume).filter_by(id=resume_id, student_id=student.id).first()
        if resume and resume.extracted_skills_dict:
            selected_skills_dict = resume.extracted_skills_dict

    app_dicts = []
    for app in apps:
        app_dict = application_to_dict(app)
        
        match_score = 0
        if selected_skills_dict and app.drive.extracted_must_haves:
            try:
                student_weighted = json.loads(selected_skills_dict)
                jd_must = json.loads(app.drive.extracted_must_haves)
                jd_nice = json.loads(app.drive.extracted_nice_to_haves) if app.drive.extracted_nice_to_haves else []
                match_score = calculate_match_score(jd_must, jd_nice, student_weighted)
            except Exception as e:
                print(f"Error calculating match score: {e}")
        
        app_dict['match_score'] = match_score
        app_dicts.append(app_dict)

    if sort_by == 'match_score':
        app_dicts.sort(key=lambda x: x.get('match_score', 0), reverse=True)

    return {
        'applications':  app_dicts,
        'total':         len(apps),
        'status_counts': status_counts
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/student/applications/<application_id>
# ─────────────────────────────────────────────────────────────────────────────

@student_bp.get('/applications/{application_id}', status_code=status.HTTP_200_OK)
def get_application_detail(application_id: str, user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    application = db.query(Application).filter_by(
        id=application_id, student_id=student.id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    return application_to_dict(application)


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /api/student/applications/<application_id>
# ─────────────────────────────────────────────────────────────────────────────

@student_bp.delete('/applications/{application_id}', status_code=status.HTTP_200_OK)
def withdraw_application(application_id: str, user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    application = db.query(Application).filter_by(
        id=application_id, student_id=student.id
    ).first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.drive.status != 'Open':
        raise HTTPException(status_code=400, detail={'error': 'Cannot withdraw application from a closed drive'})

    try:
        db.delete(application)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Withdraw failed', 'details': str(e)})

    return {'message': 'Application withdrawn successfully'}


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/student/export_csv
# ─────────────────────────────────────────────────────────────────────────────

@student_bp.post('/export_csv', status_code=status.HTTP_202_ACCEPTED)
def export_csv(user_info: dict = Depends(require_student), db: Session = Depends(get_db)):
    from tasks import export_student_csv
    student = db.query(Student).filter_by(user_id=user_info['user_id']).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    export_student_csv.delay(student.id)
    
    return {
        'message': 'Export started. You will receive an email with the CSV file shortly.'
    }
