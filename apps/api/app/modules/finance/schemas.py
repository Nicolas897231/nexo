import uuid
from datetime import date
from decimal import Decimal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.shared.money import parse_money, parse_rate, quantize_money

TRANSACTION_TYPES = {"income", "expense", "transfer", "saving", "debt_payment"}
CATEGORY_KINDS = {"income", "expense", "saving", "debt"}
INCOME_SOURCE_TYPES = {"salary", "freelance", "business", "other"}
FREQUENCIES = {"monthly", "biweekly", "weekly", "variable"}
DEBT_TYPES = {"credit_card", "personal_loan", "vehicle_loan", "other"}
DEBT_STATUSES = {"active", "paid", "paused"}


class TransactionCreate(BaseModel):
    category_id: uuid.UUID | None = None
    income_source_id: uuid.UUID | None = None
    type: str = Field(validation_alias=AliasChoices("type", "movement_type"))
    amount: Decimal = Field(gt=Decimal("0.00"))
    currency_code: str = Field(default="COP", min_length=3, max_length=3)
    transaction_date: date
    description: str | None = Field(default=None, max_length=255)
    is_fixed: bool = False
    recurrence_rule: dict | None = None
    metadata: dict | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        value = value.lower()
        aliases = {
            "movement_income": "income",
            "movement_expense": "expense",
            "income": "income",
            "expense": "expense",
            "transfer": "transfer",
            "adjustment": "transfer",
        }
        value = aliases.get(value, value)
        if value not in TRANSACTION_TYPES:
            raise ValueError("Tipo de movimiento no permitido.")
        return value

    @field_validator("currency_code")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, value) -> Decimal:
        return parse_money(value, allow_zero=False)


class TransactionUpdate(BaseModel):
    category_id: uuid.UUID | None = None
    type: str | None = Field(default=None, validation_alias=AliasChoices("type", "movement_type"))
    amount: Decimal | None = None
    transaction_date: date | None = None
    description: str | None = Field(default=None, max_length=255)
    is_fixed: bool | None = None
    recurrence_rule: dict | None = None
    metadata: dict | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        if value not in TRANSACTION_TYPES:
            raise ValueError("Tipo de movimiento no permitido.")
        return value

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, value) -> Decimal | None:
        if value is None:
            return None
        return parse_money(value, allow_zero=False)


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID | None
    type: str
    amount: Decimal
    currency_code: str
    transaction_date: date
    description: str | None
    is_fixed: bool

    @field_serializer("amount")
    def serialize_amount(self, value: Decimal) -> str:
        return f"{quantize_money(value):.2f}"


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    kind: str
    parent_id: uuid.UUID | None = None

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, value: str) -> str:
        value = value.lower()
        if value not in CATEGORY_KINDS:
            raise ValueError("Tipo de categoria no permitido.")
        return value

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return " ".join(value.strip().split())


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    kind: str | None = None
    parent_id: uuid.UUID | None = None

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        if value not in CATEGORY_KINDS:
            raise ValueError("Tipo de categoria no permitido.")
        return value


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None
    name: str
    kind: str
    parent_id: uuid.UUID | None


class IncomeSourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    source_type: str
    expected_amount: Decimal
    frequency: str
    is_active: bool = True

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, value: str) -> str:
        value = value.lower()
        if value not in INCOME_SOURCE_TYPES:
            raise ValueError("Tipo de ingreso no permitido.")
        return value

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, value: str) -> str:
        value = value.lower()
        if value not in FREQUENCIES:
            raise ValueError("Frecuencia no permitida.")
        return value

    @field_validator("expected_amount", mode="before")
    @classmethod
    def validate_amount(cls, value) -> Decimal:
        return parse_money(value)


class IncomeSourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    source_type: str | None = None
    expected_amount: Decimal | None = None
    frequency: str | None = None
    is_active: bool | None = None

    @field_validator("source_type")
    @classmethod
    def validate_source_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        if value not in INCOME_SOURCE_TYPES:
            raise ValueError("Tipo de ingreso no permitido.")
        return value

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        if value not in FREQUENCIES:
            raise ValueError("Frecuencia no permitida.")
        return value

    @field_validator("expected_amount", mode="before")
    @classmethod
    def validate_amount(cls, value) -> Decimal | None:
        if value is None:
            return None
        return parse_money(value)


class IncomeSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    source_type: str
    expected_amount: Decimal
    frequency: str
    is_active: bool

    @field_serializer("expected_amount")
    def serialize_amount(self, value: Decimal) -> str:
        return f"{quantize_money(value):.2f}"


class DebtCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    debt_type: str
    principal_balance: Decimal
    minimum_payment: Decimal
    interest_rate_annual: Decimal | None = None
    due_day: int | None = Field(default=None, ge=1, le=31)

    @field_validator("debt_type")
    @classmethod
    def validate_debt_type(cls, value: str) -> str:
        value = value.lower()
        if value not in DEBT_TYPES:
            raise ValueError("Tipo de deuda no permitido.")
        return value

    @field_validator("principal_balance", "minimum_payment", mode="before")
    @classmethod
    def validate_money(cls, value) -> Decimal:
        return parse_money(value)

    @field_validator("interest_rate_annual", mode="before")
    @classmethod
    def validate_rate(cls, value) -> Decimal | None:
        if value is None:
            return None
        return parse_rate(value)


class DebtUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    debt_type: str | None = None
    principal_balance: Decimal | None = None
    minimum_payment: Decimal | None = None
    interest_rate_annual: Decimal | None = None
    due_day: int | None = Field(default=None, ge=1, le=31)
    status: str | None = None

    @field_validator("debt_type")
    @classmethod
    def validate_debt_type(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        if value not in DEBT_TYPES:
            raise ValueError("Tipo de deuda no permitido.")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        if value not in DEBT_STATUSES:
            raise ValueError("Estado de deuda no permitido.")
        return value

    @field_validator("principal_balance", "minimum_payment", mode="before")
    @classmethod
    def validate_money(cls, value) -> Decimal | None:
        if value is None:
            return None
        return parse_money(value)

    @field_validator("interest_rate_annual", mode="before")
    @classmethod
    def validate_rate(cls, value) -> Decimal | None:
        if value is None:
            return None
        return parse_rate(value)


class DebtPaymentCreate(BaseModel):
    amount: Decimal
    payment_date: date
    description: str | None = Field(default=None, max_length=255)

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, value) -> Decimal:
        return parse_money(value, allow_zero=False)


class DebtRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    debt_type: str
    principal_balance: Decimal
    minimum_payment: Decimal
    interest_rate_annual: Decimal | None
    due_day: int | None
    status: str

    @field_serializer("principal_balance", "minimum_payment", "interest_rate_annual")
    def serialize_decimal(self, value: Decimal | None) -> str | None:
        return None if value is None else str(value)


class FinancialProfileWrite(BaseModel):
    monthly_income: Decimal | None = None
    currency_code: str | None = Field(default=None, min_length=3, max_length=3)
    city: str | None = Field(default=None, max_length=100)
    payday: int | None = Field(default=None, ge=1, le=31)
    paydays: list[int] | None = Field(default=None, min_length=1, max_length=2)
    income_frequency: str | None = None

    @field_validator("monthly_income", mode="before")
    @classmethod
    def validate_monthly_income(cls, value) -> Decimal | None:
        if value is None:
            return None
        return parse_money(value)

    @field_validator("currency_code")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return value.upper() if value else value

    @field_validator("income_frequency")
    @classmethod
    def validate_income_frequency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        if value not in FREQUENCIES:
            raise ValueError("Frecuencia no permitida.")
        return value

    @field_validator("paydays")
    @classmethod
    def validate_paydays(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return value
        unique = sorted(set(value))
        if len(unique) != len(value):
            raise ValueError("Los dias de pago no pueden repetirse.")
        if any(day < 1 or day > 31 for day in unique):
            raise ValueError("Cada dia de pago debe estar entre 1 y 31.")
        return unique
