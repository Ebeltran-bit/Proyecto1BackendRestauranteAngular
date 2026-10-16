from typing import List

from fastapi import APIRouter, Depends, status

from app.data.sample_data import CATEGORIES_BY_ID, PRODUCT_PRESENTATIONS
from app.routers.dependencies import get_product_or_404
from app.schemas import Product, ProductDetail, ProductPresentation

router = APIRouter(prefix="/products", tags=["products"])

NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Product not found"}}


@router.get(
    "/{product_id}",
    response_model=ProductDetail,
    summary="Get a product with its category and active presentations",
    responses=NOT_FOUND,
)
def get_product(product: Product = Depends(get_product_or_404)) -> ProductDetail:
    return ProductDetail(
        **product.model_dump(),
        category=CATEGORIES_BY_ID[product.category_id],
        presentations=PRODUCT_PRESENTATIONS[product.id],
    )


@router.get(
    "/{product_id}/presentations",
    response_model=List[ProductPresentation],
    summary="List only the presentations a product can be ordered in",
    responses=NOT_FOUND,
)
def list_product_presentations(product: Product = Depends(get_product_or_404)) -> List[ProductPresentation]:
    return PRODUCT_PRESENTATIONS[product.id]
