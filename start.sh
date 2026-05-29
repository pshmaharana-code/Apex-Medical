#!/bin/bash
# Start Celery in the background
celery -A celery_worker.celery_app worker -B --loglevel=info &
# Start Gunicorn in the foreground
gunicorn app:app