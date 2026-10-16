"""Paid bills, kept in memory so the manager can review the day."""

from datetime import date
from threading import Lock
from typing import Dict, List, Optional

from app.schemas import Bill


class BillStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._bills: Dict[int, Bill] = {}
        self._next_id = 1

    def reset(self) -> None:
        with self._lock:
            self._bills = {}
            self._next_id = 1

    def next_id(self) -> int:
        with self._lock:
            bill_id = self._next_id
            self._next_id += 1
            return bill_id

    def add(self, bill: Bill) -> Bill:
        with self._lock:
            self._bills[bill.id] = bill
            return bill

    def get(self, bill_id: int) -> Optional[Bill]:
        with self._lock:
            return self._bills.get(bill_id)

    def list_by_day(self, day: date) -> List[Bill]:
        """Bills paid on a day, newest first."""
        with self._lock:
            bills = [bill for bill in self._bills.values() if bill.paid_at.date() == day]
        return sorted(bills, key=lambda bill: bill.id, reverse=True)


bill_store = BillStore()
