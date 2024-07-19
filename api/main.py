from datetime import datetime

from fastapi import Depends, Request
from fastapi.applications import FastAPI

from core.database import AsyncSession
from schemas.wheater_data import WheaterData


app = FastAPI()

@app.get("/")
async def root(
):
    return {"message": "Hello World"}
