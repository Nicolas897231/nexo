import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.shared.money import parse_rate

STRATEGY_CODES = {"50_30_20", "70_20_10", "zero_based"}


class DistributionWrite(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    strategy_code: str
    needs_percentage: Decimal
    wants_percentage: Decimal
    savings_percentage: Decimal
    metadata: dict = Field(default_factory=dict)

    @field_validator("strategy_code")
    @classmethod
    def validate_strategy(cls, value: str) -> str:
        if value not in STRATEGY_CODES:
            raise ValueError("Estrategia no permitida.")
        return value

    @field_validator("needs_percentage", "wants_percentage", "savings_percentage", mode="before")
    @classmethod
    def validate_percentage(cls, value) -> Decimal:
        return parse_rate(value)

    @field_validator("savings_percentage")
    @classmethod
    def validate_total(cls, value: Decimal, info) -> Decimal:
        total = info.data.get("needs_percentage", Decimal("0"))
        total += info.data.get("wants_percentage", Decimal("0"))
        total += value
        if total != Decimal("1.000000"):
            raise ValueError("La distribucion debe sumar 1.000000.")
        return value


class DistributionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    needs_percentage: Decimal | None = None
    wants_percentage: Decimal | None = None
    savings_percentage: Decimal | None = None
    metadata: dict | None = None

    @field_validator("needs_percentage", "wants_percentage", "savings_percentage", mode="before")
    @classmethod
    def validate_percentage(cls, value) -> Decimal | None:
        if value is None:
            return None
        return parse_rate(value)


class DistributionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    strategy_code: str
    needs_percentage: Decimal
    wants_percentage: Decimal
    savings_percentage: Decimal

    @field_serializer("needs_percentage", "wants_percentage", "savings_percentage")
    def serialize_rate(self, value: Decimal) -> str:
        return str(value)


class StrategyPreviewRequest(BaseModel):
    monthly_income: Decimal
    strategy_code: str = "50_30_20"

    @field_validator("monthly_income", mode="before")
    @classmethod
    def validate_income(cls, value) -> Decimal:
        from app.shared.money import parse_money

        return parse_money(value)

    @field_validator("strategy_code")
    @classmethod
    def validate_strategy(cls, value: str) -> str:
        if value not in STRATEGY_CODES:
            raise ValueError("Estrategia no permitida.")
        return value
