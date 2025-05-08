#!/usr/bin/env python
"""
Script pour démarrer un worker Celery
Usage: python celery_worker.py
"""

import os
import logging
from src.celery_app import celery_app


logger = logging.getLogger(__name__)

if __name__ == '__main__':
  logger.info("Démarrage du worker Celery...")

  # Configuration des arguments pour le worker
  worker_args = [
      'worker',
      '--loglevel=INFO',
      '--concurrency=4',  # Nombre de processus worker
      '--prefetch-multiplier=1',  # Prendre une tâche à la fois
  ]

  # Démarrer le worker
  celery_app.worker_main(worker_args)
