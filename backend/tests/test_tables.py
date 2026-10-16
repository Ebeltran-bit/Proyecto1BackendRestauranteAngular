def test_select_table(client):
    response = client.get("/tables/4")
    assert response.status_code == 200
    assert response.json() == {
        "id": 4, "name": "Terraza 1", "status": "free", "waiter_id": None, "waiter_name": None,
        "order_count": 0, "total": 0.0,
    }


def test_unknown_table_returns_404(client):
    response = client.get("/tables/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "No existe la mesa con id 999"}


def test_occupied_table_shows_waiter_orders_and_total(client):
    table = client.get("/tables/1").json()
    # Sample orders of table 1: 2 beers at 2.80 and a ración of bravas at 8.00.
    assert table == {
        "id": 1, "name": "Mesa 1", "status": "occupied", "waiter_id": 2, "waiter_name": "Ana Martín",
        "order_count": 2, "total": 13.6,
    }


def test_table_list_reflects_new_orders(client):
    client.post("/tables/5/orders", json={"product_id": 2, "presentation_id": 1, "quantity": 3})
    barra = next(t for t in client.get("/tables").json() if t["id"] == 5)
    assert barra["status"] == "occupied"
    assert barra["total"] == 7.5


def test_assign_and_remove_waiter(waiter_client):
    response = waiter_client.put("/tables/4/waiter", json={"waiter_id": 3})
    assert response.status_code == 200
    assert response.json()["waiter_name"] == "Luis Pérez"
    assert response.json()["status"] == "occupied"
    response = waiter_client.put("/tables/4/waiter", json={"waiter_id": None})
    assert response.json()["waiter_id"] is None
    assert response.json()["status"] == "free"


def test_only_waiters_can_be_assigned(client):
    response = client.put("/tables/4/waiter", json={"waiter_id": 1})  # user 1 is the manager
    assert response.status_code == 422
    assert response.json() == {"detail": "No existe el camarero con id 1"}
    assert client.put("/tables/4/waiter", json={"waiter_id": 999}).status_code == 422
    assert client.put("/tables/999/waiter", json={"waiter_id": 2}).status_code == 404
    assert client.put("/tables/4/waiter", json={}).status_code == 422
