curl -X POST http://localhost:8008/send-parameters/ \
  -H "Content-Type: application/json" \
  -d '{
      "tenant_id": 1,
      "device_id": 1,
      "key": "temperature",
      "value": {"c": 22.5, "status": "ok"},
      "ts": "2025-10-26T12:34:56Z"
    }'
