#!/usr/bin/env python
"""
Script pour démarrer le scheduler Celery Beat
Usage: python celerybeat.py
"""

import logging
from src.celery_app import celery_app


logger = logging.getLogger(__name__)

if __name__ == '__main__':
  logger.info("Démarrage de Celery Beat...")

  # Configuration des arguments pour Beat
  beat_args = [
      'beat',
      '--loglevel=INFO',
      '--scheduler=celery.beat.PersistentScheduler',
      '--schedule=beat-schedule.db',
  ]

  # Démarrer Beat
  celery_app.start(beat_args)
