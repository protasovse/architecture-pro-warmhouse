import locale
from datetime import datetime
from decimal import Decimal

# Для локали русского языка (работает на Linux и некоторых системах)
try:
    locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
except locale.Error:
    # Фолбэк: если русская локаль не установлена — вывод будет на английском
    pass


def format_timestamp(ts: str | float | int | Decimal) -> str:
    # Преобразуем в int, если нужно
    ts_int = int(float(ts))
    dt = datetime.fromtimestamp(ts_int)
    # Например: "17 июля 2025 г. 15:32"
    return dt.strftime("%d.%m.%Y, %H:%M")
