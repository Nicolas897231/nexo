from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from uuid import UUID

from app.modules.rules.domain.enums import RuleSeverity, RuleStatus


@dataclass(frozen=True)
class Rule:
    id: UUID | None
    code: str
    scope: str
    name: str
    priority: int
    condition_json: dict[str, Any]
    action_json: dict[str, Any]
    severity: str
    version: int
    source: str


@dataclass(frozen=True)
class RuleResult:
    rule_id: UUID | None
    rule_code: str
    rule_version: int
    status: RuleStatus
    severity: RuleSeverity
    triggered: bool
    message: str | None
    developer_message: str | None = None
    suggestions: list[str] = field(default_factory=list)
    details: dict[str, str] = field(default_factory=dict)
    facts_snapshot: dict[str, Decimal | str] = field(default_factory=dict)
