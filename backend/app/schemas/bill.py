from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class BillLine(BaseModel):
    """Copy of an order at the moment of paying. Names and prices are frozen in the bill."""

    product_id: int
    product_name: str
    presentation_name: str
    quantity: int
    unit_price: float
    line_total: float
    notes: Optional[str] = None


class Bill(BaseModel):
    """Paid bill of a table: what the ticket prints and what the reports add up."""

    id: int
    table_id: int
    table_name: str
    waiter_id: int
    waiter_name: str
    paid_by: str
    paid_at: datetime
    lines: List[BillLine]
    total: float


class WaiterSales(BaseModel):
    waiter_id: int
    waiter_name: str
    bills: int
    total: float


class ProductSales(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    total: float


class DailyReport(BaseModel):
    """Summary of one day of service for the manager."""

    day: date
    bills: int
    total: float
    average_ticket: float
    by_waiter: List[WaiterSales]
    top_products: List[ProductSales]
