"""
utils/helpers.py
────────────────
Shared utility functions used across multiple route routers.
"""

import os
import re
from datetime import datetime, date
from fastapi import UploadFile
import shutil
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# ─────────────────────────────────────────────────────────────────────────────
# File helpers
# ─────────────────────────────────────────────────────────────────────────────

def secure_filename(filename: str) -> str:
    """A simple replacement for werkzeug's secure_filename."""
    if not filename:
        return ""
    # Keep only alphanumerics, dots, underscores, dashes
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    # Strip leading dots/dashes
    filename = re.sub(r'^[\.\-]+', '', filename)
    return filename

def allowed_pdf(filename: str) -> bool:
    """Return True if the file has a .pdf extension."""
    if not filename:
        return False
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def validate_grad_years(years_str: str):
    """Validate comma-separated graduation years."""
    current_year = date.today().year
    min_year     = current_year
    max_year     = current_year + 5

    try:
        years = [int(y.strip()) for y in str(years_str).split(',') if y.strip()]
    except ValueError:
        return False, 'Graduation years must be integers'

    if not years:
        return False, 'At least one graduation year is required'

    invalid = [y for y in years if y < min_year or y > max_year]
    if invalid:
        return False, f'Graduation years must be between {min_year} and {max_year}. Invalid: {invalid}'

    return True, None

def save_resume(file: UploadFile, usn: str) -> str:
    """
    Save a student resume PDF to the resumes upload folder.
    Returns the saved filename (not the full path).
    """
    timestamp  = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_usn   = secure_filename(usn)
    filename   = f"{safe_usn}_{timestamp}.pdf"
    folder     = os.path.join(os.getcwd(), 'uploads', 'resumes')

    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return filename

def save_jd(file: UploadFile, company_id: str) -> str:
    """
    Save a job description PDF to the JD upload folder.
    Returns the saved filename (not the full path).
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    original  = secure_filename(file.filename)
    filename  = f"{company_id}_{timestamp}_{original}"
    folder    = os.path.join(os.getcwd(), 'uploads', 'jd')

    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return filename


# ─────────────────────────────────────────────────────────────────────────────
# Eligibility helper
# ─────────────────────────────────────────────────────────────────────────────

def check_eligibility(student, drive):
    allowed_years    = [int(y.strip()) for y in drive.allowed_grad_years.split(',') if y.strip()]
    allowed_branches = [b.strip().lower()  for b in drive.allowed_branches.split(',')  if b.strip()]

    if student.graduation_year not in allowed_years:
        return None, []
    if student.branch.lower() not in allowed_branches:
        return None, []

    reasons = []

    if student.cgpa < drive.min_cgpa:
        reasons.append('min_cgpa')

    if drive.history_backlog_allowed == 'No' and student.backlog_history == 'Yes':
        reasons.append('history_backlog_allowed')

    if student.active_backlog > drive.allowed_active_backlogs:
        reasons.append('active_backlog')

    return (len(reasons) == 0), reasons


# ─────────────────────────────────────────────────────────────────────────────
# Round parsing helper
# ─────────────────────────────────────────────────────────────────────────────

def parse_rounds_from_form(form_data: dict):
    rounds      = []
    round_dates = []

    found_gap          = False
    name_missing_error = False
    sequence_error     = False
    chronological_error = False
    first_interview    = None
    last_valid_date    = None

    for i in range(1, 6):
        name     = form_data.get(f'round_name_{i}', '').strip()
        date_val = form_data.get(f'round_date_{i}', '').strip()

        if not name and not date_val:
            found_gap = True
            continue

        if date_val and not name:
            name_missing_error = True

        if name and found_gap:
            sequence_error = True

        if date_val:
            try:
                current_date = datetime.strptime(date_val, '%Y-%m-%d').date()
                if first_interview is None:
                    first_interview = current_date
                if last_valid_date and current_date < last_valid_date:
                    chronological_error = True
                last_valid_date = current_date
            except ValueError:
                pass 

        if name:
            rounds.append(name)
            round_dates.append(date_val if date_val else 'N/A')

    errors = []
    if name_missing_error:
        errors.append('Round name is required wherever a date is provided')
    if sequence_error:
        errors.append('Interview rounds must be entered sequentially without gaps')
    if chronological_error:
        errors.append('Interview round dates must be in chronological order')
    if len(rounds) == 0:
        errors.append('At least one interview round is required')

    return rounds, round_dates, first_interview, errors


# ─────────────────────────────────────────────────────────────────────────────
# Auto-close helper
# ─────────────────────────────────────────────────────────────────────────────

def auto_close_expired_drives(drives, db):
    today   = date.today()
    changed = False

    for drive in drives:
        if drive.approval_status == 'Approved' and drive.status == 'Open':
            if drive.deadline.date() < today:
                drive.status = 'Closed'
                changed = True

    if changed:
        db.commit()

    return changed


# ─────────────────────────────────────────────────────────────────────────────
# Email helper
# ─────────────────────────────────────────────────────────────────────────────

async def send_email(subject: str, body: str, recipient_email: str):
    """
    Send an email notification using fastapi-mail.
    """
    try:
        conf = ConnectionConfig(
            MAIL_USERNAME=os.environ.get('MAIL_USERNAME', 'noreply@placement.com'),
            MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD', ''),
            MAIL_FROM=os.environ.get('MAIL_USERNAME', 'noreply@placement.com'),
            MAIL_PORT=465,
            MAIL_SERVER='smtp.gmail.com',
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
            USE_CREDENTIALS=True
        )

        message = MessageSchema(
            subject=subject,
            recipients=[recipient_email],
            body=body,
            subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message)

    except Exception as e:
        print(f'[Email] Failed to send to {recipient_email}: {e}')


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Error Formatter
# ─────────────────────────────────────────────────────────────────────────────

def format_pydantic_errors(errors):
    formatted = []
    for err in errors:
        loc = err.get('loc', [])
        field_name = str(loc[-1]) if loc else 'Field'
        human_field = field_name.replace('_', ' ').capitalize()
        msg = err.get('msg', 'Invalid value.')
        err_type = err.get('type', '')
        
        if 'email' in err_type or err_type == 'value_error':
            if 'email' in field_name.lower():
                msg = "Please enter a valid email address."
        elif err_type == 'string_too_short':
            min_len = err.get('ctx', {}).get('min_length', '')
            msg = f"{human_field} must be at least {min_len} characters long."
        elif err_type == 'string_too_long':
            max_len = err.get('ctx', {}).get('max_length', '')
            msg = f"{human_field} cannot exceed {max_len} characters."
        elif err_type == 'missing':
            msg = f"{human_field} is required."
        elif err_type == 'greater_than':
            gt = err.get('ctx', {}).get('gt', '')
            msg = f"{human_field} must be greater than {gt}."
        elif err_type == 'greater_than_equal':
            ge = err.get('ctx', {}).get('ge', '')
            msg = f"{human_field} must be at least {ge}."
        elif err_type == 'less_than_equal':
            le = err.get('ctx', {}).get('le', '')
            msg = f"{human_field} cannot exceed {le}."
        elif 'parsing' in err_type or 'type_error' in err_type:
            if 'int' in err_type or 'float' in err_type:
                msg = f"{human_field} must be a valid number."
            else:
                msg = f"{human_field} is not in a valid format."
        elif err_type == 'literal_error':
            msg = f"Invalid selection for {human_field}."
        
        if msg == err.get('msg'):
            msg = msg.capitalize()
            
        formatted.append({'loc': list(loc), 'msg': msg})
        
    return formatted
