import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

# Configuration Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Configuration du timeout des tâches en secondes
TASK_TIMEOUT = 600

# Configuration des tentatives et délais de retry
MAX_RETRIES = 3
RETRY_DELAY = 60  # en secondes

# Configuration de la simulation d'emails
EMAIL_SIMULATION_DELAY = 10  # secondes de délai pour simuler l'envoi
EMAIL_FAILURE_RATE = 0.5    # taux d'échec simulé (20%)

# Configuration de Flower
FLOWER_PORT = 5555
FLOWER_HOST = "0.0.0.0"