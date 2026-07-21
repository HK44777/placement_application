"""
routes/company.py
─────────────────
All company-facing endpoints. Every route requires company authentication.
"""

from fastapi import APIRouter, Request, Depends, HTTPException, status
from pydantic import ValidationError
from datetime import datetime, date
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db, Company, PlacementDrive, Application
from schemas import (
    CompanyProfileUpdateSchema,
    PlacementDriveCreateSchema,
    PlacementDriveEditSchema,
    PlacementDriveTimelineEditSchema,
    ApplicationStatusUpdateSchema
)
from utils.auth import require_company
from utils.helpers import (
    allowed_pdf,
    parse_rounds_from_form,
    auto_close_expired_drives,
    validate_grad_years,
    format_pydantic_errors
)

company_bp = APIRouter(prefix="/api/company", tags=["company"])


# ─────────────────────────────────────────────────────────────────────────────
# Serializers
# ─────────────────────────────────────────────────────────────────────────────

def drive_to_dict(drive):
    return {
        'id':                      drive.id,
        'title':                   drive.title,
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
        'approval_status':         drive.approval_status,
        'status':                  drive.status,
        'created_at':              drive.created_at.isoformat() if drive.created_at else None
    }


def application_to_dict(application):
    student = application.student
    return {
        'id':                  application.id,
        'student_id':          student.id,
        'student_name':        student.name,
        'student_usn':         student.usn,
        'student_branch':      student.branch,
        'student_cgpa':        student.cgpa,
        'student_backlog_history': student.backlog_history,
        'student_active_backlog':  student.active_backlog,
        'resume_filename':     application.custom_resume_path or student.resume_path,
        'status':              application.status,
        'applied_date':        application.applied_date.isoformat() if application.applied_date else None,
        'current_round_index': application.current_round_index,
        'round_statuses':      application.round_statuses.split(',') if application.round_statuses else [],
        'round_result_dates':  application.round_result_dates.split(',') if application.round_result_dates else []
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/company/profile
# ─────────────────────────────────────────────────────────────────────────────

@company_bp.get('/profile', status_code=status.HTTP_200_OK)
def get_profile(user_info: dict = Depends(require_company), db: Session = Depends(get_db)):
    company = db.query(Company).filter_by(user_id=user_info['user_id']).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    total_drives = db.query(PlacementDrive).filter_by(company_id=company.id).count()

    total_applicants = (
        db.query(func.count(Application.id))
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .filter(PlacementDrive.company_id == company.id)
        .scalar()
    )

    return {
        'id':               company.id,
        'company_name':     company.company_name,
        'company_type':     company.company_type,
        'website':          company.website,
        'hr_contact':       company.hr_contact,
        'approval_status':  company.approval_status,
        'email':            company.user.email,
        'total_drives':     total_drives,
        'total_applicants': total_applicants
    }


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/company/profile
# ─────────────────────────────────────────────────────────────────────────────

@company_bp.put('/profile', status_code=status.HTTP_200_OK)
def update_profile(data: CompanyProfileUpdateSchema, user_info: dict = Depends(require_company), db: Session = Depends(get_db)):
    company = db.query(Company).filter_by(user_id=user_info['user_id']).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    if company.approval_status != 'Rejected':
        raise HTTPException(status_code=403, detail={'error': 'Profile can only be edited when your account has been rejected'})

    validated = data

    company.company_name    = validated.company_name
    company.website         = validated.website
    company.hr_contact      = validated.hr_contact
    company.company_type    = validated.company_type
    company.approval_status = 'Pending'

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Update failed', 'details': str(e)})

    return {
        'message': 'Profile re-submitted for admin approval. You will be notified once reviewed.'
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/company/drives
# ─────────────────────────────────────────────────────────────────────────────

@company_bp.get('/drives', status_code=status.HTTP_200_OK)
def get_drives(user_info: dict = Depends(require_company), db: Session = Depends(get_db)):
    company = db.query(Company).filter_by(user_id=user_info['user_id']).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    drives = (
        db.query(PlacementDrive)
        .filter_by(company_id=company.id)
        .order_by(PlacementDrive.id.desc())
        .all()
    )

    auto_close_expired_drives(drives, db)
    db.refresh(company)

    pending_drives  = []
    open_drives     = []
    closed_drives   = []
    rejected_drives = []

    for drive in drives:
        if drive.approval_status == 'Pending':
            pending_drives.append(drive_to_dict(drive))
        elif drive.approval_status == 'Rejected':
            rejected_drives.append(drive_to_dict(drive))
        elif drive.approval_status == 'Approved':
            if drive.status == 'Open':
                open_drives.append(drive_to_dict(drive))
            else:
                closed_drives.append(drive_to_dict(drive))

    approved_drives   = [d for d in drives if d.approval_status == 'Approved']
    chart_drive_data  = [
        {
            'drive_title': d.title,
            'count': db.query(Application).filter_by(drive_id=d.id).count()
        }
        for d in approved_drives
    ]

    all_apps = (
        db.query(Application)
        .join(PlacementDrive)
        .filter(PlacementDrive.company_id == company.id)
        .all()
    )
    status_counts = {}
    for app in all_apps:
        status_counts[app.status] = status_counts.get(app.status, 0) + 1

    return {
        'pending_drives':  pending_drives,
        'open_drives':     open_drives,
        'closed_drives':   closed_drives,
        'rejected_drives': rejected_drives,
        'total_applicants': len(all_apps),
        'chart_drives':    chart_drive_data,
        'chart_statuses':  status_counts
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/company/drives
# ─────────────────────────────────────────────────────────────────────────────

@company_bp.post('/drives', status_code=status.HTTP_201_CREATED)
async def create_drive(request: Request, user_info: dict = Depends(require_company), db: Session = Depends(get_db)):
    company = db.query(Company).filter_by(user_id=user_info['user_id']).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    details = []
    form = await request.form()
    data = dict(form)
    jd_key = data.pop('jd_key', None)

    try:
        validated = PlacementDriveCreateSchema(**data)
        validated_data = validated.dict()
    except ValidationError as e:
        details.extend(format_pydantic_errors(e.errors()))
        validated_data = data

    deadline_date = None
    if validated_data.get('deadline'):
        try:
            deadline_date = datetime.strptime(validated_data['deadline'], '%Y-%m-%d').date()
            if deadline_date < date.today():
                details.append({'loc': ['deadline'], 'msg': 'Application deadline cannot be in the past'})
        except ValueError:
            details.append({'loc': ['deadline'], 'msg': 'Invalid deadline format. Use YYYY-MM-DD'})

    if validated_data.get('allowed_grad_years'):
        valid, err = validate_grad_years(str(validated_data['allowed_grad_years']))
        if not valid:
            details.append({'loc': ['allowed_grad_years'], 'msg': err})

    rounds, round_dates, first_interview, round_errors = parse_rounds_from_form(data)

    if first_interview and deadline_date and deadline_date >= first_interview:
        round_errors.append('Application deadline must be strictly before the first interview round date')

    for r_err in round_errors:
        details.append({'loc': ['rounds'], 'msg': r_err})

    if not jd_key:
        details.append({'loc': ['jd_key'], 'msg': 'A JD key is required'})

    if details:
        raise HTTPException(status_code=400, detail={'error': 'Validation failed', 'details': details})

    jd_filename = jd_key

    try:
        drive = PlacementDrive(
            company_id               = company.id,
            title                    = validated.title,
            ctc                      = validated.ctc,
            deadline                 = datetime.strptime(validated.deadline, '%Y-%m-%d'),
            min_cgpa                 = validated.min_cgpa,
            history_backlog_allowed  = validated.history_backlog_allowed,
            allowed_active_backlogs  = validated.allowed_active_backlogs,
            allowed_branches         = validated.allowed_branches,
            allowed_grad_years       = validated.allowed_grad_years,
            skills_required          = validated.skills_required,
            rounds                   = ','.join(rounds),
            round_dates              = ','.join(round_dates),
            jd_path                  = jd_filename
        )
        db.add(drive)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Failed to create drive', 'details': str(e)})

    return {
        'message':  'Placement drive created. Awaiting admin approval.',
        'drive_id': drive.id
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/company/drives/<drive_id>
# ─────────────────────────────────────────────────────────────────────────────

@company_bp.get('/drives/{drive_id}', status_code=status.HTTP_200_OK)
def get_drive_detail(drive_id: str, user_info: dict = Depends(require_company), db: Session = Depends(get_db)):
    company = db.query(Company).filter_by(user_id=user_info['user_id']).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    drive = db.query(PlacementDrive).filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    data = drive_to_dict(drive)

    if drive.approval_status == 'Approved' and drive.status == 'Open':
        data['applicant_count'] = db.query(Application).filter_by(drive_id=drive.id).count()

    if drive.approval_status == 'Approved' and drive.status == 'Closed':
        applications = (
            db.query(Application)
            .filter_by(drive_id=drive.id)
            .order_by(Application.id)
            .all()
        )
        data['applications'] = [application_to_dict(a) for a in applications]

    return data


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/company/drives/<drive_id>
# ─────────────────────────────────────────────────────────────────────────────

@company_bp.put('/drives/{drive_id}', status_code=status.HTTP_200_OK)
async def edit_drive(drive_id: str, request: Request, user_info: dict = Depends(require_company), db: Session = Depends(get_db)):
    company = db.query(Company).filter_by(user_id=user_info['user_id']).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    drive = db.query(PlacementDrive).filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    if drive.approval_status in ('Pending', 'Rejected'):
        return await _full_edit(drive, company.id, request, db)

    if drive.approval_status == 'Approved':
        return await _timeline_edit(drive, request, db)

    raise HTTPException(status_code=400, detail={'error': 'Drive cannot be edited in its current state'})


async def _full_edit(drive, company_id, request: Request, db: Session):
    details = []
    form = await request.form()
    data = dict(form)
    jd_key = data.pop('jd_key', None)

    try:
        validated = PlacementDriveEditSchema(**data)
        validated_data = validated.dict(exclude_unset=True)
    except ValidationError as e:
        details.extend(format_pydantic_errors(e.errors()))
        validated_data = data

    deadline_date = None
    if validated_data.get('deadline'):
        try:
            deadline_date = datetime.strptime(validated_data['deadline'], '%Y-%m-%d').date()
            old_deadline = drive.deadline.date()
            if deadline_date != old_deadline and deadline_date < date.today():
                details.append({'loc': ['deadline'], 'msg': 'New deadline cannot be in the past'})
        except ValueError:
            details.append({'loc': ['deadline'], 'msg': 'Invalid deadline format. Use YYYY-MM-DD'})

    if validated_data.get('allowed_grad_years'):
        valid, err = validate_grad_years(str(validated_data['allowed_grad_years']))
        if not valid:
            details.append({'loc': ['allowed_grad_years'], 'msg': err})

    rounds, round_dates, first_interview, round_errors = parse_rounds_from_form(data)

    check_deadline = deadline_date or drive.deadline.date()
    if first_interview and check_deadline >= first_interview:
        round_errors.append('Application deadline must be strictly before the first interview round date')

    for r_err in round_errors:
        details.append({'loc': ['rounds'], 'msg': r_err})

    if details:
        raise HTTPException(status_code=400, detail={'error': 'Validation failed', 'details': details})

    if 'title' in validated_data:                   drive.title                   = validated_data['title']
    if 'ctc' in validated_data:                     drive.ctc                     = validated_data['ctc']
    if deadline_date:                               drive.deadline                = datetime.strptime(validated_data['deadline'], '%Y-%m-%d')
    if 'min_cgpa' in validated_data:                drive.min_cgpa                = validated_data['min_cgpa']
    if 'history_backlog_allowed' in validated_data: drive.history_backlog_allowed = validated_data['history_backlog_allowed']
    if 'allowed_active_backlogs' in validated_data: drive.allowed_active_backlogs = validated_data['allowed_active_backlogs']
    if 'allowed_branches' in validated_data:        drive.allowed_branches        = validated_data['allowed_branches']
    if 'allowed_grad_years' in validated_data:      drive.allowed_grad_years      = validated_data['allowed_grad_years']
    if 'skills_required' in validated_data:         drive.skills_required         = validated_data['skills_required']

    if jd_key:
        drive.jd_path = jd_key

    drive.rounds      = ','.join(rounds)
    drive.round_dates = ','.join(round_dates)

    drive.approval_status = 'Pending'

    if drive.deadline.date() >= date.today():
        drive.status = 'Open'
    else:
        drive.status = 'Closed'

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Edit failed', 'details': str(e)})

    return {'message': 'Drive updated and re-submitted for admin approval'}


async def _timeline_edit(drive, request: Request, db: Session):
    details = []
    form = await request.form()
    data = dict(form)

    try:
        validated = PlacementDriveTimelineEditSchema(**data)
        validated_data = validated.dict()
    except ValidationError as e:
        details.extend(format_pydantic_errors(e.errors()))
        validated_data = data

    new_deadline_date = None
    if validated_data.get('deadline'):
        try:
            new_deadline_date = datetime.strptime(validated_data['deadline'], '%Y-%m-%d').date()
            old_deadline = drive.deadline.date()
            if new_deadline_date != old_deadline and new_deadline_date < date.today():
                details.append({'loc': ['deadline'], 'msg': 'New deadline cannot be in the past'})
        except ValueError:
            details.append({'loc': ['deadline'], 'msg': 'Invalid deadline format. Use YYYY-MM-DD'})

    rounds, round_dates, first_interview, round_errors = parse_rounds_from_form(data)

    if first_interview and new_deadline_date and new_deadline_date >= first_interview:
        round_errors.append('Application deadline must be strictly before the first interview round date')

    for r_err in round_errors:
        details.append({'loc': ['rounds'], 'msg': r_err})

    if details:
        raise HTTPException(status_code=400, detail={'error': 'Validation failed', 'details': details})

    drive.deadline    = datetime.strptime(validated_data['deadline'], '%Y-%m-%d')
    drive.rounds      = ','.join(rounds)
    drive.round_dates = ','.join(round_dates)

    if new_deadline_date >= date.today():
        drive.status = 'Open'
    else:
        drive.status = 'Closed'

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Edit failed', 'details': str(e)})

    return {'message': 'Drive timeline updated successfully'}


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /api/company/drives/<drive_id>
# ─────────────────────────────────────────────────────────────────────────────

@company_bp.delete('/drives/{drive_id}', status_code=status.HTTP_200_OK)
def delete_drive(drive_id: str, user_info: dict = Depends(require_company), db: Session = Depends(get_db)):
    company = db.query(Company).filter_by(user_id=user_info['user_id']).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    drive = db.query(PlacementDrive).filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    if drive.approval_status not in ('Pending', 'Rejected'):
        raise HTTPException(status_code=403, detail={'error': 'Only Pending or Rejected drives can be deleted'})

    try:
        db.delete(drive)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Delete failed', 'details': str(e)})

    return {'message': 'Drive deleted successfully'}


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/company/drives/<drive_id>/close
# ─────────────────────────────────────────────────────────────────────────────

@company_bp.post('/drives/{drive_id}/close', status_code=status.HTTP_200_OK)
def close_drive(drive_id: str, user_info: dict = Depends(require_company), db: Session = Depends(get_db)):
    company = db.query(Company).filter_by(user_id=user_info['user_id']).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    drive = db.query(PlacementDrive).filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    if drive.status != 'Open':
        return {'message': 'Drive is already closed'}

    drive.status = 'Closed'

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Failed to close drive', 'details': str(e)})

    return {'message': 'Drive closed successfully. No further applications will be accepted.'}


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/company/drives/<drive_id>/applications
# ─────────────────────────────────────────────────────────────────────────────

@company_bp.get('/drives/{drive_id}/applications', status_code=status.HTTP_200_OK)
def get_drive_applications(drive_id: str, user_info: dict = Depends(require_company), db: Session = Depends(get_db)):
    company = db.query(Company).filter_by(user_id=user_info['user_id']).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    drive = db.query(PlacementDrive).filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        raise HTTPException(status_code=404, detail="Drive not found")

    applications = (
        db.query(Application)
        .filter_by(drive_id=drive.id)
        .order_by(Application.id)
        .all()
    )

    return {
        'drive_id':     drive.id,
        'drive_title':  drive.title,
        'rounds':       drive.rounds.split(',') if drive.rounds else [],
        'round_dates':  drive.round_dates.split(',') if drive.round_dates else [],
        'applications': [application_to_dict(a) for a in applications]
    }


# ─────────────────────────────────────────────────────────────────────────────
# PUT /api/company/applications/<application_id>/status
# ─────────────────────────────────────────────────────────────────────────────

@company_bp.put('/applications/{application_id}/status', status_code=status.HTTP_200_OK)
def update_application_status(application_id: str, data: ApplicationStatusUpdateSchema, user_info: dict = Depends(require_company), db: Session = Depends(get_db)):
    company = db.query(Company).filter_by(user_id=user_info['user_id']).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    validated = data
    application = db.query(Application).get(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    if application.drive.company_id != company.id:
        raise HTTPException(status_code=403, detail={'error': 'Unauthorized — this application does not belong to your company'})

    if not application.student.user.is_active:
        raise HTTPException(status_code=403, detail={'error': 'Action denied — this student has been deactivated by admin'})

    drive         = application.drive
    rounds        = drive.rounds.split(',') if drive.rounds else []
    today         = date.today().isoformat()
    current_index = application.current_round_index

    statuses = application.round_statuses.split(',') if application.round_statuses else ['Pending'] * len(rounds)
    dates    = application.round_result_dates.split(',') if application.round_result_dates else [''] * len(rounds)

    cleared_round = rounds[current_index] if current_index < len(rounds) else 'Unknown Round'

    student_name = application.student.name
    company_name = company.company_name
    drive_title  = drive.title
    email_subject = ''
    email_body    = ''

    if validated.action == 'next_round':
        statuses[current_index] = 'Cleared'
        dates[current_index]    = today
        application.current_round_index += 1
        application.status              = 'In Progress'

        next_index     = current_index + 1
        next_round     = rounds[next_index] if next_index < len(rounds) else 'TBD'
        all_dates      = drive.round_dates.split(',') if drive.round_dates else []
        next_date      = all_dates[next_index] if next_index < len(all_dates) and all_dates[next_index] else 'TBD'

        email_subject = f'Interview Update: {company_name} - {drive_title}'
        email_body = (
            f'Hello {student_name},\n\n'
            f'Congratulations! You have cleared {cleared_round}.\n\n'
            f'Your next round is: {next_round}.\n'
            f'Scheduled date: {next_date}.\n\n'
            f'Best of luck,\nPlacement Portal'
        )

    elif validated.action == 'select':
        statuses[current_index] = 'Selected'
        dates[current_index]    = today
        application.status      = 'Selected'

        email_subject = f'Offer Selected: {company_name} - {drive_title}'
        email_body = (
            f'Hello {student_name},\n\n'
            f'Congratulations! You have been selected for the role of {drive_title} '
            f'at {company_name} after clearing {cleared_round}.\n\n'
            f'HR will reach out to you shortly.\n\nBest regards,\nPlacement Portal'
        )

    elif validated.action == 'reject':
        statuses[current_index] = 'Rejected'
        dates[current_index]    = today
        application.status      = 'Rejected'

        email_subject = f'Application Update: {company_name} - {drive_title}'
        email_body = (
            f'Hello {student_name},\n\n'
            f'Thank you for applying to {company_name} for the role of {drive_title}.\n\n'
            f'Unfortunately, we will not be moving forward with your application '
            f'following the {cleared_round}.\n\nBest regards,\nPlacement Portal'
        )

    application.round_statuses     = ','.join(statuses)
    application.round_result_dates = ','.join(dates)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Status update failed', 'details': str(e)})

    student_email = application.student.user.email
    if email_subject and student_email:
        try:
            from tasks import send_round_update_email
            send_round_update_email.delay(student_email, email_subject, email_body)
        except Exception:
            pass

    return {
        'message':    'Application status updated successfully',
        'new_status': application.status
    }
