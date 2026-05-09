import uuid
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.modules.auth.models import User, UserProfile
from app.modules.finance.repository import TransactionRepository
from app.modules.finance.schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    DebtCreate,
    DebtPaymentCreate,
    DebtRead,
    DebtUpdate,
    FinancialProfileWrite,
    IncomeSourceCreate,
    IncomeSourceRead,
    IncomeSourceUpdate,
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)
from app.modules.finance.service import (
    DebtService,
    FinanceCatalogService,
    FinancialProfileService,
    IncomeSourceService,
    TransactionService,
)
from app.shared.money import decimal_to_string

router = APIRouter()
movements_router = APIRouter()
categories_router = APIRouter()
income_sources_router = APIRouter()
debts_router = APIRouter()
financial_profile_router = APIRouter()


def _read_transaction(transaction) -> dict:
    payload = TransactionRead.model_validate(transaction, from_attributes=True).model_dump(
        mode="json"
    )
    payload["movement_type"] = payload["type"]
    return payload


def _read_category(category) -> dict:
    return CategoryRead.model_validate(category, from_attributes=True).model_dump(mode="json")


def _read_income_source(source) -> dict:
    return IncomeSourceRead.model_validate(source, from_attributes=True).model_dump(mode="json")


def _read_debt(debt) -> dict:
    return DebtRead.model_validate(debt, from_attributes=True).model_dump(mode="json")


@router.get("/transactions")
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    date_from: date | None = None,
    date_to: date | None = None,
):
    service = TransactionService(db)
    items = service.list(current_user.id, limit, offset, date_from, date_to)
    return ok(
        [_read_transaction(item) for item in items], pagination={"limit": limit, "offset": offset}
    )


@router.post("/transactions", status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    transaction = TransactionService(db).create(current_user.id, payload, idempotency_key)
    return ok(_read_transaction(transaction))


@movements_router.get("")
def list_movements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    date_from: date | None = None,
    date_to: date | None = None,
):
    return list_transactions(db, current_user, limit, offset, date_from, date_to)


@movements_router.post("", status_code=status.HTTP_201_CREATED)
def create_movement(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    return create_transaction(payload, db, current_user, idempotency_key)


@movements_router.get("/summary/monthly")
def get_movements_monthly_summary(
    month: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_snapshot(month, db, current_user)


@movements_router.get("/{movement_id}")
def get_movement(
    movement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_transaction(movement_id, db, current_user)


@movements_router.patch("/{movement_id}")
def update_movement(
    movement_id: uuid.UUID,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_transaction(movement_id, payload, db, current_user)


@movements_router.delete("/{movement_id}")
def delete_movement(
    movement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delete_transaction(movement_id, db, current_user)


@categories_router.get("")
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items = FinanceCatalogService(db).list_categories(current_user.id)
    return ok([_read_category(item) for item in items])


@categories_router.post("", status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(_read_category(FinanceCatalogService(db).create_category(current_user.id, payload)))


@categories_router.patch("/{category_id}")
def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    category = FinanceCatalogService(db).update_category(current_user.id, category_id, payload)
    return ok(_read_category(category))


@categories_router.delete("/{category_id}")
def delete_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    FinanceCatalogService(db).delete_category(current_user.id, category_id)
    return ok({"status": "deleted"})


@income_sources_router.get("")
def list_income_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok([_read_income_source(item) for item in IncomeSourceService(db).list(current_user.id)])


@income_sources_router.post("", status_code=status.HTTP_201_CREATED)
def create_income_source(
    payload: IncomeSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(_read_income_source(IncomeSourceService(db).create(current_user.id, payload)))


@income_sources_router.patch("/{source_id}")
def update_income_source(
    source_id: uuid.UUID,
    payload: IncomeSourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(
        _read_income_source(IncomeSourceService(db).update(current_user.id, source_id, payload))
    )


@income_sources_router.delete("/{source_id}")
def delete_income_source(
    source_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    IncomeSourceService(db).delete(current_user.id, source_id)
    return ok({"status": "deleted"})


@debts_router.get("")
def list_debts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ok([_read_debt(item) for item in DebtService(db).list(current_user.id)])


@debts_router.post("", status_code=status.HTTP_201_CREATED)
def create_debt(
    payload: DebtCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(_read_debt(DebtService(db).create(current_user.id, payload)))


@debts_router.get("/strategy")
def get_debt_strategy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(DebtService(db).strategy(current_user.id))


@debts_router.patch("/{debt_id}")
def update_debt(
    debt_id: uuid.UUID,
    payload: DebtUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(_read_debt(DebtService(db).update(current_user.id, debt_id, payload)))


@debts_router.post("/{debt_id}/payments", status_code=status.HTTP_201_CREATED)
def add_debt_payment(
    debt_id: uuid.UUID,
    payload: DebtPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(_read_debt(DebtService(db).add_payment(current_user.id, debt_id, payload)))


@financial_profile_router.get("")
def get_financial_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = current_user.profile or UserProfile(
        user_id=current_user.id, country_code="CO", currency_code="COP"
    )
    db.add(profile)
    return ok(FinancialProfileService(db).read(current_user.id, profile))


@financial_profile_router.put("")
@financial_profile_router.patch("")
def update_financial_profile(
    payload: FinancialProfileWrite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = current_user.profile or UserProfile(
        user_id=current_user.id, country_code="CO", currency_code="COP"
    )
    return ok(FinancialProfileService(db).update(current_user.id, profile, payload))


@financial_profile_router.get("/health-score")
def get_financial_health_score(
    month: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    snapshot = get_snapshot(month, db, current_user)["data"]
    income = Decimal(snapshot["total_income"])
    available = Decimal(snapshot["available_cashflow"])
    debt = Decimal(snapshot["debt_payments"])
    score = 100
    if income <= Decimal("0.00"):
        score = 20
    elif available <= Decimal("0.00"):
        score -= 35
    if income > Decimal("0.00") and debt / income > Decimal("0.35"):
        score -= 25
    return ok({"score": max(score, 0), "period_month": month.replace(day=1).isoformat()})


@financial_profile_router.post("/recalculate")
def recalculate_financial_profile(
    month: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_snapshot(month, db, current_user)


@router.get("/transactions/{transaction_id}")
def get_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = TransactionService(db).get_owned(current_user.id, transaction_id)
    return ok(_read_transaction(transaction))


@router.patch("/transactions/{transaction_id}")
def update_transaction(
    transaction_id: uuid.UUID,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = TransactionService(db).update(current_user.id, transaction_id, payload)
    return ok(_read_transaction(transaction))


@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    TransactionService(db).soft_delete(current_user.id, transaction_id)
    return ok({"status": "deleted"})


@router.get("/snapshot")
def get_snapshot(
    month: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    month_start = month.replace(day=1)
    next_month = (
        month_start.replace(year=month_start.year + 1, month=1)
        if month_start.month == 12
        else month_start.replace(month=month_start.month + 1)
    )
    month_end = date.fromordinal(next_month.toordinal() - 1)
    totals = TransactionRepository(db).monthly_totals(current_user.id, month_start, month_end)
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
        }
    )
