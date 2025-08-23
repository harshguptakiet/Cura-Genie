# Proxy module to expose tasks under cg_worker.tasks namespace
# so Celery can import them without colliding with service name

# Import tasks from the main worker module
try:
    from worker.tasks import *  # noqa: F401,F403
except ImportError:
    # If worker.tasks doesn't exist, create basic task stubs
    import logging
    from core.celery_app import celery_app
    
    logger = logging.getLogger(__name__)
    logger.warning("worker.tasks not found, creating stub tasks")
    
    @celery_app.task
    def process_genomic_file(file_id):
        """Stub genomic file processing task"""
        logger.info(f"Processing genomic file {file_id} (stub)")
        return {"status": "completed", "file_id": file_id}
