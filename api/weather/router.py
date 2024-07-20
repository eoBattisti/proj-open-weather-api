from datetime import datetime
import orjson

from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractRobustConnection
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from fastapi.responses import ORJSONResponse
from redis import Redis

from core.rabbit import get_rabbit_connection
from core.redis import get_redis, get_progress_from_redis
from core.settings import CITY_IDS, RABBITMQ_QUEUE


router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("")
async def get_weather(
    ref_id: int,
    redis: Redis = Depends(dependency=get_redis)
):
    try:
        if not redis.hexists(name=str(ref_id), key=str(CITY_IDS[0])):
            raise RuntimeError
        progress = get_progress_from_redis(redis=redis, ref_id=ref_id)
    except RuntimeError:
        raise HTTPException(status_code=404, detail="User ref_id not found! Please try again with a valid ref_id.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: %s" % e)
    else:
        return ORJSONResponse(content={"id": ref_id, "progress": "{:.2f}%".format(progress)})


@router.post("")
async def collect_weather(
    ref_id: int,
    redis: Redis = Depends(dependency=get_redis),
    rabbitmq: AbstractRobustConnection= Depends(dependency=get_rabbit_connection)
):
    try:
        if redis.hexists(name=str(ref_id), key=str(CITY_IDS[0])):
            raise ValueError

        async with rabbitmq.channel() as channel:
            await channel.default_exchange.publish(
                Message(
                    orjson.dumps(
                        {
                         "ref_id": ref_id,
                         "requested_at": datetime.now().isoformat()
                        }
                    ),
                    delivery_mode=DeliveryMode.PERSISTENT
                ),
                routing_key=RABBITMQ_QUEUE
            )
    except ValueError:
        raise HTTPException(status_code=400, detail="User ref_id already exists. Please try again with a new ref_id.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: %s" % e)
    else:
        return ORJSONResponse(content={"message": "Task created", "ref_id": ref_id})
