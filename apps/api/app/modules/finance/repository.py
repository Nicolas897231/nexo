import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.finance.models import FinancialTransaction


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_idempotency_key(
        self,
        user_id: uuid.UUID,
        idempotency_key: str | None,
    ) -> FinancialTransaction | None:
        if not idempotency_key:
            return None
        return self.db.scalar(
            select(FinancialTransaction).where(
                FinancialTransaction.user_id == user_id,
                FinancialTransaction.idempotency_key == idempotency_key,
                FinancialTransaction.deleted_at.is_(None),
            )
        )

    def list(
        self,
        user_id: uuid.UUID,
        limit: int,
        offset: int,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[FinancialTransaction]:
        query = select(FinancialTransaction).where(
            FinancialTransaction.user_id == user_id,
            FinancialTransaction.deleted_at.is_(None),
        )
        if date_from:
            query = query.where(FinancialTransaction.transaction_date >= date_from)
        if date_to:
            query = query.where(FinancialTransaction.transaction_date <= date_to)
        return list(
            self.db.scalars(
                query.order_by(FinancialTransaction.transaction_date.desc())
                .limit(limit)
                .offset(offset)
            )
        )

    def get_owned(
        self, user_id: uuid.UUID, transaction_id: uuid.UUID
    ) -> FinancialTransaction | None:
        return self.db.scalar(
            select(FinancialTransaction).where(
                FinancialTransaction.id == transaction_id,
                FinancialTransaction.user_id == user_id,
                FinancialTransaction.deleted_at.is_(None),
            )
        )

    def monthly_totals(
        self, user_id: uuid.UUID, month_start: date, month_end: date
    ) -> dict[str, Decimal]:
        rows = self.db.execute(
            select(
                FinancialTransaction.type, func.coalesce(func.sum(FinancialTransaction.amount), 0)
            )
            .where(
                FinancialTransaction.user_id == user_id,
                FinancialTransaction.deleted_at.is_(None),
                FinancialTransaction.transaction_date >= month_start,
                FinancialTransaction.transaction_date <= month_end,
            )
            .group_by(FinancialTransaction.type)
        ).all()
        return {row[0]: Decimal(row[1]) for row in rows}
