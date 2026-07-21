"""
app.py
──────
FastAPI application entry point.

- Creates the FastAPI app
- Configures CORS
- Registers all APIRouters
- Creates DB tables on startup
- Creates a default admin account if none exists

Run with:
    uvicorn app:app --reload
"""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base, SessionLocal, User

# ── DB setup and default admin ─────────────────────────────────────────────
def _create_default_admin():
    """Create a default admin account if no admin exists."""
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == 'admin').first()
        if not existing_admin:
            admin = User(email='admin@admin.com', role='admin', is_active=True)
            admin.set_password('admin123')
            db.add(admin)
            db.commit()
            print('Default admin created: admin@admin.com / admin123')
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create upload folders
    upload_resumes = os.path.join(os.getcwd(), 'uploads', 'resumes')
    upload_jd = os.path.join(os.getcwd(), 'uploads', 'jd')
    os.makedirs(upload_resumes, exist_ok=True)
    os.makedirs(upload_jd, exist_ok=True)
    
    # Create all DB tables
    Base.metadata.create_all(bind=engine)
    
    # Seed default admin account
    _create_default_admin()
    
    # Seed testing data if DB is empty
    db = SessionLocal()
    try:
        from seed import seed_database
        seed_database(db)
    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        db.close()
        
    yield
    # Clean up on shutdown if needed

# ── Application Initialization ────────────────────────────────────────────────
app = FastAPI(title="Placement Portal API", lifespan=lifespan)

# ── CORS setup ───────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount Static Files ────────────────────────────────────────────────────────
# This allows serving uploaded files directly, or we can use the files router.
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ── Register routers ──────────────────────────────────────────────────────────
# We will import these after we rewrite them.
from routes.auth import auth_bp
from routes.student import student_bp
from routes.company import company_bp
from routes.admin import admin_bp
from routes.files import files_bp

app.include_router(auth_bp)
app.include_router(student_bp)
app.include_router(company_bp)
app.include_router(admin_bp)
app.include_router(files_bp)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
