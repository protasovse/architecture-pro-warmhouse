from django.conf import settings
from django.db import models

from apps.core.models import Tenant, TimeStampedModel


class TenantUser(TimeStampedModel):
    """Членство пользователя в тенанте (m2m с дополнительными полями)."""

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="memberships",
        verbose_name="Тенант",
        help_text="Тенант, в котором состоит пользователь.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tenant_memberships",
        verbose_name="Пользователь",
        help_text="Пользователь, являющийся участником тенанта.",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активное членство",
        help_text="Определяет, активно ли членство пользователя в тенанте.",
    )

    class Meta:
        db_table = "tenants_tenant_user"
        unique_together = (("tenant", "user"),)
        verbose_name = "Членство пользователя"
        verbose_name_plural = "Членства пользователей"

    def __str__(self):
        return f"{self.user}@{self.tenant}"
