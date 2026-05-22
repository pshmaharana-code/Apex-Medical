from celery import Celery, Task

from app import app

#Initialize the celery app
celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/1',   # The Pinboard (Incoming Tasks)
    backend='redis://localhost:6379/2',  # The Pickup Counter (Results)
    include=['tasks']                    # Tells Celery to look in tasks.py
)

# The "VIP Pass" logic to let Celery talk to your database
class FlaskTask(Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return super().__call__(*args, **kwargs)
        
# Apply the VIP pass to our Celery app
celery_app.Task = FlaskTask