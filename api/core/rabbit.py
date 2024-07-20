from aio_pika import connect_robust
from aio_pika.abc import AbstractRobustConnection

from core.settings import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_DEFAULT_USER,
    RABBITMQ_DEFAULT_PASSWORD,
    RABBITMQ_DEFAULT_VHOST
)

async def get_rabbit_connection() -> AbstractRobustConnection: 
    connection = await connect_robust(f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASSWORD}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_DEFAULT_VHOST}") 
    return connection
