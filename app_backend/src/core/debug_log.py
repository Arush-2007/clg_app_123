from __future__ import annotations

import json
import os
import time
from pathlib import Path
from uuid import uuid4

LOG_PATH = Path("debug-4c90a2.log")
SESSION_ID = "4c90a2"


def debug_log(*, run_id: str, hypothesis_id: str, location: str, message: str, data: dict) -> None:
    if os.environ.get("APP_ENV", "development") == "production":
        return
    payload = {
        "sessionId": SESSION_ID,
        "id": f"log_{int(time.time() * 1000)}_{uuid4().hex[:8]}",
        "timestamp": int(time.time() * 1000),
        "location": location,
        "message": message,
        "data": data,
        "runId": run_id,
        "hypothesisId": hypothesis_id,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")
