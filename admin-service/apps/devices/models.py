
from django.db import models

from apps.core.models import TenantBoundModel
from apps.locations.models import Home, Room


class DeviceType(TenantBoundModel):
    """Тип устройства задаёт набор возможностей (capabilities)."""

    key = models.SlugField(
        max_length=80,
        verbose_name="Ключ типа",
        help_text="Уникальный ключ типа устройства в пределах тенанта (например, thermostat).",
    )
    display_name = models.CharField(
        max_length=120,
        verbose_name="Название типа",
        help_text="Человеко-читаемое название типа устройства.",
    )
    capabilities = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Возможности",
        help_text="Произвольный JSON с поддерживаемыми атрибутами и командами.",
    )

    class Meta:
        db_table = "devices_device_type"
        unique_together = (("tenant", "key"),)
        verbose_name = "Тип устройства"
        verbose_name_plural = "Типы устройств"

    def __str__(self):
        return self.display_name


class Device(TenantBoundModel):
    """Конкретное устройство."""

    type = models.ForeignKey(
        DeviceType,
        on_delete=models.PROTECT,
        related_name="devices",
        verbose_name="Тип устройства",
        help_text="Тип, определяющий возможности устройства.",
    )
    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="devices",
        verbose_name="Дом",
        help_text="Дом, в котором расположено устройство.",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="devices",
        verbose_name="Комната",
        help_text="Комната/зона, где находится устройство (необязательно).",
    )
    name = models.CharField(
        max_length=120,
        verbose_name="Название устройства",
        help_text="Отображаемое имя устройства.",
    )
    slug = models.SlugField(
        max_length=80,
        verbose_name="Слаг устройства",
        help_text="Короткий уникальный идентификатор устройства в пределах тенанта.",
    )
    external_id = models.CharField(
        max_length=160,
        blank=True,
        db_index=True,
        verbose_name="Внешний идентификатор",
        help_text="Серийный номер или ID во внешней системе/облаке.",
    )
    properties = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Свойства",
        help_text="Произвольные свойства (модель, производитель, лимиты и т.п.).",
    )
    is_online = models.BooleanField(
        default=False,
        verbose_name="Онлайн",
        help_text="Признак текущей онлайн-доступности устройства.",
    )
    last_seen_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Последняя активность",
        help_text="Метка времени последней связи с устройством.",
    )

    class Meta:
        db_table = "devices_device"
        unique_together = (("tenant", "slug"),)
        verbose_name = "Устройство"
        verbose_name_plural = "Устройства"

    def __str__(self):
        return f"{self.name} [{self.type.display_name}]"
