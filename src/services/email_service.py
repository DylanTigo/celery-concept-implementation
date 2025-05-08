import time
import random
import logging
from typing import List, Dict, Any, Optional
from ..config import EMAIL_SIMULATION_DELAY, EMAIL_FAILURE_RATE

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service simulant l'envoi d'emails
    Return: True si l'envoi est réussi, False sinon
    """
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        body: str,
    ) -> bool:
        
        # Simuler le délai d'envoi
        time.sleep(EMAIL_SIMULATION_DELAY)
        
        # Simuler un échec aléatoire
        if random.random() < EMAIL_FAILURE_RATE:
            logger.error(f"Échec de l'envoi d'email à {to_email}")
            return False
        
        # Logger les détails de l'email
        logger.info(f"Email envoyé à {to_email} | Sujet: {subject} | Corps: {body}")
        return True

    @staticmethod
    def send_bulk_emails(
        recipients: List[str],
        subject: str,
        body: str
    ) -> Dict[str, bool]:
      
        results = {}
        for recipient in recipients:
            results[recipient] = EmailService.send_email(
                to_email=recipient,
                subject=subject,
                body=body
            )
        
        # Calculer les statistiques
        success_count = sum(1 for status in results.values() if status)
        logger.info(f"Envoi en masse terminé: {success_count}/{len(recipients)} emails envoyés avec succès")
        
        return results
        
    @staticmethod
    def generate_email_report(results: Dict[str, bool]) -> str:
        success_count = sum(1 for status in results.values() if status)
        failure_count = len(results) - success_count
        
        report = f"""
        Rapport d'envoi d'emails
        -----------------------
        Total des emails: {len(results)}
        Envois réussis: {success_count}
        Échecs: {failure_count}
        Taux de réussite: {(success_count / len(results)) * 100:.2f}%
        
        Détails:
        """
        
        for email, status in results.items():
            report += f"\n- {email}: {'Succès' if status else 'Échec'}"
            
        return report