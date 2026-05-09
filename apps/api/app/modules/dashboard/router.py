from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.modules.alerts.models import Alert
from app.modules.auth.models import User
from app.modules.finance.models import FinancialTransaction
from app.modules.finance.repository import TransactionRepository
from app.modules.goals.models import Goal
from app.shared.money import decimal_to_string

router = APIRouter()


def _month_bounds(month: date) -> tuple[date, date]:
    month_start = month.replace(day=1)
    next_month = (
        month_start.replace(year=month_start.year + 1, month=1)
        if month_start.month == 12
        else month_start.replace(month=month_start.month + 1)
    )
    return month_start, date.fromordinal(next_month.toordinal() - 1)


@router.get("/summary")
def dashboard_summary(
    month: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    month_start, month_end = _month_bounds(month)
    totals = TransactionRepository(db).monthly_totals(current_user.id, month_start, month_end)
    goal_count = db.scalar(
        select(func.count(Goal.id)).where(
            Goal.user_id == current_user.id,
            Goal.deleted_at.is_(None),
            Goal.status.in_(["planning", "active", "paused"]),
        )
    )
    active_alerts = db.scalar(
        select(func.count(Alert.id)).where(
            Alert.user_id == current_user.id, Alert.status == "active"
        )
    )
    income = totals.get("income", Decimal("0.00"))
    expenses = totals.get("expense", Decimal("0.00"))
    debt = totals.get("debt_payment", Decimal("0.00"))
    saving = totals.get("saving", Decimal("0.00"))
    available = income - expenses - debt - saving
    return ok(
        {
            "period_month": month_start.isoformat(),
            "total_income": decimal_to_string(income),
            "total_expenses": decimal_to_string(expenses),
            "debt_payments": decimal_to_string(debt),
            "savings_amount": decimal_to_string(saving),
            "available_cashflow": decimal_to_string(available),
            "active_goals": int(goal_count or 0),
            "active_alerts": int(active_alerts or 0),
        }
    )


@router.get("/cashflow")
def dashboard_cashflow(
    month: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    month_start, month_end = _month_bounds(month)
    rows = db.execute(
        select(
            FinancialTransaction.transaction_date,
            FinancialTransaction.type,
            func.coalesce(func.sum(FinancialTransaction.amount), 0),
        )
        .where(
            FinancialTransaction.user_id == current_user.id,
            FinancialTransaction.deleted_at.is_(None),
            FinancialTransaction.transaction_date >= month_start,
            FinancialTransaction.transaction_date <= month_end,
        )
        .group_by(FinancialTransaction.transaction_date, FinancialTransaction.type)
        .order_by(FinancialTransaction.transaction_date.asc())
    ).all()
    return ok(
        [
            {
                "date": row[0].isoformat(),
                "movement_type": row[1],
                "amount": decimal_to_string(Decimal(row[2])),
            }
            for row in rows
        ]
    )
