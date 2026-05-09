from decimal import Decimal

import pytest

from app.modules.rules.math.financial_math import (
    financeable_principal,
    healthy_rent_range,
    loan_monthly_payment,
    max_car_price_by_payment,
    months_to_goal,
)


def test_loan_monthly_payment_with_zero_rate_uses_decimal_money():
    assert loan_monthly_payment(Decimal("1200000.00"), Decimal("0.000000"), 12) == Decimal(
        "100000.00"
    )


def test_financeable_principal_and_max_car_price_are_decimal():
    principal = financeable_principal(Decimal("525000.00"), Decimal("0.016000"), 48)

    assert principal > Decimal("0.00")
    assert max_car_price_by_payment(
        Decimal("525000.00"),
        Decimal("0.016000"),
        48,
        Decimal("8000000.00"),
    ) == principal + Decimal("8000000.00")


def test_months_to_goal_returns_none_when_contribution_is_zero():
    assert months_to_goal(Decimal("1000.00"), Decimal("0.00"), Decimal("0.00")) is None


def test_healthy_rent_range_matches_phase2_example():
    rent = healthy_rent_range(Decimal("3500000.00"))

    assert rent["min"] == Decimal("700000.00")
    assert rent["ideal"] == Decimal("875000.00")
    assert rent["max"] == Decimal("1050000.00")


def test_loan_monthly_payment_rejects_invalid_months():
    with pytest.raises(ValueError):
        loan_monthly_payment(Decimal("1000.00"), Decimal("0.01"), 0)
