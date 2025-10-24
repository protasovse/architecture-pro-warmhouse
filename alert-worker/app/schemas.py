from decimal import Decimal

from pydantic import BaseModel


class ParameterDetail(BaseModel):
    name: str
    value: str | bool | Decimal


class Sensor(BaseModel):
    name: str
    parameters: list[ParameterDetail]


class DeviceParameters(BaseModel):
    device_name: str
    timestamp: Decimal
    sensors: list[Sensor]
