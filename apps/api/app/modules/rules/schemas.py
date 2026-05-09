import uuid
from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.modules.rules.domain.enums import EvaluationStatus
from app.modules.rules.engine import ALLOWED_FACTS, RuleEngine

RULE_SCOPES = {"general", "saving", "housing", "car", "travel"}
ALLOWED_ACTION_STATUSES = {"WARN", "FAIL", "BLOCK", "INFO"}
ALLOWED_ACTION_SEVERITIES = {"INFO", "SUCCESS", "WARNING", "CRITICAL", "BLOCKING", "HIGH_RISK"}


class UserRuleCreate(BaseModel):
    template_id: uuid.UUID | None = None
    name: str = Field(min_length=1, max_length=120)
    scope: str = "general"
    condition_json: dict[str, Any]
    action_json: dict[str, Any]
    priority: int = Field(default=100, ge=1, le=1000)

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, value: str) -> str:
        value = value.lower()
        if value not in RULE_SCOPES:
            raise ValueError("Alcance de regla no permitido.")
        return value

    @field_validator("condition_json")
    @classmethod
    def validate_condition(cls, value: dict[str, Any]) -> dict[str, Any]:
        RuleEngine().validate_condition(value)
        return value

    @field_validator("action_json")
    @classmethod
    def validate_action(cls, value: dict[str, Any]) -> dict[str, Any]:
        validate_action_json(value)
        return value


class UserRuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    scope: str | None = None
    condition_json: dict[str, Any] | None = None
    action_json: dict[str, Any] | None = None
    priority: int | None = Field(default=None, ge=1, le=1000)
    is_active: bool | None = None

    @field_validator("scope")
    @classmethod
    def validate_scope(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.lower()
        if value not in RULE_SCOPES:
            raise ValueError("Alcance de regla no permitido.")
        return value

    @field_validator("condition_json")
    @classmethod
    def validate_condition(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is not None:
            RuleEngine().validate_condition(value)
        return value

    @field_validator("action_json")
    @classmethod
    def validate_action(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is not None:
            validate_action_json(value)
        return value


class UserRuleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    scope: str
    condition_json: dict[str, Any]
    action_json: dict[str, Any]
    priority: int
    version: int
    is_active: bool


class RuleEvaluationRequest(BaseModel):
    facts: dict[str, Decimal | str]
    rule: dict[str, Any] | None = None

    @field_validator("facts", mode="before")
    @classmethod
    def validate_facts(cls, value: dict[str, Any]) -> dict[str, Decimal | str]:
        parsed: dict[str, Decimal | str] = {}
        for key, item in value.items():
            if key not in ALLOWED_FACTS:
                raise ValueError(f"Fact no permitido: {key}")
            if key in {"goal_type", "status", "category"}:
                parsed[key] = str(item)
            else:
                if isinstance(item, float):
                    raise ValueError("Los facts numéricos deben ser string decimal.")
                parsed[key] = Decimal(str(item))
        return parsed


class ProfileEvaluationRequest(BaseModel):
    period_month: date | None = None


class GoalEvaluationRequest(BaseModel):
    period_month: date | None = None


class RuleResultRead(BaseModel):
    rule_id: uuid.UUID | None
    rule_code: str
    rule_version: int
    status: str
    severity: str
    triggered: bool
    message: str | None
    developer_message: str | None
    suggestions: list[str]
    details: dict[str, str]
    facts_snapshot: dict[str, Decimal | str]

    @field_serializer("facts_snapshot")
    def serialize_facts(self, value: dict[str, Decimal | str]) -> dict[str, str]:
        return {key: str(item) for key, item in value.items()}


class EvaluationResponse(BaseModel):
    evaluation_id: uuid.UUID
    overall_status: EvaluationStatus
    score: int = Field(ge=0, le=100)
    currency: str = "COP"
    headline: str
    summary: str
    limits: list[dict[str, str]]
    alerts: list[dict[str, str]]
    suggestions: list[str]
    rule_results: list[RuleResultRead]
    charts_data: dict[str, Any]


def validate_action_json(value: dict[str, Any]) -> None:
    status = value.get("status", "WARN")
    severity = value.get("severity", "WARNING")
    message = value.get("user_message") or value.get("message")
    if status not in ALLOWED_ACTION_STATUSES:
        raise ValueError("Estado de acción no permitido.")
    if severity not in ALLOWED_ACTION_SEVERITIES:
        raise ValueError("Severidad no permitida.")
    if not isinstance(message, str) or not 1 <= len(message) <= 240:
        raise ValueError("La acción requiere un mensaje válido.")
    suggestions = value.get("suggestions", [])
    if suggestions is not None:
        if not isinstance(suggestions, list) or len(suggestions) > 3:
            raise ValueError("La acción permite máximo 3 sugerencias.")
        if any(not isinstance(item, str) or len(item) > 160 for item in suggestions):
            raise ValueError("Las sugerencias no son válidas.")
    recommendation = value.get("recommendation")
    if recommendation is not None and (
        not isinstance(recommendation, str) or len(recommendation) > 240
    ):
        raise ValueError("La recomendación no es válida.")
