import os
from pathlib import Path
from uuid import uuid4


def _get_provider() -> str:
    return os.environ.get("STORAGE_PROVIDER", "local").lower()


async def upload_file(
    file_bytes: bytes,
    original_filename: str,
    content_type: str,
) -> str:
    """
    Upload file bytes to the configured storage backend.
    Returns the public URL of the uploaded file.
    """
    ext = Path(original_filename or "upload").suffix.lower() or ".jpg"
    safe_name = f"{uuid4().hex}{ext}"

    provider = _get_provider()

    if provider == "gcs":
        return await _upload_gcs(file_bytes, safe_name, content_type)
    else:
        return _upload_local(file_bytes, safe_name)


async def _upload_gcs(file_bytes: bytes, filename: str, content_type: str) -> str:
    try:
        from google.cloud import storage as gcs
    except ImportError:
        raise RuntimeError(
            "[storage] google-cloud-storage is not installed. "
            "Run: pip install google-cloud-storage"
        )

    bucket_name = os.environ.get("GCS_BUCKET_NAME")
    if not bucket_name:
        raise RuntimeError(
            "[storage] GCS_BUCKET_NAME env var is required when STORAGE_PROVIDER=gcs"
        )

    client = gcs.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"uploads/{filename}")
    blob.upload_from_string(file_bytes, content_type=content_type)
    blob.make_public()
    return blob.public_url


def _upload_local(file_bytes: bytes, filename: str) -> str:
    upload_dir = Path(__file__).resolve().parents[2] / os.environ.get("UPLOAD_DIR", "uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / filename
    file_path.write_bytes(file_bytes)
    # Return a relative path — the route will build the full URL
    return filename
