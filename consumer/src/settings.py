import os

# Open Weather
OPEN_WEATHER_API_KEY = os.environ.get("OPEN_WEATHER_API_KEY")
OPEN_WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Constants
BATCH_SIZE = 60
MAX_RETRIES = 5
BACKOFF = 1

# Database Settings
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")

# RabbitMQ Settings
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT")
RABBITMQ_DEFAULT_USER = os.environ.get("RABBITMQ_DEFAULT_USER")
RABBITMQ_DEFAULT_PASSWORD = os.environ.get("RABBITMQ_DEFAULT_PASS")
RABBITMQ_DEFAULT_VHOST = os.environ.get("RABBITMQ_DEFAULT_VHOST")
RABBITMQ_QUEUE = os.environ.get("RABBITMQ_QUEUE")
