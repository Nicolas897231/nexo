import hashlib
import json
import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.middleware.request_context import get_request_id
from app.modules.audit.service import write_audit_log
from app.modules.rules.domain.entities import RuleResult
from app.modules.rules.models import RuleEvaluation, RuleEvaluationItem, RuleEvaluationLog


class RuleAuditWriter:
    def __init__(self, db: Session):
        self.db = db

    def save_evaluation(
        self,
        *,
        user_id: uuid.UUID,
        scope: str,
        facts: dict[str, Decimal | str],
        results: list[RuleResult],
        response: dict,
        goal_id: uuid.UUID | None = None,
    ) -> RuleEvaluation:
        safe_facts = self._serialize(facts)
        evaluation = RuleEvaluation(
            user_id=user_id,
            goal_id=goal_id,
            request_id=uuid.UUID(get_request_id()),
            scope=scope,
            status=response["overall_status"].value,
            score=response["score"],
            facts_snapshot=safe_facts,
            response_json=self._serialize(response),
        )
        self.db.add(evaluation)
        self.db.flush()
        context_hash = hashlib.sha256(
            json.dumps(safe_facts, sort_keys=True).encode("utf-8")
        ).hexdigest()
        for result in results:
            self.db.add(
                RuleEvaluationItem(
                    user_id=user_id,
                    evaluation_id=evaluation.id,
                    rule_id=result.rule_id,
                    rule_code=result.rule_code,
                    rule_version=result.rule_version,
                    status=result.status.value,
                    severity=result.severity.value,
                    facts_snapshot=self._serialize(result.facts_snapshot),
                    output_message=result.message,
                )
            )
            self.db.add(
                RuleEvaluationLog(
                    user_id=user_id,
                    rule_code=result.rule_code,
                    input_context_hash=context_hash,
                    result_json=self._serialize(
                        {
                            "status": result.status.value,
                            "severity": result.severity.value,
                            "triggered": result.triggered,
                            "message": result.message,
                        }
                    ),
                    triggered=result.triggered,
                )
            )
        write_audit_log(
            self.db,
            event_type="rule.evaluation.created",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="rule_evaluation",
            entity_id=evaluation.id,
            after_state={"scope": scope, "status": response["overall_status"].value},
        )
        return evaluation

    def get_owned(self, user_id: uuid.UUID, evaluation_id: uuid.UUID) -> RuleEvaluation | None:
        from sqlalchemy import select

        return self.db.scalar(
            select(RuleEvaluation).where(
                RuleEvaluation.id == evaluation_id,
                RuleEvaluation.user_id == user_id,
            )
        )

    def _serialize(self, value):
        if isinstance(value, Decimal):
            return str(value)
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, dict):
            return {key: self._serialize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._serialize(item) for item in value]
        if hasattr(value, "value"):
            return value.value
        return value
