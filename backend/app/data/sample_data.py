"""In-memory sample data.

It replaces the MySQL database until Phase 3. Lookup indexes are built once at
import time so each request is a dictionary access instead of a list scan.
"""

from typing import Dict, List, Tuple

from app.schemas import Category, Order, Presentation, Product, ProductPresentation, Table

CATEGORIES: List[Category] = [
    Category(id=1, name="Bebidas"),
    Category(id=2, name="Entrantes"),
    Category(id=3, name="Carnes"),
    Category(id=4, name="Pescados"),
    Category(id=5, name="Postres"),
]

PRODUCTS: List[Product] = [
    Product(id=1, name="Agua mineral", category_id=1),
    Product(id=2, name="Refresco de cola", category_id=1),
    Product(id=3, name="Cerveza", category_id=1),
    Product(id=4, name="Patatas bravas", category_id=2),
    Product(id=5, name="Croquetas caseras", category_id=2),
    Product(id=6, name="Ensaladilla rusa", category_id=2),
    Product(id=7, name="Secreto ibérico", category_id=3),
    Product(id=8, name="Albóndigas en salsa", category_id=3),
    Product(id=9, name="Calamares a la romana", category_id=4),
    Product(id=10, name="Boquerones fritos", category_id=4),
    Product(id=11, name="Tarta de queso", category_id=5),
    Product(id=12, name="Flan casero", category_id=5),
]

PRESENTATIONS: List[Presentation] = [
    Presentation(id=1, name="Unidad"),
    Presentation(id=2, name="Tapa"),
    Presentation(id=3, name="Media ración"),
    Presentation(id=4, name="Ración"),
]

# Price in cents of each product in each presentation it can currently be
# ordered in. It mirrors the availability and price columns of the `Carta` table
# (unidad, tapa, media ración, ración). Cents avoid rounding errors in totals.
PRODUCT_PRICES_CENTS: Dict[int, Dict[int, int]] = {
    1: {1: 180},
    2: {1: 250},
    3: {1: 280},
    4: {2: 300, 3: 550, 4: 800},
    5: {1: 150, 3: 650, 4: 1100},
    6: {2: 300, 4: 900},
    7: {3: 950, 4: 1650},
    8: {2: 350, 3: 700, 4: 1200},
    9: {2: 400, 3: 800, 4: 1400},
    10: {2: 350, 4: 1100},
    11: {1: 550},
    12: {1: 450},
}

PRODUCT_PRESENTATION_IDS: Dict[int, List[int]] = {
    product_id: list(prices) for product_id, prices in PRODUCT_PRICES_CENTS.items()
}

TABLES: List[Table] = [
    Table(id=1, name="Mesa 1"),
    Table(id=2, name="Mesa 2"),
    Table(id=3, name="Mesa 3"),
    Table(id=4, name="Terraza 1"),
    Table(id=5, name="Barra"),
]

CATEGORIES_BY_ID: Dict[int, Category] = {category.id: category for category in CATEGORIES}

PRODUCTS_BY_CATEGORY: Dict[int, List[Product]] = {category.id: [] for category in CATEGORIES}
for _product in PRODUCTS:
    PRODUCTS_BY_CATEGORY[_product.category_id].append(_product)

PRESENTATIONS_BY_ID: Dict[int, Presentation] = {p.id: p for p in PRESENTATIONS}

PRODUCTS_BY_ID: Dict[int, Product] = {product.id: product for product in PRODUCTS}

PRODUCT_PRESENTATIONS: Dict[int, List[ProductPresentation]] = {
    product_id: [
        ProductPresentation(**PRESENTATIONS_BY_ID[pid].model_dump(), price=cents / 100)
        for pid, cents in prices.items()
    ]
    for product_id, prices in PRODUCT_PRICES_CENTS.items()
}


def unit_price(product_id: int, presentation_id: int) -> float:
    """Price in euros of one unit of a product in a presentation it is sold in."""
    return PRODUCT_PRICES_CENTS[product_id][presentation_id] / 100

TABLES_BY_ID: Dict[int, Table] = {table.id: table for table in TABLES}

# Orders the API starts with, so a table already has something to list.
SAMPLE_ORDERS: List[Order] = [
    Order(id=1, table_id=1, product_id=3, presentation_id=1, quantity=2, unit_price=unit_price(3, 1)),
    Order(id=2, table_id=1, product_id=4, presentation_id=4, quantity=1, unit_price=unit_price(4, 4)),
    Order(id=3, table_id=2, product_id=9, presentation_id=3, quantity=1, unit_price=unit_price(9, 3)),
]

# Waiter serving each table when the API starts (tables without orders have none).
SAMPLE_TABLE_WAITERS: Dict[int, int] = {1: 2, 2: 3}

# Demo staff: (username, full name, role, password). Passwords are only for the
# demo; they are hashed when loaded and never stored or returned in plain text.
SAMPLE_USERS: List[Tuple[str, str, str, str]] = [
    ("manager", "Laura Gómez", "manager", "manager123"),
    ("ana", "Ana Martín", "waiter", "camarero123"),
    ("luis", "Luis Pérez", "waiter", "camarero123"),
]
