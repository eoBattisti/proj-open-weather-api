from __future__ import annotations
from collections.abc import AsyncIterator

from datetime import datetime

from sqlalchemy import DateTime, Integer, select
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped

from models.base import Base


class WeatherData(Base):
    __tablename__ = "weather_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ref_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=True)


    @classmethod
    async def read_by_id(cls, session: AsyncSession, ref_id: int) -> AsyncIterator[WeatherData]:
        stmt = select(cls).where(cls.ref_id == ref_id)
        stream = await session.stream_scalars(stmt.order_by(cls.id))
        async for obj in stream:
            yield obj
