from itertools import count

import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture(autouse=True)
def reset_store() -> None:
    main.favorites.clear()
    main.id_counter = count(1)


@pytest.fixture
def client() -> TestClient:
    return TestClient(main.app)


def login_headers(client: TestClient, username: str) -> dict[str, str]:
    res = client.post("/login", json={"username": username})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def alice(client: TestClient) -> dict[str, str]:
    return login_headers(client, "alice")


@pytest.fixture
def bob(client: TestClient) -> dict[str, str]:
    return login_headers(client, "bob")
