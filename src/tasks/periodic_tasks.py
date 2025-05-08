import logging
import time
from datetime import datetime
from typing import List
from ..celery_app import celery_app
from ..services.email_service import EmailService

logger = logging.getLogger(__name__)


# Envoi quotidien de rapport
@celery_app.task(name="src.tasks.periodic_tasks.send_daily_report")
def send_daily_report():
    """
    Tâche périodique pour envoyer un rapport quotidien
    Programmée via Celery Beat
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Exécution de la tâche périodique send_daily_report à {current_time}")

    # Simuler la génération d'un rapport
    report = f"""
    Rapport quotidien - {current_time}
    ================================
    
    Statistiques du jour:
    - Emails envoyés: 547
    - Taux d'ouverture: 32.4%
    - Taux de clic: 12.8%
    
    Cordialement,
    Le système automatique
    """

    # Envoyer le rapport aux administrateurs
    admin_emails = ["admin1@example.com", "admin2@example.com"]
    for admin in admin_emails:
        result = EmailService.send_email(
            to_email=admin,
            subject=f"Rapport quotidien - {datetime.now().strftime('%Y-%m-%d')}",
            body=report,
        )

        if not result:
            logger.error(f"Échec de l'envoi du rapport quotidien à {admin}")

    return True


# Envoi de rappels aux utilisateurs inactifs
@celery_app.task(name="src.tasks.periodic_tasks.send_inactivity_reminders")
def send_inactivity_reminders() -> List[bool]:

    # Simulation de récupération d'utilisateurs inactifs
    inactive_users = [
        {"email": "user1@example.com", "name": "User 1", "days_inactive": 15},
        {"email": "user2@example.com", "name": "User 2", "days_inactive": 20},
        {"email": "user3@example.com", "name": "User 3", "days_inactive": 30},
    ]

    results = []

    for user in inactive_users:
        if user["days_inactive"] > 25:
            subject = "Nous vous avons manqué !"
        else:
            subject = "Restez connecté avec nous"

        body = f"""
        Bonjour {user['name']},
        
        Nous avons remarqué que vous n'avez pas utilisé notre service 
        depuis {user['days_inactive']} jours. Reconnectez-vous pour 
        découvrir nos nouvelles fonctionnalités !
        
        Cordialement,
        L'équipe
        """

        # Envoi du rappel
        result = EmailService.send_email(
            to_email=user["email"], subject=subject, body=body
        )
        results.append(result)

    logger.info(
        f"Rappels d'inactivité envoyés à {sum(results)}/{len(results)} utilisateurs"
    )
    return results
