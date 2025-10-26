import asyncio
import logging

from aiokafka import AIOKafkaConsumer
from app.db import DB
from app.schemas import TelemetryMessage
from app.settings import KAFKA_SETTINGS, KAFKA_TOPIC, POSTGRES_DSN

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


async def consume():
    logger.info(
        "Connecting to Kafka: %s, topic: %s",
        KAFKA_SETTINGS.get("bootstrap_servers"),
        KAFKA_TOPIC,
    )

    db = DB(POSTGRES_DSN)
    await db.connect()
    logger.info("Connected to Postgres.")

    consumer = AIOKafkaConsumer(KAFKA_TOPIC, **KAFKA_SETTINGS)

    await consumer.start()
    logger.info("Kafka consumer started.")
    try:
        async for msg in consumer:
            try:
                telemetry = TelemetryMessage.from_kafka_bytes(msg.value)
            except Exception as e:
                logger.exception(
                    "Failed to parse message at offset %s: %s", msg.offset, e
                )
                continue

            try:
                await db.insert_telemetry(
                    tenant_id=telemetry.tenant_id,
                    device_id=telemetry.device_id,
                    key=telemetry.key,
                    value=telemetry.value,
                    ts=telemetry.ts,
                )
                logger.info(
                    "Inserted telemetry: tenant=%s device=%s key=%s ts=%s offset=%s",
                    telemetry.tenant_id,
                    telemetry.device_id,
                    telemetry.key,
                    telemetry.ts.isoformat(),
                    msg.offset,
                )
            except Exception as e:
                logger.exception("Failed to insert telemetry into DB: %s", e)

    finally:
        await consumer.stop()
        await db.close()
        logger.info("Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(consume())
