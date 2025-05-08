import logging
from typing import List, Dict
from celery import chain, group, chord
from ..celery_app import celery_app
from ..services.email_service import EmailService
from ..config import MAX_RETRIES, RETRY_DELAY

logger = logging.getLogger(__name__)


# Envoi d'un email simple avec gestion des retries
@celery_app.task(
    bind=True,
    name="send_single_email",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=MAX_RETRIES,
    default_retry_delay=RETRY_DELAY,
)
def send_single_email(self, to_email: str, subject: str, body: str):

    result = EmailService.send_email(
        to_email=to_email,
        subject=subject,
        body=body,
    )

    if not result:
        logger.warning(
            f"Échec de l'envoi d'email à {to_email}, tentative de retry: {self.request.retries + 1}/{MAX_RETRIES}"
        )
        raise Exception("Email sending failed")

    return True


# Traitement parallèle - Envoi en masse
@celery_app.task(name="process_bulk_emails")
def process_bulk_emails(recipients: List[str], subject: str, body: str):
    email_tasks_group = group(
        send_single_email.s(recipient, subject, body) for recipient in recipients
    ) 
    return email_tasks_group.apply_async()


# Collecte des résultats
@celery_app.task(name="collect_bulk_results")
def collect_bulk_results(results, recipients):
    return dict(zip(recipients, results))


# Tache aux résultats genérer un rapport après l'envoi de masse
@celery_app.task(name="generate_email_report")
def generate_email_report(results: Dict[str, bool]) -> str:
    return EmailService.generate_email_report(results)


# Workflow complet avec tâches dépendantes
@celery_app.task(name="email_campaign_workflow")
def email_campaign_workflow(recipients: List[str], subject: str, body: str) -> str:
    """
    Workflow complet pour une campagne d'emails:
    1. Envoi en masse d'emails
    2. Génération d'un rapport sur les envois
    3. Envoi du rapport à l'administrateur
    """
    # 1. Envoi en masse (group)
    bulk_group = group(
        send_single_email.s(recipient, subject, body) for recipient in recipients
    )
    
    workflow = chord(
        bulk_group,
        chain(
            collect_bulk_results.s(recipients),
            generate_email_report.s(),
            send_single_email.s(
                "admin@example.com",
                "Rapport de campagne d'emails",
            ),
        ),
    )
    result = workflow.apply_async()
    return result.id
