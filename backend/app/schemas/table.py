from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

TableState = Literal["free", "occupied"]

class Table(BaseModel):
    """Restaurant table where orders are taken (table `Mesas` in the classroom database)."""

    id: int
    name: str

class TableStatus(Table):
    """Table with the state of its open bill, so the floor plan can be drawn in one request."""

    status: TableState
    waiter_id: Optional[int] = None
    waiter_name: Optional[str] = None
    order_count: int
    total: float

class WaiterAssignment(BaseModel):
    """JSON body to choose the waiter serving a table. null removes the waiter."""

    model_config = ConfigDict(strict=True, extra="forbid")

    waiter_id: Optional[int] = Field(gt=0)
