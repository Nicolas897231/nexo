from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer, field_validator

from app.shared.money import parse_money, parse_rate


class CarSimulationRequest(BaseModel):
    monthly_net_income: Decimal
    vehicle_price: Decimal
    down_payment: Decimal = Decimal("0.00")
    monthly_rate: Decimal
    term_months: int = Field(gt=0, le=120)
    insurance_monthly: Decimal = Decimal("0.00")
    fuel_monthly: Decimal = Decimal("0.00")
    maintenance_monthly: Decimal = Decimal("0.00")
    parking_monthly: Decimal = Decimal("0.00")

    @field_validator(
        "monthly_net_income",
        "vehicle_price",
        "down_payment",
        "insurance_monthly",
        "fuel_monthly",
        "maintenance_monthly",
        "parking_monthly",
        mode="before",
    )
    @classmethod
    def validate_money(cls, value) -> Decimal:
        return parse_money(value)

    @field_validator("monthly_rate", mode="before")
    @classmethod
    def validate_rate(cls, value) -> Decimal:
        return parse_rate(value)


class LiveAloneSimulationRequest(BaseModel):
    monthly_net_income: Decimal
    rent_amount: Decimal
    utilities_amount: Decimal = Decimal("0.00")
    food_amount: Decimal = Decimal("0.00")
    transport_amount: Decimal = Decimal("0.00")
    internet_amount: Decimal = Decimal("0.00")
    personal_basics_amount: Decimal = Decimal("0.00")
    moving_initial_cost: Decimal = Decimal("0.00")
    emergency_fund_amount: Decimal = Decimal("0.00")

    @field_validator("*", mode="before")
    @classmethod
    def validate_money(cls, value) -> Decimal:
        return parse_money(value)


class SavingsSimulationRequest(BaseModel):
    monthly_net_income: Decimal
    target_amount: Decimal
    current_amount: Decimal = Decimal("0.00")
    monthly_contribution: Decimal

    @field_validator("*", mode="before")
    @classmethod
    def validate_money(cls, value) -> Decimal:
        return parse_money(value)


class TravelSimulationRequest(BaseModel):
    monthly_net_income: Decimal
    destination: str = Field(min_length=1, max_length=120)
    travel_date: date | None = None
    flights_amount: Decimal = Decimal("0.00")
    lodging_amount: Decimal = Decimal("0.00")
    food_amount: Decimal = Decimal("0.00")
    extras_amount: Decimal = Decimal("0.00")
    current_amount: Decimal = Decimal("0.00")

    @field_validator(
        "monthly_net_income",
        "flights_amount",
        "lodging_amount",
        "food_amount",
        "extras_amount",
        "current_amount",
        mode="before",
    )
    @classmethod
    def validate_money(cls, value) -> Decimal:
        return parse_money(value)


class MoneyResult(BaseModel):
    value: Decimal

    @field_serializer("value")
    def serialize_value(self, value: Decimal) -> str:
        return f"{value:.2f}"
