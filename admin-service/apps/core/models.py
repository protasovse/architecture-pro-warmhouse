import uuid

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Создано",
        help_text="Дата и время создания записи.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено",
        help_text="Дата и время последнего изменения записи.",
    )

    class Meta:
        abstract = True


class Tenant(TimeStampedModel):
    """Тенант — организация/семья/учётная область."""

    slug = models.SlugField(
        unique=True,
        max_length=80,
        verbose_name="Слаг",
        help_text="Уникальный человеко-читаемый идентификатор тенанта.",
    )
    name = models.CharField(
        max_length=160,
        verbose_name="Название",
        help_text="Отображаемое название тенанта.",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Признак, что тенант активен и доступен.",
    )

    class Meta:
        db_table = "core_tenant"
        verbose_name = "Тенант"
        verbose_name_plural = "Тенанты"

    def __str__(self):
        return self.name


class TenantBoundModel(TimeStampedModel):
    """Базовый класс для всех предметных сущностей — всегда привязка к тенанту."""

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        verbose_name="Тенант",
        help_text="Тенант, к которому принадлежит запись.",
    )

    class Meta:
        abstract = True
        verbose_name = "Сущность тенанта"
        verbose_name_plural = "Сущности тенанта"
