from fastapi.applications import FastAPI

from weather.router import router as weather_router 

app = FastAPI()

app.include_router(router=weather_router)
