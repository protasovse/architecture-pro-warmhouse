import logging

from aiokafka import AIOKafkaProducer

from .config import ACKS, BROKER_URL, LINGER_MS, MAX_BATCH_SIZE

logger = logging.getLogger(__name__)
log = logger.info


class _SingletonWrapper:
    """Класс-обёртка для реализации паттерна Одиночка."""

    def __init__(self, cls):
        self.__wrapped__ = cls  # Оригинальный класс
        self._instance = None  # Здесь будет храниться экземпляр класса

    def __call__(self, *args, **kwargs):
        """Возвращает единственный экземпляр класса"""
        if self._instance is None:
            self._instance = self.__wrapped__(*args, **kwargs)
        return self._instance


def singleton(cls):
    """Декоратор для класса, реализующий синглтон."""
    return _SingletonWrapper(cls)


@singleton
class KafkaProducer:
    """Синглтон-класс для управления Kafka-продюсером."""

    def __init__(self):
        self._producer: AIOKafkaProducer | None = None

    async def start(self):
        """Асинхронная инициализация Kafka-продюсера."""
        if not self._producer:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=BROKER_URL,
                linger_ms=LINGER_MS,
                max_batch_size=MAX_BATCH_SIZE,
                acks=ACKS,
            )
            await self._producer.start()
            log("Kafka producer успешно запущен.")

    async def stop(self):
        """Асинхронная остановка Kafka-продюсера."""
        if self._producer:
            await self._producer.stop()
            self._producer = None
            log("Kafka producer успешно остановлен.")

    async def send(self, topic: str, key: bytes, value: bytes):
        """Асинхронная отправка сообщения в Kafka.

        Args:
            topic (str): Название Kafka-топика.
            key (bytes): Ключ сообщения.
            value (bytes): Значение сообщения.
        """
        if not self._producer:
            raise RuntimeError(
                "Kafka producer не инициализирован. "
                "Вызовите `start` перед отправкой сообщений."
            )
        await self._producer.send_and_wait(topic, key=key, value=value)


kafka_producer = KafkaProducer()

__all__ = ["kafka_producer", "KafkaProducer"]
