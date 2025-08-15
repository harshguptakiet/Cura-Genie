from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from core.config import settings
from db.database import create_tables

# Import API routers
from api.auth import router as auth_router
from api.local_upload import router as local_upload_router
from api.genomic_variants import router as genomic_variants_router
from api.chatbot import router as chatbot_router
from api.direct_prs import router as direct_prs_router
from api.timeline import router as timeline_router
from api.reports import router as reports_router
from api.mri_analysis import router as mri_router
from api.supabase_upload import router as supabase_upload_router
# Optional routers that require heavy deps
import os
_ENHANCED_MRI_ENABLED = os.getenv("ENABLE_ENHANCED_MRI", "false").lower() in ("1", "true", "yes")
if _ENHANCED_MRI_ENABLED:
    try:
        from api.enhanced_mri_analysis import router as enhanced_mri_router
        _HAS_ENHANCED_MRI = True
    except Exception as e:
        enhanced_mri_router = None
        _HAS_ENHANCED_MRI = False
        logging.warning(f"Enhanced MRI router disabled: {e}")
else:
    enhanced_mri_router = None
    _HAS_ENHANCED_MRI = False
from api.profile import router as profile_router

# Optional ML router (heavy deps like boto3/tensorflow)
_ENABLE_ML = os.getenv("ENABLE_ML", "false").lower() in ("1", "true", "yes")
if _ENABLE_ML:
    try:
        from api.ml import router as ml_router
        _HAS_ML = True
    except Exception as e:
        ml_router = None
        _HAS_ML = False
        logging.warning(f"ML router disabled: {e}")
else:
    ml_router = None
    _HAS_ML = False

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CuraGenie API",
    description="Production-ready FastAPI app with persistent DB",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(local_upload_router)
app.include_router(genomic_variants_router)
app.include_router(chatbot_router)
app.include_router(direct_prs_router)
app.include_router(timeline_router)
app.include_router(reports_router)
app.include_router(mri_router)
app.include_router(supabase_upload_router)
if _HAS_ENHANCED_MRI and enhanced_mri_router is not None:
    app.include_router(enhanced_mri_router)
app.include_router(profile_router)
if _HAS_ML and ml_router is not None:
    app.include_router(ml_router)

@app.on_event("startup")
def on_startup():
    try:
        create_tables()
        logger.info("✅ Database tables ensured on startup")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "curagenie-api",
        "version": "2.0.0",
    }

@app.get("/")
def root():
    return {
        "message": "CuraGenie API",
        "version": "2.0.0",
        "docs": "/docs",
    }
