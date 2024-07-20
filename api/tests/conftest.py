from typing import Generator

import pytest
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient
from core.redis import get_redis

from main import app

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


