import asyncio
from aiohttp.client import ClientSession
from redis import Redis

from core.settings import BACKOFF, MAX_RETRIES, OPEN_WEATHER_API_KEY, OPEN_WEATHER_BASE_URL
from core.redis import store_weather_data


def kelvin_to_celsius(kelvin: int) -> float:
    return kelvin - 273.15


async def fetch_weather(
    redis: Redis,
    session: ClientSession,
    ref_id: int,
    city_id: int,
    backoff: float = BACKOFF,
    max_retries: int = MAX_RETRIES,
) -> None:
    for attempt in range(max_retries):
        try:
            url = f"{OPEN_WEATHER_BASE_URL}?id={city_id}&appid={OPEN_WEATHER_API_KEY}"

            async with session.get(url, timeout=10) as response:

                if response.status != 200:
                    response.raise_for_status()

                request_data = await response.json()
                temperature = kelvin_to_celsius(kelvin=request_data["main"]["temp"])
                data = {
                    "city_id": city_id,
                    "humidity": request_data["main"]["humidity"],
                    "temperature": temperature,
                }
                store_weather_data(redis=redis, ref_id=ref_id, city_id=city_id, data=data)

        except asyncio.TimeoutError:
            if attempt < max_retries - 1:
                await asyncio.sleep(backoff)
                backoff *= 2
            else:
                raise
