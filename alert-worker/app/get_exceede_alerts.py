import logging

from app.schemas import DeviceParameters

logger = logging.getLogger(__name__)

CONDITIONS = {
    "ABOVE": "выше",
    "BELOW": "ниже",
}


async def get_exceeded_alert(device_data: DeviceParameters) -> bool:
    """Проверяет значения параметров устройства на превышение заданных алерт-условий."""

    return True


async def get_exceeded_control(device_data: DeviceParameters) -> bool:
    """Проверяет значения параметров устройства на превышение заданных алерт-условий."""

    return True
