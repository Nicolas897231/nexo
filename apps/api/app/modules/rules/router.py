import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.rules.repository import RuleRepository
from app.modules.rules.schemas import (
    GoalEvaluationRequest,
    ProfileEvaluationRequest,
    RuleEvaluationRequest,
    UserRuleCreate,
    UserRuleRead,
    UserRuleUpdate,
)
from app.modules.rules.service import RuleService

router = APIRouter()
alias_router = APIRouter()
evaluations_router = APIRouter()


def _template_payload(template) -> dict:
    return {
        "id": str(template.id),
        "code": template.code,
        "name": template.name,
        "description": template.description,
        "allowed_fields": template.allowed_fields,
        "allowed_operators": template.allowed_operators,
        "schema_json": template.schema_json,
    }


def _user_rule_payload(rule) -> dict:
    return UserRuleRead.model_validate(rule, from_attributes=True).model_dump(mode="json")


@router.get("/templates")
def list_templates(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return ok([_template_payload(template) for template in RuleRepository(db).templates()])


@router.get("/predefined")
def list_predefined_rules(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rules = RuleRepository(db).predefined_rules()
    return ok(
        [
            {
                "id": str(rule.id),
                "code": rule.code,
                "name": rule.name,
                "description": rule.description,
                "scope": rule.scope,
                "rule_type": rule.rule_type,
                "condition_json": rule.condition_json,
                "action_json": rule.action_json,
                "severity": rule.severity,
                "priority": rule.priority,
                "version": rule.version,
            }
            for rule in rules
        ]
    )


@router.get("/custom")
@router.get("/user-rules")
def list_user_rules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return ok([_user_rule_payload(rule) for rule in RuleRepository(db).user_rules(current_user.id)])


@router.post("/custom/validate")
@router.post("/user-rules/validate")
def validate_user_rule(payload: UserRuleCreate, _: User = Depends(get_current_user)):
    return ok({"valid": True})


@router.post("/custom", status_code=status.HTTP_201_CREATED)
@router.post("/user-rules", status_code=status.HTTP_201_CREATED)
def create_user_rule(
    payload: UserRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = RuleService(db).create_user_rule(current_user.id, payload)
    return ok(_user_rule_payload(rule))


@router.patch("/custom/{rule_id}")
@router.patch("/user-rules/{rule_id}")
def update_user_rule(
    rule_id: uuid.UUID,
    payload: UserRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = RuleService(db).update_user_rule(current_user.id, rule_id, payload)
    return ok(_user_rule_payload(rule))


@router.delete("/custom/{rule_id}")
@router.delete("/user-rules/{rule_id}")
def delete_user_rule(
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    RuleService(db).delete_user_rule(current_user.id, rule_id)
    return ok({"status": "deleted"})


@router.post("/evaluate")
def evaluate_inline_rule(
    payload: RuleEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(
        RuleService(db).evaluate_inline_rule(current_user.id, payload).model_dump(mode="json")
    )


@alias_router.get("/rule-templates")
def list_rule_templates_alias(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_templates(db, current_user)


@alias_router.get("/user-rules")
def list_user_rules_alias(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return list_user_rules(db, current_user)


@alias_router.post("/user-rules", status_code=status.HTTP_201_CREATED)
def create_user_rule_alias(
    payload: UserRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_user_rule(payload, db, current_user)


@alias_router.patch("/user-rules/{rule_id}")
def update_user_rule_alias(
    rule_id: uuid.UUID,
    payload: UserRuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user_rule(rule_id, payload, db, current_user)


@alias_router.get("/rule-evaluations/{evaluation_id}")
def get_rule_evaluation(
    evaluation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(RuleService(db).get_evaluation(current_user.id, evaluation_id))


@alias_router.get("/decision-engine/recommendations")
def get_decision_engine_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    evaluation = RuleService(db).evaluate_profile(current_user.id)
    return ok(
        {
            "evaluation_id": str(evaluation.evaluation_id),
            "overall_status": evaluation.overall_status.value,
            "score": evaluation.score,
            "headline": evaluation.headline,
            "summary": evaluation.summary,
            "alerts": evaluation.alerts,
            "suggestions": evaluation.suggestions,
        }
    )


@evaluations_router.post("/profile")
def evaluate_profile(
    payload: ProfileEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    response = RuleService(db).evaluate_profile(current_user.id, payload.period_month)
    return ok(response.model_dump(mode="json"))


@evaluations_router.post("/goals/{goal_id}")
def evaluate_goal(
    goal_id: uuid.UUID,
    payload: GoalEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    response = RuleService(db).evaluate_goal(current_user.id, goal_id, payload.period_month)
    return ok(response.model_dump(mode="json"))
