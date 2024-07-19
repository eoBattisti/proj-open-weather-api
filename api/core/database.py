import logging
from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.settings import DB_URL


logger = logging.getLogger(__name__)

async_engine = create_async_engine(DB_URL, echo=False, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(bind=async_engine, autoflush=False, future=True)


async def get_session() -> AsyncIterator[async_sessionmaker]:
    try:
        yield AsyncSessionLocal
    except SQLAlchemyError as e:
        logger.exception(e)


AsyncSession = Annotated[AsyncSession, Depends(get_session)]
