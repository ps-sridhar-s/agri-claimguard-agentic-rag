from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel


AUDIT_DIR = Path("storage/audit_logs")


def write_audit_event(event_type: str, payload: BaseModel | dict) -> str:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    audit_id = str(uuid4())
    if isinstance(payload, BaseModel):
        data = payload.model_dump(mode="json")
    else:
        data = payload

    event = {
        "audit_id": audit_id,
        "event_type": event_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "payload": data,
    }
    with open(AUDIT_DIR / f"{audit_id}.json", "w", encoding="utf-8") as f:
        json.dump(event, f, indent=2)
    return audit_id

