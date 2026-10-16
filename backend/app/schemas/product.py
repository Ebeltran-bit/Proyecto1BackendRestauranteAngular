from typing import List

from pydantic import BaseModel

from app.schemas.category import Category
from app.schemas.presentation import ProductPresentation


class Product(BaseModel):
    """Menu item that belongs to one category (table `Carta` in the classroom database)."""

    id: int
    name: str
    category_id: int


class ProductDetail(Product):
    """Product with its category and the presentations it can currently be ordered in."""

    category: Category
    presentations: List[ProductPresentation]


class MenuProduct(Product):
    """Product inside the full menu, with its active presentations and prices."""

    presentations: List[ProductPresentation]


class MenuCategory(Category):
    """Category of the full menu with all its products."""

    products: List[MenuProduct]
