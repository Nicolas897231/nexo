import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import UserProfile
from app.modules.finance.models import Debt, FinancialTransaction, IncomeSource, TransactionCategory
from app.modules.finance.repository import TransactionRepository
from app.modules.finance.schemas import (
    CategoryCreate,
    CategoryUpdate,
    DebtCreate,
    DebtPaymentCreate,
    DebtUpdate,
    FinancialProfileWrite,
    IncomeSourceCreate,
    IncomeSourceUpdate,
    TransactionCreate,
    TransactionUpdate,
)
from app.shared.money import decimal_to_string, quantize_money


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = TransactionRepository(db)

    def create(
        self,
        user_id: uuid.UUID,
        payload: TransactionCreate,
        idempotency_key: str | None,
    ) -> FinancialTransaction:
        existing = self.repo.find_by_idempotency_key(user_id, idempotency_key)
        if existing:
            return existing
        transaction = FinancialTransaction(
            user_id=user_id,
            category_id=payload.category_id,
            income_source_id=payload.income_source_id,
            type=payload.type,
            amount=payload.amount,
            currency_code=payload.currency_code,
            transaction_date=payload.transaction_date,
            description=payload.description,
            is_fixed=payload.is_fixed,
            recurrence_rule=payload.recurrence_rule,
            extra_metadata=payload.metadata,
            idempotency_key=idempotency_key,
        )
        self.db.add(transaction)
        self.db.flush()
        write_audit_log(
            self.db,
            event_type="financial_transaction.created",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="financial_transaction",
            entity_id=transaction.id,
            after_state={"type": transaction.type, "amount": str(transaction.amount)},
        )
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def list(
        self,
        user_id: uuid.UUID,
        limit: int,
        offset: int,
        date_from: date | None,
        date_to: date | None,
    ) -> list[FinancialTransaction]:
        return self.repo.list(user_id, min(limit, 100), offset, date_from, date_to)

    def get_owned(self, user_id: uuid.UUID, transaction_id: uuid.UUID) -> FinancialTransaction:
        transaction = self.repo.get_owned(user_id, transaction_id)
        if transaction is None:
            raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
        return transaction

    def update(
        self,
        user_id: uuid.UUID,
        transaction_id: uuid.UUID,
        payload: TransactionUpdate,
    ) -> FinancialTransaction:
        transaction = self.get_owned(user_id, transaction_id)
        values = payload.model_dump(exclude_unset=True)
        if "metadata" in values:
            values["extra_metadata"] = values.pop("metadata")
        before = {field: getattr(transaction, field) for field in values}
        for field, value in values.items():
            setattr(transaction, field, value)
        write_audit_log(
            self.db,
            event_type="financial_transaction.updated",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="financial_transaction",
            entity_id=transaction.id,
            before_state={key: str(value) for key, value in before.items()},
            after_state={key: str(getattr(transaction, key)) for key in values},
        )
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def soft_delete(self, user_id: uuid.UUID, transaction_id: uuid.UUID) -> None:
        transaction = self.get_owned(user_id, transaction_id)
        transaction.deleted_at = datetime.now(UTC)
        write_audit_log(
            self.db,
            event_type="financial_transaction.deleted",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="financial_transaction",
            entity_id=transaction.id,
        )
        self.db.commit()


class FinanceCatalogService:
    def __init__(self, db: Session):
        self.db = db

    def list_categories(self, user_id: uuid.UUID) -> list[TransactionCategory]:
        return list(
            self.db.scalars(
                select(TransactionCategory)
                .where(
                    (TransactionCategory.user_id.is_(None))
                    | (TransactionCategory.user_id == user_id),
                    TransactionCategory.deleted_at.is_(None),
                )
                .order_by(TransactionCategory.kind.asc(), TransactionCategory.name.asc())
            )
        )

    def get_category_owned(self, user_id: uuid.UUID, category_id: uuid.UUID) -> TransactionCategory:
        category = self.db.scalar(
            select(TransactionCategory).where(
                TransactionCategory.id == category_id,
                TransactionCategory.user_id == user_id,
                TransactionCategory.deleted_at.is_(None),
            )
        )
        if category is None:
            raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
        return category

    def create_category(self, user_id: uuid.UUID, payload: CategoryCreate) -> TransactionCategory:
        category = TransactionCategory(user_id=user_id, **payload.model_dump())
        self.db.add(category)
        self.db.flush()
        write_audit_log(
            self.db,
            event_type="category.created",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="transaction_category",
            entity_id=category.id,
            after_state={"name": category.name, "kind": category.kind},
        )
        self.db.commit()
        self.db.refresh(category)
        return category

    def update_category(
        self, user_id: uuid.UUID, category_id: uuid.UUID, payload: CategoryUpdate
    ) -> TransactionCategory:
        category = self.get_category_owned(user_id, category_id)
        values = payload.model_dump(exclude_unset=True)
        before = {field: getattr(category, field) for field in values}
        for field, value in values.items():
            setattr(category, field, value)
        write_audit_log(
            self.db,
            event_type="category.updated",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="transaction_category",
            entity_id=category.id,
            before_state={key: str(value) for key, value in before.items()},
            after_state={key: str(getattr(category, key)) for key in values},
        )
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, user_id: uuid.UUID, category_id: uuid.UUID) -> None:
        category = self.get_category_owned(user_id, category_id)
        category.deleted_at = datetime.now(UTC)
        write_audit_log(
            self.db,
            event_type="category.deleted",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="transaction_category",
            entity_id=category.id,
        )
        self.db.commit()


class IncomeSourceService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, user_id: uuid.UUID) -> list[IncomeSource]:
        return list(
            self.db.scalars(
                select(IncomeSource)
                .where(IncomeSource.user_id == user_id, IncomeSource.deleted_at.is_(None))
                .order_by(IncomeSource.created_at.desc())
            )
        )

    def get_owned(self, user_id: uuid.UUID, source_id: uuid.UUID) -> IncomeSource:
        source = self.db.scalar(
            select(IncomeSource).where(
                IncomeSource.id == source_id,
                IncomeSource.user_id == user_id,
                IncomeSource.deleted_at.is_(None),
            )
        )
        if source is None:
            raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
        return source

    def upsert_primary_monthly(self, user_id: uuid.UUID, amount: Decimal) -> IncomeSource:
        source = self.db.scalar(
            select(IncomeSource).where(
                IncomeSource.user_id == user_id,
                IncomeSource.name == "Ingreso principal",
                IncomeSource.deleted_at.is_(None),
            )
        )
        if source is None:
            source = IncomeSource(
                user_id=user_id,
                name="Ingreso principal",
                source_type="salary",
                expected_amount=amount,
                frequency="monthly",
                is_active=True,
            )
            self.db.add(source)
        else:
            source.expected_amount = amount
            source.frequency = "monthly"
            source.is_active = True
        return source

    def create(self, user_id: uuid.UUID, payload: IncomeSourceCreate) -> IncomeSource:
        source = IncomeSource(user_id=user_id, **payload.model_dump())
        self.db.add(source)
        self.db.flush()
        write_audit_log(
            self.db,
            event_type="income_source.created",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="income_source",
            entity_id=source.id,
            after_state={"name": source.name, "expected_amount": str(source.expected_amount)},
        )
        self.db.commit()
        self.db.refresh(source)
        return source

    def update(
        self, user_id: uuid.UUID, source_id: uuid.UUID, payload: IncomeSourceUpdate
    ) -> IncomeSource:
        source = self.get_owned(user_id, source_id)
        values = payload.model_dump(exclude_unset=True)
        before = {field: getattr(source, field) for field in values}
        for field, value in values.items():
            setattr(source, field, value)
        write_audit_log(
            self.db,
            event_type="income_source.updated",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="income_source",
            entity_id=source.id,
            before_state={key: str(value) for key, value in before.items()},
            after_state={key: str(getattr(source, key)) for key in values},
        )
        self.db.commit()
        self.db.refresh(source)
        return source

    def delete(self, user_id: uuid.UUID, source_id: uuid.UUID) -> None:
        source = self.get_owned(user_id, source_id)
        source.deleted_at = datetime.now(UTC)
        write_audit_log(
            self.db,
            event_type="income_source.deleted",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="income_source",
            entity_id=source.id,
        )
        self.db.commit()


class DebtService:
    def __init__(self, db: Session):
        self.db = db

    def list(self, user_id: uuid.UUID) -> list[Debt]:
        return list(
            self.db.scalars(
                select(Debt)
                .where(Debt.user_id == user_id, Debt.deleted_at.is_(None))
                .order_by(Debt.created_at.desc())
            )
        )

    def get_owned(self, user_id: uuid.UUID, debt_id: uuid.UUID) -> Debt:
        debt = self.db.scalar(
            select(Debt).where(
                Debt.id == debt_id, Debt.user_id == user_id, Debt.deleted_at.is_(None)
            )
        )
        if debt is None:
            raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
        return debt

    def create(self, user_id: uuid.UUID, payload: DebtCreate) -> Debt:
        debt = Debt(user_id=user_id, status="active", **payload.model_dump())
        self.db.add(debt)
        self.db.flush()
        write_audit_log(
            self.db,
            event_type="debt.created",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="debt",
            entity_id=debt.id,
            after_state={"name": debt.name, "principal_balance": str(debt.principal_balance)},
        )
        self.db.commit()
        self.db.refresh(debt)
        return debt

    def update(self, user_id: uuid.UUID, debt_id: uuid.UUID, payload: DebtUpdate) -> Debt:
        debt = self.get_owned(user_id, debt_id)
        values = payload.model_dump(exclude_unset=True)
        before = {field: getattr(debt, field) for field in values}
        for field, value in values.items():
            setattr(debt, field, value)
        write_audit_log(
            self.db,
            event_type="debt.updated",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="debt",
            entity_id=debt.id,
            before_state={key: str(value) for key, value in before.items()},
            after_state={key: str(getattr(debt, key)) for key in values},
        )
        self.db.commit()
        self.db.refresh(debt)
        return debt

    def add_payment(
        self, user_id: uuid.UUID, debt_id: uuid.UUID, payload: DebtPaymentCreate
    ) -> Debt:
        debt = self.get_owned(user_id, debt_id)
        debt.principal_balance = quantize_money(
            max(debt.principal_balance - payload.amount, Decimal("0.00"))
        )
        if debt.principal_balance == Decimal("0.00"):
            debt.status = "paid"
        transaction = FinancialTransaction(
            user_id=user_id,
            type="debt_payment",
            amount=payload.amount,
            currency_code="COP",
            transaction_date=payload.payment_date,
            description=payload.description or f"Pago deuda: {debt.name}",
            extra_metadata={"debt_id": str(debt.id)},
        )
        self.db.add(transaction)
        self.db.flush()
        write_audit_log(
            self.db,
            event_type="debt.payment.created",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="debt",
            entity_id=debt.id,
            after_state={"amount": str(payload.amount), "balance": str(debt.principal_balance)},
        )
        self.db.commit()
        self.db.refresh(debt)
        return debt

    def strategy(self, user_id: uuid.UUID) -> dict:
        debts = [debt for debt in self.list(user_id) if debt.status == "active"]
        debts.sort(
            key=lambda item: (-(item.interest_rate_annual or Decimal("0")), item.minimum_payment)
        )
        return {
            "strategy": "avalanche",
            "ordered_debts": [
                {
                    "id": str(debt.id),
                    "name": debt.name,
                    "principal_balance": decimal_to_string(debt.principal_balance),
                    "minimum_payment": decimal_to_string(debt.minimum_payment),
                    "interest_rate_annual": str(debt.interest_rate_annual)
                    if debt.interest_rate_annual is not None
                    else None,
                }
                for debt in debts
            ],
        }


class FinancialProfileService:
    def __init__(self, db: Session):
        self.db = db

    def read(self, user_id: uuid.UUID, profile: UserProfile) -> dict:
        income_total = self.db.scalar(
            select(func.coalesce(func.sum(IncomeSource.expected_amount), 0)).where(
                IncomeSource.user_id == user_id,
                IncomeSource.is_active.is_(True),
                IncomeSource.deleted_at.is_(None),
            )
        )
        return {
            "monthly_income": decimal_to_string(Decimal(income_total or 0)),
            "currency_code": profile.currency_code,
            "city": profile.city,
            "payday": profile.payday,
            "income_frequency": profile.income_frequency,
        }

    def update(
        self, user_id: uuid.UUID, profile: UserProfile, payload: FinancialProfileWrite
    ) -> dict:
        values = payload.model_dump(exclude_unset=True)
        monthly_income = values.pop("monthly_income", None)
        for field, value in values.items():
            setattr(profile, field, value)
        if monthly_income is not None:
            IncomeSourceService(self.db).upsert_primary_monthly(user_id, monthly_income)
        self.db.add(profile)
        write_audit_log(
            self.db,
            event_type="financial_profile.updated",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="user_profile",
            entity_id=user_id,
            after_state={
                key: str(value) for key, value in payload.model_dump(exclude_unset=True).items()
            },
        )
        self.db.commit()
        return self.read(user_id, profile)
