from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, status

from app.data.bill_store import bill_store
from app.routers.dependencies import get_bill_or_404, require_manager
from app.schemas import Bill, DailyReport
from app.services.billing import daily_report

router = APIRouter(tags=["bills"])


@router.get(
    "/bills",
    response_model=List[Bill],
    summary="Bills paid on a day, newest first (manager only). Today by default",
    dependencies=[Depends(require_manager)],
)
def list_bills(day: Optional[date] = None) -> List[Bill]:
    return bill_store.list_by_day(day or date.today())


@router.get(
    "/bills/{bill_id}",
    response_model=Bill,
    summary="Get one paid bill, for example to print its ticket again",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Bill not found"}},
)
def get_bill(bill: Bill = Depends(get_bill_or_404)) -> Bill:
    return bill


@router.get(
    "/reports/daily",
    response_model=DailyReport,
    summary="Summary of a day: totals, sales per waiter and best sellers (manager only)",
    dependencies=[Depends(require_manager)],
)
def get_daily_report(day: Optional[date] = None) -> DailyReport:
    return daily_report(day or date.today())
