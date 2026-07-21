from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal


# ─────────────────────────────────────────────────────────────────────────────
# Auth schemas
# ─────────────────────────────────────────────────────────────────────────────

class LoginSchema(BaseModel):
    email:    EmailStr
    password: str


class StudentRegisterSchema(BaseModel):
    email:           EmailStr
    password:        str   = Field(..., min_length=8)
    confirm_password:str   = Field(..., min_length=8)
    name:            str   = Field(..., min_length=2)
    usn:             str   = Field(..., min_length=5)
    branch:          str   = Field(..., min_length=2)
    cgpa:            float = Field(..., ge=0.0, le=10.0)
    graduation_year: int   = Field(..., ge=2000, le=2100)
    backlog_history: str   # 'Yes' or 'No'
    active_backlog:  int   = Field(..., ge=0)
    skills:          Optional[str] = None
    # Resume PDF is handled separately (multipart file upload)


class CompanyRegisterSchema(BaseModel):
    email:        EmailStr
    password:     str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    company_name: str = Field(..., min_length=2)
    website:      Optional[str] = None
    hr_contact:   str = Field(..., min_length=2)
    company_type: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Student schemas
# ─────────────────────────────────────────────────────────────────────────────

class StudentProfileUpdateSchema(BaseModel):
    name:            str   = Field(..., min_length=2)
    cgpa:            float = Field(..., ge=0.0, le=10.0)
    backlog_history: str   # 'Yes' or 'No'
    active_backlog:  int   = Field(..., ge=0)
    skills:          Optional[str] = None
    # New resume PDF is handled separately (multipart file upload)


# ─────────────────────────────────────────────────────────────────────────────
# Company schemas
# ─────────────────────────────────────────────────────────────────────────────

class CompanyProfileUpdateSchema(BaseModel):
    company_name: str = Field(..., min_length=2)
    website:      Optional[str] = None
    hr_contact:   str = Field(..., min_length=2)
    company_type: Optional[str] = None


class PlacementDriveCreateSchema(BaseModel):
    """
    Used for creating a new placement drive.
    Fields come as multipart/form-data (because of JD PDF upload).
    Rounds are parsed separately from dynamic round_name_X / round_date_X fields.
    allowed_branches and allowed_grad_years are comma-separated strings.
    """
    title:                   str   = Field(..., min_length=2)
    ctc:                     float = Field(..., gt=0)
    deadline:                str   # date string 'YYYY-MM-DD'
    min_cgpa:                float = Field(..., ge=0.0, le=10.0)
    history_backlog_allowed: str   # 'Yes' or 'No'
    allowed_active_backlogs: int   = Field(..., ge=0)
    allowed_branches:        str   = Field(..., min_length=2)  # comma-separated e.g. "CSE,ISE"
    allowed_grad_years:      str   = Field(..., min_length=4)  # comma-separated e.g. "2025,2026"
    skills_required:         Optional[str] = None
    # JD PDF handled separately; rounds/round_dates parsed separately


class PlacementDriveEditSchema(BaseModel):
    """
    Full edit for Pending or Rejected drives. All fields optional since
    the frontend may send only changed fields.
    """
    title:                   Optional[str]   = None
    ctc:                     Optional[float] = Field(None, gt=0)
    deadline:                Optional[str]   = None
    min_cgpa:                Optional[float] = Field(None, ge=0.0, le=10.0)
    history_backlog_allowed: Optional[str]   = None
    allowed_active_backlogs: Optional[int]   = Field(None, ge=0)
    allowed_branches:        Optional[str]   = None
    allowed_grad_years:      Optional[str]   = None
    skills_required:         Optional[str]   = None


class PlacementDriveTimelineEditSchema(BaseModel):
    """
    Limited edit for Open or Closed drives — only deadline is required.
    Rounds are parsed separately from dynamic round_name_X / round_date_X fields.
    """
    deadline: str  # date string 'YYYY-MM-DD'


# ─────────────────────────────────────────────────────────────────────────────
# Application status update schema
# ─────────────────────────────────────────────────────────────────────────────

class ApplicationStatusUpdateSchema(BaseModel):
    action: Literal['next_round', 'select', 'reject']
