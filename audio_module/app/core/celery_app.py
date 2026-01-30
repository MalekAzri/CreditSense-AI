"""
Configuration Celery pour le traitement asynchrone
"""
from celery import Celery
from app.core.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Initialiser Celery
celery_app = Celery(
    "audio_module",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['app.workers.audio_worker']  # Modules contenant les tâches
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max par tâche
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50
)

if __name__ == '__main__':
    celery_app.start()