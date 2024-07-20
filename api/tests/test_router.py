import aio_pika
import pytest

from aio_pika.abc import AbstractRobustConnection
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import redis

from core.rabbit import get_rabbit_connection
from core.redis import get_redis
from core.settings import CITY_IDS


@pytest.mark.asyncio
async def test_get_weather_success(client: TestClient):
    ref_id = 1
    mock_redis = AsyncMock(spec=redis.Redis)
    mock_redis.hexists.return_value = True
    mock_redis.hgetall.return_value = {
        str(CITY_IDS[0]): b'{"request_at": "2022-01-01T00:00:00", "city_id": 1, "temperature": 25, "humidity": 50}'
    }

    client.app.dependency_overrides[get_redis] = lambda: mock_redis

    with patch("weather.router.get_redis", return_value=mock_redis):
        response = client.get(f"/weather?ref_id={ref_id}")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_weather_not_found(client: TestClient):
    ref_id = 2
    mock_redis = AsyncMock(spec=redis.Redis)
    mock_redis.hexists.return_value = False

    client.app.dependency_overrides[get_redis] = lambda: mock_redis

    with patch("weather.router.get_redis", return_value=mock_redis):
        response = client.get(f"/weather?ref_id={ref_id}")
        print(response.json())
        assert response.status_code == 404
        assert response.json() == {"detail": "User ref_id not found! Please try again with a valid ref_id."}

@pytest.mark.asyncio
async def test_get_weather_with_unexpected_error(client: TestClient):
    ref_id = 3
    mock_redis = AsyncMock(spec=redis.Redis)
    mock_redis.hexists.return_value = True

    client.app.dependency_overrides[get_redis] = lambda: mock_redis

    with patch("weather.router.get_redis", return_value=mock_redis):
        with pytest.raises(Exception):
            reponse = client.get(f"/weather?ref_id={ref_id}")
            assert reponse.status_code == 500

@pytest.mark.asyncio
async def test_collect_weather_success(client: TestClient):
    ref_id = 3
    mock_redis = AsyncMock(spec=redis.Redis)
    mock_rabbitmq = AsyncMock(spec=AbstractRobustConnection)
    mock_channel = AsyncMock(spec=aio_pika.abc.AbstractChannel)
    mock_default_exchange = AsyncMock(spec=aio_pika.abc.AbstractExchange)

    mock_channel.default_exchange = mock_default_exchange
    mock_rabbitmq.channel.return_value.__aenter__.return_value = mock_channel
    mock_redis.hexists.return_value = False

    client.app.dependency_overrides[get_redis] = lambda: mock_redis
    client.app.dependency_overrides[get_rabbit_connection] = lambda: mock_rabbitmq

    with patch("weather.router.get_redis", return_value=mock_redis):
        with patch("core.rabbit.get_rabbit_connection", return_value=mock_rabbitmq):
            response = client.post(f"/weather?ref_id={ref_id}")
            print(response.json())
            assert response.status_code == 200
            assert response.json() == {"message": "Task created", "ref_id": ref_id}

@pytest.mark.asyncio
async def test_collect_weather_with_unexpected_error(client: TestClient):
    ref_id = 3
    mock_redis = AsyncMock(spec=redis.Redis)
    mock_rabbitmq = AsyncMock(spec=AbstractRobustConnection)

    client.app.dependency_overrides[get_redis] = lambda: mock_redis
    client.app.dependency_overrides[get_rabbit_connection] = lambda: mock_rabbitmq

    with patch("weather.router.get_redis", return_value=mock_redis):
        with patch("core.rabbit.get_rabbit_connection", return_value=mock_rabbitmq):
            with pytest.raises(Exception):
                response = client.post(f"/weather?ref_id={ref_id}")
                assert response.status_code == 500

@pytest.mark.asyncio
async def test_collect_weather_already_exists(client: TestClient):
    ref_id = 3
    mock_redis = AsyncMock(spec=redis.Redis)
    mock_redis.hexists.return_value = True
    mock_rabbitmq = AsyncMock(spec=AbstractRobustConnection)

    client.app.dependency_overrides[get_redis] = lambda: mock_redis
    client.app.dependency_overrides[get_rabbit_connection] = lambda: mock_rabbitmq

    with patch("weather.router.get_redis", return_value=mock_redis):
        with patch("core.rabbit.get_rabbit_connection", return_value=mock_rabbitmq):
            response = client.post(f"/weather?ref_id={ref_id}")
            assert response.status_code == 400
            assert response.json() == {"detail": "User ref_id already exists. Please try again with a new ref_id."}

