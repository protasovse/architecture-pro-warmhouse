import asyncio
import logging

from aiokafka import AIOKafkaConsumer
from services import MessageHandler
from settings import KAFKA_SETTINGS, KAFKA_TOPIC

from .schemas import DeviceParameters

logging.basicConfig(level=logging.INFO)


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
            setting_schema = DeviceParameters.model_validate_json(
                msg.value.decode("utf-8")
            )
            message_handler = MessageHandler()
            await message_handler(setting_schema)
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume())
