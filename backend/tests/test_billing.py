from datetime import date, timedelta


def test_pay_table_returns_bill_and_empties_the_table(waiter_client):
    response = waiter_client.post("/tables/1/pay")
    assert response.status_code == 201
    bill = response.json()
    assert bill["id"] == 1
    assert bill["table_name"] == "Mesa 1"
    assert bill["waiter_name"] == "Ana Martín"
    assert bill["paid_by"] == "Ana Martín"
    assert bill["total"] == 13.6
    assert bill["lines"][0] == {
        "product_id": 3, "product_name": "Cerveza", "presentation_name": "Unidad",
        "quantity": 2, "unit_price": 2.8, "line_total": 5.6, "notes": None,
    }
    table = waiter_client.get("/tables/1").json()
    assert table["status"] == "free"
    assert table["order_count"] == 0
    assert table["waiter_id"] is None
    assert waiter_client.get("/tables/1/orders").json() == []
    assert waiter_client.get("/bills/1").json() == bill


def test_paid_table_can_take_a_new_order_straight_away(client):
    client.post("/tables/1/pay")
    response = client.post("/tables/1/orders", json={"product_id": 1, "presentation_id": 1, "quantity": 1})
    assert response.status_code == 201
    assert client.get("/tables/1/orders").json() == [response.json()]


def test_paying_needs_a_waiter(client):
    client.post("/tables/4/orders", json={"product_id": 1, "presentation_id": 1, "quantity": 1})
    response = client.post("/tables/4/pay")
    assert response.status_code == 409
    assert response.json() == {"detail": "Elige el camarero que ha servido Terraza 1 antes de cobrarla"}
    assert len(client.get("/tables/4/orders").json()) == 1  # nothing was lost


def test_paying_an_empty_table_returns_409(client):
    client.put("/tables/4/waiter", json={"waiter_id": 3})
    response = client.post("/tables/4/pay")
    assert response.status_code == 409
    assert response.json() == {"detail": "Terraza 1 no tiene pedidos que cobrar"}


def test_bill_keeps_names_after_the_waiter_is_deleted(client):
    client.post("/tables/2/pay")  # served by Luis, id 3
    assert client.delete("/users/3").status_code == 204
    assert client.get("/bills/1").json()["waiter_name"] == "Luis Pérez"


def test_daily_report_adds_up_the_bills(client):
    client.post("/tables/1/orders", json={"product_id": 3, "presentation_id": 1, "quantity": 1})
    client.post("/tables/1/pay")  # Ana: 13.60 + 2.80 = 16.40
    client.post("/tables/2/pay")  # Luis: 8.00
    report = client.get("/reports/daily").json()
    assert report["day"] == date.today().isoformat()
    assert report["bills"] == 2
    assert report["total"] == 24.4
    assert report["average_ticket"] == 12.2
    assert report["by_waiter"] == [
        {"waiter_id": 2, "waiter_name": "Ana Martín", "bills": 1, "total": 16.4},
        {"waiter_id": 3, "waiter_name": "Luis Pérez", "bills": 1, "total": 8.0},
    ]
    assert report["top_products"][0] == {"product_id": 3, "product_name": "Cerveza", "quantity": 3, "total": 8.4}
    assert [bill["id"] for bill in client.get("/bills").json()] == [2, 1]


def test_report_of_another_day_is_empty(client):
    client.post("/tables/1/pay")
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    assert client.get("/bills", params={"day": yesterday}).json() == []
    report = client.get("/reports/daily", params={"day": yesterday}).json()
    assert report["bills"] == 0
    assert report["average_ticket"] == 0


def test_waiter_cannot_see_reports(waiter_client):
    assert waiter_client.get("/reports/daily").status_code == 403
    assert waiter_client.get("/bills").status_code == 403


def test_unknown_bill_returns_404(client):
    assert client.get("/bills/999").status_code == 404
