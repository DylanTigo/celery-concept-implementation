from fastapi import FastAPI
import logging

# Import des routes et configuration
from .api.routes import router
from .celery_app import celery_app


# Création de l'application FastAPI
app = FastAPI(
    title="Celery Email Service",
    description="API pour démontrer les fonctionnalités de Celery avec l'envoi d'emails",
    version="1.0.0"
)

app.include_router(router)


@app.get("/", tags=["health"])
async def root():
  return {
      "message": "Bienvenue sur l'API Celery Email Service",
      "status": "online"
  }


@app.get("/health", tags=["health"])
async def health_check():
  celery_inspect = celery_app.control.inspect()
  workers = celery_inspect.ping() or {}

  worker_status = "up" if workers else "down"

  return {
      "status": "ok",
      "celery": {
          "status": worker_status,
          "workers": list(workers.keys()) if workers else []
      }
  }

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(
      "src.main:app",
      host="0.0.0.0",
      port=8000,
      log_level="info",
      reload=True
  )
