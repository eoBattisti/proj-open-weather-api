from fastapi.applications import FastAPI
from fastapi.responses import ORJSONResponse

from weather.router import router as weather_router 


app = FastAPI(
    title="OpenWeather microservice",
    version="0.1.0",
    description="API to fetch weather data from OpenWeather and show the progress of the requests",
    default_response_class=ORJSONResponse
)

app.include_router(router=weather_router)
