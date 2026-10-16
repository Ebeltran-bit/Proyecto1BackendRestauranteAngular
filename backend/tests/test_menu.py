from app.data.sample_data import CATEGORIES, PRODUCTS


def test_menu_has_every_category_product_and_price(client):
    menu = client.get("/menu").json()
    assert [c["id"] for c in menu] == [c.id for c in CATEGORIES]
    assert sum(len(c["products"]) for c in menu) == len(PRODUCTS)
    bravas = next(p for c in menu for p in c["products"] if p["id"] == 4)
    assert bravas["presentations"] == [
        {"id": 2, "name": "Tapa", "price": 3.0},
        {"id": 3, "name": "Media ración", "price": 5.5},
        {"id": 4, "name": "Ración", "price": 8.0},
    ]
