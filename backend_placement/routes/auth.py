"""
routes/auth.py
──────────────
Authentication endpoints.
"""

from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session
import jwt
import datetime
import pytz

from database import get_db, User, Student, Company, RefreshToken, StudentResume
from schemas import LoginSchema, StudentRegisterSchema, CompanyRegisterSchema
from utils.auth import (
    generate_access_token, generate_refresh_token,
    set_refresh_cookie, require_any_auth, revoke_access_token
)
from utils.helpers import save_resume, allowed_pdf, validate_grad_years, format_pydantic_errors

auth_bp = APIRouter(prefix="/api/auth", tags=["auth"])

# ─────────────────────────────────────────────────────────────────────────────
# Register Student
# ─────────────────────────────────────────────────────────────────────────────

@auth_bp.post('/register/student', status_code=status.HTTP_201_CREATED)
async def register_student(request: Request, response: Response, db: Session = Depends(get_db)):
    details = []
    form = await request.form()
    data = dict(form)

    # File upload handling from form
    resume_file = form.get("resume")
    if resume_file:
        data.pop("resume", None)

    try:
        validated = StudentRegisterSchema(**data)
        validated_data = validated.dict()
    except ValidationError as e:
        details.extend(format_pydantic_errors(e.errors()))
        validated_data = data

    email = validated_data.get('email')
    usn = validated_data.get('usn')
    password = validated_data.get('password')
    confirm_password = validated_data.get('confirm_password')

    if password and confirm_password and password != confirm_password:
        details.append({'loc': ['confirm_password'], 'msg': 'Passwords do not match'})

    if email and db.query(User).filter_by(email=email).first():
        details.append({'loc': ['email'], 'msg': 'Email is already registered'})
    
    if usn and db.query(Student).filter_by(usn=usn).first():
        details.append({'loc': ['usn'], 'msg': 'USN is already registered'})

    grad_year = validated_data.get('graduation_year')
    if grad_year:
        valid, err = validate_grad_years(str(grad_year))
        if not valid:
            details.append({'loc': ['graduation_year'], 'msg': err})

    if not resume_file or not hasattr(resume_file, "filename"):
        details.append({'loc': ['resume'], 'msg': 'A valid PDF resume is required'})
    elif not allowed_pdf(resume_file.filename):
        details.append({'loc': ['resume'], 'msg': 'Only PDF files are allowed'})

    if details:
        raise HTTPException(status_code=400, detail={'error': 'Validation failed', 'details': details})

    resume_filename = save_resume(resume_file, usn)

    # Save to DB
    try:
        new_user = User(email=validated_data['email'], role='student')
        new_user.set_password(validated_data['password'])
        db.add(new_user)
        db.flush()

        new_student = Student(
            user_id         = new_user.id,
            name            = validated_data['name'],
            usn             = validated_data['usn'],
            branch          = validated_data['branch'],
            cgpa            = validated_data['cgpa'],
            graduation_year = validated_data['graduation_year'],
            backlog_history = validated_data['backlog_history'],
            active_backlog  = validated_data['active_backlog'],
            skills          = validated_data.get('skills'),
            resume_path     = resume_filename
        )
        db.add(new_student)
        db.flush()

        # Create Default Resume
        default_resume = StudentResume(
            student_id = new_student.id,
            name = "Default Resume",
            file_path = resume_filename
        )
        db.add(default_resume)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Registration failed', 'details': str(e)})

    access_token  = generate_access_token(new_user.id, new_user.role)
    refresh_token = generate_refresh_token(new_user.id, db)

    set_refresh_cookie(response, refresh_token)
    
    return {
        'message':      'Student registered successfully',
        'access_token': access_token,
        'role':         new_user.role,
        'user_id':      new_user.id
    }


# ─────────────────────────────────────────────────────────────────────────────
# Register Company
# ─────────────────────────────────────────────────────────────────────────────

@auth_bp.post('/register/company', status_code=status.HTTP_201_CREATED)
def register_company(data: CompanyRegisterSchema, response: Response, db: Session = Depends(get_db)):
    details = []
    validated_data = data.dict()

    email = validated_data.get('email')
    password = validated_data.get('password')
    confirm_password = validated_data.get('confirm_password')

    if password and confirm_password and password != confirm_password:
        details.append({'loc': ['confirm_password'], 'msg': 'Passwords do not match'})

    if email and db.query(User).filter_by(email=email).first():
        details.append({'loc': ['email'], 'msg': 'Email is already registered'})

    if details:
        raise HTTPException(status_code=400, detail={'error': 'Validation failed', 'details': details})

    try:
        new_user = User(email=validated_data['email'], role='company')
        new_user.set_password(validated_data['password'])
        db.add(new_user)
        db.flush()

        new_company = Company(
            user_id      = new_user.id,
            company_name = validated_data['company_name'],
            website      = validated_data.get('website'),
            hr_contact   = validated_data['hr_contact'],
            company_type = validated_data.get('company_type')
        )
        db.add(new_company)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail={'error': 'Registration failed', 'details': str(e)})

    return {
        'message':         'Registration successful! You can proceed only after admin\'s approval.',
        'approval_status': new_company.approval_status
    }


# ─────────────────────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────────────────────

@auth_bp.post('/login', status_code=status.HTTP_200_OK)
def login(data: LoginSchema, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email).first()
    if not user or not user.check_password(data.password):
        raise HTTPException(status_code=401, detail={'error': 'Invalid email or password'})

    if user.role == 'student':
        if not user.is_active:
            raise HTTPException(status_code=403, detail={'error': 'Your account has been deactivated by admin'})

    elif user.role == 'company':
        company = user.company_profile
        if company.approval_status == 'Pending':
            raise HTTPException(status_code=403, detail={'error': 'Your account is pending admin approval', 'status': 'pending'})

        if not user.is_active:
            raise HTTPException(status_code=403, detail={'error': 'Your account has been deactivated', 'status': 'deactivated'})

        if company.approval_status == 'Rejected':
            access_token  = generate_access_token(user.id, user.role)
            refresh_token = generate_refresh_token(user.id, db)
            set_refresh_cookie(response, refresh_token)
            return {
                'message':         'Login successful',
                'access_token':    access_token,
                'role':            user.role,
                'user_id':         user.id,
                'approval_status': 'rejected'
            }

    access_token  = generate_access_token(user.id, user.role)
    refresh_token = generate_refresh_token(user.id, db)

    set_refresh_cookie(response, refresh_token)
    return {
        'message':      'Login successful',
        'access_token': access_token,
        'role':         user.role,
        'user_id':      user.id
    }


# ─────────────────────────────────────────────────────────────────────────────
# Refresh Token
# ─────────────────────────────────────────────────────────────────────────────

@auth_bp.post('/refresh', status_code=status.HTTP_200_OK)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        raise HTTPException(status_code=401, detail={'error': 'No refresh token provided'})

    token_record = db.query(RefreshToken).filter_by(token=refresh_token).first()
    if not token_record:
        raise HTTPException(status_code=401, detail={'error': 'Invalid refresh token'})

    ist_now = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)
    if token_record.expires_at < ist_now:
        db.delete(token_record)
        db.commit()
        raise HTTPException(status_code=401, detail={'error': 'Refresh token expired. Please login again.'})

    user = token_record.user
    if not user.is_active:
        raise HTTPException(status_code=403, detail={'error': 'Your account has been deactivated'})

    new_access_token = generate_access_token(user.id, user.role)

    return {
        'message':      'Token refreshed successfully',
        'access_token': new_access_token
    }


# ─────────────────────────────────────────────────────────────────────────────
# Logout
# ─────────────────────────────────────────────────────────────────────────────

@auth_bp.post('/logout', status_code=status.HTTP_200_OK)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1]
        try:
            import os
            secret_key = os.environ.get('JWT_SECRET_KEY', 'dev_secret')
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            jti = payload.get('jti')
            if jti:
                revoke_access_token(jti)
        except jwt.InvalidTokenError:
            pass

    refresh_token = request.cookies.get('refresh_token')
    if refresh_token:
        token_record = db.query(RefreshToken).filter_by(token=refresh_token).first()
        if token_record:
            db.delete(token_record)
            db.commit()

    response.delete_cookie('refresh_token', httponly=True, samesite='strict')
    return {'message': 'Logged out successfully'}


# ─────────────────────────────────────────────────────────────────────────────
# Me
# ─────────────────────────────────────────────────────────────────────────────

@auth_bp.get('/me', status_code=status.HTTP_200_OK)
def me(user_info: dict = Depends(require_any_auth), db: Session = Depends(get_db)):
    user = db.query(User).get(user_info['user_id'])
    if not user:
        raise HTTPException(status_code=404, detail={'error': 'User not found'})

    data = {
        'user_id': user.id,
        'email':   user.email,
        'role':    user.role
    }

    if user.role == 'student' and user.student_profile:
        s = user.student_profile
        data['name'] = s.name
        data['usn']  = s.usn

    elif user.role == 'company' and user.company_profile:
        c = user.company_profile
        data['company_name']    = c.company_name
        data['approval_status'] = c.approval_status

    return data
