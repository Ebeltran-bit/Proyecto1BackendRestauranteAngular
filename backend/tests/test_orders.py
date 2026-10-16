import pytest


def test_list_orders_of_a_table(client):
    response = client.get("/tables/1/orders")
    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "table_id": 1, "product_id": 3, "presentation_id": 1, "quantity": 2, "unit_price": 2.8, "notes": None},
        {"id": 2, "table_id": 1, "product_id": 4, "presentation_id": 4, "quantity": 1, "unit_price": 8.0, "notes": None},
    ]


def test_table_without_orders_returns_empty_list(client):
    response = client.get("/tables/5/orders")
    assert response.status_code == 200
    assert response.json() == []


def test_orders_of_unknown_table_return_404(client):
    response = client.get("/tables/999/orders")
    assert response.status_code == 404
    assert response.json() == {"detail": "No existe la mesa con id 999"}


def test_create_order_then_it_appears_in_the_table(client):
    body = {"product_id": 5, "presentation_id": 3, "quantity": 2}
    response = client.post("/tables/3/orders", json=body)
    assert response.status_code == 201
    created = response.json()
    assert created == {"id": 4, "table_id": 3, **body, "unit_price": 6.5, "notes": None}
    assert client.get("/tables/3/orders").json() == [created]
    assert client.get(f"/tables/3/orders/{created['id']}").json() == created


def test_created_ids_are_unique(client):
    body = {"product_id": 1, "presentation_id": 1, "quantity": 1}
    ids = {client.post("/tables/2/orders", json=body).json()["id"] for _ in range(5)}
    assert len(ids) == 5


def test_create_order_in_unknown_table_returns_404(client):
    response = client.post("/tables/999/orders", json={"product_id": 1, "presentation_id": 1, "quantity": 1})
    assert response.status_code == 404


def test_create_order_with_unknown_product_returns_422(client):
    response = client.post("/tables/1/orders", json={"product_id": 999, "presentation_id": 1, "quantity": 1})
    assert response.status_code == 422
    assert response.json() == {"detail": "No existe el producto con id 999"}


def test_create_order_with_unknown_presentation_returns_422(client):
    response = client.post("/tables/1/orders", json={"product_id": 4, "presentation_id": 99, "quantity": 1})
    assert response.status_code == 422
    assert response.json() == {"detail": "No existe la presentación con id 99"}


def test_create_order_with_inactive_presentation_returns_422(client):
    response = client.post("/tables/1/orders", json={"product_id": 1, "presentation_id": 4, "quantity": 1})
    assert response.status_code == 422
    assert response.json() == {"detail": "Agua mineral no está disponible en Ración"}


@pytest.mark.parametrize(
    "body",
    [
        {"product_id": 1, "presentation_id": 1},  # missing quantity
        {"product_id": 1, "presentation_id": 1, "quantity": 0},
        {"product_id": 1, "presentation_id": 1, "quantity": 100},
        {"product_id": 1, "presentation_id": 1, "quantity": "2"},  # string, not number
        {"product_id": 1, "presentation_id": 1, "quantity": 1.5},
        {"product_id": 1, "presentation_id": 1, "quantity": 1, "price": 3},  # unknown field
        {"product_id": -1, "presentation_id": 1, "quantity": 1},
    ],
)
def test_create_order_with_invalid_json_returns_422(client, body):
    response = client.post("/tables/1/orders", json=body)
    assert response.status_code == 422
    assert len(client.get("/tables/1/orders").json()) == 2  # nothing was saved


def test_create_order_with_malformed_json_returns_422(client):
    response = client.post(
        "/tables/1/orders", content="{not json", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


def test_update_quantity(client):
    response = client.patch("/tables/1/orders/1", json={"quantity": 5})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1, "table_id": 1, "product_id": 3, "presentation_id": 1, "quantity": 5, "unit_price": 2.8, "notes": None
    }
    assert client.get("/tables/1/orders/1").json()["quantity"] == 5


def test_update_presentation_and_quantity(client):
    response = client.patch("/tables/1/orders/2", json={"presentation_id": 2, "quantity": 3})
    assert response.status_code == 200
    # The price follows the new presentation: a tapa of bravas costs 3.00, not 8.00.
    assert response.json() == {
        "id": 2, "table_id": 1, "product_id": 4, "presentation_id": 2, "quantity": 3, "unit_price": 3.0, "notes": None
    }


def test_update_to_inactive_presentation_returns_422_and_keeps_order(client):
    response = client.patch("/tables/1/orders/1", json={"presentation_id": 4})
    assert response.status_code == 422
    assert response.json() == {"detail": "Cerveza no está disponible en Ración"}
    assert client.get("/tables/1/orders/1").json()["presentation_id"] == 1


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"quantity": None},
        {"quantity": 0},
        {"product_id": 2},  # the product of an order cannot be changed
        {"table_id": 2},
        {"unit_price": 0.1},  # the price comes from the menu, never from the client
        {"notes": "x" * 201},
    ],
)
def test_update_with_invalid_json_returns_422(client, body):
    response = client.patch("/tables/1/orders/1", json=body)
    assert response.status_code == 422


def test_order_of_another_table_returns_404(client):
    # Order 3 belongs to table 2, so it cannot be read or changed through table 1.
    assert client.get("/tables/1/orders/3").status_code == 404
    response = client.patch("/tables/1/orders/3", json={"quantity": 9})
    assert response.status_code == 404
    assert response.json() == {"detail": "La mesa 1 no tiene ningún pedido con id 3"}
    assert client.get("/tables/2/orders/3").json()["quantity"] == 1


def test_unknown_order_returns_404(client):
    assert client.get("/tables/1/orders/999").status_code == 404
    assert client.patch("/tables/1/orders/999", json={"quantity": 1}).status_code == 404


def test_create_order_with_notes(client):
    body = {"product_id": 7, "presentation_id": 4, "quantity": 1, "notes": "  Poco hecho  "}
    created = client.post("/tables/3/orders", json=body).json()
    assert created["notes"] == "Poco hecho"
    assert created["unit_price"] == 16.5


def test_update_and_clear_notes(client):
    assert client.patch("/tables/1/orders/1", json={"notes": "Sin gluten"}).json()["notes"] == "Sin gluten"
    assert client.patch("/tables/1/orders/1", json={"notes": None}).json()["notes"] is None
    client.patch("/tables/1/orders/1", json={"notes": "Fría"})
    assert client.patch("/tables/1/orders/1", json={"notes": ""}).json()["notes"] is None


def test_delete_order(client):
    response = client.delete("/tables/1/orders/1")
    assert response.status_code == 204
    assert [order["id"] for order in client.get("/tables/1/orders").json()] == [2]
    assert client.get("/tables/1/orders/1").status_code == 404


def test_delete_order_of_another_table_returns_404(client):
    assert client.delete("/tables/1/orders/3").status_code == 404
    assert client.get("/tables/2/orders/3").status_code == 200


def test_waiter_can_manage_orders(waiter_client):
    created = waiter_client.post("/tables/4/orders", json={"product_id": 1, "presentation_id": 1, "quantity": 1})
    assert created.status_code == 201
    order_id = created.json()["id"]
    assert waiter_client.patch(f"/tables/4/orders/{order_id}", json={"quantity": 2}).status_code == 200
    assert waiter_client.delete(f"/tables/4/orders/{order_id}").status_code == 204
