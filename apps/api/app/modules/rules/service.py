import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.modules.audit.service import write_audit_log
from app.modules.rules.engine import RuleEngine
from app.modules.rules.models import RuleChangeLog, UserRuleDefinition
from app.modules.rules.repository import RuleRepository
from app.modules.rules.schemas import (
    EvaluationResponse,
    RuleResultRead,
    UserRuleCreate,
    UserRuleUpdate,
)
from app.modules.rules.services.audit_writer import RuleAuditWriter
from app.modules.rules.services.fact_builder import FactBuilder
from app.modules.rules.services.recommendation_builder import RecommendationBuilder
from app.modules.rules.services.rule_registry import RuleRegistry

MAX_ACTIVE_USER_RULES = 50


class RuleService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = RuleRepository(db)
        self.engine = RuleEngine()

    def create_user_rule(self, user_id: uuid.UUID, payload: UserRuleCreate) -> UserRuleDefinition:
        if self.repo.active_user_rule_count(user_id) >= MAX_ACTIVE_USER_RULES:
            raise AppError("RULE_LIMIT_EXCEEDED", "Alcanzaste el máximo de reglas activas.", 409)
        condition = payload.condition_json
        action = payload.action_json
        self.engine.validate_condition(condition)
        rule = UserRuleDefinition(
            user_id=user_id,
            template_id=payload.template_id,
            name=payload.name,
            scope=payload.scope,
            condition_json=condition,
            action_json=action,
            priority=payload.priority,
            version=1,
            is_active=True,
        )
        self.db.add(rule)
        self.db.flush()
        self._write_change_log(user_id, rule, None, self._rule_state(rule))
        write_audit_log(
            self.db,
            event_type="rule.created",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="rule",
            entity_id=rule.id,
            after_state={"name": rule.name, "scope": rule.scope, "version": rule.version},
        )
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def update_user_rule(
        self,
        user_id: uuid.UUID,
        rule_id: uuid.UUID,
        payload: UserRuleUpdate,
    ) -> UserRuleDefinition:
        rule = self._get_owned_rule(user_id, rule_id)
        before = self._rule_state(rule)
        values = payload.model_dump(exclude_unset=True)
        if values.get("is_active") is True and not rule.is_active:
            if self.repo.active_user_rule_count(user_id) >= MAX_ACTIVE_USER_RULES:
                raise AppError(
                    "RULE_LIMIT_EXCEEDED", "Alcanzaste el máximo de reglas activas.", 409
                )
        for field, value in values.items():
            setattr(rule, field, value)
        rule.version += 1
        self.db.flush()
        after = self._rule_state(rule)
        self._write_change_log(user_id, rule, before, after)
        write_audit_log(
            self.db,
            event_type=self._event_for_update(before, after),
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="rule",
            entity_id=rule.id,
            before_state=before,
            after_state=after,
        )
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete_user_rule(self, user_id: uuid.UUID, rule_id: uuid.UUID) -> None:
        rule = self._get_owned_rule(user_id, rule_id)
        before = self._rule_state(rule)
        rule.deleted_at = datetime.now(UTC)
        rule.is_active = False
        rule.version += 1
        self.db.flush()
        self._write_change_log(user_id, rule, before, self._rule_state(rule))
        write_audit_log(
            self.db,
            event_type="rule.deleted",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="rule",
            entity_id=rule.id,
            before_state=before,
        )
        self.db.commit()

    def evaluate_profile(self, user_id: uuid.UUID, period_month=None) -> EvaluationResponse:
        facts_obj = FactBuilder(self.db).build_profile(user_id, period_month)
        return self._evaluate(
            user_id=user_id, scope="general", facts=facts_obj.as_dict(), limits=[]
        )

    def evaluate_goal(
        self,
        user_id: uuid.UUID,
        goal_id: uuid.UUID,
        period_month=None,
    ) -> EvaluationResponse:
        builder = FactBuilder(self.db)
        facts_obj = builder.build_goal(user_id, goal_id, period_month)
        scope = self._scope_from_goal_type(str(facts_obj.goal_type))
        return self._evaluate(
            user_id=user_id,
            scope=scope,
            facts=facts_obj.as_dict(),
            limits=builder.ui_limits(facts_obj),
            goal_id=goal_id,
        )

    def evaluate_inline_rule(self, user_id: uuid.UUID, payload) -> EvaluationResponse:
        rule = payload.rule or {
            "code": "GEN-002",
            "condition_json": {
                "fact": "monthly_available",
                "operator": "lte",
                "value": "0.000000",
            },
            "action_json": {
                "status": "WARN",
                "severity": "WARNING",
                "message": "Tu capacidad mensual disponible no es positiva.",
            },
        }
        rule_result = self.engine.evaluate(rule, payload.facts)
        response = RecommendationBuilder().build([rule_result])
        evaluation = RuleAuditWriter(self.db).save_evaluation(
            user_id=user_id,
            scope="inline",
            facts=payload.facts,
            results=[rule_result],
            response=response,
        )
        self.db.commit()
        return self._response_model(evaluation.id, response, [rule_result])

    def evaluate_scope_facts(
        self,
        *,
        user_id: uuid.UUID,
        scope: str,
        facts: dict,
        limits: list[dict[str, str]] | None = None,
    ) -> EvaluationResponse:
        return self._evaluate(user_id=user_id, scope=scope, facts=facts, limits=limits or [])

    def get_evaluation(self, user_id: uuid.UUID, evaluation_id: uuid.UUID) -> dict:
        evaluation = RuleAuditWriter(self.db).get_owned(user_id, evaluation_id)
        if evaluation is None:
            raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
        return {
            "id": str(evaluation.id),
            "scope": evaluation.scope,
            "status": evaluation.status,
            "score": evaluation.score,
            "facts_snapshot": evaluation.facts_snapshot,
            "response": evaluation.response_json,
            "created_at": evaluation.created_at.isoformat(),
        }

    def _evaluate(
        self,
        *,
        user_id: uuid.UUID,
        scope: str,
        facts: dict,
        limits: list[dict[str, str]],
        goal_id: uuid.UUID | None = None,
    ) -> EvaluationResponse:
        rules = RuleRegistry(self.db).load_active_rules(user_id, scope)
        results = []
        for rule in rules:
            result = self.engine.evaluate(rule, facts)
            results.append(result)
            if result.status.value == "BLOCK" and result.triggered:
                break
        response = RecommendationBuilder().build(results, limits)
        evaluation = RuleAuditWriter(self.db).save_evaluation(
            user_id=user_id,
            scope=scope,
            facts=facts,
            results=results,
            response=response,
            goal_id=goal_id,
        )
        self.db.commit()
        return self._response_model(evaluation.id, response, results)

    def _get_owned_rule(self, user_id: uuid.UUID, rule_id: uuid.UUID) -> UserRuleDefinition:
        rule = self.repo.get_user_rule(user_id, rule_id)
        if rule is None:
            raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
        return rule

    def _write_change_log(
        self,
        user_id: uuid.UUID,
        rule: UserRuleDefinition,
        before: dict | None,
        after: dict | None,
    ) -> None:
        self.db.add(
            RuleChangeLog(
                rule_id=rule.id,
                changed_by_user_id=user_id,
                before_json=before,
                after_json=after,
            )
        )

    @staticmethod
    def _rule_state(rule: UserRuleDefinition) -> dict:
        return {
            "name": rule.name,
            "scope": rule.scope,
            "condition_json": rule.condition_json,
            "action_json": rule.action_json,
            "priority": rule.priority,
            "version": rule.version,
            "is_active": rule.is_active,
            "deleted_at": rule.deleted_at.isoformat() if rule.deleted_at else None,
        }

    @staticmethod
    def _event_for_update(before: dict, after: dict) -> str:
        if before["is_active"] is False and after["is_active"] is True:
            return "rule.activated"
        if before["is_active"] is True and after["is_active"] is False:
            return "rule.paused"
        return "rule.updated"

    @staticmethod
    def _scope_from_goal_type(goal_type: str) -> str:
        mapping = {
            "SAVING": "saving",
            "LIVE_ALONE": "housing",
            "BUY_CAR": "car",
            "TRAVEL": "travel",
        }
        return mapping.get(goal_type.upper(), "general")

    @staticmethod
    def _response_model(
        evaluation_id: uuid.UUID, response: dict, results: list
    ) -> EvaluationResponse:
        return EvaluationResponse(
            evaluation_id=evaluation_id,
            rule_results=[
                RuleResultRead(
                    rule_id=result.rule_id,
                    rule_code=result.rule_code,
                    rule_version=result.rule_version,
                    status=result.status.value,
                    severity=result.severity.value,
                    triggered=result.triggered,
                    message=result.message,
                    developer_message=result.developer_message,
                    suggestions=result.suggestions,
                    details=result.details,
                    facts_snapshot=result.facts_snapshot,
                )
                for result in results
            ],
            **response,
        )
