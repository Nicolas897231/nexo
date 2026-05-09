import uuid

from sqlalchemy.orm import Session

from app.modules.rules.domain.entities import Rule
from app.modules.rules.repository import RuleRepository


class RuleRegistry:
    def __init__(self, db: Session):
        self.repo = RuleRepository(db)

    def load_active_rules(self, user_id: uuid.UUID, scope: str) -> list[Rule]:
        scopes = ["general"] if scope == "general" else ["general", scope]
        rules: list[Rule] = []
        for item in self.repo.predefined_rules(scopes):
            rules.append(
                Rule(
                    id=item.id,
                    code=item.code,
                    scope=item.scope,
                    name=item.name or item.code,
                    priority=item.priority,
                    condition_json=item.condition_json,
                    action_json=item.action_json,
                    severity=item.severity,
                    version=item.version,
                    source="GLOBAL",
                )
            )
        for item in self.repo.user_rules(user_id, scopes, active_only=True):
            rules.append(
                Rule(
                    id=item.id,
                    code=f"USER-{item.id}",
                    scope=item.scope,
                    name=item.name,
                    priority=item.priority + 1000,
                    condition_json=item.condition_json,
                    action_json=item.action_json,
                    severity=item.action_json.get("severity", "WARNING"),
                    version=item.version,
                    source="USER",
                )
            )
        return sorted(rules, key=lambda rule: rule.priority)
