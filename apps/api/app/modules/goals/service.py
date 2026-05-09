import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.modules.audit.service import write_audit_log
from app.modules.goals.models import Goal, GoalContribution
from app.modules.goals.repository import GoalRepository
from app.modules.goals.schemas import GoalContributionCreate, GoalCreate, GoalUpdate
from app.shared.money import decimal_to_string, quantize_money


class GoalService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = GoalRepository(db)

    def list(self, user_id: uuid.UUID, limit: int, offset: int) -> list[Goal]:
        return self.repo.list(user_id, min(limit, 100), offset)

    def create(self, user_id: uuid.UUID, payload: GoalCreate) -> Goal:
        goal = Goal(user_id=user_id, status="planning", **payload.model_dump())
        self.db.add(goal)
        self.db.flush()
        write_audit_log(
            self.db,
            event_type="goal.created",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="goal",
            entity_id=goal.id,
            after_state={"goal_type": goal.goal_type, "target_amount": str(goal.target_amount)},
        )
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def get_owned(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> Goal:
        goal = self.repo.get_owned(user_id, goal_id)
        if goal is None:
            raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
        return goal

    def update(self, user_id: uuid.UUID, goal_id: uuid.UUID, payload: GoalUpdate) -> Goal:
        goal = self.get_owned(user_id, goal_id)
        values = payload.model_dump(exclude_unset=True)
        before = {field: getattr(goal, field) for field in values}
        for field, value in values.items():
            setattr(goal, field, value)
        write_audit_log(
            self.db,
            event_type="goal.updated",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="goal",
            entity_id=goal.id,
            before_state={key: str(value) for key, value in before.items()},
            after_state={key: str(getattr(goal, key)) for key in values},
        )
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def soft_delete(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> None:
        goal = self.get_owned(user_id, goal_id)
        goal.deleted_at = datetime.now(UTC)
        write_audit_log(
            self.db,
            event_type="goal.deleted",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="goal",
            entity_id=goal.id,
        )
        self.db.commit()

    def add_contribution(
        self,
        user_id: uuid.UUID,
        goal_id: uuid.UUID,
        payload: GoalContributionCreate,
    ) -> Goal:
        goal = self.get_owned(user_id, goal_id)
        contribution = GoalContribution(
            user_id=user_id,
            goal_id=goal.id,
            amount=payload.amount,
            contribution_date=payload.contribution_date,
        )
        goal.current_amount = quantize_money(goal.current_amount + payload.amount)
        if goal.current_amount >= goal.target_amount:
            goal.status = "completed"
        self.db.add(contribution)
        self.db.flush()
        write_audit_log(
            self.db,
            event_type="goal.contribution.created",
            user_id=user_id,
            actor_user_id=user_id,
            entity_type="goal",
            entity_id=goal.id,
            after_state={"amount": str(payload.amount)},
        )
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def timeline(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> dict:
        goal = self.get_owned(user_id, goal_id)
        contributions = self.repo.contributions(user_id, goal.id)
        running_total = goal.current_amount - sum(
            (item.amount for item in contributions), start=Decimal("0.00")
        )
        events = []
        for contribution in contributions:
            running_total = quantize_money(running_total + contribution.amount)
            events.append(
                {
                    "date": contribution.contribution_date.isoformat(),
                    "event_type": "contribution",
                    "amount": decimal_to_string(contribution.amount),
                    "current_amount": decimal_to_string(running_total),
                }
            )
        return {
            "goal_id": str(goal.id),
            "target_amount": decimal_to_string(goal.target_amount),
            "current_amount": decimal_to_string(goal.current_amount),
            "events": events,
        }
