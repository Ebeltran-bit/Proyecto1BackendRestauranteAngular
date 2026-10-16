from typing import List

from fastapi import APIRouter

from app.data.sample_data import CATEGORIES, PRODUCT_PRESENTATIONS, PRODUCTS_BY_CATEGORY
from app.schemas import MenuCategory, MenuProduct

router = APIRouter(prefix="/menu", tags=["menu"])


@router.get("", response_model=List[MenuCategory], summary="Whole menu with presentations and prices in one request")
def get_menu() -> List[MenuCategory]:
    return [
        MenuCategory(
            **category.model_dump(),
            products=[
                MenuProduct(**product.model_dump(), presentations=PRODUCT_PRESENTATIONS[product.id])
                for product in PRODUCTS_BY_CATEGORY[category.id]
            ],
        )
        for category in CATEGORIES
    ]
