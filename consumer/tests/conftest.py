import pytest
from unittest.mock import AsyncMock

import aiohttp
from redis.asyncio import Redis

from src.open_weather import OpenWeatherClient


@pytest.fixture
def mock_redis():
    return AsyncMock(spec=Redis)

@pytest.fixture
def mock_open_weather_client():
    return AsyncMock(OpenWeatherClient)

@pytest.fixture
async def mock_aiohttp_session():
    async with aiohttp.ClientSession() as session:
        yield session
