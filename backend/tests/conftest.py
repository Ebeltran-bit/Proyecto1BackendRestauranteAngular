import pytest
from fastapi.testclient import TestClient

from app.data.bill_store import bill_store
from app.data.order_store import order_store
from app.data.table_waiters import table_waiter_store
from app.data.user_store import user_store
from app.main import app

MANAGER = ("manager", "manager123")
WAITER = ("ana", "camarero123")  # id 2


def _logged_in(username: str, password: str) -> TestClient:
    client = TestClient(app)
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
    return client


@pytest.fixture
def client():
    """Logged in as a manager, who can call every route."""
    return _logged_in(*MANAGER)


@pytest.fixture
def waiter_client():
    return _logged_in(*WAITER)


@pytest.fixture
def anon_client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_data():
    """Each test starts from the sample data, whatever the previous test changed."""
    stores = (order_store, table_waiter_store, user_store, bill_store)
    for store in stores:
        store.reset()
    yield
    for store in stores:
        store.reset()
