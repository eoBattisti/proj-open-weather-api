import json
from typing import Dict
import redis

from .settings import REDIS_HOST, REDIS_PORT, CITY_IDS


async def get_redis() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def store_weather_data(
    redis_client: redis.Redis,
    ref_id: int,
    city_id: int,
    data: Dict
) -> None:
    redis_client.hset(name=str(ref_id), key=str(city_id), value=json.dumps(data))


def get_progress_from_redis(
    redis_client: redis.Redis,
    user_id: int
) -> float:
    data = redis_client.hgetall(name=str(user_id))
    progres = (len(data) / len(CITY_IDS)) * 100
    return progres

