"""In-memory order storage. It will be replaced by MySQL in a later phase.

FastAPI runs normal (non async) endpoints in a thread pool, so every access is
guarded by a lock to keep ids unique and changes consistent.
"""

from threading import Lock
from typing import Any, Dict, List, Optional

from app.data.sample_data import SAMPLE_ORDERS
from app.schemas import Order


class OrderStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._orders: Dict[int, Order] = {}
        self._next_id = 1
        self.reset()

    def reset(self) -> None:
        """Go back to the sample orders. Used on start-up and by the tests."""
        with self._lock:
            self._orders = {order.id: order for order in SAMPLE_ORDERS}
            self._next_id = max(self._orders, default=0) + 1

    def list_by_table(self, table_id: int) -> List[Order]:
        with self._lock:
            return [order for order in self._orders.values() if order.table_id == table_id]

    def get(self, order_id: int) -> Optional[Order]:
        with self._lock:
            return self._orders.get(order_id)

    def add(
        self,
        table_id: int,
        product_id: int,
        presentation_id: int,
        quantity: int,
        unit_price: float,
        notes: Optional[str] = None,
    ) -> Order:
        with self._lock:
            order = Order(
                id=self._next_id,
                table_id=table_id,
                product_id=product_id,
                presentation_id=presentation_id,
                quantity=quantity,
                unit_price=unit_price,
                notes=notes,
            )
            self._orders[order.id] = order
            self._next_id += 1
            return order

    def update(self, order_id: int, changes: Dict[str, Any]) -> Order:
        with self._lock:
            order = self._orders[order_id].model_copy(update=changes)
            self._orders[order_id] = order
            return order

    def delete(self, order_id: int) -> None:
        with self._lock:
            self._orders.pop(order_id, None)

    def take_table(self, table_id: int) -> List[Order]:
        """Remove and return every order of a table in one step (used when it is paid)."""
        with self._lock:
            taken = [order for order in self._orders.values() if order.table_id == table_id]
            for order in taken:
                del self._orders[order.id]
            return taken


order_store = OrderStore()
