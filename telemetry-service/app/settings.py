import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

KAFKA_SETTINGS = {
    "bootstrap_servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    "group_id": os.getenv("KAFKA_GROUP_ID", "telemetry-service-group"),
    "auto_offset_reset": os.getenv("KAFKA_AUTO_OFFSET_RESET", "latest"),
}
KAFKA_TOPIC = os.getenv("TOPIC", "parametres")

pg_user = os.getenv("POSTGRES_USER", "postgres")
pg_pass = quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
pg_host = os.getenv("POSTGRES_HOST", "localhost")
pg_port = os.getenv("POSTGRES_PORT", "5432")
pg_db = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_DSN = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
