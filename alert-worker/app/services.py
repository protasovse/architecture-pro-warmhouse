import logging
from dataclasses import dataclass
from typing import Callable, final

from app.get_exceede_alerts import get_exceeded_alert, get_exceeded_control
from app.schemas import DeviceParameters

logger = logging.getLogger(__name__)


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class MessageHandler:
    exceeded_alert_getter: Callable[[DeviceParameters], bool] = get_exceeded_alert
    exceeded_control_getter: Callable[[DeviceParameters], bool] = get_exceeded_control

    async def __call__(self, device_data: DeviceParameters) -> tuple[bool, bool]:
        is_alert = await self.exceeded_alert_getter(device_data)
        if is_alert:
            """Оповещаем пользователя"""
            logger.warning("Оповещаем пользователя")

        is_control = await self.exceeded_control_getter(device_data)
        if is_control:
            """Отправляем сигнал контроля на устройство"""
            logger.warning("Отправляем сигнал контроля на устройство")

        return is_alert, is_control
