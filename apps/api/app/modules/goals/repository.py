from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.goals.models import Goal, GoalContribution


class GoalRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, user_id: uuid.UUID, limit: int, offset: int) -> list[Goal]:
        return list(
            self.db.scalars(
                select(Goal)
                .where(Goal.user_id == user_id, Goal.deleted_at.is_(None))
                .order_by(Goal.priority.asc(), Goal.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
        )

    def get_owned(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> Goal | None:
        return self.db.scalar(
            select(Goal).where(
                Goal.id == goal_id, Goal.user_id == user_id, Goal.deleted_at.is_(None)
            )
        )

    def contributions(self, user_id: uuid.UUID, goal_id: uuid.UUID) -> list[GoalContribution]:
        return list(
            self.db.scalars(
                select(GoalContribution)
                .where(GoalContribution.user_id == user_id, GoalContribution.goal_id == goal_id)
                .order_by(GoalContribution.contribution_date.asc())
            )
        )
