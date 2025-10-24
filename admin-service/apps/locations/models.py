import uuid

from django.db import models

from apps.core.models import TenantBoundModel


class Home(TenantBoundModel):
    """Дом/квартира/объект управления пользователя."""

    name = models.CharField(
        max_length=120,
        verbose_name="Название дома",
        help_text="Отображаемое имя объекта (например, «Дом», «Квартира»).",
    )
    slug = models.SlugField(
        max_length=80,
        verbose_name="Слаг дома",
        help_text="Короткий уникальный идентификатор дома в пределах тенанта.",
    )

    class Meta:
        db_table = "locations_home"
        unique_together = (("tenant", "slug"),)
        verbose_name = "Дом"
        verbose_name_plural = "Дома"

    def __str__(self):
        return f"Объект: {self.name}@{self.tenant}"


class Room(TenantBoundModel):
    """Логическая зона внутри дома (комната/зона)."""

    home = models.ForeignKey(
        Home,
        on_delete=models.CASCADE,
        related_name="rooms",
        verbose_name="Дом",
        help_text="Дом, к которому относится комната.",
    )
    name = models.CharField(
        max_length=120,
        verbose_name="Название комнаты",
        help_text="Отображаемое имя комнаты/зоны (например, «Гостиная»).",
    )
    slug = models.SlugField(
        max_length=80,
        verbose_name="Слаг комнаты",
        help_text="Короткий уникальный идентификатор комнаты в пределах дома.",
    )

    class Meta:
        db_table = "locations_room"
        unique_together = (("tenant", "home", "slug"),)
        verbose_name = "Комната"
        verbose_name_plural = "Комнаты"

    def __str__(self):
        return f"Помещение: {self.name}@{self.home.name}"
