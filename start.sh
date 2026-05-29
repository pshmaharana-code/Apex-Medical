#!/bin/bash
# Start Celery in the background with only 1 worker to save memory
celery -A celery_worker.celery_app worker -B -c 1 --loglevel=info &

# Start Gunicorn in the foreground
gunicorn app:app