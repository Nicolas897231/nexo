import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.shared.types import TimestampMixin, UUIDPrimaryKeyMixin


class UserDistribution(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_distributions"
    __table_args__ = (
        CheckConstraint("needs_percentage >= 0", name="ck_dist_needs_non_negative"),
        CheckConstraint("wants_percentage >= 0", name="ck_dist_wants_non_negative"),
        CheckConstraint("savings_percentage >= 0", name="ck_dist_savings_non_negative"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    strategy_code: Mapped[str] = mapped_column(String(40), nullable=False)
    needs_percentage: Mapped[Decimal] = mapped_column(Numeric(9, 6, asdecimal=True), nullable=False)
    wants_percentage: Mapped[Decimal] = mapped_column(Numeric(9, 6, asdecimal=True), nullable=False)
    savings_percentage: Mapped[Decimal] = mapped_column(
        Numeric(9, 6, asdecimal=True), nullable=False
    )
    extra_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSONB, default=dict)
