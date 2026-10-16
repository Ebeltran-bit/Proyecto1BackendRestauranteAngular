from app.data.order_store import order_store
from app.data.table_waiters import table_waiter_store
from app.data.user_store import user_store
from app.schemas import Table, TableStatus


def to_cents(amount: float) -> int:
    return int(round(amount * 100))


def table_status(table: Table) -> TableStatus:
    orders = order_store.list_by_table(table.id)
    waiter_id = table_waiter_store.get(table.id)
    waiter = user_store.get(waiter_id) if waiter_id is not None else None
    total_cents = sum(to_cents(order.unit_price) * order.quantity for order in orders)
    return TableStatus(
        **table.model_dump(),
        status="occupied" if orders or waiter else "free",
        waiter_id=waiter.id if waiter else None,
        waiter_name=waiter.full_name if waiter else None,
        order_count=len(orders),
        total=total_cents / 100,
    )
