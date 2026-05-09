import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.strategies.schemas import (
    DistributionRead,
    DistributionUpdate,
    DistributionWrite,
    StrategyPreviewRequest,
)
from app.modules.strategies.service import StrategyService

strategies_router = APIRouter()
distributions_router = APIRouter()


def _read_distribution(distribution) -> dict:
    return DistributionRead.model_validate(distribution, from_attributes=True).model_dump(
        mode="json"
    )


@strategies_router.get("")
def list_strategies(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return ok(StrategyService(db).list_strategies())


@strategies_router.post("/preview")
def preview_strategy(
    payload: StrategyPreviewRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ok(StrategyService(db).preview(payload.monthly_income, payload.strategy_code))


@strategies_router.get("/{strategy_id}")
def get_strategy(
    strategy_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ok(StrategyService(db).get_strategy(strategy_id))


@distributions_router.post("", status_code=status.HTTP_201_CREATED)
def create_distribution(
    payload: DistributionWrite,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ok(_read_distribution(StrategyService(db).create_distribution(current_user.id, payload)))


@distributions_router.get("/current")
def current_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    distribution = StrategyService(db).current_distribution(current_user.id)
    return ok(_read_distribution(distribution) if distribution else None)


@distributions_router.patch("/{distribution_id}")
def update_distribution(
    distribution_id: uuid.UUID,
    payload: DistributionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    distribution = StrategyService(db).update_distribution(
        current_user.id, distribution_id, payload
    )
    return ok(_read_distribution(distribution))
