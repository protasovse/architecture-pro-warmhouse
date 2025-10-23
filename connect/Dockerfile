FROM confluentinc/cp-kafka-connect:7.5.0

# Устанавливаем плагин MQTT Source из Confluent Hub
# Версию можно зафиксировать, напр.: confluentinc/kafka-connect-mqtt:1.7.0
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-mqtt:latest

# Папка для секретов и доп. плагинов (если нужно)
RUN mkdir -p /connect && chown -R appuser:appuser /connect
USER appuser
