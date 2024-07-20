import asyncio
import json
import pytest
from unittest.mock import AsyncMock, patch

import aiohttp
import aio_pika
from redis import Redis
from src.open_weather import OpenWeatherClient

from main import process_task, main
from src.settings import OPEN_WEATHER_BATCH_SIZE

@pytest.mark.asyncio
async def test_process_task():
    # Mock the message
    body = {
        "ref_id": 123,
        "requested_at": "2023-01-01T00:00:00Z",
        "city_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }
    message = AsyncMock(spec=aio_pika.IncomingMessage)
    message.body = json.dumps(body).encode()

    # Mock Redis
    mock_redis = AsyncMock(Redis)
    with patch('main.Redis', return_value=mock_redis):
        # Mock OpenWeatherClient
        mock_open_weather_client = AsyncMock(OpenWeatherClient)
        with patch('main.OpenWeatherClient', return_value=mock_open_weather_client):
            # Mock aiohttp ClientSession
            async with aiohttp.ClientSession() as session:
                with patch('aiohttp.ClientSession', return_value=session):
                    # Call the process_task function
                    await process_task(message)

                    # Assertions
                    assert mock_open_weather_client.fetch_weather_by_city.call_count == len(body["city_ids"])
                    for i in range(0, len(body["city_ids"]), OPEN_WEATHER_BATCH_SIZE):
                        for city in body["city_ids"][i:i + OPEN_WEATHER_BATCH_SIZE]:
                            mock_open_weather_client.fetch_weather_by_city.assert_any_call(
                                redis=mock_redis,
                                session=session,
                                ref_id=body["ref_id"],
                                city_id=city,
                                requested_at=body["requested_at"]
                            )


@pytest.mark.asyncio
async def test_main():
    mock_connection = AsyncMock(spec=aio_pika.abc.AbstractRobustConnection)
    mock_channel = AsyncMock(spec=aio_pika.abc.AbstractChannel)
    mock_queue = AsyncMock(spec=aio_pika.abc.AbstractQueue)

    mock_connection.channel.return_value = mock_channel
    mock_channel.declare_queue.return_value = mock_queue
    mock_queue.consume.return_value = AsyncMock()

    async def async_mock():
        return mock_channel
    mock_connection.channel.side_effect = async_mock

    async def async_mock_declare_queue(*args, **kwargs):
        return mock_queue
    mock_channel.declare_queue.side_effect = async_mock_declare_queue

    with patch('aio_pika.connect_robust', return_value=mock_connection):
        task = asyncio.create_task(main())

        await asyncio.sleep(0.1)

        mock_queue.consume.assert_called_once()

        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
