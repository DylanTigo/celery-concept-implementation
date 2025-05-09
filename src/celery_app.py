from celery import Celery
from celery.signals import task_failure
import logging
from .config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND


logger = logging.getLogger(__name__)

# Initialisation du Celery app
celery_app = Celery(
    'email_tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['src.tasks.email_tasks', 'src.tasks.periodic_tasks']
)

# Configuration du Celery app
celery_app.conf.update(
    # Résilience et tolérance aux pannes
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,

    # Persistance des résultats
    result_persistent=True,

    # Configuration de l'envoi des tâches
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',

    # Définition du fuseau horaire pour les tâches périodiques
    timezone='Africa/Douala',
    enable_utc=True,
)

# Configuration pour les tâches périodiques (Celery Beat)
celery_app.conf.beat_schedule = {
    'send-daily-report': {
        'task': 'src.tasks.periodic_tasks.send_daily_report',
        'schedule': 300.0,
    },
    'send-inactivity-reminders': {
        'task': 'src.tasks.periodic_tasks.send_inactivity_reminders',
        'schedule': 86400.0,  # Une fois par jour
    },
}


@task_failure.connect
def log_task_failure(sender=None, task_id=None, exception=None, **kwargs):
  logger.error(f"Task {task_id} failed: {exception}")
