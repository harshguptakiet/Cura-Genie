#!/usr/bin/env python3
"""
Celery Worker Entry Point (renamed package to avoid import collision with service name)
"""
import os
import sys
import logging

# Ensure project root is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.append(PROJECT_ROOT)

from core.celery_app import celery_app

# Ensure tasks are imported so Celery can register them
import cg_worker.tasks  # noqa: F401

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Starting CuraGenie Celery Worker (cg_worker)...")
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--queues=genomic_processing,prs_calculation,ml_inference',
        '--concurrency=1',
        '--prefetch-multiplier=1',
    ])

