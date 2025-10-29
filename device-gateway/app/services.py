from dataclasses import dataclass
from typing import final
from uuid import uuid4

from .config import TOPIC
from .producer import KafkaProducer, kafka_producer
from .schemas import DeviceParameters


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class SendParametersService:
    """Сервис для отправки параметров устройств в Kafka."""

    producer: KafkaProducer = kafka_producer
    topic: str = TOPIC

    async def __call__(
        self,
        parameters: DeviceParameters | list[DeviceParameters],
    ):
        """Основной метод для отправки параметров устройств в Kafka."""
        if not self.producer:
            raise Exception("Kafka producer не инициализирован.")

        if isinstance(parameters, list) and len(parameters) == 0:
            raise Exception("Нет данных.")

        # Преобразуем одиночный объект в список для унификации обработки
        if isinstance(parameters, DeviceParameters):
            parameters = [parameters]

        # Асинхронная отправка каждого параметра в Kafka
        for parameter in parameters:
            await self.producer.send(
                self.topic,
                key=str(uuid4()).encode("utf-8"),
                value=bytes(parameter.model_dump_json(), encoding="utf-8"),
            )
