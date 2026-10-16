"""Orders of a table.

The routes follow the waiter's flow: select the table first and then list,
add, change or remove its orders. That is why every route starts with /tables/{table_id}.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.data.order_store import order_store
from app.data.sample_data import PRESENTATIONS_BY_ID, PRODUCT_PRESENTATION_IDS, PRODUCTS_BY_ID, unit_price
from app.routers.dependencies import get_order_or_404, get_table_or_404
from app.schemas import Order, OrderCreate, OrderUpdate, Table

router = APIRouter(prefix="/tables/{table_id}/orders", tags=["orders"])

TABLE_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Table not found"}}
ORDER_NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Table or order not found"}}


def _invalid(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=message)


def _check_presentation(product_id: int, presentation_id: int) -> None:
    """Reject a presentation that does not exist or is not active for the product."""
    if presentation_id not in PRESENTATIONS_BY_ID:
        raise _invalid(f"No existe la presentación con id {presentation_id}")
    if presentation_id not in PRODUCT_PRESENTATION_IDS[product_id]:
        product = PRODUCTS_BY_ID[product_id]
        presentation = PRESENTATIONS_BY_ID[presentation_id]
        raise _invalid(f"{product.name} no está disponible en {presentation.name}")


@router.get("", response_model=List[Order], summary="List the orders of a table", responses=TABLE_NOT_FOUND)
def list_orders(table: Table = Depends(get_table_or_404)) -> List[Order]:
    return order_store.list_by_table(table.id)


@router.post(
    "",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    summary="Add an order to a table",
    responses=TABLE_NOT_FOUND,
)
def create_order(body: OrderCreate, table: Table = Depends(get_table_or_404)) -> Order:
    if body.product_id not in PRODUCTS_BY_ID:
        raise _invalid(f"No existe el producto con id {body.product_id}")
    _check_presentation(body.product_id, body.presentation_id)
    return order_store.add(
        table.id,
        body.product_id,
        body.presentation_id,
        body.quantity,
        unit_price=unit_price(body.product_id, body.presentation_id),
        notes=body.notes or None,
    )


@router.get("/{order_id}", response_model=Order, summary="Get one order of a table", responses=ORDER_NOT_FOUND)
def get_order(order: Order = Depends(get_order_or_404)) -> Order:
    return order


@router.patch(
    "/{order_id}",
    response_model=Order,
    summary="Change the presentation, quantity or notes of an order",
    responses=ORDER_NOT_FOUND,
)
def update_order(body: OrderUpdate, order: Order = Depends(get_order_or_404)) -> Order:
    changes = body.model_dump(exclude_unset=True)
    if "presentation_id" in changes:
        _check_presentation(order.product_id, changes["presentation_id"])
        changes["unit_price"] = unit_price(order.product_id, changes["presentation_id"])
    if "notes" in changes:
        changes["notes"] = changes["notes"] or None
    return order_store.update(order.id, changes)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove an order line from the table",
    responses=ORDER_NOT_FOUND,
)
def delete_order(order: Order = Depends(get_order_or_404)) -> None:
    order_store.delete(order.id)
