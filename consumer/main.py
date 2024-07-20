import os
import sys
import asyncio
import pika
import json

import aiohttp
from aio_pika.log import logger
import aio_pika

from src.settings import (
    CITY_IDS, BATCH_SIZE, RABBITMQ_DEFAULT_PASSWORD,
    RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_VHOST,
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_QUEUE,
    REDIS_HOST, REDIS_PORT
)
from redis.asyncio import Redis
from src.utils import fetch_weather, get_redis


def callback(ch, method, properties, body):
    body = json.loads(body)
    ref_id = body["ref_id"]
    print("Received task with ref_id: %s", ref_id)

async def process_task(message: aio_pika.IncomingMessage) -> None:
    async with message.process():
        body = json.loads(message.body)
        ref_id = body["ref_id"]
        logger.info("Received task with ref_id: %s", ref_id)

        redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(CITY_IDS), BATCH_SIZE):
                tasks = []

                logger.info("Fetching weather for %s", CITY_IDS[i:i + BATCH_SIZE])
                for city in CITY_IDS[i:i + BATCH_SIZE]:
                    tasks.append(
                        fetch_weather(
                            redis=redis,
                            session=session,
                            ref_id=ref_id,
                            city_id=city
                        )
                    )

                logger.info("Running tasks for %s", CITY_IDS[i:i + BATCH_SIZE])
                await asyncio.gather(*tasks)
                logger.info("Tasks runned for %s", CITY_IDS[i:i + BATCH_SIZE])
                await asyncio.sleep(60)  # Respect rate limit


async def main() -> None:
    connection = await aio_pika.connect_robust(f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_DEFAULT_VHOST}")
    channel = await connection.channel()
    queue = await channel.declare_queue("weather_task_queue", durable=True)

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

