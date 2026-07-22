# 🎓 Placement Portal

A full-stack campus placement management system that connects **students**, **companies**, and **placement administrators** on a single platform. Students discover and apply for placement drives, companies post and manage them, and admins oversee the entire process — all powered by an AI-driven resume scoring engine.

---

## 📋 Table of Contents

- [What It Does](#-what-it-does)
- [System Flow](#-system-flow)
- [Features](#-features)
- [AI & Automation Engine](#-ai--automation-engine)
- [Tech Stack](#-tech-stack)
- [AWS Services](#-aws-services)
- [Project Structure](#-project-structure)
- [Environment Variables](#-environment-variables)
- [Running Locally](#-running-locally)
- [Deployment Architecture](#-deployment-architecture)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Seed Data](#-seed-data)
- [Default Credentials](#-default-credentials)

---

## 🔍 What It Does

The Placement Portal is a role-based platform with three actors:

- **Students** — Register, upload resumes, browse open drives, apply with eligibility auto-check, and track application status through each interview round.
- **Companies** — Register (pending admin approval), post placement drives with detailed eligibility criteria and JD upload, and review AI-scored applicant shortlists.
- **Admins** — Approve company registrations, manage all users and drives, and access a statistics dashboard.

---

## 🔄 System Flow

### End-to-End User Journey

```
┌─────────────────────────────────────────────────────────────────────────┐
│  ONBOARDING                                                             │
│                                                                         │
│  Student Registers ──────────────────────────────────────── Active     │
│                                                                         │
│  Company Registers ──► Admin Reviews ──► Approve / Reject              │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  DRIVE CREATION (Company)                                               │
│                                                                         │
│  Company posts a Drive (title, CTC, eligibility, deadline, JD PDF)     │
│                ↓                                                        │
│  Background Job triggers:                                               │
│  Groq AI extracts Must-Have & Nice-to-Have skills from the JD PDF      │
│  SentenceTransformer maps them to a predefined skill taxonomy           │
│  Extracted skills stored in DB against the Drive                        │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  STUDENT APPLIES                                                        │
│                                                                         │
│  Student browses open, approved drives                                  │
│  Backend auto-checks eligibility (CGPA, branch, graduation year)       │
│  Student selects which resume to apply with (can have multiple)        │
│  Student submits application                                            │
│                ↓                                                        │
│  System computes AI Match Score:                                        │
│  Student's extracted resume skills (weighted by context)               │
│     vs. JD's Must-Have & Nice-to-Have skills                           │
│  Score saved against the application                                    │
│                                                                         │
│  ★ The score is VISIBLE TO COMPANIES & ADMINS, NOT to the student ★   │
│    Students only see their application status per round                 │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  SELECTION PROCESS (Company)                                            │
│                                                                         │
│  Company views applicant list sorted by AI Match Score                 │
│  Company updates round results: Aptitude → Technical → HR              │
│  Each round update triggers an email notification to the student       │
│  Company marks final status: Selected / Rejected / On Hold             │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  AUTOMATED BACKGROUND JOBS (Celery)                                     │
│                                                                         │
│  Daily    → Email eligible unapplied students about drives closing      │
│             tomorrow                                                    │
│  Monthly  → Email admins a placement activity summary report            │
│  On-demand → Student can export their full application history as CSV   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### Student
- Register with personal details, skills, CGPA, branch, and graduation year
- Upload multiple resumes and name them (e.g., "Frontend Resume", "Backend Resume")
- Browse all open, admin-approved placement drives
- View full drive details: company info, CTC, eligibility criteria, rounds, deadline
- Apply to a drive by selecting which resume to use (eligibility auto-checked)
- Track application status through each interview round in real time
- Export full application history as a CSV (emailed automatically)

### Company
- Register with company details (pending admin approval before going live)
- Post placement drives with:
  - Eligibility filters: min CGPA, allowed branches, graduation year
  - Interview rounds definition
  - Job Description PDF upload
- View AI-scored applicant list for each drive (sorted by match percentage)
- Update round results for each applicant (triggers email to student)
- Mark final selection status (Selected / Rejected / On Hold)
- Edit or delete drives, update company profile

### Admin
- Approve or reject company registrations
- View all registered students and companies
- Monitor all placement drives across all companies
- Dashboard with key stats: total drives, applications, companies, placements
- Full control over the platform

---

## 🤖 AI & Automation Engine

### Resume Scoring — How It Works

The AI scoring pipeline runs entirely in the **background** using Celery tasks, so the API response is never blocked.

**Step 1 — JD Processing (when company uploads a drive)**
```
Company uploads JD PDF
        ↓
Celery Task: process_jd_skills
        ↓
PyPDF2 extracts raw text from the PDF
        ↓
Groq API (LLM) reads the JD and outputs:
  - "must_have" skills list
  - "nice_to_have" skills list
        ↓
SentenceTransformer (all-MiniLM-L6-v2) maps each extracted skill
to the closest skill in the platform's predefined skill taxonomy
        ↓
Mapped skills stored in DB against the Drive
```

**Step 2 — Resume Processing (when student uploads a resume)**
```
Student uploads resume PDF
        ↓
Celery Task: process_resume_skills
        ↓
PyPDF2 extracts raw text from the PDF
        ↓
Groq API (LLM) reads the resume and categorises skills into:
  - "internship_skills"  → highest weight (1.0) — proven real-world experience
  - "project_skills"     → medium weight (0.8) — applied in a project
  - "general_skills"     → base weight (0.5) — self-listed or mentioned once
        ↓
SentenceTransformer maps each skill to the predefined taxonomy
        ↓
Weighted skill dictionary stored in DB against the resume
```

**Step 3 — Match Scoring (when student applies)**
```
Student applies to a drive
        ↓
Backend compares:
  Student's weighted resume skills dict
    vs.
  Drive's must-have & nice-to-have skills
        ↓
Match % calculated:
  Must-have coverage contributes more to the score
  Nice-to-have coverage adds bonus points
        ↓
Score stored in the Application record
        ↓
Visible to Company & Admin in the applicant list (sorted by score)
Students do NOT see their own score — they only see round status
```

### Why this approach?
- **Groq** handles semantic understanding (reads natural language, categorises skills correctly)
- **SentenceTransformer** normalises skill names (e.g., "React.js" and "ReactJS" map to the same taxonomy entry)
- **Skill weighting** rewards real experience over self-listing
- **Predefined taxonomy** ensures scores are consistent and comparable across resumes

---

## 🛠 Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **FastAPI** (Python) | REST API framework — async, fast, auto docs |
| **PostgreSQL** | Primary relational database |
| **SQLAlchemy** | ORM for all database models and queries |
| **Redis** | Message broker for Celery task queue |
| **Celery Worker** | Processes async background tasks (resume/JD scoring, emails, exports) |
| **Celery Beat** | Cron-like scheduler (daily reminders, monthly reports) |
| **SentenceTransformer** `all-MiniLM-L6-v2` | HuggingFace ML model — skill embedding and similarity matching |
| **Groq API** | LLM for skill extraction from PDF text |
| **PyPDF2** | Extract raw text from uploaded PDFs |
| **PyJWT** | JWT-based stateless authentication |
| **FastAPI-Mail** | HTML email notifications via SMTP |
| **boto3** | AWS SDK — S3 file storage integration |
| **python-dotenv** | Environment variable management |

### Frontend
| Technology | Purpose |
|---|---|
| **Vue 3** | Progressive frontend framework |
| **Vite** | Lightning-fast dev server and build tool |
| **Vue Router** | Client-side SPA routing |
| **Chart.js** | Analytics and statistics charts on admin dashboard |

### Infrastructure
| Technology | Purpose |
|---|---|
| **Docker** | Containerisation of all backend services |
| **Docker Compose** | Multi-container orchestration on EC2 |
| **AWS EC2** (`t3.micro`) | Backend server hosting |
| **AWS ECR** | Private Docker image registry |
| **Vercel** | Frontend hosting with auto-deploy |
| **GitHub Actions** | CI/CD — build on GitHub, deploy to EC2 |

---

## ☁️ AWS Services

| Service | How It Is Used |
|---|---|
| **EC2** (`t3.micro`, `eu-north-1`) | Runs all 4 Docker containers (FastAPI, Celery Worker, Celery Beat, Redis) behind port 80 |
| **RDS** (PostgreSQL, `eu-north-1`) | Managed PostgreSQL database hosted on a separate AWS-managed machine. EC2 connects to it via `DATABASE_URL` in `.env`. 
| **ECR** (Elastic Container Registry) | Stores the private Docker image. GitHub Actions builds and pushes to ECR. EC2 pulls from ECR. The image is fully private — inaccessible to anyone without IAM credentials |
| **IAM** | IAM User with `AdministratorAccess` used by GitHub Actions to push to ECR. EC2 uses `aws configure` credentials to pull from ECR |
| **S3** *(integration ready)* | boto3 is configured for S3 file storage. Resume and JD PDFs are intended to be stored in S3 instead of local disk for persistence across deployments |

---

## 📁 Project Structure

```
placement_application/
├── backend_placement/
│   ├── app.py                  # FastAPI entry point, CORS, router registration, DB init
│   ├── database.py             # SQLAlchemy models: User, Student, Company, Drive, Application
│   ├── schemas.py              # Pydantic request/response validation schemas
│   ├── tasks.py                # Celery tasks: scoring, emails, CSV export, scheduled jobs
│   ├── celery_app.py           # Celery configuration (broker, beat schedule)
│   ├── seed.py                 # Auto-seeds DB on first startup with test data
│   ├── Dockerfile              # Docker image — includes ML model pre-download
│   ├── predefined_skills.txt   # Taxonomy of skills used for ML matching
│   ├── routes/
│   │   ├── auth.py             # Login, register, JWT issue and refresh
│   │   ├── student.py          # Student profile, resume upload, drive browse, applications
│   │   ├── company.py          # Company profile, drive CRUD, applicant management
│   │   ├── admin.py            # Admin dashboard, user management, drive oversight
│   │   └── files.py            # File upload and download endpoints
│   ├── utils/
│   │   ├── scoring.py          # Resume-JD skill extraction, mapping, and match scoring
│   │   └── helpers.py          # Eligibility check, email sender utility
│   └── uploads/                # Local file storage for resumes, JDs, CSV exports
│
├── frontend_placement/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Home.vue                    # Landing page
│   │   │   ├── Login.vue                   # Unified login for all roles
│   │   │   ├── StudentRegister.vue         # Student registration form
│   │   │   ├── CompanyRegister.vue         # Company registration form
│   │   │   ├── student/                    # Student dashboard (home, job detail, profile, applications)
│   │   │   ├── company/                    # Company dashboard (drives, applicants, profile)
│   │   │   └── admin/                      # Admin dashboard (students, companies, drives, stats)
│   │   ├── components/                     # Shared reusable components
│   │   ├── router/                         # Vue Router — role-based route guards
│   │   ├── store/                          # Global state (auth, user info)
│   │   └── composables/                   # Reusable Vue composition functions
│   ├── vercel.json                          # Vercel SPA routing config
│   └── vite.config.js                      # Vite proxy and build settings
│
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions: build image on GitHub → push to ECR → pull on EC2
│
├── docker-compose.yml          # Orchestrates: web, celery_worker, celery_beat, redis
├── requirements.txt            # All Python dependencies
└── .env                        # Environment variables (never committed to Git)
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# ── Database ──────────────────────────────────────────────
DATABASE_URL=postgresql://username:password@host:5432/dbname

# ── Security ──────────────────────────────────────────────
SECRET_KEY=your_jwt_secret_key_min_32_chars

# ── Redis / Celery ────────────────────────────────────────
REDIS_URL=redis://redis:6379/0

# ── Email (Gmail SMTP) ────────────────────────────────────
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_FROM=your_email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# ── AWS ───────────────────────────────────────────────────
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket_name
AWS_REGION=eu-north-1

# ── AI ────────────────────────────────────────────────────
GROQ_API_KEY=your_groq_api_key

# ── Frontend ──────────────────────────────────────────────
FRONTEND_URL=http://localhost:5173
```

---

## 💻 Running Locally

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Node.js](https://nodejs.org/) v18+ for the frontend
- A PostgreSQL database (local or cloud-hosted, e.g., Supabase free tier)

---

### Backend — Option 1: Docker (Recommended)

Starts all 4 services together: FastAPI, Redis, Celery Worker, Celery Beat.

```bash
# 1. Clone the repository
git clone https://github.com/HK44777/placement_application.git
cd placement_application

# 2. Create your .env file (copy from the section above and fill in values)

# 3. Build and start all services
docker compose up --build
```

> First build will take ~5-10 minutes — the Dockerfile downloads the `all-MiniLM-L6-v2` ML model (~90MB). Subsequent builds use Docker's cache and take seconds.

- **API Base URL:** `http://localhost:80`
- **Swagger Docs:** `http://localhost:80/docs`

---

### Backend — Option 2: Without Docker

```bash
# 1. Create and activate a Python virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# 2. Install all Python dependencies
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 3. Start Redis (Celery requires it — run in background via Docker)
docker run -d -p 6379:6379 redis:alpine

# 4. Start the FastAPI server
cd backend_placement
uvicorn app:app --reload --port 5000

# 5. In a new terminal — Start Celery Worker (handles background tasks)
cd backend_placement
celery -A celery_app.celery worker --loglevel=info

# 6. In another terminal — Start Celery Beat (scheduler for cron jobs)
cd backend_placement
celery -A celery_app.celery beat --loglevel=info
```

---

### Frontend

```bash
cd frontend_placement

# Install dependencies
npm install

# Start development server (proxies API calls to localhost:80)
npm run dev
```

Frontend available at: `http://localhost:5173`

---


### Required GitHub Secrets

| Secret | Description |
|---|---|
| `EC2_HOST` | EC2 public IP address |
| `EC2_USERNAME` | SSH username (`ubuntu`) |
| `EC2_SSH_KEY` | Full contents of the `.pem` private key file |
| `AWS_ACCESS_KEY_ID` | IAM user Access Key ID (for ECR push from GitHub) |
| `AWS_SECRET_ACCESS_KEY` | IAM user Secret Access Key |
| `AWS_REGION` | `eu-north-1` |

---

## 🌱 Seed Data

On **first startup**, the app automatically seeds the database with test data so you can explore all features immediately. Seeding is skipped if the database already has students.

### Seeded Companies

| Company | Type | Status | Login Email | Password |
|---|---|---|---|---|
| Google | Product | ✅ Approved | google@example.com | 321321321 |
| Microsoft | Product | ✅ Approved | microsoft@example.com | 321321321 |
| Amazon | Product | ✅ Approved | amazon@example.com | 321321321 |
| Innovate Startup | Startup | ⏳ Pending | innovatestartup@example.com | 321321321 |
| Tech Mahindra | Service | ⏳ Pending | techmahindra@example.com | 321321321 |

### Seeded Students

| Name | USN | CGPA | Branch | Login Email | Password |
|---|---|---|---|---|---|
| Alice Sharma | 1RN20CS001 | 9.5 | Computer Science | alicesharma@example.com | 321321321 |
| Bob Kumar | 1RN20IS010 | 8.2 | Information Science | bobkumar@example.com | 321321321 |
| Charlie Singh | 1RN20EC045 | 7.8 | Electronics | charliesingh@example.com | 321321321 |
| David Raj | 1RN20ME050 | 6.5 | Mechanical | davidraj@example.com | 321321321 |
| Eva Reddy | 1RN20CS105 | 9.0 | Computer Science | evareddy@example.com | 321321321 |

> Alice has **2 resumes** (Frontend Resume, Backend Resume) to test the resume-selection feature at apply time.

### Seeded Drives

| Company | Drive Title | CTC | Status | Must-Have Skills |
|---|---|---|---|---|
| Google | SDE Intern | 15 LPA | 🟢 Open | ReactJS, JavaScript |
| Microsoft | Data Scientist | 18 LPA | 🔴 Closed | Python, SQL |
| Google | Backend Dev | 14 LPA | 🟢 Open | Python, Django, PostgreSQL |
| Amazon | Cloud Architect | 22 LPA | 🟢 Open | AWS, Linux |

### Seeded Applications

| Student | Drive | Status |
|---|---|---|
| Alice Sharma | Google SDE Intern | Applied (Round 1 Pending) |
| Alice Sharma | Microsoft Data Scientist | ✅ Selected (All rounds cleared) |

---

## 🔑 Default Credentials

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@admin.com` | `admin123` |


---

## 📖 API Documentation

When the backend is running, interactive docs are available at:

- **Swagger UI** (try endpoints live): `http://localhost:80/docs`
- **ReDoc** (clean readable format): `http://localhost:80/redoc`
