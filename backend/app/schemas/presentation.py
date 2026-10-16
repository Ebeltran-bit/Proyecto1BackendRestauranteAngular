from pydantic import BaseModel


class Presentation(BaseModel):
    """Serving size a product can be ordered in (table `Tipos` in the classroom database)."""

    id: int
    name: str


class ProductPresentation(Presentation):
    """Presentation of one specific product, with the price it is sold at."""

    price: float
