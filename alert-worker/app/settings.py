import os

from dotenv import load_dotenv

load_dotenv()

KAFKA_SETTINGS = {
    "bootstrap_servers": os.getenv("KAFKA_BROKER_URL"),
    "group_id": "alert_worker_group",
    "auto_offset_reset": "latest",
}
KAFKA_TOPIC = os.getenv("TOPIC")
