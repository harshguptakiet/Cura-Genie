from celery import Celery
from core.config import settings

# Create Celery instance
celery_app = Celery(
    "curagenie",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "cg_worker.tasks.process_genomic_file": {"queue": "genomic_processing"},
        "cg_worker.tasks.calculate_prs_score": {"queue": "prs_calculation"},
        "cg_worker.tasks.run_ml_inference": {"queue": "ml_inference"},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

if __name__ == "__main__":
    celery_app.start()
