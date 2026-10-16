import pytest


def test_login_returns_token_and_user(anon_client):
    response = anon_client.post("/auth/login", json={"username": "Ana", "password": "camarero123"})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20
    assert body["user"] == {"id": 2, "username": "ana", "full_name": "Ana Martín", "role": "waiter"}


@pytest.mark.parametrize("username,password", [("ana", "wrong"), ("nobody", "camarero123")])
def test_wrong_credentials_return_401(anon_client, username, password):
    response = anon_client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 401
    assert response.json() == {"detail": "Usuario o contraseña incorrectos"}


def test_me_returns_logged_user(waiter_client):
    assert waiter_client.get("/auth/me").json()["username"] == "ana"


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/tables"),
        ("get", "/tables/1/orders"),
        ("get", "/menu"),
        ("get", "/categories"),
        ("get", "/products/1"),
        ("get", "/users"),
        ("post", "/tables/1/pay"),
        ("get", "/reports/daily"),
    ],
)
def test_routes_need_a_session(anon_client, method, path):
    response = getattr(anon_client, method)(path)
    assert response.status_code == 401
    assert response.json() == {"detail": "Inicia sesión para continuar"}


def test_invalid_token_returns_401(anon_client):
    response = anon_client.get("/tables", headers={"Authorization": "Bearer invented"})
    assert response.status_code == 401
    assert response.json() == {"detail": "La sesión ha caducado. Vuelve a iniciar sesión"}


def test_health_is_public(anon_client):
    assert anon_client.get("/health").status_code == 200


def test_logout_invalidates_the_token(waiter_client):
    assert waiter_client.post("/auth/logout").status_code == 204
    assert waiter_client.get("/tables").status_code == 401


def test_passwords_are_never_returned(client):
    for user in client.get("/users").json():
        assert set(user) == {"id", "username", "full_name", "role"}
