curl -X POST http://localhost:8008/send-parameters/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_name": "thermostat_1",
    "timestamp": 1734972290.55,
    "sensors": [
      {
        "name": "temperature",
        "parameters": [
          { "name": "current", "value": 21.5 },
          { "name": "target", "value": 23.0 }
        ]
      },
      {
        "name": "humidity",
        "parameters": [
          { "name": "current", "value": 45 },
          { "name": "enabled", "value": true }
        ]
      }
    ]
  }'
