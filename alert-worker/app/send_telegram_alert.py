import logging

import aiohttp
from schemas import AlertChannelSettingSchema

logging.basicConfig(level=logging.INFO)


async def send_telegram_alert(
    channel_config: AlertChannelSettingSchema,
    text: str,
) -> None:
    bot_token = channel_config.config.bot_token
    chat_id = channel_config.config.chat_id
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    async with aiohttp.ClientSession() as session:
        logging.info(f"Send message to telegram: {url}:{payload}")
        await session.post(url, json=payload)
        logging.info("Отправлено")
