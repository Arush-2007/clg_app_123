from functools import lru_cache
import os

def get_secret(secret_id: str) -> str:
    """
    Fetch a secret value. Behaviour is controlled by SECRETS_PROVIDER env var:
      env  (default) — read directly from os.environ, raise if missing
      gcp            — fetch from GCP Secret Manager, cache result
    """
    provider = os.environ.get("SECRETS_PROVIDER", "env").lower()

    if provider == "gcp":
        return _get_from_gcp(secret_id)
    else:
        value = os.environ.get(secret_id)
        if not value:
            raise RuntimeError(
                f"[secrets] Required secret '{secret_id}' is not set in environment. "
                f"Set SECRETS_PROVIDER=gcp or set the env var directly."
            )
        return value


def _get_from_gcp(secret_id: str) -> str:
    """Fetch from GCP Secret Manager. Cached per secret_id per process lifetime."""
    try:
        from google.cloud import secretmanager
    except ImportError:
        raise RuntimeError(
            "[secrets] google-cloud-secret-manager is not installed. "
            "Run: pip install google-cloud-secret-manager"
        )

    project_id = os.environ.get("GCP_PROJECT_ID")
    if not project_id:
        raise RuntimeError(
            "[secrets] GCP_PROJECT_ID env var is required when SECRETS_PROVIDER=gcp"
        )

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

    try:
        response = client.access_secret_version(request={"name": name})
        value = response.payload.data.decode("UTF-8").strip()
        if not value:
            raise RuntimeError(f"[secrets] Secret '{secret_id}' exists but is empty in GCP.")
        return value
    except Exception as e:
        raise RuntimeError(
            f"[secrets] Failed to fetch secret '{secret_id}' from GCP Secret Manager: {e}"
        )


# Module-level cache: called once per secret per process
_cache: dict[str, str] = {}

def get_secret_cached(secret_id: str) -> str:
    if secret_id not in _cache:
        _cache[secret_id] = get_secret(secret_id)
    return _cache[secret_id]
