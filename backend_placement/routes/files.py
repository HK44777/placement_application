"""
routes/files.py
───────────────
File serving endpoints. Serves uploaded PDFs (resumes and job descriptions).
Any authenticated user can access these endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import os
from utils.auth import require_any_auth
from utils.s3 import generate_presigned_download_url, generate_presigned_upload_url

files_bp = APIRouter(prefix="/api/files", tags=["files"])

class PresignedUrlRequest(BaseModel):
    file_name: str
    file_type: str
    folder: str # 'resumes' or 'jd'

@files_bp.post('/presigned-url', status_code=status.HTTP_200_OK)
def get_presigned_url(request: PresignedUrlRequest, user_info: dict = Depends(require_any_auth)):
    """Generate a presigned URL for direct S3 upload."""
    if request.folder not in ['resumes', 'jd']:
        raise HTTPException(status_code=400, detail={'error': 'Invalid folder'})
        
    url, object_key = generate_presigned_upload_url(request.file_name, request.file_type, request.folder)
    
    if not url:
        raise HTTPException(status_code=500, detail={'error': 'Failed to generate upload URL'})
        
    return {'url': url, 'object_key': object_key}

@files_bp.get('/resume/{filename:path}', status_code=status.HTTP_200_OK)
def serve_resume(filename: str, user_info: dict = Depends(require_any_auth)):
    """Serve a student resume PDF from S3 via presigned URL redirect."""
    object_key = f"resumes/{filename}" if not filename.startswith('resumes/') else filename
    url = generate_presigned_download_url(object_key)
    if not url:
        raise HTTPException(status_code=404, detail={'error': 'Resume file not found or inaccessible'})
        
    return RedirectResponse(url=url)


@files_bp.get('/jd/{filename:path}', status_code=status.HTTP_200_OK)
def serve_jd(filename: str, user_info: dict = Depends(require_any_auth)):
    """Serve a job description PDF from S3 via presigned URL redirect."""
    object_key = f"jd/{filename}" if not filename.startswith('jd/') else filename
    url = generate_presigned_download_url(object_key)
    if not url:
        raise HTTPException(status_code=404, detail={'error': 'Job description file not found or inaccessible'})
        
    return RedirectResponse(url=url)
