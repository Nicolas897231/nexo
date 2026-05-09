from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from app.core.errors import AppError

MONEY_QUANT = Decimal("0.01")
RATE_QUANT = Decimal("0.000001")


def parse_money(value: Any, *, allow_zero: bool = True) -> Decimal:
    if isinstance(value, float):
        raise AppError(
            "MONEY_INVALID_AMOUNT", "Los montos deben enviarse como string decimal.", 400
        )
    if not isinstance(value, str | int | Decimal):
        raise AppError(
            "MONEY_INVALID_AMOUNT", "Los montos deben enviarse como string decimal.", 400
        )
    try:
        amount = Decimal(str(value)).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise AppError(
            "MONEY_INVALID_AMOUNT", "El monto no tiene formato decimal válido.", 400
        ) from exc
    if amount < Decimal("0.00") or (not allow_zero and amount == Decimal("0.00")):
        raise AppError("MONEY_INVALID_AMOUNT", "El monto debe ser mayor a cero.", 400)
    return amount


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def decimal_to_string(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return f"{quantize_money(value):.2f}"


def parse_rate(value: Any) -> Decimal:
    if isinstance(value, float):
        raise AppError("RATE_INVALID", "Las tasas deben enviarse como string decimal.", 400)
    try:
        rate = Decimal(str(value)).quantize(RATE_QUANT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise AppError("RATE_INVALID", "La tasa no tiene formato decimal válido.", 400) from exc
    if rate < Decimal("0"):
        raise AppError("RATE_INVALID", "La tasa no puede ser negativa.", 400)
    return rate
