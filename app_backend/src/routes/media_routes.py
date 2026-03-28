from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from src.core.security import verify_firebase_token
from src.services.storage_service import upload_file, _get_provider

router = APIRouter(prefix="/media", tags=["media"])

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

    try:
        result = await upload_file(
            file_bytes=data,
            original_filename=image.filename or "upload.jpg",
            content_type=image.content_type,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # For local provider, result is just the filename — build the full URL
    if _get_provider() == "local":
        base_url = str(request.base_url).rstrip("/")
        image_url = f"{base_url}/uploads/{result}"
    else:
        image_url = result  # GCS returns full public URL directly

    return {
        "imageUrl": image_url,
        "sizeBytes": len(data),
        "contentType": image.content_type,
    }
