from decimal import Decimal

import pytest

from app.core.errors import AppError
from app.modules.rules.engine import RuleEngine


def test_rule_engine_evaluates_allowed_condition():
    result = RuleEngine().evaluate(
        {
            "code": "GEN-002",
            "condition_json": {"fact": "monthly_available", "operator": "lte", "value": "0.000000"},
            "action_json": {"severity": "WARNING", "message": "Disponible no positivo."},
        },
        {"monthly_available": Decimal("-1.000000")},
    )

    assert result.triggered is True
    assert result.status.value == "WARN"


def test_rule_engine_rejects_unknown_operator():
    with pytest.raises(AppError):
        RuleEngine().validate_condition(
            {"fact": "monthly_available", "operator": "eval", "value": "0.000000"}
        )


def test_rule_engine_rejects_unknown_fact():
    with pytest.raises(AppError):
        RuleEngine().validate_condition({"fact": "password_hash", "operator": "eq", "value": "1"})


def test_rule_engine_evaluates_nested_all_condition():
    result = RuleEngine().evaluate(
        {
            "code": "LIVE-READY",
            "condition_json": {
                "all": [
                    {"fact": "housing_cost_ratio", "operator": "lte", "value": "0.350000"},
                    {"fact": "emergency_fund_months", "operator": "gte", "value": "3.000000"},
                ]
            },
            "action_json": {
                "status": "INFO",
                "severity": "INFO",
                "message": "Condiciones base completas.",
            },
        },
        {
            "housing_cost_ratio": Decimal("0.300000"),
            "emergency_fund_months": Decimal("3.500000"),
        },
    )

    assert result.triggered is True


def test_rule_engine_evaluates_safe_formula_expression():
    result = RuleEngine().evaluate(
        {
            "code": "CAR_TOTAL_MONTHLY_COST_MAX_RATIO",
            "condition_json": {
                "left": {"formula": "sum", "fields": ["car_loan_payment", "car_monthly_expenses"]},
                "operator": "gt",
                "right": {
                    "formula": "percent_of",
                    "field": "monthly_net_income",
                    "value": "0.20",
                },
            },
            "action_json": {
                "status": "FAIL",
                "severity": "HIGH_RISK",
                "message": "Costo alto.",
            },
        },
        {
            "monthly_net_income": Decimal("3500000.00"),
            "car_loan_payment": Decimal("600000.00"),
            "car_monthly_expenses": Decimal("200000.00"),
        },
    )

    assert result.triggered is True
    assert result.severity.value == "HIGH_RISK"


def test_rule_engine_rejects_unsafe_expression_tokens():
    with pytest.raises(AppError):
        RuleEngine().validate_condition(
            {"fact": "monthly_available", "operator": "gt", "value": "__import__('os')"}
        )
