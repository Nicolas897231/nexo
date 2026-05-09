from decimal import Decimal

import pytest

from app.core.errors import AppError
from app.shared.money import parse_money, quantize_money


def test_parse_money_accepts_decimal_string_and_quantizes_half_up():
    assert parse_money("100.005") == Decimal("100.01")


def test_parse_money_rejects_float_payloads():
    with pytest.raises(AppError):
        parse_money(0.1)


def test_quantize_money_keeps_decimal_precision():
    value = Decimal("0.10") + Decimal("0.20")
    assert quantize_money(value) == Decimal("0.30")
