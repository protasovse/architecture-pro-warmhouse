import logging
from decimal import Decimal

from date_utils import format_timestamp
from redis.asyncio import Redis
from schemas import (
    AlertExceededSchema,
    AlertSubscriptionSchema,
    DeviceParametersFromMessageSchema,
    ResolveStatus,
)

logger = logging.getLogger(__name__)

CONDITIONS = {
    "ABOVE": "выше",
    "BELOW": "ниже",
}


async def get_exceeded_alerts(
    device_data: DeviceParametersFromMessageSchema,
    alert_settings: list[AlertSubscriptionSchema],
    redis_client: Redis,
) -> list[AlertExceededSchema]:
    """
    Проверяет значения параметров устройства на превышение заданных алерт-условий.

    Args:
        device_data: Объект DeviceParameters (pydantic-модель), содержащий данные
        от устройства, включая значения всех сенсоров и параметров.
        alert_settings: Список подписок AlertSubscriptionSchema (pydantic-модели),
        каждая из которых содержит условие, канал и шаблон для алерта.
        redis_client:


    Returns:
        list[AlertExceededSchema]: Список сработавших алертов (превышений),
        каждая запись — pydantic-модель с подробной информацией об алерте.

    Note:
        Функция предполагает, что имена сенсоров и параметров уникальны
        в рамках одного устройства.
    """
    alerts: list[AlertExceededSchema] = []

    sensors_map = {}
    for sensor in device_data.sensors:
        param_map = {param.name: param.value for param in sensor.parameters}
        sensors_map[sensor.name] = param_map

    now_str = format_timestamp(device_data.timestamp)

    for sub in alert_settings:
        ac = sub.alert_condition
        sensor_name = ac.device_sensor.name
        param_name = ac.sensor_parameter.name
        condition = ac.condition
        limit = Decimal(ac.limit_value)

        value_str = sensors_map.get(sensor_name, {}).get(param_name)
        try:
            value = Decimal(value_str)
        except (TypeError, ValueError):
            continue

        match = (condition == "ABOVE" and value > limit) or (
            condition == "BELOW" and value < limit
        )
        redis_key = (
            f":1:alert_state:"
            f"{device_data.serial}:"
            f"{sensor_name}:"
            f"{param_name}:"
            f"{condition}:"
            f"{limit}"
        )
        previous_state_b_or_none = await redis_client.get(redis_key)
        if previous_state_b_or_none is None:
            previous_state = "normal"
        else:
            previous_state = previous_state_b_or_none.decode("utf8")
        current_state = "exceeded" if match else "normal"

        if previous_state != current_state:
            alerts.append(
                AlertExceededSchema(
                    subscription=sub,
                    device_name=device_data.device_name,
                    device_serial=device_data.serial,
                    sensor_name=sensor_name,
                    sensor_description=ac.device_sensor.description,
                    parameter_name=param_name,
                    parameter_description=ac.sensor_parameter.description,
                    limit_value=limit,
                    condition=CONDITIONS[condition],
                    date=now_str,
                    current_value=value,
                    resolve_status=ResolveStatus.EXCEEDED
                    if match
                    else ResolveStatus.RESOLVED,
                )
            )
            # Обновляем состояние в Redis
            await redis_client.set(redis_key, current_state)

    return alerts
