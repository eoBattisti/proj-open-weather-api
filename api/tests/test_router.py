import asyncio
import pytest

from unittest.mock import AsyncMock, patch

from aioresponses import aioresponses
from fastapi.testclient import TestClient

from core.settings import CITY_IDS, OPEN_WEATHER_BASE_URL, OPEN_WEATHER_API_KEY
from weather.utils import fetch_weather


@pytest.mark.asyncio
async def test_get_weather(get_client: TestClient) -> None:
    ref_id = 1234
    mock_redis = AsyncMock()

    with patch("weather.router.get_redis", return_value=mock_redis):
        response = get_client.get(f"/weather?ref_id={ref_id}")
        assert response.status_code == 200
        assert response.json() == {
            "id": ref_id,
            "progress": "0%"
        }

@pytest.mark.asyncio
async def test_collect_weather(get_client: TestClient) -> None:
    ref_id = 1
    mock_redis = AsyncMock()

    async def mock_fetch_weather(redis, session, user_id, city_id):
        return {"id": city_id, "weather": "sunny"}

    with patch("core.redis.get_redis", return_value=mock_redis):
        with patch("weather.utils.fetch_weather", side_effect=mock_fetch_weather):
            response = get_client.post(f"/weather?ref_id={ref_id}")
            assert response.status_code == 200
            assert response.json() == {"message": "Completed", "ref_id": ref_id}

@pytest.mark.asyncio
async def test_fetch_weather_with_retries_success_after_timeout() -> None:
    ref_id = 2
    city_id = CITY_IDS[0]

    async def mock_get(*args, **kwargs):
        return asyncio.TimeoutError

    mock_session = AsyncMock()
    mock_session.get.side_effect = mock_get

    with aioresponses() as mock:
        mock.get(f"{OPEN_WEATHER_BASE_URL}?id={city_id}&appid={OPEN_WEATHER_API_KEY}", exception=asyncio.TimeoutError)

        with pytest.raises(asyncio.TimeoutError):
            await fetch_weather(
                redis=AsyncMock(),
                session=mock_session,
                user_id=ref_id,
                city_id=city_id
            )
