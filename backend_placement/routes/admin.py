"""
routes/admin.py
───────────────
All admin-facing endpoints. Every route requires admin authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db, User, Student, Company, PlacementDrive, Application
from utils.auth import require_admin, block_user, unblock_user
from tasks import process_jd_skills

admin_bp = APIRouter(prefix="/api/admin", tags=["admin"])


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
        'is_active':       student.user.is_active,
        'resume_filename': student.resume_path
    }


def company_to_dict(company):
    return {
        'id':              company.id,
        'company_name':    company.company_name,
        'company_type':    company.company_type,
        'website':         company.website,
        'hr_contact':      company.hr_contact,
        'email':           company.user.email,
        'approval_status': company.approval_status,
        'is_active':       company.user.is_active
    }


def drive_to_dict(drive, db: Session):
    return {
        'id':               drive.id,
        'title':            drive.title,
        'company_name':     drive.company.company_name,
        'company_id':       drive.company_id,
        'ctc':              drive.ctc,
        'deadline':         drive.deadline.strftime('%Y-%m-%d'),
        'min_cgpa':         drive.min_cgpa,
        'allowed_branches': drive.allowed_branches.split(',') if drive.allowed_branches else [],
        'allowed_grad_years': drive.allowed_grad_years.split(',') if drive.allowed_grad_years else [],
        'skills_required':  drive.skills_required,
        'history_backlog_allowed': drive.history_backlog_allowed,
        'allowed_active_backlogs': drive.allowed_active_backlogs,
        'approval_status':  drive.approval_status,
        'status':           drive.status,
        'created_at':       drive.created_at.isoformat() if drive.created_at else None,
        'applicant_count':  db.query(Application).filter_by(drive_id=drive.id).count()
    }


def application_to_dict(application):
    return {
        'id':           application.id,
        'student_name': application.student.name,
        'student_usn':  application.student.usn,
        'status':       application.status,
        'applied_date': application.applied_date.isoformat() if application.applied_date else None
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/admin/dashboard
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.get('/dashboard', status_code=status.HTTP_200_OK)
def get_dashboard(user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    total_students    = db.query(Student).count()
    total_companies   = db.query(Company).count()
    total_drives      = db.query(PlacementDrive).count()
    total_applications = db.query(Application).count()

    status_rows = (
        db.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )
    chart_status = {status: count for status, count in status_rows}

    drive_rows = (
        db.query(PlacementDrive.title, func.count(Application.id))
        .join(Application, Application.drive_id == PlacementDrive.id)
        .group_by(PlacementDrive.id)
        .all()
    )
    chart_drives = {title: count for title, count in drive_rows}

    company_rows = (
        db.query(Company.company_name, func.count(Application.id))
        .join(PlacementDrive, PlacementDrive.company_id == Company.id)
        .join(Application, Application.drive_id == PlacementDrive.id)
        .filter(Application.status == 'Selected')
        .group_by(Company.id)
        .all()
    )
    chart_companies = {name: count for name, count in company_rows}

    branch_rows = (
        db.query(Student.branch, func.count(Application.id))
        .join(Application, Application.student_id == Student.id)
        .group_by(Student.branch)
        .all()
    )
    chart_branches = {branch: count for branch, count in branch_rows}

    return {
        'totals': {
            'students':     total_students,
            'companies':    total_companies,
            'drives':       total_drives,
            'applications': total_applications
        },
        'charts': {
            'application_status':   chart_status,
            'applications_per_drive': chart_drives,
            'company_selections':   chart_companies,
            'branch_applications':  chart_branches
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/admin/students
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.get('/students', status_code=status.HTTP_200_OK)
def get_students(search: Optional[str] = None, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    query = db.query(Student).join(User)

    if search:
        search = search.strip()
        query = query.filter(or_(
            Student.name.ilike(f'%{search}%'),
            Student.usn.ilike(f'%{search}%')
        ))

    students = query.order_by(Student.name.asc()).all()

    return {
        'students': [student_to_dict(s) for s in students],
        'total':    len(students)
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/admin/students/<student_id>
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.get('/students/{student_id}', status_code=status.HTTP_200_OK)
def get_student_detail(student_id: str, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    student = db.query(Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    applications = (
        db.query(Application)
        .filter_by(student_id=student.id)
        .all()
    )

    apps_data = [
        {
            'id':          app.id,
            'drive_title': app.drive.title,
            'company_name': app.drive.company.company_name,
            'status':      app.status,
            'applied_date': app.applied_date.isoformat() if app.applied_date else None
        }
        for app in applications
    ]

    return {
        'student':      student_to_dict(student),
        'applications': apps_data
    }


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/admin/students/<student_id>/activate
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.put('/students/{student_id}/activate', status_code=status.HTTP_200_OK)
def activate_student(student_id: str, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    student = db.query(Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.user.is_active = True
    unblock_user(student.user_id)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': str(e)})

    return {'message': f'{student.name} has been activated'}


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/admin/students/<student_id>/deactivate
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.put('/students/{student_id}/deactivate', status_code=status.HTTP_200_OK)
def deactivate_student(student_id: str, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    student = db.query(Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.user.is_active = False
    block_user(student.user_id)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': str(e)})

    return {'message': f'{student.name} has been deactivated'}


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/admin/companies
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.get('/companies', status_code=status.HTTP_200_OK)
def get_companies(search: Optional[str] = None, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    def apply_search(query):
        if search:
            query = query.filter(or_(
                Company.company_name.ilike(f'%{search.strip()}%'),
                Company.hr_contact.ilike(f'%{search.strip()}%')
            ))
        return query

    pending_query  = apply_search(db.query(Company).filter_by(approval_status='Pending'))
    approved_query = apply_search(db.query(Company).filter_by(approval_status='Approved'))

    pending_companies  = pending_query.order_by(Company.company_name.asc()).all()
    approved_companies = approved_query.order_by(Company.company_name.asc()).all()

    return {
        'pending_companies':  [company_to_dict(c) for c in pending_companies],
        'approved_companies': [company_to_dict(c) for c in approved_companies]
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/admin/companies/<company_id>
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.get('/companies/{company_id}', status_code=status.HTTP_200_OK)
def get_company_detail(company_id: str, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    company = db.query(Company).get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    drives = (
        db.query(PlacementDrive)
        .filter_by(company_id=company.id)
        .order_by(PlacementDrive.created_at.desc())
        .all()
    )

    return {
        'company': company_to_dict(company),
        'drives':  [drive_to_dict(d, db) for d in drives]
    }


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/admin/companies/<company_id>/approve
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.put('/companies/{company_id}/approve', status_code=status.HTTP_200_OK)
def approve_company(company_id: str, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    company = db.query(Company).get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.approval_status = 'Approved'
    company.user.is_active  = True

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': str(e)})

    return {'message': f'{company.company_name} has been approved'}


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/admin/companies/<company_id>/reject
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.put('/companies/{company_id}/reject', status_code=status.HTTP_200_OK)
def reject_company(company_id: str, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    company = db.query(Company).get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.approval_status = 'Rejected'

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': str(e)})

    return {'message': f'{company.company_name} has been rejected'}


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/admin/companies/<company_id>/activate
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.put('/companies/{company_id}/activate', status_code=status.HTTP_200_OK)
def activate_company(company_id: str, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    company = db.query(Company).get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.user.is_active = True
    unblock_user(company.user_id)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': str(e)})

    return {'message': f'{company.company_name} has been activated'}


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/admin/companies/<company_id>/deactivate
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.put('/companies/{company_id}/deactivate', status_code=status.HTTP_200_OK)
def deactivate_company(company_id: str, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    company = db.query(Company).get(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.user.is_active = False
    block_user(company.user_id)

    open_drives = db.query(PlacementDrive).filter_by(company_id=company.id, status='Open').all()
    for drive in open_drives:
        drive.status = 'Closed'

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': str(e)})

    return {
        'message':       f'{company.company_name} has been deactivated',
        'drives_closed': len(open_drives)
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/admin/drives
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.get('/drives', status_code=status.HTTP_200_OK)
def get_drives(search: Optional[str] = None, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    def apply_search(query):
        if search:
            query = query.join(Company).filter(or_(
                PlacementDrive.title.ilike(f'%{search.strip()}%'),
                Company.company_name.ilike(f'%{search.strip()}%')
            ))
        return query

    pending_query  = apply_search(db.query(PlacementDrive).filter_by(approval_status='Pending'))
    approved_query = apply_search(db.query(PlacementDrive).filter_by(approval_status='Approved'))

    pending_drives  = pending_query.order_by(PlacementDrive.created_at.desc()).all()
    approved_drives = approved_query.order_by(PlacementDrive.created_at.desc()).all()

    return {
        'pending_drives':  [drive_to_dict(d, db) for d in pending_drives],
        'approved_drives': [drive_to_dict(d, db) for d in approved_drives]
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/admin/drives/<drive_id>
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.get('/drives/{drive_id}', status_code=status.HTTP_200_OK)
def get_drive_detail(drive_id: str, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    drive = db.query(PlacementDrive).get(drive_id)
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    applications = db.query(Application).filter_by(drive_id=drive.id).all()

    applicant_label = 'Total students applied' if drive.status == 'Closed' else 'Total applicants so far'

    return {
        'drive':            drive_to_dict(drive, db),
        'rounds':           drive.rounds.split(',') if drive.rounds else [],
        'round_dates':      drive.round_dates.split(',') if drive.round_dates else [],
        'jd_filename':      drive.jd_path,
        'applicant_label':  applicant_label,
        'applications':     [application_to_dict(a) for a in applications]
    }


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/admin/drives/<drive_id>/approve
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.put('/drives/{drive_id}/approve', status_code=status.HTTP_200_OK)
def approve_drive(drive_id: str, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    drive = db.query(PlacementDrive).get(drive_id)
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    drive.approval_status = 'Approved'
    drive.status          = 'Open'

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': str(e)})

    # Trigger async AI processing
    try:
        process_jd_skills.delay(drive_id)
    except Exception as e:
        print(f"Error triggering background task: {e}")

    return {'message': f'Drive "{drive.title}" has been approved and is now Open'}


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/admin/drives/<drive_id>/reject
# ─────────────────────────────────────────────────────────────────────────────

@admin_bp.put('/drives/{drive_id}/reject', status_code=status.HTTP_200_OK)
def reject_drive(drive_id: str, user_info: dict = Depends(require_admin), db: Session = Depends(get_db)):
    drive = db.query(PlacementDrive).get(drive_id)
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    drive.approval_status = 'Rejected'

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': str(e)})

    return {'message': f'Drive "{drive.title}" has been rejected'}
