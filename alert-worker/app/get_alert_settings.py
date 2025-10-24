import json

import aiohttp
from redis.asyncio import Redis
from schemas import AlertSubscriptionSchema
from settings import API_URL, INTERNAL_API_KEY, REDIS_URL


async def get_alert_settings(serial_number: str) -> list[AlertSubscriptionSchema]:
    cache_key = f":1:alert:subs:{serial_number}"
    redis = Redis.from_url(REDIS_URL, decode_responses=True)

    cached = await redis.get(cache_key)
    if cached:
        return [
            AlertSubscriptionSchema.model_validate(item) for item in json.loads(cached)
        ]

    # --- Нет в кэше, идём в API
    headers = {"X-Internal-Api-Key": INTERNAL_API_KEY}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            API_URL,
            json={"serial_number": serial_number},
            headers=headers,
        ) as resp:
            data = await resp.json()
            if "payload" not in data:
                raise ValueError("Нет payload в ответе API")

            # Сохраняем в кэш (только payload, а не весь resp.text)
            await redis.set(cache_key, json.dumps(data["payload"]))

            return [
                AlertSubscriptionSchema.model_validate(item) for item in data["payload"]
            ]
