"""Waiter serving each table while its bill is open. In memory, like the orders."""

from threading import Lock
from typing import Dict, Optional

from app.data.sample_data import SAMPLE_TABLE_WAITERS


class TableWaiterStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._waiters: Dict[int, int] = {}
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self._waiters = dict(SAMPLE_TABLE_WAITERS)

    def get(self, table_id: int) -> Optional[int]:
        with self._lock:
            return self._waiters.get(table_id)

    def set(self, table_id: int, waiter_id: Optional[int]) -> None:
        with self._lock:
            if waiter_id is None:
                self._waiters.pop(table_id, None)
            else:
                self._waiters[table_id] = waiter_id

    def is_serving(self, waiter_id: int) -> bool:
        with self._lock:
            return waiter_id in self._waiters.values()


table_waiter_store = TableWaiterStore()
