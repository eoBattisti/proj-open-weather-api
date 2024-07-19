from typing import Generator

import pytest

from fastapi.testclient import TestClient

from main import app

@pytest.fixture
def get_client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


