import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.rules.models import RuleDefinition, RuleTemplate, UserRuleDefinition


class RuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def templates(self) -> list[RuleTemplate]:
        return list(self.db.scalars(select(RuleTemplate).where(RuleTemplate.deleted_at.is_(None))))

    def predefined_rules(self, scopes: list[str] | None = None) -> list[RuleDefinition]:
        query = select(RuleDefinition).where(
            RuleDefinition.deleted_at.is_(None),
            RuleDefinition.is_active.is_(True),
        )
        if scopes:
            query = query.where(RuleDefinition.scope.in_(scopes))
        return list(self.db.scalars(query.order_by(RuleDefinition.priority.asc())))

    def user_rules(
        self,
        user_id: uuid.UUID,
        scopes: list[str] | None = None,
        active_only: bool = False,
    ) -> list[UserRuleDefinition]:
        query = select(UserRuleDefinition).where(
            UserRuleDefinition.user_id == user_id,
            UserRuleDefinition.deleted_at.is_(None),
        )
        if scopes:
            query = query.where(UserRuleDefinition.scope.in_(scopes))
        if active_only:
            query = query.where(UserRuleDefinition.is_active.is_(True))
        return list(
            self.db.scalars(
                query.order_by(
                    UserRuleDefinition.priority.asc(), UserRuleDefinition.created_at.asc()
                )
            )
        )

    def get_user_rule(self, user_id: uuid.UUID, rule_id: uuid.UUID) -> UserRuleDefinition | None:
        return self.db.scalar(
            select(UserRuleDefinition).where(
                UserRuleDefinition.id == rule_id,
                UserRuleDefinition.user_id == user_id,
                UserRuleDefinition.deleted_at.is_(None),
            )
        )

    def active_user_rule_count(self, user_id: uuid.UUID) -> int:
        return int(
            self.db.scalar(
                select(func.count(UserRuleDefinition.id)).where(
                    UserRuleDefinition.user_id == user_id,
                    UserRuleDefinition.deleted_at.is_(None),
                    UserRuleDefinition.is_active.is_(True),
                )
            )
            or 0
        )
