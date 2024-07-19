from datetime import datetime

from core.schema import BaseSchema


class Data(BaseSchema):
    city_id: int
    humidity: int
    temperature: int


class WheaterData(BaseSchema):
    id: int
    ref_id: int
    requested_at: datetime
    status: int
    data: dict
