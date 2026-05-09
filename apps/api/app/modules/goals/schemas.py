import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.shared.money import parse_money, quantize_money

GOAL_TYPES = {"saving", "live_alone", "buy_car", "travel"}
GOAL_STATUSES = {"planning", "active", "paused", "completed", "not_viable"}


class GoalCreate(BaseModel):
    goal_type: str
    name: str = Field(min_length=1, max_length=120)
    target_amount: Decimal
    current_amount: Decimal = Decimal("0.00")
    monthly_contribution: Decimal = Decimal("0.00")
    target_date: date | None = None
    priority: int = Field(default=3, ge=1, le=5)
    parameters: dict = Field(default_factory=dict)

    @field_validator("goal_type")
    @classmethod
    def validate_goal_type(cls, value: str) -> str:
        value = value.lower()
        if value not in GOAL_TYPES:
            raise ValueError("Tipo de meta no permitido.")
        return value

    @field_validator("target_amount", "current_amount", "monthly_contribution", mode="before")
    @classmethod
    def validate_money(cls, value) -> Decimal:
        return parse_money(value)

    @field_validator("target_amount")
    @classmethod
    def target_positive(cls, value: Decimal) -> Decimal:
        if value <= Decimal("0.00"):
            raise ValueError("La meta debe ser mayor a cero.")
        return value


class GoalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    target_amount: Decimal | None = None
    current_amount: Decimal | None = None
    monthly_contribution: Decimal | None = None
    target_date: date | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    status: str | None = None
    parameters: dict | None = None

    @field_validator("target_amount", "current_amount", "monthly_contribution", mode="before")
    @classmethod
    def validate_money(cls, value) -> Decimal | None:
        if value is None:
            return None
        return parse_money(value)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        if value not in GOAL_STATUSES:
            raise ValueError("Estado de meta no permitido.")
        return value


class GoalContributionCreate(BaseModel):
    amount: Decimal
    contribution_date: date

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, value) -> Decimal:
        return parse_money(value, allow_zero=False)


class GoalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    goal_type: str
    name: str
    target_amount: Decimal
    current_amount: Decimal
    monthly_contribution: Decimal
    target_date: date | None
    priority: int
    status: str
    parameters: dict

    @field_serializer("target_amount", "current_amount", "monthly_contribution")
    def serialize_money(self, value: Decimal) -> str:
        return f"{quantize_money(value):.2f}"
