import os
import sys
import asyncio
import json
from typing import List

import aiohttp
import aio_pika

from src.settings import (
    BATCH_SIZE, RABBITMQ_DEFAULT_PASSWORD,
    RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_VHOST,
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE,
    REDIS_HOST, REDIS_PORT
)
from redis.asyncio import Redis
from src.utils import fetch_weather


async def process_task(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        body = json.loads(message.body)
        ref_id: int = body["ref_id"]
        requested_at: str = body["requested_at"]
        city_ids: List[int] = body["city_ids"]

        redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(city_ids), BATCH_SIZE):
                tasks = []

                for city in city_ids[i:i + BATCH_SIZE]:
                    tasks.append(
                        fetch_weather(
                            redis=redis,
                            session=session,
                            ref_id=ref_id,
                            city_id=city,
                            requested_at=requested_at
                        )
                    )

                await asyncio.gather(*tasks)
                await asyncio.sleep(60)  # Respect rate limit


async def main() -> None:
    connection = await aio_pika.connect_robust(f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_DEFAULT_VHOST}")
    channel = await connection.channel()
    queue = await channel.declare_queue(RABBITMQ_QUEUE, durable=True)

    await queue.consume(process_task)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

