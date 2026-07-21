"""
routes/files.py
───────────────
File serving endpoints. Serves uploaded PDFs (resumes and job descriptions).
Any authenticated user can access these endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
import os
from utils.auth import require_any_auth

files_bp = APIRouter(prefix="/api/files", tags=["files"])


@files_bp.get('/resume/{filename:path}', status_code=status.HTTP_200_OK)
def serve_resume(filename: str, user_info: dict = Depends(require_any_auth)):
    """Serve a student resume PDF from the resumes upload folder."""
    folder = os.path.join(os.getcwd(), 'uploads', 'resumes')
    file_path = os.path.join(folder, filename)
    
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail={'error': 'Resume file not found'})
        
    return FileResponse(file_path, media_type='application/pdf', filename=filename)


@files_bp.get('/jd/{filename:path}', status_code=status.HTTP_200_OK)
def serve_jd(filename: str, user_info: dict = Depends(require_any_auth)):
    """Serve a job description PDF from the JD upload folder."""
    folder = os.path.join(os.getcwd(), 'uploads', 'jd')
    file_path = os.path.join(folder, filename)
    
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail={'error': 'Job description file not found'})
        
    return FileResponse(file_path, media_type='application/pdf', filename=filename)
