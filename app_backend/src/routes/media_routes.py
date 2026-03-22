from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from src.core.config import get_settings
from src.core.security import verify_firebase_token

router = APIRouter(prefix="/media", tags=["media"])
_BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = _BASE_DIR / get_settings().upload_dir
MAX_SIZE_BYTES = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/upload")
async def upload_image(
    request: Request,
    image: UploadFile = File(...),
    _: dict = Depends(verify_firebase_token),
):
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only jpeg/png/webp are allowed")

    data = await image.read()
    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="Image must be <= 5MB")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    ext = Path(image.filename or "upload").suffix or ".jpg"
    safe_name = f"{uuid4().hex}{ext.lower()}"
    file_path = UPLOAD_DIR / safe_name
    file_path.write_bytes(data)

    base_url = str(request.base_url).rstrip("/")
    return {
        "imageUrl": f"{base_url}/uploads/{safe_name}",
        "sizeBytes": len(data),
        "contentType": image.content_type,
    }
