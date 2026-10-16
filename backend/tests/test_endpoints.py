from app.data.sample_data import CATEGORIES, PRODUCTS, TABLES


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_categories_returns_all_categories(client):
    response = client.get("/categories")
    assert response.status_code == 200
    assert response.json() == [category.model_dump() for category in CATEGORIES]


def test_list_tables_returns_all_tables(client):
    response = client.get("/tables")
    assert response.status_code == 200
    assert [{"id": t["id"], "name": t["name"]} for t in response.json()] == [t.model_dump() for t in TABLES]


def test_category_products_only_include_that_category(client):
    for category in CATEGORIES:
        response = client.get(f"/categories/{category.id}/products")
        assert response.status_code == 200
        expected = [p.model_dump() for p in PRODUCTS if p.category_id == category.id]
        assert response.json() == expected
        assert expected, f"category {category.id} should have sample products"


def test_unknown_category_returns_404_with_message(client):
    response = client.get("/categories/999/products")
    assert response.status_code == 404
    assert response.json() == {"detail": "No existe la categoría con id 999"}


def test_non_numeric_category_id_returns_422(client):
    response = client.get("/categories/abc/products")
    assert response.status_code == 422


def test_docs_and_openapi_list_every_endpoint(client):
    assert client.get("/docs").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    expected_paths = (
        "/health",
        "/categories",
        "/categories/{category_id}/products",
        "/products/{product_id}",
        "/products/{product_id}/presentations",
        "/tables",
        "/tables/{table_id}",
        "/tables/{table_id}/orders",
        "/tables/{table_id}/orders/{order_id}",
    )
    for path in expected_paths:
        assert path in paths
