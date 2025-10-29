# Project_template

# WarmHouse — микросервисная платформа «умного дома»
> Старый монолит (Go) → новая экосистема микросервисов (Python/Django + Kafka + Postgres)

Этот репозиторий содержит **два поколения** проекта:
- `apps/smart_home` — **исторический монолит** на Go (Gin + Postgres), использующий внешнее API температуры;
- `admin-service`, `device-gateway`, `telemetry-service`, `alert-worker` — **новые микросервисы**, объединённые брокером сообщений Kafka и общей БД Postgres.
В корне расположен `docker-compose.yml` для локального запуска всей системы.

---

## 1) Концепция и целевая архитектура

### Назначение
Платформа собирает телеметрию от устройств, хранит её, позволяет управлять устройствами и настраивать правила оповещений/автоконтроля.

### Переход от монолита к микросервисам
Монолит на Go обеспечивал REST‑интерфейс для устройств и UI‑операций. В новой версии функциональность разделена:
- **Входной шлюз устройств** (`device-gateway`) принимает параметры от устройств и публикует события в Kafka.
- **Сервис телеметрии** (`telemetry-service`) читает поток событий из Kafka и **записывает** данные в Postgres.
- **Сервис алертов** (`alert-worker`) анализирует поток телеметрии и принимает решения по **оповещениям** и **сигналам управления**.
- **Админ‑панель / справочники** (`admin-service`) — Django‑приложение с моделями «тенанты / локации / устройства / телеметрия», работает на той же БД.

Таким образом, запись телеметрии и реакция на события вынесены из веб‑контуров и распараллелены через Kafka.

### Высокоуровневый поток данных
```
Device → (HTTP POST) → device-gateway → (Kafka topic: TOPIC)
         └──────────────────────────────────────┬─────────────────────────────┘
                                                ▼
                                       telemetry-service (→ Postgres)
                                                ▼
                                          admin-service (чтение из БД)
                                                ▲
                                       alert-worker (реакции/алерты)
```

---

## 2) Состав репозитория

```
architecture-pro-warmhouse/
├─ admin-service/                # Django 5: админка и доменные модели
│  ├─ apps/
│  │  ├─ core/                   # Базовые модели: TimeStamped, Tenant, TenantBoundModel
│  │  ├─ tenants/                # Пользователи ↔ тенанты
│  │  ├─ locations/              # Локации/помещения
│  │  ├─ devices/                # Устройства
│  │  └─ telemetry/              # Модель TelemetryRecord (табл. telemetry_telemetry)
│  ├─ config/                    # settings/urls/wsgi/asgi
│  ├─ Dockerfile, pyproject.toml, poetry.lock
│  └─ manage.py
│
├─ device-gateway/               # FastAPI: входной REST для устройств → Kafka
│  ├─ app/
│  │  ├─ api/endpoints.py        # POST /send-parameters/
│  │  ├─ schemas.py              # DeviceParameters (Pydantic)
│  │  ├─ producer.py             # AIOKafkaProducer (singleton)
│  │  ├─ services.py             # Пакетная/штучная отправка в Kafka
│  │  └─ config.py               # BROKER_URL, TOPIC, ACKS, LINGER_MS, etc.
│  ├─ Dockerfile, pyproject.toml
│
├─ telemetry-service/            # Consumer: Kafka → Postgres
│  ├─ app/
│  │  ├─ main.py                 # Читает Kafka, валидирует, пишет в БД
│  │  ├─ db.py                   # psycopg_pool, insert into telemetry_telemetry
│  │  ├─ schemas.py              # TelemetryMessage (Pydantic)
│  │  └─ settings.py             # POSTGRES_DSN, KAFKA_* из .env
│  ├─ Dockerfile, pyproject.toml
│
├─ alert-worker/                 # Реакции/правила на поток телеметрии
│  ├─ app/
│  │  ├─ main.py                 # Consumer Kafka
│  │  ├─ services.py             # MessageHandler → exceeded_alert/control
│  │  ├─ get_exceede_alerts.py   # Заглушки правил (TODO)
│  │  └─ settings.py
│  ├─ Dockerfile, pyproject.toml
│
├─ apps/smart_home/              # Исторический монолит на Go (Gin + Postgres)
│  ├─ handlers/, models/, services/, db/
│  ├─ main.go, openapi.yaml, Dockerfile, go.mod
│
├─ apps/wiremock/                # Стаб внешнего API температуры (GET /temperature?location=...)
│  └─ mappings/temperature.json
│
├─ plantuml/                     # Диаграммы C4/контекст (по заданию)
├─ docker-compose.yml            # Композиция: Postgres, Kafka, микросервисы и т. п.
└─ .env                          # Конфигурация окружения
```

---

## 3) Домены и модели (Django `admin-service`)

- **Core**
  - `Tenant` — владелец данных.
  - `TenantBoundModel` — базовый класс для всех «мульти‑тенант» сущностей.
  - `TimeStampedModel` — `created_at` / `updated_at`.
- **Devices**
  - `Device` — принадлежит Tenant; имеет атрибуты устройства.
- **Locations**
  - `Location` — географические/логические места, к которым могут быть привязаны устройства.
- **Telemetry**
  - `TelemetryRecord` — временной ряд `device + key + value + ts`.
  - Таблица: `telemetry_telemetry`, индексы на `(tenant, device, key, ts)` и `(tenant, ts)`.
- **Tenants**
  - `TenantUser` — членство пользователя в тенанте.

Все модели уже мигрированы (папки `migrations` присутствуют).

---

## 4) API и контракты

### 4.1 Входной REST для устройств (`device-gateway`)
- **POST** `/send-parameters/` — принимает **один объект** или **список**:
```json
{
  "tenant_id": 1,
  "device_id": 42,
  "key": "temperature",
  "value": {"c": 22.5, "status": "ok"},
  "ts": "2025-10-26T12:34:56Z"
}
```
Валидируется Pydantic‑моделью `DeviceParameters`, затем каждое сообщение сериализуется в JSON и публикуется в Kafka (топик `TOPIC`).

### 4.2 Поток телеметрии (Kafka)
- Ключ: UUID, значение: JSON (`DeviceParameters`).
- Топик задаётся переменной окружения `TOPIC`.

### 4.3 Запись в БД (`telemetry-service`)
- Консьюмер преобразует вход в `TelemetryMessage` и вызывает `DB.insert_telemetry(...)`.
- Запись попадает в `telemetry_telemetry` и видна в `admin-service`.

### 4.4 Админ‑панель (`admin-service`)
- Доступно `/admin/` (Django Admin) для выполнения CRUD‑операций по доменным сущностям и просмотра телеметрии.

### 4.5 Монолит (Go) — для сравнения и обратной совместимости
- Swagger/OAS: `apps/smart_home/openapi.yaml`.
- Использует **WireMock** (`apps/wiremock`) для эмуляции внешнего API температуры:
  - `GET /temperature?location=...` возвращает шаблонный JSON.

---

## 5) Запуск и локальная среда

### 5.1 Подготовка
1. Установите Docker и Docker Compose.
2. Скопируйте `.env` из примера и заполните ключевые параметры (см. ниже).

### 5.2 Минимальный набор переменных окружения (`.env`)
> Значения зависят от вашей машины; приведены имена, используемые кодом.

**Postgres**
```
POSTGRES_DB=smarthome
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

**Kafka**
```
KAFKA_BOOTSTRAP_SERVERS=smarthome-micro-kafka:9092
TOPIC=parameters
KAFKA_GROUP_ID=telemetry-service-group
KAFKA_AUTO_OFFSET_RESET=latest
KAFKA_TOPIC_PARTITIONS=1
```

**Device Gateway**
```
BROKER_URL=smarthome-micro-kafka:9092
SERVER_SCHEME=http
SERVER_IP=0.0.0.0
SERVER_DOMAIN=localhost
SERVER_PORT=8088
KAFKA_ACKS=1
LINGER_MS=0
KAFKA_MAX_BATCH_SIZE=16384
```

**Django Admin**
```
DEBUG=True
ALLOWED_HOSTS=*
```

### 5.3 Запуск через Docker Compose
Из корня репозитория:
```bash
docker compose up -d --build
```

Ожидаемые эндпоинты (по умолчанию, см. порты в `docker-compose.yml`):
- **Device Gateway** (FastAPI): `http://localhost:<PORT>/openapi.json`
- **Django Admin**: `http://localhost:<PORT>/admin/`
- **WireMock (температура)**: `http://localhost:8081/temperature?location=living-room`

> Примечание: в `docker-compose.yml` уже предусмотрены сервисы Postgres, Kafka и консоль/инициализация топика. Если порт‑маппинги изменены — используйте фактические значения.

### 5.4 Быстрая проверка
Отправьте одно измерение в шлюз устройств:
```bash
curl -X POST http://localhost:<DEVICE_GATEWAY_PORT>/send-parameters/   -H "Content-Type: application/json"   -d '{
        "tenant_id": 1,
        "device_id": 42,
        "key": "temperature",
        "value": {"c": 22.5, "status": "ok"},
        "ts": "2025-10-26T12:34:56Z"
      }'
```
Ожидаемо:
- сообщение попадёт в Kafka (`TOPIC`);
- `telemetry-service` запишет строку в Postgres (`telemetry_telemetry`);
- запись будет видна в Django Admin.

---

## 6) Сборка/запуск сервисов без Docker (опционально)

### Python‑сервисы
```bash
# Пример для device-gateway
cd device-gateway
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8088
```

### Go‑монолит
```bash
cd apps/smart_home
go mod download
go run main.go
```

---

## 7) Разработка и TODO

- [ ] **alert-worker** — реализовать реальные правила в `get_exceede_alerts.py` (сейчас заглушки `return True`).
- [ ] **observability** — добавить Prometheus/Grafana и структурированные логи.
- [ ] **аутентификация/авторизация** — сквозные tenant‑контексты от шлюза до БД.
- [ ] **контроль устройств** — отдельный топик/сервис для команд управления.
- [ ] **миграции БД** — зафиксировать стратегию применения миграций вместе с CI.
- [ ] **контрактные тесты** между `device-gateway` ↔ `telemetry-service` (Pact, JSONSchema).

---

## 8) Справка по ключевым файлам

- `device-gateway/app/schemas.py` — контракт `DeviceParameters`.
- `telemetry-service/app/schemas.py` — нормализация входа (`ts` как ISO8601/Unix).
- `telemetry-service/app/db.py` — вставка в `telemetry_telemetry` через `psycopg_pool`.
- `admin-service/apps/telemetry/models.py` — целевая таблица и индексы.
- `apps/wiremock/mappings/temperature.json` — стаб внешнего API.

---

## 9) Лицензия и авторство
Автор: Sergey Protasov <protasovse@yandex.ru>. Стек и код предназначены для учебно‑практической разработки и демонстрации перехода от монолита к микросервисам.
