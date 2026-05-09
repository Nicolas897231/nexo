import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, SmallInteger, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.types import TimestampMixin, UUIDPrimaryKeyMixin


class Goal(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "goals"
    __table_args__ = (
        CheckConstraint("target_amount >= 0", name="ck_goals_target_amount_non_negative"),
        CheckConstraint("current_amount >= 0", name="ck_goals_current_amount_non_negative"),
        CheckConstraint(
            "monthly_contribution >= 0", name="ck_goals_monthly_contribution_non_negative"
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    goal_type: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2, asdecimal=True), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2, asdecimal=True),
        default=Decimal("0.00"),
        nullable=False,
    )
    monthly_contribution: Mapped[Decimal] = mapped_column(
        Numeric(18, 2, asdecimal=True),
        default=Decimal("0.00"),
        nullable=False,
    )
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[int] = mapped_column(SmallInteger, default=3, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="planning", nullable=False)
    strategy_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)


class GoalContribution(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "goal_contributions"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_goal_contributions_amount_non_negative"),
    )

    goal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2, asdecimal=True), nullable=False)
    contribution_date: Mapped[date] = mapped_column(Date, nullable=False)


class GoalEvent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "goal_events"

    goal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("goals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
