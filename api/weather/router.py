import asyncio
from typing import Coroutine, List
import aiohttp

from fastapi import Depends

from fastapi.routing import APIRouter
from fastapi.responses import ORJSONResponse
from redis import Redis

from core.redis import get_redis, get_progress_from_redis
from core.settings import CITY_IDS, BATCH_SIZE
from weather.utils import fetch_weather


router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("", response_class=ORJSONResponse)
async def get_weather(
    ref_id: int,
    redis: Redis = Depends(dependency=get_redis)
):
    progress = get_progress_from_redis(redis_client=redis, ref_id=ref_id)
    return ORJSONResponse(content={"id": ref_id, "progress": "{:.2f}%".format(progress)})


@router.post("", response_class=ORJSONResponse)
async def collect_weather(
    ref_id: int,
    redis: Redis = Depends(get_redis)
):
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(CITY_IDS), BATCH_SIZE):
            tasks: List[Coroutine] = []

            for city in CITY_IDS[i:i + BATCH_SIZE]:
                tasks.append(
                    fetch_weather(
                        redis=redis,
                        session=session,
                        user_id=ref_id,
                        city_id=city
                    )
                )

            await asyncio.gather(*tasks)
            await asyncio.sleep(60)  # Respect rate limit

    return ORJSONResponse(content={"message": "Completed", "ref_id": ref_id})
