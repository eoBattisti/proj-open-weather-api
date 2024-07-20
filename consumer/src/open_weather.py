import asyncio
import json

from aiohttp import ClientSession
from redis.asyncio import Redis

import src.settings as settings

class OpenWeatherClient:

    def __init__(
        self,
        url = None,
        timeout: int = settings.OPEN_WEATHER_TIMEOUT_SECONDS,
        max_retries: int = settings.OPEN_WEATHER_MAX_RETRIES,
        backoff: int = settings.OPEN_WEATHER_BACKOFF
    ) -> None:
        self.url = settings.OPEN_WEATHER_BASE_URL if url is None else url
        self.headers = {"Content-Type": "application/json", "Accept": "application/json"}
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff

    def _kelvin_to_celsius(self, kelvin: int) -> float:
        return round(kelvin - 273.15, 2)

    async def fetch_weather_by_city(
        self, 
        redis: Redis,
        session: ClientSession,
        ref_id: int,
        city_id: int,
        requested_at: str,
    ) -> None:
        for attempt in range(self.max_retries):
            try:
                url = f"{self.url}?id={city_id}&appid={settings.OPEN_WEATHER_API_KEY}"

                async with session.get(url, timeout=self.timeout) as response:

                    if response.status != 200:
                        response.raise_for_status()

                    request_data = await response.json()
                    temperature = self._kelvin_to_celsius(kelvin=request_data["main"]["temp"])
                    data = {
                        "requested_at": requested_at,
                        "city_id": city_id,
                        "humidity": request_data["main"]["humidity"],
                        "temperature": temperature,
                    }
                    print(json.dumps(data))
                    await redis.hset(name=str(ref_id), key=str(city_id), value=json.dumps(data))

            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.backoff)
                    self.backoff *= 2
                else:
                    raise
