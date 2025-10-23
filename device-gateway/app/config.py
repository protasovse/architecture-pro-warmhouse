from decouple import config

# Загрузка конфигурации Kafka
BROKER_URL = config("BROKER_URL")
TOPIC = config("TOPIC")
LINGER_MS = config("LINGER_MS", cast=int)
MAX_BATCH_SIZE = config("KAFKA_MAX_BATCH_SIZE", cast=int)
ACKS = config("KAFKA_ACKS", cast=int)


SERVER_SCHEME = config("SERVER_SCHEME")
SERVER_IP = config("SERVER_IP")
SERVER_DOMAIN = config("SERVER_DOMAIN")
SERVER_PORT = config("SERVER_PORT")
