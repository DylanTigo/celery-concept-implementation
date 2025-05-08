from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..tasks.email_tasks import (
    send_single_email,
    process_bulk_emails,
    email_campaign_workflow,
    email_campaign_with_report
)
from ..tasks.periodic_tasks import send_inactivity_reminders

router = APIRouter(prefix="/api", tags=["emails"])

# Modèles de données
class EmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str

class BulkEmailRequest(BaseModel):
    recipients: List[str]
    subject: str
    body: str

class TaskResponse(BaseModel):
    task_id: str
    message: str

class EmailResultResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None

# Routes
@router.post("/email/send", response_model=TaskResponse)
async def send_email(email_request: EmailRequest):
    """Envoie un email de façon asynchrone"""
    task = send_single_email.delay(
        to_email=email_request.to_email,
        subject=email_request.subject,
        body=email_request.body,
    )
    
    return {
        "task_id": task.id,
        "message": f"Email en cours d'envoi à {email_request.to_email}"
    }

@router.post("/email/bulk", response_model=TaskResponse)
async def send_bulk_emails(bulk_request: BulkEmailRequest):
    """Envoie des emails en masse de façon parallèle"""
    task = process_bulk_emails.delay(
        recipients=bulk_request.recipients,
        subject=bulk_request.subject,
        body=bulk_request.body
    )
    
    return {
        "task_id": task.id,
        "message": f"Envoi en masse de {len(bulk_request.recipients)} emails en cours"
    }

@router.post("/email/campaign", response_model=TaskResponse)
async def start_email_campaign(bulk_request: BulkEmailRequest):
    """Démarre une campagne d'emails complète avec workflow"""
    task_id = email_campaign_workflow.delay(
        recipients=bulk_request.recipients,
        subject=bulk_request.subject,
        body=bulk_request.body
    )
    
    return {
        "task_id": str(task_id),
        "message": "Campagne d'emails démarrée avec workflow complet"
    }

@router.post("/email/campaign-with-report", response_model=TaskResponse)
async def start_email_campaign_with_report(bulk_request: BulkEmailRequest):
    """Démarre une campagne d'emails avec chord (groupe + callback)"""
    task_id = email_campaign_with_report.delay(
        recipients=bulk_request.recipients,
        subject=bulk_request.subject,
        body=bulk_request.body
    )
    
    return {
        "task_id": str(task_id),
        "message": "Campagne d'emails avec rapport démarrée"
    }

@router.post("/email/reminders", response_model=TaskResponse)
async def trigger_inactivity_reminders():
    """Déclenche l'envoi de rappels aux utilisateurs inactifs"""
    task = send_inactivity_reminders.delay()
    
    return {
        "task_id": task.id,
        "message": "Envoi de rappels aux utilisateurs inactifs en cours"
    }

@router.get("/task/{task_id}", response_model=EmailResultResponse)
async def get_task_status(task_id: str):
    """Récupère le statut d'une tâche par son ID"""
    from ..celery_app import celery_app
    
    try:
        result = celery_app.AsyncResult(task_id)
        
        if result.ready():
            if result.successful():
                return {
                    "success": True,
                    "message": "Tâche terminée avec succès",
                    "details": {
                        "result": result.get(),
                        "state": result.state
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Tâche terminée avec des erreurs",
                    "details": {
                        "error": str(result.result),
                        "state": result.state
                    }
                }
        else:
            return {
                "success": True,
                "message": "Tâche en cours d'exécution",
                "details": {
                    "state": result.state
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tâche non trouvée ou erreur lors de la récupération: {str(e)}"
        )