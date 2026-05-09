import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.types import TimestampMixin, UUIDPrimaryKeyMixin


class IncomeSource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "income_sources"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    expected_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2, asdecimal=True), nullable=False)
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class TransactionCategory(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "transaction_categories"

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    kind: Mapped[str] = mapped_column(String(20), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transaction_categories.id"),
        nullable=True,
    )


class FinancialTransaction(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "financial_transactions"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_financial_transactions_amount_non_negative"),
        UniqueConstraint("user_id", "idempotency_key", name="uq_transactions_user_idempotency_key"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transaction_categories.id"),
        nullable=True,
    )
    income_source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("income_sources.id"),
        nullable=True,
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2, asdecimal=True), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), default="COP", nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_fixed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurrence_rule: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(120), nullable=True)


class Debt(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "debts"
    __table_args__ = (
        CheckConstraint("principal_balance >= 0", name="ck_debts_principal_non_negative"),
        CheckConstraint("minimum_payment >= 0", name="ck_debts_payment_non_negative"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    debt_type: Mapped[str] = mapped_column(String(30), nullable=False)
    principal_balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2, asdecimal=True), nullable=False
    )
    minimum_payment: Mapped[Decimal] = mapped_column(Numeric(18, 2, asdecimal=True), nullable=False)
    interest_rate_annual: Mapped[Decimal | None] = mapped_column(Numeric(9, 6, asdecimal=True))
    due_day: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
