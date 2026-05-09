import pytest
from pydantic import ValidationError

from app.modules.rules.schemas import UserRuleCreate


def test_custom_rule_payload_accepts_safe_declarative_json():
    payload = UserRuleCreate(
        name="Límite de ocio",
        scope="general",
        condition_json={"fact": "savings_rate", "operator": "lt", "value": "0.200000"},
        action_json={
            "status": "WARN",
            "severity": "WARNING",
            "message": "Tu ahorro está por debajo del objetivo.",
        },
    )

    assert payload.scope == "general"


def test_custom_rule_payload_rejects_unknown_action_status():
    with pytest.raises(ValidationError):
        UserRuleCreate(
            name="Acción inválida",
            scope="general",
            condition_json={"fact": "savings_rate", "operator": "lt", "value": "0.200000"},
            action_json={
                "status": "DELETE_DATABASE",
                "severity": "WARNING",
                "message": "No permitido.",
            },
        )


def test_custom_rule_payload_rejects_too_many_suggestions():
    with pytest.raises(ValidationError):
        UserRuleCreate(
            name="Muchas sugerencias",
            scope="general",
            condition_json={"fact": "savings_rate", "operator": "lt", "value": "0.200000"},
            action_json={
                "status": "WARN",
                "severity": "WARNING",
                "message": "Mensaje válido.",
                "suggestions": ["a", "b", "c", "d"],
            },
        )
