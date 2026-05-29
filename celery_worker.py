import os
from celery import Celery, Task
from celery.schedules import crontab
from app import app

# Grab the Render Redis URL, default to localhost for testing
base_redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")

# Initialize the celery app
celery_app = Celery(
    'tasks',
    broker=f'{base_redis_url}/1',   
    backend=f'{base_redis_url}/2',  
    include=['tasks']                    
)

celery_app.conf.timezone = 'Asia/Kolkata'
celery_app.conf.enable_utc = False


# --- THE MASTER SCHEDULER ---
celery_app.conf.beat_schedule = {
    # 1. The Daily Patient Reminders
    'send-daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0), 
    },
    
    # 2. The Monthly Admin Report (We will build this next)
    'generate-monthly-report': {
        'task': 'tasks.generate_monthly_report',
        'schedule': crontab(minute='*'),
    }
}


# The "VIP Pass" logic to let Celery talk to your database
class FlaskTask(Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return super().__call__(*args, **kwargs)
        
# Apply the VIP pass to our Celery app
celery_app.Task = FlaskTask