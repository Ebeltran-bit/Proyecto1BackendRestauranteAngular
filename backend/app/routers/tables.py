from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.data.sample_data import TABLES
from app.data.table_waiters import table_waiter_store
from app.data.user_store import user_store
from app.routers.dependencies import get_current_user, get_table_or_404
from app.schemas import Bill, Table, TableStatus, User, WaiterAssignment
from app.services.billing import pay_table
from app.services.tables import table_status

router = APIRouter(prefix="/tables", tags=["tables"])

NOT_FOUND = {status.HTTP_404_NOT_FOUND: {"description": "Table not found"}}


@router.get("", response_model=List[TableStatus], summary="List restaurant tables with their state")
def list_tables() -> List[TableStatus]:
    return [table_status(table) for table in TABLES]


@router.get("/{table_id}", response_model=TableStatus, summary="Select a table", responses=NOT_FOUND)
def get_table(table: Table = Depends(get_table_or_404)) -> TableStatus:
    return table_status(table)


@router.put(
    "/{table_id}/waiter",
    response_model=TableStatus,
    summary="Choose the waiter serving a table",
    responses=NOT_FOUND,
)
def assign_waiter(body: WaiterAssignment, table: Table = Depends(get_table_or_404)) -> TableStatus:
    if body.waiter_id is not None:
        waiter = user_store.get(body.waiter_id)
        if waiter is None or waiter.role != "waiter":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"No existe el camarero con id {body.waiter_id}",
            )
    table_waiter_store.set(table.id, body.waiter_id)
    return table_status(table)


@router.post(
    "/{table_id}/pay",
    response_model=Bill,
    status_code=status.HTTP_201_CREATED,
    summary="Mark the table as paid: saves the bill and empties the table",
    responses={**NOT_FOUND, status.HTTP_409_CONFLICT: {"description": "No orders or no waiter chosen"}},
)
def pay(table: Table = Depends(get_table_or_404), user: User = Depends(get_current_user)) -> Bill:
    return pay_table(table, paid_by=user)
