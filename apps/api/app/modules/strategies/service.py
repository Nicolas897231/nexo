import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.modules.audit.service import write_audit_log
from app.modules.strategies.models import UserDistribution
from app.modules.strategies.schemas import DistributionUpdate, DistributionWrite
from app.shared.money import decimal_to_string, quantize_money

STRATEGIES = {
    "50_30_20": {
        "code": "50_30_20",
        "name": "50/30/20",
        "needs_percentage": Decimal("0.500000"),
        "wants_percentage": Decimal("0.300000"),
        "savings_percentage": Decimal("0.200000"),
    },
    "70_20_10": {
        "code": "70_20_10",
        "name": "70/20/10",
        "needs_percentage": Decimal("0.700000"),
        "wants_percentage": Decimal("0.200000"),
        "savings_percentage": Decimal("0.100000"),
    },
    "zero_based": {
        "code": "zero_based",
        "name": "Base cero",
        "needs_percentage": Decimal("1.000000"),
        "wants_percentage": Decimal("0.000000"),
        "savings_percentage": Decimal("0.000000"),
    },
}


class StrategyService:
    def __init__(self, db: Session):
        self.db = db

    def list_strategies(self) -> list[dict]:
        return [self._strategy_payload(item) for item in STRATEGIES.values()]

    def get_strategy(self, strategy_id: str) -> dict:
        strategy = STRATEGIES.get(strategy_id)
        if strategy is None:
            raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
        return self._strategy_payload(strategy)

    def preview(self, monthly_income: Decimal, strategy_code: str) -> dict:
        strategy = STRATEGIES[strategy_code]
        return {
            "strategy_code": strategy_code,
            "needs_amount": decimal_to_string(
                quantize_money(monthly_income * strategy["needs_percentage"])
            ),
            "wants_amount": decimal_to_string(
                quantize_money(monthly_income * strategy["wants_percentage"])
            ),
            "savings_amount": decimal_to_string(
                quantize_money(monthly_income * strategy["savings_percentage"])
            ),
        }

    def current_distribution(self, user_id: uuid.UUID) -> UserDistribution | None:
        return self.db.scalar(
            select(UserDistribution)
            .where(UserDistribution.user_id == user_id, UserDistribution.deleted_at.is_(None))
            .order_by(UserDistribution.created_at.desc())
        )

    def create_distribution(
        self, user_id: uuid.UUID, payload: DistributionWrite
    ) -> UserDistribution:
        distribution = UserDistribution(
            user_id=user_id,
            name=payload.name,
            strategy_code=payload.strategy_code,
            needs_percentage=payload.needs_percentage,
            wants_percentage=payload.wants_percentage,
            savings_percentage=payload.savings_percentage,
            extra_metadata=payload.metadata,
        )
        self.db.add(distribution)
        self.db.flush()
        write_audit_log(
            self.db,
            event_type="distribution.created",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="user_distribution",
            entity_id=distribution.id,
        )
        self.db.commit()
        self.db.refresh(distribution)
        return distribution

    def update_distribution(
        self, user_id: uuid.UUID, distribution_id: uuid.UUID, payload: DistributionUpdate
    ) -> UserDistribution:
        distribution = self.db.scalar(
            select(UserDistribution).where(
                UserDistribution.id == distribution_id,
                UserDistribution.user_id == user_id,
                UserDistribution.deleted_at.is_(None),
            )
        )
        if distribution is None:
            raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
        values = payload.model_dump(exclude_unset=True)
        if "metadata" in values:
            values["extra_metadata"] = values.pop("metadata")
        for field, value in values.items():
            setattr(distribution, field, value)
        total = (
            distribution.needs_percentage
            + distribution.wants_percentage
            + distribution.savings_percentage
        )
        if total != Decimal("1.000000"):
            raise AppError("DISTRIBUTION_INVALID", "La distribucion debe sumar 1.000000.", 400)
        write_audit_log(
            self.db,
            event_type="distribution.updated",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="user_distribution",
            entity_id=distribution.id,
        )
        self.db.commit()
        self.db.refresh(distribution)
        return distribution

    @staticmethod
    def _strategy_payload(strategy: dict) -> dict:
        return {
            "code": strategy["code"],
            "name": strategy["name"],
            "needs_percentage": str(strategy["needs_percentage"]),
            "wants_percentage": str(strategy["wants_percentage"]),
            "savings_percentage": str(strategy["savings_percentage"]),
        }
