from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from supabase import create_client, Client

router = APIRouter(prefix="/api/upload/supabase", tags=["upload-supabase"])

class PresignRequest(BaseModel):
    path: str  # e.g., "vcf/2025-08-10_file.vcf"

class PresignResponse(BaseModel):
    path: str
    token: str

_def_client: Client | None = None

def get_supabase() -> Client:
    global _def_client
    if _def_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not configured")
        _def_client = create_client(url, key)
    return _def_client

@router.post("/presign", response_model=PresignResponse)
def create_signed_upload_url(body: PresignRequest):
    try:
        bucket = os.environ.get("SUPABASE_BUCKET", "uploads")
        client = get_supabase()
        res = client.storage.from_(bucket).create_signed_upload_url(body.path)
        # res example: { 'signed_url': '...', 'token': '...' }
        token = res.get("token")
        if not token:
            raise RuntimeError("Supabase did not return a token")
        return PresignResponse(path=body.path, token=token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to presign: {e}")

