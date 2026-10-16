from app.data.sample_data import PRODUCT_PRESENTATIONS, PRODUCTS


def test_product_detail_includes_category_and_presentations(client):
    response = client.get("/products/4")
    assert response.status_code == 200
    assert response.json() == {
        "id": 4,
        "name": "Patatas bravas",
        "category_id": 2,
        "category": {"id": 2, "name": "Entrantes"},
        "presentations": [
            {"id": 2, "name": "Tapa", "price": 3.0},
            {"id": 3, "name": "Media ración", "price": 5.5},
            {"id": 4, "name": "Ración", "price": 8.0},
        ],
    }


def test_presentations_only_include_active_ones(client):
    for product in PRODUCTS:
        response = client.get(f"/products/{product.id}/presentations")
        assert response.status_code == 200
        expected = [p.model_dump() for p in PRODUCT_PRESENTATIONS[product.id]]
        assert response.json() == expected
        assert expected, f"product {product.id} should have at least one presentation"


def test_drink_is_only_sold_by_unit(client):
    assert client.get("/products/1/presentations").json() == [{"id": 1, "name": "Unidad", "price": 1.8}]


def test_unknown_product_returns_404(client):
    for path in ("/products/999", "/products/999/presentations"):
        response = client.get(path)
        assert response.status_code == 404
        assert response.json() == {"detail": "No existe el producto con id 999"}


def test_non_numeric_product_id_returns_422(client):
    assert client.get("/products/abc").status_code == 422
