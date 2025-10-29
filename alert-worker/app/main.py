import asyncio
import logging

from aiokafka import AIOKafkaConsumer

from app.schemas import DeviceParameters
from app.services import MessageHandler
from app.settings import KAFKA_SETTINGS, KAFKA_TOPIC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def consume():
    logging.info(
        f"Connecting to Kafka: {KAFKA_SETTINGS['bootstrap_servers']}, "
        f"topic: {KAFKA_TOPIC}"
    )

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        **KAFKA_SETTINGS,
    )

    await consumer.start()

    try:
        async for msg in consumer:
            logger.info(f"Received message: {msg.value}")
            msg_schema = DeviceParameters.model_validate_json(
                msg.value.decode("utf-8")
            )
            logger.info(f"Setting schema: {msg_schema}")
            message_handler = MessageHandler()
            res = await message_handler(msg_schema)
            logger.info(f"Message handler: {res}")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume())
