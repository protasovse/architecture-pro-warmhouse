import logging
from dataclasses import dataclass
from typing import Callable, NewType, final

from get_exceede_alerts import get_exceeded_alerts
from render_alert_message import render_alert_message
from send_telegram_alert import send_telegram_alert

from .schemas import DeviceParameters

logger = logging.getLogger(__name__)

SerialNumber = NewType("SerialNumber", str)


@final
@dataclass(frozen=True, kw_only=True, slots=True)
class MessageHandler:
    exceeded_alerts_getter: Callable = get_exceeded_alerts
    alert_message_getter: Callable = render_alert_message
    telegram_alert_sender: Callable = send_telegram_alert

    async def __call__(self, device_data: DeviceParameters):
        alert_settings = await self.alert_settings_getter(device_data.serial)

        alerts: list[AlertExceededSchema] = await self.exceeded_alerts_getter(
            device_data,
            alert_settings,
            self.redis_client,
        )

        for alert in alerts:
            msg = render_alert_message(alert)
            channel = alert.subscription.channel

            if channel.type == "telegram":
                await send_telegram_alert(channel, msg)
