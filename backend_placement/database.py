import os
import uuid
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Uuid as UUID
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')

# For SQLite, check_same_thread=False is needed when using FastAPI
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URI.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URI, 
    connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_ist_now():
    return datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# User
# ─────────────────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = 'users'

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email         = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role          = Column(String(20), nullable=False)  # 'admin', 'company', 'student'
    is_active     = Column(Boolean, default=True, nullable=False)

    refresh_tokens  = relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan')
    student_profile = relationship('Student', back_populates='user', uselist=False, cascade='all, delete-orphan')
    company_profile = relationship('Company', back_populates='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ─────────────────────────────────────────────────────────────────────────────
# RefreshToken
# ─────────────────────────────────────────────────────────────────────────────
class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id    = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    token      = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=get_ist_now)

    user = relationship('User', back_populates='refresh_tokens')


# ─────────────────────────────────────────────────────────────────────────────
# Student
# ─────────────────────────────────────────────────────────────────────────────
class Student(Base):
    __tablename__ = 'students'

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id         = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True)
    name            = Column(String(150), nullable=False)
    usn             = Column(String(20),  nullable=False, unique=True, index=True)
    cgpa            = Column(Float,  nullable=False)
    graduation_year = Column(Integer, nullable=False)
    branch          = Column(String(150), nullable=False)
    backlog_history = Column(String(10), nullable=False, default='No')  # 'Yes' or 'No'
    active_backlog  = Column(Integer, nullable=False, default=0)
    skills          = Column(String(255), nullable=True)
    resume_path     = Column(String(255), nullable=True)  # stored filename only
    extracted_skills_dict = Column(Text, nullable=True)   # stored as JSON string

    user         = relationship('User', back_populates='student_profile')
    applications = relationship('Application', back_populates='student', cascade='all, delete-orphan')
    resumes      = relationship('StudentResume', back_populates='student', cascade='all, delete-orphan')


# ─────────────────────────────────────────────────────────────────────────────
# StudentResume
# ─────────────────────────────────────────────────────────────────────────────
class StudentResume(Base):
    __tablename__ = 'student_resumes'

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey('students.id'), nullable=False)
    name       = Column(String(150), nullable=False)
    file_path  = Column(String(255), nullable=False)
    extracted_skills_dict = Column(Text, nullable=True)   # stored as JSON string
    created_at = Column(DateTime, default=get_ist_now)

    student    = relationship('Student', back_populates='resumes')


# ─────────────────────────────────────────────────────────────────────────────
# Company
# ─────────────────────────────────────────────────────────────────────────────
class Company(Base):
    __tablename__ = 'companies'

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id         = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True)
    company_name    = Column(String(150), nullable=False)
    company_type    = Column(String(100), nullable=True)
    website         = Column(String(255), nullable=True)
    hr_contact      = Column(String(150), nullable=False)
    approval_status = Column(String(20), default='Pending', nullable=False)

    user             = relationship('User', back_populates='company_profile')
    placement_drives = relationship('PlacementDrive', back_populates='company', cascade='all, delete-orphan')


# ─────────────────────────────────────────────────────────────────────────────
# PlacementDrive
# ─────────────────────────────────────────────────────────────────────────────
class PlacementDrive(Base):
    __tablename__ = 'placement_drives'

    id                     = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    company_id             = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=False)
    title                  = Column(String(150), nullable=False)
    ctc                    = Column(Float, nullable=False)
    min_cgpa               = Column(Float, nullable=False)
    history_backlog_allowed= Column(String(10), default='No')   # 'Yes' or 'No'
    allowed_active_backlogs= Column(Integer, default=0)
    allowed_branches       = Column(String(255), nullable=False)  # comma-separated
    allowed_grad_years     = Column(String(255), nullable=False)  # comma-separated
    skills_required        = Column(String(255), nullable=True)
    rounds                 = Column(Text, nullable=True)          # comma-separated
    round_dates            = Column(Text, nullable=True)          # comma-separated
    jd_path                = Column(String(255), nullable=True)   # stored filename only
    extracted_must_haves   = Column(Text, nullable=True)          # stored as JSON array string
    extracted_nice_to_haves= Column(Text, nullable=True)          # stored as JSON array string
    deadline               = Column(DateTime, nullable=False)
    approval_status        = Column(String(20), default='Pending', nullable=False)
    status                 = Column(String(20), default='Open')   # 'Open' or 'Closed'
    created_at             = Column(DateTime, default=get_ist_now)

    company      = relationship('Company', back_populates='placement_drives')
    applications = relationship('Application', back_populates='drive', cascade='all, delete-orphan')


# ─────────────────────────────────────────────────────────────────────────────
# Application
# ─────────────────────────────────────────────────────────────────────────────
class Application(Base):
    __tablename__ = 'applications'
    
    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id          = Column(UUID(as_uuid=True), ForeignKey('students.id'), nullable=False)
    drive_id            = Column(UUID(as_uuid=True), ForeignKey('placement_drives.id'), nullable=False)
    current_round_index = Column(Integer, default=0)
    round_statuses      = Column(Text, nullable=True)       # comma-separated e.g. "Cleared,Pending,Pending"
    round_result_dates  = Column(Text, nullable=True)       # comma-separated e.g. "2025-12-01,,"
    custom_resume_path  = Column(String(255), nullable=True) # filename if different from student default
    status              = Column(String(20), default='Applied', nullable=False)
    applied_date        = Column(DateTime, default=get_ist_now)

    student = relationship('Student', back_populates='applications')
    drive   = relationship('PlacementDrive', back_populates='applications')
