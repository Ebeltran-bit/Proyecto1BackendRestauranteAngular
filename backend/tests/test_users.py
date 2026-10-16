import pytest

NEW_WAITER = {"username": "marta", "full_name": "Marta Ruiz", "password": "secreta1"}


def test_list_users_and_filter_by_role(waiter_client):
    users = waiter_client.get("/users").json()
    assert [u["username"] for u in users] == ["manager", "ana", "luis"]
    waiters = waiter_client.get("/users", params={"role": "waiter"}).json()
    assert [u["username"] for u in waiters] == ["ana", "luis"]


def test_manager_creates_a_waiter_who_can_log_in(client, anon_client):
    response = client.post("/users", json=NEW_WAITER)
    assert response.status_code == 201
    assert response.json() == {"id": 4, "username": "marta", "full_name": "Marta Ruiz", "role": "waiter"}
    login = anon_client.post("/auth/login", json={"username": "marta", "password": "secreta1"})
    assert login.status_code == 200


def test_waiter_cannot_create_or_delete_users(waiter_client):
    response = waiter_client.post("/users", json=NEW_WAITER)
    assert response.status_code == 403
    assert response.json() == {"detail": "Solo un manager puede hacer esto"}
    assert waiter_client.delete("/users/3").status_code == 403


def test_duplicate_username_returns_409(client):
    response = client.post("/users", json={**NEW_WAITER, "username": "ana"})
    assert response.status_code == 409
    assert response.json() == {"detail": "Ya existe un usuario con el nombre ana"}


@pytest.mark.parametrize(
    "changes",
    [
        {"username": "a"},
        {"username": "Con Espacios"},
        {"password": "123"},
        {"full_name": ""},
        {"role": "chef"},
        {"is_admin": True},
    ],
)
def test_invalid_user_returns_422(client, changes):
    assert client.post("/users", json={**NEW_WAITER, **changes}).status_code == 422


def test_delete_waiter_closes_their_sessions(client, anon_client):
    client.post("/users", json=NEW_WAITER)
    token = anon_client.post("/auth/login", json={"username": "marta", "password": "secreta1"}).json()["access_token"]
    assert client.delete("/users/4").status_code == 204
    assert [u["id"] for u in client.get("/users").json()] == [1, 2, 3]
    assert anon_client.get("/tables", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_cannot_delete_waiter_serving_open_tables(client):
    response = client.delete("/users/2")  # Ana serves table 1
    assert response.status_code == 409
    assert "Ana Martín" in response.json()["detail"]


def test_cannot_delete_yourself(client):
    response = client.delete("/users/1")
    assert response.status_code == 409
    assert response.json() == {"detail": "No puedes borrar tu propio usuario"}


def test_delete_unknown_user_returns_404(client):
    assert client.delete("/users/999").status_code == 404
