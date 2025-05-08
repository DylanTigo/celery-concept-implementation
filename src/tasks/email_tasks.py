import logging
from typing import List, Dict
from celery import chain, group, chord
from celery.exceptions import MaxRetriesExceededError
from ..celery_app import celery_app
from ..services.email_service import EmailService
from ..config import MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)

# Tâche 1: Envoi d'un email simple avec gestion des retries
@celery_app.task(
    bind=True,
    name="send_single_email",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=MAX_RETRIES,
    default_retry_delay=RETRY_DELAY,
)
def send_single_email(
    self,
    to_email: str,
    subject: str,
    body: str,
) -> bool:
  
    result = EmailService.send_email(
        to_email=to_email,
        subject=subject,
        body=body,
    )
    
    if not result:
        logger.warning(f"Échec de l'envoi d'email à {to_email}, tentative de retry: {self.request.retries + 1}/{MAX_RETRIES}")
        raise Exception("Email sending failed")


# Tâche 2: Traitement parallèle - Envoi en masse 
@celery_app.task(name="process_bulk_emails")
def process_bulk_emails(
    recipients: List[str],
    subject: str,
    body: str
) -> Dict[str, bool]:
    """
    Tâche qui distribue l'envoi d'emails en masse vers des workers en parallèle
    """
    # Création d'un groupe de tâches individuelles
    email_tasks = group(
        send_single_email.s(recipient, subject, body)
        for recipient in recipients
    )
    
    # Exécution du groupe et récupération des résultats
    results = email_tasks.apply_async()
    task_results = results.get()
    
    # Construction du dictionnaire de résultats
    return dict(zip(recipients, task_results))


# Tâche 3: Tâche de finalisation pour générer un rapport
@celery_app.task(name="generate_email_report")
def generate_email_report(results: Dict[str, bool]) -> str:
    """
    Tâche pour générer un rapport après l'envoi en masse
    """
    return EmailService.generate_email_report(results)


# Tâche 4: Workflow complet avec tâches dépendantes 
@celery_app.task(name="email_campaign_workflow")
def email_campaign_workflow(
    recipients: List[str],
    subject: str,
    body: str
) -> str:
    """
    Workflow complet pour une campagne d'emails:
    1. Envoi en masse d'emails
    2. Génération d'un rapport sur les envois
    3. Envoi du rapport à l'administrateur
    """
    # Créer une chaîne de tâches dépendantes
    workflow = chain(
        # Étape 1: Envoi en masse
        process_bulk_emails.s(recipients, subject, body),
        
        # Étape 2: Génération du rapport
        generate_email_report.s(),
        
        # Étape 3: Envoi du rapport à l'admin
        send_single_email.s(
            "admin@example.com",
            "Rapport de campagne d'emails",
            "Veuillez trouver ci-joint le rapport de la campagne d'emails."
        )
    )
    
    # Lancement du workflow
    result = workflow.apply_async()
    return result.id


# Tâche 5: Exemple de Chord (groupe + callback)
@celery_app.task(name="email_campaign_with_report")
def email_campaign_with_report(
    recipients: List[str],
    subject: str,
    body: str
) -> str:
    """
    Utilisation d'un chord Celery:
    - Header: groupe de tâches d'envoi d'emails en parallèle
    - Callback: génération et envoi du rapport une fois tous les emails traités
    """
    # Créer les tâches individuelles d'envoi
    header = [
        send_single_email.s(recipient, subject, body)
        for recipient in recipients
    ]
    
    # Créer le chord (groupe + callback)
    workflow = chord(
        header=header,
        body=generate_and_send_report.s(recipients)
    )
    
    # Lancement du chord
    result = workflow.apply_async()
    return f"Tâche lancée avec l'id: {result.id}"


# Tâche auxiliaire pour le chord
@celery_app.task(name="generate_and_send_report")
def generate_and_send_report(results: List[bool], recipients: List[str]) -> str:
    """
    Callback du chord: génère et envoie un rapport une fois tous les emails envoyés
    """
    # Création du dictionnaire de résultats
    email_results = dict(zip(recipients, results))
    
    # Génération du rapport
    report = EmailService.generate_email_report(email_results)
    
    # Envoi du rapport à l'administrateur
    EmailService.send_email(
        to_email="admin@example.com",
        subject="Rapport de campagne d'emails",
        body=report
    )
    
    return report