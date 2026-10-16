"""Paying a table and summarising the bills of a day."""

from collections import defaultdict
from datetime import date, datetime
from typing import Dict, List

from fastapi import HTTPException, status

from app.data.bill_store import bill_store
from app.data.order_store import order_store
from app.data.sample_data import PRESENTATIONS_BY_ID, PRODUCTS_BY_ID
from app.data.table_waiters import table_waiter_store
from app.data.user_store import user_store
from app.schemas import Bill, BillLine, DailyReport, ProductSales, Table, User, WaiterSales
from app.services.tables import to_cents

TOP_PRODUCTS = 5


def _conflict(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def pay_table(table: Table, paid_by: User) -> Bill:
    """Close the bill of a table: save it, empty the table and free its waiter."""
    waiter_id = table_waiter_store.get(table.id)
    waiter = user_store.get(waiter_id) if waiter_id is not None else None
    if waiter is None:
        raise _conflict(f"Elige el camarero que ha servido {table.name} antes de cobrarla")
    if not order_store.list_by_table(table.id):
        raise _conflict(f"{table.name} no tiene pedidos que cobrar")

    orders = order_store.take_table(table.id)
    if not orders:  # someone paid it at the same moment
        raise _conflict(f"{table.name} no tiene pedidos que cobrar")
    table_waiter_store.set(table.id, None)

    lines = [
        BillLine(
            product_id=order.product_id,
            product_name=PRODUCTS_BY_ID[order.product_id].name,
            presentation_name=PRESENTATIONS_BY_ID[order.presentation_id].name,
            quantity=order.quantity,
            unit_price=order.unit_price,
            line_total=to_cents(order.unit_price) * order.quantity / 100,
            notes=order.notes,
        )
        for order in orders
    ]
    bill = Bill(
        id=bill_store.next_id(),
        table_id=table.id,
        table_name=table.name,
        waiter_id=waiter.id,
        waiter_name=waiter.full_name,
        paid_by=paid_by.full_name,
        paid_at=datetime.now().astimezone().replace(microsecond=0),
        lines=lines,
        total=sum(to_cents(line.line_total) for line in lines) / 100,
    )
    return bill_store.add(bill)


def daily_report(day: date) -> DailyReport:
    bills = bill_store.list_by_day(day)
    total_cents = sum(to_cents(bill.total) for bill in bills)

    waiters: Dict[int, WaiterSales] = {}
    for bill in bills:
        sales = waiters.setdefault(
            bill.waiter_id,
            WaiterSales(waiter_id=bill.waiter_id, waiter_name=bill.waiter_name, bills=0, total=0),
        )
        sales.bills += 1
        sales.total = (to_cents(sales.total) + to_cents(bill.total)) / 100

    quantities: Dict[int, int] = defaultdict(int)
    product_cents: Dict[int, int] = defaultdict(int)
    names: Dict[int, str] = {}
    for bill in bills:
        for line in bill.lines:
            quantities[line.product_id] += line.quantity
            product_cents[line.product_id] += to_cents(line.line_total)
            names[line.product_id] = line.product_name
    top: List[ProductSales] = [
        ProductSales(product_id=pid, product_name=names[pid], quantity=quantities[pid], total=product_cents[pid] / 100)
        for pid in sorted(quantities, key=lambda pid: (-quantities[pid], -product_cents[pid]))[:TOP_PRODUCTS]
    ]

    return DailyReport(
        day=day,
        bills=len(bills),
        total=total_cents / 100,
        average_ticket=round(total_cents / len(bills)) / 100 if bills else 0,
        by_waiter=sorted(waiters.values(), key=lambda sales: -sales.total),
        top_products=top,
    )
