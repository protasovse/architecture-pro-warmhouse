import os

from dotenv import load_dotenv

load_dotenv()

KAFKA_SETTINGS = {
    "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    "group_id": "alert-worker-group",
    "auto_offset_reset": "latest",
}
KAFKA_TOPIC = os.getenv("TOPIC")
