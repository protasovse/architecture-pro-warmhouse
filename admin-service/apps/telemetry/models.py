from django.db import models
from django.utils import timezone

from apps.core.models import TenantBoundModel
from apps.devices.models import Device


class TelemetryRecord(TenantBoundModel):
    """Временной ряд телеметрии (key/value во времени)."""

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="telemetry",
        verbose_name="Устройство",
        help_text="Устройство, от которого получена телеметрия.",
    )
    key = models.CharField(
        max_length=80,
        db_index=True,
        verbose_name="Ключ телеметрии",
        help_text="Имя метрики (например, temperature, humidity, power_w).",
    )
    value = models.JSONField(
        verbose_name="Значение",
        help_text="Произвольный JSON со значением (например, {'v': 22.5, 'unit': '°C'}).",
    )
    ts = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Время события",
        help_text="Метка времени получения телеметрии.",
    )

    class Meta:
        db_table = "telemetry_telemetry"
        indexes = [
            models.Index(
                fields=["tenant", "device", "key", "ts"], name="telemetry_comp_idx"
            ),
            models.Index(fields=["tenant", "ts"], name="telemetry_tenant_ts_idx"),
        ]
        verbose_name = "Запись телеметрии"
        verbose_name_plural = "Записи телеметрии"

    def __str__(self):
        return f"{self.device_id}:{self.key}@{self.ts.isoformat()}"
