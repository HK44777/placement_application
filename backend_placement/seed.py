import json
from datetime import datetime, timedelta
import pytz
from database import User, Company, Student, PlacementDrive, Application, StudentResume

def seed_database(db):
    print("Checking if database needs seeding...")
    if db.query(Student).count() > 0:
        print("Database already seeded with students. Skipping seed.")
        return

    print("Seeding database...")
    now = datetime.now(pytz.timezone('Asia/Kolkata')).replace(tzinfo=None)
    
    # 1. Create Companies
    companies_data = [
        {"name": "Google", "status": "Approved", "type": "Product"},
        {"name": "Microsoft", "status": "Approved", "type": "Product"},
        {"name": "Amazon", "status": "Approved", "type": "Product"},
        {"name": "Innovate Startup", "status": "Pending", "type": "Startup"},
        {"name": "Tech Mahindra", "status": "Pending", "type": "Service"},
    ]
    companies = []
    for i, c_data in enumerate(companies_data):
        user = User(email=f"{c_data['name'].lower().replace(' ', '')}@example.com", role='company', is_active=True)
        user.set_password('321321321')
        db.add(user)
        db.flush() # flush to get user.id
        
        company = Company(
            user_id=user.id,
            company_name=c_data['name'],
            company_type=c_data['type'],
            hr_contact=f"HR {c_data['name']}",
            approval_status=c_data['status']
        )
        db.add(company)
        db.flush()
        companies.append(company)

    # 2. Create Students
    students_data = [
        {"name": "Alice Sharma", "usn": "1RN20CS001", "cgpa": 9.5, "branch": "Computer Science"},
        {"name": "Bob Kumar", "usn": "1RN20IS010", "cgpa": 8.2, "branch": "Information Science"},
        {"name": "Charlie Singh", "usn": "1RN20EC045", "cgpa": 7.8, "branch": "Electronics"},
        {"name": "David Raj", "usn": "1RN20ME050", "cgpa": 6.5, "branch": "Mechanical"},
        {"name": "Eva Reddy", "usn": "1RN20CS105", "cgpa": 9.0, "branch": "Computer Science"},
    ]
    students = []
    for s_data in students_data:
        user = User(email=f"{s_data['name'].lower().replace(' ', '')}@example.com", role='student', is_active=True)
        user.set_password('321321321')
        db.add(user)
        db.flush()
        
        # Simple generic extracted skills
        generic_skills = json.dumps({"Python": 1.0, "C++": 0.8, "SQL": 0.5})
        
        student = Student(
            user_id=user.id,
            name=s_data['name'],
            usn=s_data['usn'],
            cgpa=s_data['cgpa'],
            graduation_year=2024,
            branch=s_data['branch'],
            skills="Python, C++, SQL",
            extracted_skills_dict=generic_skills
        )
        db.add(student)
        db.flush()
        students.append(student)

        # Add resumes
        # Give Alice two resumes to test the dropdown logic
        if s_data['name'] == "Alice Sharma":
            frontend_skills = json.dumps({"ReactJS": 1.0, "JavaScript": 1.0, "HTML": 0.8, "CSS": 0.8})
            backend_skills = json.dumps({"Python": 1.0, "Django": 1.0, "PostgreSQL": 0.8})
            
            res1 = StudentResume(
                student_id=student.id,
                name="Frontend Resume",
                file_path="mock_resume_1.pdf",
                extracted_skills_dict=frontend_skills
            )
            res2 = StudentResume(
                student_id=student.id,
                name="Backend Resume",
                file_path="mock_resume_2.pdf",
                extracted_skills_dict=backend_skills
            )
            db.add_all([res1, res2])
        else:
            # Everyone else gets 1 resume
            res = StudentResume(
                student_id=student.id,
                name="Main Resume",
                file_path=f"mock_resume_{student.usn}.pdf",
                extracted_skills_dict=generic_skills
            )
            db.add(res)
            
    # 3. Create Drives
    drives_data = [
        {"company": companies[0], "title": "SDE Intern", "ctc": 15.0, "status": "Open", "approval": "Approved", "must": ["ReactJS", "JavaScript"], "nice": ["AWS"]},
        {"company": companies[1], "title": "Data Scientist", "ctc": 18.0, "status": "Closed", "approval": "Approved", "must": ["Python", "SQL"], "nice": ["Machine Learning"]},
        {"company": companies[0], "title": "Backend Dev", "ctc": 14.0, "status": "Open", "approval": "Approved", "must": ["Python", "Django", "PostgreSQL"], "nice": ["Docker"]},
        {"company": companies[2], "title": "Cloud Architect", "ctc": 22.0, "status": "Open", "approval": "Approved", "must": ["AWS", "Linux"], "nice": ["Python"]},
    ]
    
    drives = []
    for d in drives_data:
        drive = PlacementDrive(
            company_id=d['company'].id,
            title=d['title'],
            ctc=d['ctc'],
            min_cgpa=7.0,
            allowed_branches="Computer Science,Information Science,Electronics",
            allowed_grad_years="2024,2025",
            extracted_must_haves=json.dumps(d['must']),
            extracted_nice_to_haves=json.dumps(d['nice']),
            deadline=now + timedelta(days=10) if d['status'] == "Open" else now - timedelta(days=5),
            status=d['status'],
            approval_status=d['approval'],
            rounds="Aptitude,Technical,HR",
            round_dates="2024-01-01,2024-01-02,2024-01-03"
        )
        db.add(drive)
        db.flush()
        drives.append(drive)
        
    # 4. Create some Applications
    # Alice applies to Google SDE (Drive 0) and Microsoft Data Scientist (Drive 1)
    app1 = Application(
        student_id=students[0].id,
        drive_id=drives[0].id,
        status='Applied',
        current_round_index=0,
        round_statuses='Pending,Pending,Pending',
        custom_resume_path="mock_resume_1.pdf"
    )
    app2 = Application(
        student_id=students[0].id,
        drive_id=drives[1].id,
        status='Selected',
        current_round_index=2,
        round_statuses='Cleared,Cleared,Cleared',
        custom_resume_path="mock_resume_2.pdf"
    )
    db.add_all([app1, app2])

    db.commit()
    print("Database seeded successfully with test data.")
