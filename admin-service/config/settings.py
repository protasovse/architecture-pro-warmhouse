import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = "django-insecure-@2n9a2a#qjpt56hul=-!io!wbjzilr4x--mh92**ug=zm(0eq2"
DEBUG = os.getenv("DEBUG", "True").lower() in ("1", "true", "yes")

if DEBUG:
    env_path = Path(BASE_DIR).resolve().parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded .env from {env_path}")

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.core",
    "apps.devices",
    "apps.locations",
    "apps.telemetry",
    "apps.tenants",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "smarthome"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "OPTIONS": {
            # Если вы используете sslmode в DATABASE_URL — можно убрать
            "sslmode": os.getenv("POSTGRES_SSLMODE", "disable"),
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


SERVER_SCHEME = os.getenv("SERVER_SCHEME", "http")
SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")
SERVER_DOMAIN = os.getenv("SERVER_DOMAIN", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", 8080))

TEMPERATURE_API_URL = os.getenv("TEMPERATURE_API_URL", "http://temperature-api:8080")

BROKER_URL = os.getenv("BROKER_URL", "smarthome-micro-kafka:9092")
TOPIC = os.getenv("TOPIC", "parameters")
LINGER_MS = int(os.getenv("LINGER_MS", 10))

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", BROKER_URL)
KAFKA_MAX_BATCH_SIZE = int(os.getenv("KAFKA_MAX_BATCH_SIZE", 16384))
KAFKA_ACKS = int(os.getenv("KAFKA_ACKS", 1))
KAFKA_TOPIC_PARTITIONS = int(os.getenv("KAFKA_TOPIC_PARTITIONS", 2))
