from __future__ import annotations

from typing import List

from django.apps import apps
from django.contrib import admin
from django.db import models as dj_models
from django.utils.text import capfirst

# --- Оформление шапки сайта админки ---
admin.site.site_header = "Админ-панель SmartHome"
admin.site.site_title = "SmartHome Admin"
admin.site.index_title = "Управление данными"

# --- Настраиваемые параметры авто-регистрации ---
# Префиксы приложений, которые нужно включить (оставьте пустым, чтобы включить все локальные)
INCLUDE_APP_LABEL_PREFIXES: List[
    str
] = []  # например: ["tenants", "devices", "telemetry"]

# Модели/приложения, которые точно пропускаем
EXCLUDE_APP_LABELS = {
    "admin",
    "auth",
    "contenttypes",
    "sessions",
    "messages",
    "staticfiles",
}
EXCLUDE_MODEL_NAMES = {
    # Добавьте сюда имена моделей, которые не хотите показывать в админке
    # пример: "AuditLog",
}

# --- Вспомогательные функции для авто-настроек ModelAdmin ---


def is_included_app(app_label: str) -> bool:
    if app_label in EXCLUDE_APP_LABELS:
        return False
    if not INCLUDE_APP_LABEL_PREFIXES:
        return True
    return any(app_label.startswith(p) for p in INCLUDE_APP_LABEL_PREFIXES)


def guess_list_display(model) -> List[str]:
    """
    Подбираем 3-6 информативных столбцов для списка.
    Приоритет: id, ключевые текстовые поля, связи с тенантом/пользователем, таймстемпы.
    """
    fields = model._meta.get_fields()
    names = [f.name for f in fields if isinstance(f, dj_models.Field)]

    candidate_order = [
        "id",
        "uuid",
        "slug",
        "name",
        "title",
        "code",
        "key",
        "email",
        "username",
        "device",
        "device_id",
        "device_type",
        "sensor",
        "sensor_type",
        "tenant",
        "organization",
        "location",
        "status",
        "state",
        "level",
        "value",
        "unit",
        "created_at",
        "updated_at",
        "created",
        "modified",
    ]
    picked = []

    # 1) Добавляем то, что реально есть в модели, по списку приоритетов
    for c in candidate_order:
        if c in names and c not in picked:
            picked.append(c)

    # 2) Добираем ещё парочку полезных полей (строковые/числовые), если мало
    if len(picked) < 3:
        for f in fields:
            if isinstance(f, dj_models.Field) and f.name not in picked:
                if isinstance(
                    f,
                    (
                        dj_models.CharField,
                        dj_models.TextField,
                        dj_models.IntegerField,
                        dj_models.FloatField,
                        dj_models.BooleanField,
                        dj_models.DateTimeField,
                        dj_models.DateField,
                        dj_models.ForeignKey,
                    ),
                ):
                    picked.append(f.name)
                if len(picked) >= 6:
                    break

    # Ограничим количество
    return picked[:6] if picked else ["id"]


def guess_search_fields(model) -> List[str]:
    """Ищем по текстовым полям и некоторым ключевым потенциальным идентификаторам."""
    fields = model._meta.get_fields()
    search = []
    for f in fields:
        if isinstance(f, dj_models.CharField) or isinstance(f, dj_models.TextField):
            search.append(f.name)
        elif f.name in ("uuid", "slug", "code", "email", "username"):
            search.append(f.name)
    # ограничим, чтобы админка не тормозила
    return search[:5]


def guess_list_filter(model) -> List[str]:
    """Фильтры по булевым, выборочным и FK полям."""
    fields = model._meta.get_fields()
    filters = []
    for f in fields:
        if isinstance(f, dj_models.BooleanField):
            filters.append(f.name)
        elif isinstance(f, dj_models.ForeignKey):
            filters.append(f.name)
        elif isinstance(f, dj_models.IntegerField) and f.choices:
            filters.append(f.name)
        elif isinstance(f, dj_models.CharField) and f.choices:
            filters.append(f.name)
    return filters[:6]


def guess_readonly_fields(model) -> List[str]:
    """Часто встречающиеся поля, которые разумно сделать read-only."""
    names = {f.name for f in model._meta.get_fields() if isinstance(f, dj_models.Field)}
    ro = []
    for c in ("id", "created_at", "updated_at", "created", "modified"):
        if c in names:
            ro.append(c)
    return ro


def guess_ordering(model) -> List[str]:
    names = {f.name for f in model._meta.get_fields() if isinstance(f, dj_models.Field)}
    if "created_at" in names:
        return ["-created_at"]
    if "created" in names:
        return ["-created"]
    if "updated_at" in names:
        return ["-updated_at"]
    if "modified" in names:
        return ["-modified"]
    if "id" in names:
        return ["-id"]
    return []


# --- Авто-регистрация всех моделей проекта (кроме исключений) ---


class AutoAdmin(admin.ModelAdmin):
    """Базовый админ с автоконфигом; конкретные значения проставим динамически при регистрации."""

    pass


def register_all_models():
    for model in apps.get_models():
        app_label = model._meta.app_label
        model_name = model.__name__

        if not is_included_app(app_label):
            continue
        if model_name in EXCLUDE_MODEL_NAMES:
            continue

        # Уже зарегистрированы?
        if app_label in admin.site._registry and model in admin.site._registry:
            continue

        # Формируем динамический класс админа
        attrs = {
            "list_display": guess_list_display(model),
            "search_fields": guess_search_fields(model),
            "list_filter": guess_list_filter(model),
            "readonly_fields": guess_readonly_fields(model),
            "ordering": guess_ordering(model),
        }

        # Красивое имя в шапке списка
        verbose_name = capfirst(model._meta.verbose_name_plural)
        if verbose_name:
            attrs["__doc__"] = f"Админка: {verbose_name}"

        DynamicAdmin = type(f"{model.__name__}AutoAdmin", (AutoAdmin,), attrs)

        try:
            admin.site.register(model, DynamicAdmin)
        except admin.sites.AlreadyRegistered:
            # кто-то уже зарегистрировал — пропускаем
            pass


register_all_models()
