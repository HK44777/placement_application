"""
celery_app.py
─────────────
Initializes Celery and sets up the beat schedule.
"""

from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

# Explicitly load .env from the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

def make_celery(app_name=__name__):
    # Determine the Redis URL from the environment
    redis_url = os.environ.get('REDIS_URL')
    
    celery = Celery(
        app_name,
        backend=redis_url,
        broker=redis_url,
        include=['tasks']
    )
    
    # Configure timezone
    celery.conf.timezone = 'Asia/Kolkata'
    
    # Configure the Beat Schedule
    celery.conf.beat_schedule = {
        'daily-reminders': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=19, minute=0),  # Every day at 09:00
        },
        'monthly-activity-report': {
            'task': 'tasks.generate_monthly_report',
            'schedule': crontab(hour=19, minute=50),  # 1st of month at 08:00
        },
    }
    
    return celery

celery = make_celery('placement_celery')
