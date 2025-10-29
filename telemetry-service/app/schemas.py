from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator


class TelemetryMessage(BaseModel):
    tenant_id: int = Field(..., ge=1)
    device_id: int = Field(..., ge=1)
    key: str = Field(..., min_length=1, max_length=80)
    value: Dict[str, Any]
    ts: datetime

    @field_validator("ts", mode="before")
    @classmethod
    def _parse_ts(cls, v):
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(v, tz=timezone.utc)
        return v

    @classmethod
    def from_kafka_bytes(cls, raw: bytes) -> "TelemetryMessage":
        import json

        data = json.loads(raw.decode("utf-8"))
        if isinstance(data, dict):
            for key in ("payload", "data", "message"):
                if key in data and isinstance(data[key], dict):
                    data = data[key]
                    break
        return cls.model_validate(data)
