import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.goals.schemas import GoalContributionCreate, GoalCreate, GoalRead, GoalUpdate
from app.modules.goals.service import GoalService

router = APIRouter()


def _read_goal(goal) -> dict:
    return GoalRead.model_validate(goal, from_attributes=True).model_dump(mode="json")


@router.get("")
def list_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    goals = GoalService(db).list(current_user.id, limit, offset)
    return ok([_read_goal(goal) for goal in goals], pagination={"limit": limit, "offset": offset})


@router.post("", status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = GoalService(db).create(current_user.id, payload)
    return ok(_read_goal(goal))


@router.get("/{goal_id}")
def get_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(_read_goal(GoalService(db).get_owned(current_user.id, goal_id)))


@router.patch("/{goal_id}")
def update_goal(
    goal_id: uuid.UUID,
    payload: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = GoalService(db).update(current_user.id, goal_id, payload)
    return ok(_read_goal(goal))


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    GoalService(db).soft_delete(current_user.id, goal_id)
    return ok({"status": "deleted"})


@router.post("/{goal_id}/contributions", status_code=status.HTTP_201_CREATED)
def add_contribution(
    goal_id: uuid.UUID,
    payload: GoalContributionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    goal = GoalService(db).add_contribution(current_user.id, goal_id, payload)
    return ok(_read_goal(goal))


@router.get("/{goal_id}/timeline")
def get_timeline(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(GoalService(db).timeline(current_user.id, goal_id))
