from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.core.errors import AppError
from app.main import create_app
from app.modules.finance.schemas import TransactionCreate
from app.modules.strategies.schemas import DistributionWrite


def test_phase3_openapi_contains_documented_paths():
    client = TestClient(create_app())

    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    expected_paths = {
        "/api/v1/auth/forgot-password",
        "/api/v1/auth/reset-password",
        "/api/v1/auth/change-password",
        "/api/v1/users/me/preferences",
        "/api/v1/users/me/security-settings",
        "/api/v1/users/me/activity",
        "/api/v1/financial-profile",
        "/api/v1/categories",
        "/api/v1/income-sources",
        "/api/v1/movements",
        "/api/v1/movements/summary/monthly",
        "/api/v1/debts",
        "/api/v1/debts/strategy",
        "/api/v1/strategies",
        "/api/v1/strategies/preview",
        "/api/v1/distributions",
        "/api/v1/distributions/current",
        "/api/v1/goals/{goal_id}/timeline",
        "/api/v1/rules/custom/validate",
        "/api/v1/decision-engine/recommendations",
        "/api/v1/simulations/savings",
        "/api/v1/simulations/living-alone",
        "/api/v1/simulations/travel",
        "/api/v1/simulations/{simulation_id}/convert-to-goal",
        "/api/v1/dashboard/summary",
        "/api/v1/dashboard/cashflow",
        "/api/v1/alerts",
        "/api/v1/audit/activity",
        "/api/v1/health",
    }
    assert expected_paths.issubset(paths)


def test_phase3_health_endpoint_is_public():
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_movement_amount_rejects_float_and_accepts_movement_type_alias():
    payload = {
        "movement_type": "INCOME",
        "amount": "1234.50",
        "transaction_date": "2026-05-07",
    }

    movement = TransactionCreate.model_validate(payload)

    assert movement.type == "income"
    assert movement.amount == Decimal("1234.50")

    payload["amount"] = 1234.50
    with pytest.raises(AppError):
        TransactionCreate.model_validate(payload)


def test_distribution_requires_total_one():
    valid = DistributionWrite.model_validate(
        {
            "name": "Mi regla 50/30/20",
            "strategy_code": "50_30_20",
            "needs_percentage": "0.500000",
            "wants_percentage": "0.300000",
            "savings_percentage": "0.200000",
        }
    )
    assert valid.savings_percentage == Decimal("0.200000")

    with pytest.raises(ValueError):
        DistributionWrite.model_validate(
            {
                "name": "Invalida",
                "strategy_code": "50_30_20",
                "needs_percentage": "0.600000",
                "wants_percentage": "0.300000",
                "savings_percentage": "0.200000",
            }
        )
