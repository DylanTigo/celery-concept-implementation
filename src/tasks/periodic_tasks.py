import logging
import time
from datetime import datetime
from typing import List
from ..celery_app import celery_app
from ..services.email_service import EmailService

logger = logging.getLogger(__name__)

# Tâche périodique 1: Envoi quotidien de rapport
@celery_app.task(name="src.tasks.periodic_tasks.send_daily_report")
def send_daily_report() -> bool:
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
            body=report
        )
        
        if not result:
            logger.error(f"Échec de l'envoi du rapport quotidien à {admin}")
    
    return True


# Tâche périodique 2: Nettoyage des anciennes tâches
@celery_app.task(name="src.tasks.periodic_tasks.clean_old_tasks")
def clean_old_tasks() -> int:
    """
    Tâche périodique pour nettoyer les anciennes tâches et résultats
    Programmée via Celery Beat
    """
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Exécution de la tâche périodique clean_old_tasks à {current_time}")
    
    # Dans un cas réel, on pourrait utiliser la fonction celery_app.backend.cleanup()
    # pour nettoyer les résultats dans Redis. Ici, on simule juste.
    
    # Simulation du nettoyage
    time.sleep(1)
    cleaned_count = 25  # Nombre fictif de tâches nettoyées
    
    logger.info(f"Nettoyage terminé: {cleaned_count} tâches supprimées")
    return cleaned_count


# Tâche périodique 3: Envoi de rappels aux utilisateurs inactifs
@celery_app.task(name="src.tasks.periodic_tasks.send_inactivity_reminders")
def send_inactivity_reminders() -> List[bool]:
    """
    Tâche périodique pour envoyer des rappels aux utilisateurs inactifs
    Cette tâche peut être programmée manuellement ou via Celery Beat
    """
    # Simulation de récupération d'utilisateurs inactifs
    inactive_users = [
        {"email": "user1@example.com", "name": "User 1", "days_inactive": 15},
        {"email": "user2@example.com", "name": "User 2", "days_inactive": 20},
        {"email": "user3@example.com", "name": "User 3", "days_inactive": 30},
    ]
    
    results = []
    
    for user in inactive_users:
        # Personnalisation du message selon la durée d'inactivité
        if user["days_inactive"] > 25:
            subject = "Nous vous avons manqué !"
            urgency = "urgent"
        else:
            subject = "Restez connecté avec nous"
            urgency = "normal"
            
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
            to_email=user["email"],
            subject=subject,
            body=body
        )
        
        results.append(result)
        
    logger.info(f"Rappels d'inactivité envoyés à {sum(results)}/{len(results)} utilisateurs")
    return results