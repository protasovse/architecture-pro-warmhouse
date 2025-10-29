from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.endpoints import router
from .producer import kafka_producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекст жизненного цикла приложения для управления ресурсами Kafka."""

    try:
        await kafka_producer.start()
        yield
    finally:
        if kafka_producer:
            await kafka_producer.stop()


# Приложение FastAPI с жизненным циклом
app = FastAPI(
    lifespan=lifespan,
    openapi_url="/openapi.json",
    redoc_url=None,
)

# Подключаем роуты
app.include_router(router)
