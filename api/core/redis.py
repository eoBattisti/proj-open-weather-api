import redis

from .settings import REDIS_HOST, REDIS_PORT, CITY_IDS


async def get_redis() -> redis.Redis:
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def get_progress_from_redis(
    redis: redis.Redis,
    ref_id: int
) -> float:
    data = redis.hgetall(name=str(ref_id))
    progres = (len(data) / len(CITY_IDS)) * 100
    return progres

