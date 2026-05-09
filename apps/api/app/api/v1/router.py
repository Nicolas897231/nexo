from fastapi import APIRouter

from app.modules.alerts.router import router as alerts_router
from app.modules.audit.router import router as audit_router
from app.modules.auth.router import router as auth_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.finance.router import (
    categories_router,
    debts_router,
    financial_profile_router,
    income_sources_router,
    movements_router,
)
from app.modules.finance.router import router as finance_router
from app.modules.goals.router import router as goals_router
from app.modules.rules.router import alias_router as rules_alias_router
from app.modules.rules.router import evaluations_router
from app.modules.rules.router import router as rules_router
from app.modules.simulations.router import router as simulations_router
from app.modules.strategies.router import distributions_router, strategies_router
from app.modules.users.router import router as users_router

api_router = APIRouter()


@api_router.get("/health", tags=["health"])
def api_health() -> dict[str, str]:
    return {"status": "ok", "service": "NexoVia API"}


api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, tags=["users"])
api_router.include_router(finance_router, prefix="/finance", tags=["finance"])
api_router.include_router(
    financial_profile_router, prefix="/financial-profile", tags=["financial-profile"]
)
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_router.include_router(income_sources_router, prefix="/income-sources", tags=["income-sources"])
api_router.include_router(movements_router, prefix="/movements", tags=["movements"])
api_router.include_router(debts_router, prefix="/debts", tags=["debts"])
api_router.include_router(strategies_router, prefix="/strategies", tags=["strategies"])
api_router.include_router(distributions_router, prefix="/distributions", tags=["distributions"])
api_router.include_router(goals_router, prefix="/goals", tags=["goals"])
api_router.include_router(rules_router, prefix="/rules", tags=["rules"])
api_router.include_router(rules_alias_router, tags=["rules"])
api_router.include_router(evaluations_router, prefix="/evaluations", tags=["evaluations"])
api_router.include_router(simulations_router, prefix="/simulations", tags=["simulations"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
api_router.include_router(audit_router, prefix="/audit", tags=["audit"])
