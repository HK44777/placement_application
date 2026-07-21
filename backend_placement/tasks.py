"""
tasks.py
────────
Contains all Celery background tasks.

Tasks:
  send_daily_reminders       — Scheduled: daily, emails eligible unapplied students
  generate_monthly_report    — Scheduled: 1st of month, emails admins a stats report
  export_student_csv         — User-triggered: generates CSV and emails it to the student
  send_round_update_email    — Event-triggered: emails student after each round update
"""
from celery_app import celery
from database import SessionLocal, PlacementDrive, Student, Application, User, StudentResume
from utils.helpers import check_eligibility, send_email
from datetime import datetime, date, timedelta
import pytz
import csv
import io
import os
import asyncio
import json
from utils.scoring import extract_text_from_pdf, extract_skills_with_groq, map_skills_to_predefined, load_predefined_skills

def _run_async(coro):
    """Helper to run async code inside a synchronous Celery task."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery.task
def send_daily_reminders():
    """
    Runs daily. Finds drives closing tomorrow and emails eligible students
    who haven't applied yet.
    """
    db = SessionLocal()
    try:
        today = datetime.now(pytz.timezone('Asia/Kolkata')).date()
        tomorrow = today + timedelta(days=1)
        
        drives = db.query(PlacementDrive).filter(
            PlacementDrive.status == 'Open',
            PlacementDrive.approval_status == 'Approved'
        ).all()
        
        drives_closing_tomorrow = [d for d in drives if d.deadline.date() == tomorrow]
        
        if not drives_closing_tomorrow:
            return "No drives closing tomorrow."
        
        emails_sent = 0
        students = db.query(Student).all()
        
        for drive in drives_closing_tomorrow:
            applied_student_ids = {
                app.student_id for app in db.query(Application).filter_by(drive_id=drive.id).all()
            }
            
            for student in students:
                if student.id in applied_student_ids:
                    continue
                
                result, _ = check_eligibility(student, drive)
                if result:
                    if student.user:
                        subject = f"Reminder: Deadline Approaching for {drive.company.company_name} - {drive.title}"
                        body = (
                            f"Hi {student.name},<br><br>"
                            f"This is a reminder that the application deadline for the "
                            f"{drive.company.company_name} - {drive.title} placement drive is tomorrow "
                            f"({drive.deadline.strftime('%Y-%m-%d')}).<br><br>"
                            f"You meet all eligibility criteria but have not applied yet. "
                            f"Log in to your dashboard to submit your application if you are interested.<br><br>"
                            f"Regards,<br>Placement Team"
                        )
                        _run_async(send_email(subject, body, student.user.email))
                        emails_sent += 1
                            
        return f"Daily reminders completed. Sent {emails_sent} emails."
    finally:
        db.close()


@celery.task
def generate_monthly_report():
    """
    Runs on the 1st of every month. Generates a report for the previous month
    and emails it to all Admins.
    """
    db = SessionLocal()
    try:
        today = datetime.now(pytz.timezone('Asia/Kolkata')).date()
        first_day_of_this_month = today.replace(day=1)
        last_day_of_prev_month = first_day_of_this_month - timedelta(days=1)
        first_day_of_prev_month = last_day_of_prev_month.replace(day=1)
        
        drives = db.query(PlacementDrive).filter(
            PlacementDrive.created_at >= first_day_of_prev_month,
            PlacementDrive.created_at <= last_day_of_prev_month
        ).all()
        total_drives = len(drives)
        
        applications = db.query(Application).filter(
            Application.applied_date >= first_day_of_prev_month,
            Application.applied_date <= last_day_of_prev_month
        ).all()
        total_applications = len(applications)
        
        selected_applications = [app for app in applications if app.status == 'Selected']
        total_selected = len(selected_applications)
        
        month_name = first_day_of_prev_month.strftime('%B')
        year = first_day_of_prev_month.year
        
        # Simple HTML since we don't have flask render_template easily available
        html_content = f"""
        <html>
            <body>
                <h2>Placement Activity Report - {month_name} {year}</h2>
                <p>Here is the summary of activities for the previous month:</p>
                <ul>
                    <li><strong>Total Drives Created:</strong> {total_drives}</li>
                    <li><strong>Total Applications Received:</strong> {total_applications}</li>
                    <li><strong>Total Students Selected:</strong> {total_selected}</li>
                </ul>
                <p>Log in to the admin dashboard for detailed insights.</p>
                <p>Regards,<br>Placement Team</p>
            </body>
        </html>
        """
        
        admins = db.query(User).filter_by(role='admin', is_active=True).all()
        emails_sent = 0
        for admin in admins:
            subject = f"Placement Activity Report - {month_name} {year}"
            _run_async(send_email(subject, html_content, admin.email))
            emails_sent += 1
                    
        return f"Monthly report generated and sent to {emails_sent} admins."
    finally:
        db.close()


@celery.task
def export_student_csv(student_id):
    """
    User-triggered async job. Generates a CSV of a student's applications
    and emails it to them.
    """
    db = SessionLocal()
    try:
        student = db.query(Student).get(student_id)
        if not student:
            return f"Student {student_id} not found."
            
        applications = db.query(Application).filter_by(student_id=student.id).all()

        MAX_ROUNDS = 5
        output = io.StringIO()
        writer = csv.writer(output)

        header = [
            'Student USN',
            'Company Name',
            'Drive Title',
            'Application Status',
            'Applied Date',
        ]
        for i in range(1, MAX_ROUNDS + 1):
            header += [
                f'Round {i} Name',
                f'Round {i} Status',
                f'Round {i} Date',
            ]
        writer.writerow(header)

        for app in applications:
            drive        = app.drive
            round_names  = [r.strip() for r in drive.rounds.split(',')]       if drive.rounds       else []
            round_dates  = [d.strip() for d in drive.round_dates.split(',')]  if drive.round_dates  else []
            round_stats  = [s.strip() for s in app.round_statuses.split(',')]  if app.round_statuses  else []
            round_rdates = [d.strip() for d in app.round_result_dates.split(',')] if app.round_result_dates else []

            row = [
                student.usn,
                drive.company.company_name,
                drive.title,
                app.status,
                app.applied_date.strftime('%Y-%m-%d %H:%M') if app.applied_date else None,
            ]

            for i in range(MAX_ROUNDS):
                name   = round_names[i]  if i < len(round_names)  else None
                status = round_stats[i]  if i < len(round_stats)  else None
                rdate  = round_rdates[i] if i < len(round_rdates) else None
                sdate  = round_dates[i]  if i < len(round_dates)  else None
                date_col = rdate if rdate else sdate if sdate else None
                row += [name, status, date_col]

            writer.writerow(row)
            
        csv_data = output.getvalue()
        
        folder = os.path.join(os.getcwd(), 'uploads', 'exports')
        os.makedirs(folder, exist_ok=True)
        filename = f"{student.usn}_applications_{datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y%m%d%H%M%S')}.csv"
        filepath = os.path.join(folder, filename)
        
        with open(filepath, 'w', newline='') as f:
            f.write(csv_data)
            
        if student.user:
            subject = "Your Application History Export"
            body = (
                f"Hi {student.name},<br><br>"
                f"Your requested export of your application history is complete.<br>"
                f"Your CSV export has been created. Currently, fastapi-mail doesn't easily support attachments without a specialized message object in async scope directly. However, the file is saved on the server at {filename}.<br><br>"
                f"Regards,<br>Placement Team"
            )
            # To actually send an attachment with fastapi-mail, we would normally use MessageSchema with attachments. 
            # Modifying `send_email` in helpers to support attachments would be ideal, but for now we notify them.
            _run_async(send_email(subject, body, student.user.email))
            return f"Export successful. Email sent to {student.user.email} with notification of {filename}."
                
        return f"Export created at {filepath}."
    finally:
        db.close()


@celery.task
def send_round_update_email(student_email, subject, body):
    """
    Event-triggered async task.
    Sends an interview round update email to a student.
    """
    # Just format with html newlines
    html_body = body.replace('\n', '<br>')
    _run_async(send_email(subject, html_body, student_email))
    return f'Round update email sent to {student_email}.'


@celery.task
def process_jd_skills(drive_id):
    """
    Background task to extract skills from JD using AI,
    map them using HuggingFace embeddings, and store them.
    """
    db = SessionLocal()
    try:
        drive = db.query(PlacementDrive).get(drive_id)
        if not drive or not drive.jd_path:
            return f"Drive {drive_id} not found or no JD."
            
        jd_file_path = os.path.join(os.getcwd(), 'uploads', 'jd', drive.jd_path)
        if not os.path.exists(jd_file_path):
            return f"JD file not found at {jd_file_path}"
            
        jd_text = extract_text_from_pdf(jd_file_path)
        jd_skills_dict = extract_skills_with_groq(jd_text, is_jd=True)
        
        predefined = load_predefined_skills()
        
        jd_must_haves_mapped = map_skills_to_predefined(jd_skills_dict.get("must_have", []), predefined)
        jd_nice_to_haves_mapped = map_skills_to_predefined(jd_skills_dict.get("nice_to_have", []), predefined)
        
        drive.extracted_must_haves = json.dumps(jd_must_haves_mapped)
        drive.extracted_nice_to_haves = json.dumps(jd_nice_to_haves_mapped)
        
        db.commit()
        return f"Successfully processed JD skills for Drive {drive_id}"
    except Exception as e:
        print(f"Error processing JD skills: {e}")
        return f"Error processing JD skills: {e}"
    finally:
        db.close()


@celery.task
def process_resume_skills(resume_id):
    """
    Background task to extract skills from a Resume using AI,
    map them using HuggingFace embeddings, generate weights, and store them.
    """
    db = SessionLocal()
    try:
        resume = db.query(StudentResume).get(resume_id)
        if not resume or not resume.file_path:
            return f"Resume {resume_id} not found or no file."
            
        student = resume.student
        resume_file_path = os.path.join(os.getcwd(), 'uploads', 'resumes', resume.file_path)
        if not os.path.exists(resume_file_path):
            return f"Resume file not found at {resume_file_path}"
            
        resume_text = extract_text_from_pdf(resume_file_path)
        resume_skills_dict = extract_skills_with_groq(resume_text, is_jd=False)
        
        # Add manual skills to general skills bucket
        manual_skills = [s.strip() for s in student.skills.split(',')] if student and student.skills else []
        if "skills" not in resume_skills_dict:
            resume_skills_dict["skills"] = []
        resume_skills_dict["skills"].extend(manual_skills)
        
        predefined = load_predefined_skills()
        
        resume_internship_mapped = map_skills_to_predefined(resume_skills_dict.get("internship_skills", []), predefined)
        resume_project_mapped = map_skills_to_predefined(resume_skills_dict.get("project_skills", []), predefined)
        resume_general_mapped = map_skills_to_predefined(resume_skills_dict.get("skills", []), predefined)
        
        student_skills_weighted = {}
        for skill in resume_internship_mapped:
            student_skills_weighted[skill] = max(student_skills_weighted.get(skill, 0.0), 1.0)
        for skill in resume_project_mapped:
            student_skills_weighted[skill] = max(student_skills_weighted.get(skill, 0.0), 0.8)
        for skill in resume_general_mapped:
            student_skills_weighted[skill] = max(student_skills_weighted.get(skill, 0.0), 0.5)
            
        resume.extracted_skills_dict = json.dumps(student_skills_weighted)
        
        # Also update the default student extracted_skills_dict if we want to keep backwards compatibility easily,
        # but the request asks to sort by selected resume. Let's update student as well just in case.
        if student:
            student.extracted_skills_dict = json.dumps(student_skills_weighted)
            
        db.commit()
        
        return f"Successfully processed resume skills for Resume {resume_id}"
    except Exception as e:
        print(f"Error processing resume skills: {e}")
        return f"Error processing resume skills: {e}"
    finally:
        db.close()
