from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from app import auth


def make_favorite(
    client: TestClient, headers: dict[str, str], name: str = "pikachu"
) -> dict[str, object]:
    res = client.post(
        "/favorites", json={"pokemon_name": name, "note": "nice"}, headers=headers
    )
    assert res.status_code == 201
    data: dict[str, object] = res.json()
    return data


# --- login ---
def test_login_returns_token(client: TestClient) -> None:
    res = client.post("/login", json={"username": "alice"})
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"
    assert res.json()["access_token"]


def test_login_rejects_empty_username(client: TestClient) -> None:
    res = client.post("/login", json={"username": ""})
    assert res.status_code == 422


# --- CRUD happy paths ---
def test_create_favorite(client: TestClient, alice: dict[str, str]) -> None:
    fav = make_favorite(client, alice)
    assert fav["id"] == 1
    assert fav["pokemon_name"] == "pikachu"
    assert fav["user_id"] == "alice"
    assert "date_added" in fav


def test_list_returns_only_own_favorites(
    client: TestClient, alice: dict[str, str], bob: dict[str, str]
) -> None:
    make_favorite(client, alice, "pikachu")
    make_favorite(client, bob, "eevee")
    res = client.get("/favorites", headers=alice)
    assert res.status_code == 200
    assert [f["pokemon_name"] for f in res.json()] == ["pikachu"]


def test_get_one(client: TestClient, alice: dict[str, str]) -> None:
    make_favorite(client, alice)
    res = client.get("/favorites/1", headers=alice)
    assert res.status_code == 200
    assert res.json()["pokemon_name"] == "pikachu"


def test_patch_updates_note(client: TestClient, alice: dict[str, str]) -> None:
    make_favorite(client, alice)
    res = client.patch("/favorites/1", json={"note": "updated"}, headers=alice)
    assert res.status_code == 200
    assert res.json()["note"] == "updated"


def test_patch_null_clears_note(client: TestClient, alice: dict[str, str]) -> None:
    make_favorite(client, alice)
    res = client.patch("/favorites/1", json={"note": None}, headers=alice)
    assert res.json()["note"] is None


def test_delete_then_404(client: TestClient, alice: dict[str, str]) -> None:
    make_favorite(client, alice)
    assert client.delete("/favorites/1", headers=alice).status_code == 204
    assert client.get("/favorites/1", headers=alice).status_code == 404


# --- 404s ---
def test_get_missing_returns_404(client: TestClient, alice: dict[str, str]) -> None:
    assert client.get("/favorites/999", headers=alice).status_code == 404


# --- auth failures ---
ROUTES = [
    ("POST", "/favorites"),
    ("GET", "/favorites"),
    ("GET", "/favorites/1"),
    ("PATCH", "/favorites/1"),
    ("DELETE", "/favorites/1"),
]


@pytest.mark.parametrize(("method", "path"), ROUTES)
def test_no_token_returns_401(client: TestClient, method: str, path: str) -> None:
    res = client.request(method, path, json={"pokemon_name": "pikachu"})
    assert res.status_code == 401


def test_invalid_token_returns_401(client: TestClient) -> None:
    res = client.get("/favorites", headers={"Authorization": "Bearer garbage"})
    assert res.status_code == 401


def test_expired_token_returns_401(client: TestClient) -> None:
    expired = jwt.encode(
        {"sub": "alice", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        auth.SECRET_KEY,
        algorithm=auth.ALGORITHM,
    )
    res = client.get("/favorites", headers={"Authorization": f"Bearer {expired}"})
    assert res.status_code == 401


# --- wrong user ---
def test_other_user_cannot_read(
    client: TestClient, alice: dict[str, str], bob: dict[str, str]
) -> None:
    make_favorite(client, alice)
    assert client.get("/favorites/1", headers=bob).status_code == 404


def test_other_user_cannot_edit_or_delete(
    client: TestClient, alice: dict[str, str], bob: dict[str, str]
) -> None:
    make_favorite(client, alice)
    assert (
        client.patch("/favorites/1", json={"note": "hax"}, headers=bob).status_code
        == 404
    )
    assert client.delete("/favorites/1", headers=bob).status_code == 404
    # alice's favorite is untouched
    assert client.get("/favorites/1", headers=alice).json()["note"] == "nice"


# --- validation ---
def test_create_rejects_empty_name(client: TestClient, alice: dict[str, str]) -> None:
    res = client.post("/favorites", json={"pokemon_name": ""}, headers=alice)
    assert res.status_code == 422


def test_create_rejects_missing_name(client: TestClient, alice: dict[str, str]) -> None:
    res = client.post("/favorites", json={"note": "no name"}, headers=alice)
    assert res.status_code == 422
