import aiohttp
import pytest
from unittest.mock import AsyncMock, patch

from aioresponses import aioresponses
from redis.asyncio import Redis
from aiohttp import ClientSession

from src.open_weather import OpenWeatherClient
from src import settings


@pytest.mark.asyncio
def test_open_weather_client_init():
    client = OpenWeatherClient()

    assert client.url == settings.OPEN_WEATHER_BASE_URL
    assert client.headers == {"Content-Type": "application/json", "Accept": "application/json"}
    assert client.timeout == settings.OPEN_WEATHER_TIMEOUT_SECONDS
    assert client.max_retries == settings.OPEN_WEATHER_MAX_RETRIES
    assert client.backoff == settings.OPEN_WEATHER_BACKOFF

@pytest.mark.asyncio
def test_kelvin_to_celsius():
    client = OpenWeatherClient()
    kelvin = 300
    celsius = client._kelvin_to_celsius(kelvin)
    assert celsius == 26.85

@pytest.mark.asyncio
async def test_fetch_weather_by_city_success():
    client = OpenWeatherClient()
    mock_redis = AsyncMock(spec=Redis)
    ref_id = 1
    city_id = 3439525
    requested_at = "2023-01-01T00:00:00Z"

    mock_redis.hset = AsyncMock()

    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = AsyncMock(spec=aiohttp.ClientResponse)
        mock_response.status = 200

        async def mock_json():
            return {
                "main": {"temp": 300, "humidity": 50}
            }

        mock_response.json = mock_json
        mock_get.return_value.__aenter__.return_value = mock_response

        async with ClientSession() as session:
            await client.fetch_weather_by_city(mock_redis, session, ref_id, city_id, requested_at)

    mock_redis.hset.assert_called()


@pytest.mark.asyncio
async def test_fetch_weather_by_city_retry(mock_redis, mock_aiohttp_session):
    client = OpenWeatherClient()
    ref_id = 1
    city_id = 3439525
    requested_at = "2023-01-01T00:00:00Z"

    with aioresponses() as m:
        url = f"{client.url}?id={city_id}&appid={settings.OPEN_WEATHER_API_KEY}"
        m.get(url, status=500)

        with pytest.raises(Exception):
            await client.fetch_weather_by_city(mock_redis, mock_aiohttp_session, ref_id, city_id, requested_at)

        assert mock_redis.hset.call_count == 0
