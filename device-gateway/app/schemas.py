from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DeviceParameters(BaseModel):
    tenant_id: int = Field(..., ge=1, description="ID арендатора (тенанта)")
    device_id: int = Field(..., ge=1, description="ID устройства")
    key: str = Field(..., max_length=80, description="Имя параметра")
    value: dict[str, Any] = Field(..., description="Значение параметра в JSON-формате")
    ts: datetime = Field(..., description="Время измерения в ISO8601 формате")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenant_id": 1,
                "device_id": 42,
                "key": "temperature",
                "value": {"c": 22.5, "status": "ok"},
                "ts": "2025-10-26T12:34:56Z",
            }
        }
    }
