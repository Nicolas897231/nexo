import uuid
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AppError
from app.core.responses import ok
from app.core.security import get_current_user
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import User
from app.modules.goals.schemas import GoalCreate
from app.modules.goals.service import GoalService
from app.modules.rules.math.financial_math import (
    healthy_rent_range,
    loan_monthly_payment,
    money,
    ratio,
)
from app.modules.rules.service import RuleService
from app.modules.simulations.models import Simulation
from app.modules.simulations.schemas import (
    CarSimulationRequest,
    LiveAloneSimulationRequest,
    SavingsSimulationRequest,
    TravelSimulationRequest,
)
from app.shared.money import decimal_to_string

router = APIRouter()


def _jsonable(value):
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def _store_simulation(
    db: Session,
    user_id: uuid.UUID,
    simulation_type: str,
    input_payload: dict,
    result_payload: dict,
) -> Simulation:
    simulation = Simulation(
        user_id=user_id,
        simulation_type=simulation_type,
        input_payload=_jsonable(input_payload),
        result_payload=_jsonable(result_payload),
    )
    db.add(simulation)
    db.flush()
    write_audit_log(
        db,
        event_type="simulation.created",
        user_id=user_id,
        actor_user_id=user_id,
        entity_type="simulation",
        entity_id=simulation.id,
        after_state={"simulation_type": simulation_type},
    )
    db.commit()
    db.refresh(simulation)
    return simulation


def _with_simulation_id(simulation: Simulation) -> dict:
    payload = dict(simulation.result_payload)
    payload["simulation_id"] = str(simulation.id)
    return payload


@router.post("/savings")
def simulate_savings(
    payload: SavingsSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pending = money(max(payload.target_amount - payload.current_amount, Decimal("0.00")))
    months_required = 0
    if payload.monthly_contribution > Decimal("0.00"):
        months_required = int((pending / payload.monthly_contribution).to_integral_value())
        if pending % payload.monthly_contribution:
            months_required += 1
    facts = {
        "monthly_net_income": payload.monthly_net_income,
        "monthly_available": payload.monthly_net_income,
        "savings_rate": ratio(payload.monthly_contribution, payload.monthly_net_income),
        "debt_payment_ratio": Decimal("0.000000"),
        "emergency_fund_months": Decimal("0.000000"),
        "target_amount": payload.target_amount,
        "monthly_contribution": payload.monthly_contribution,
        "remaining_after_goals": payload.monthly_net_income - payload.monthly_contribution,
        "minimum_liquidity_buffer": payload.monthly_net_income * Decimal("0.10"),
        "goal_type": "SAVING",
    }
    evaluation = RuleService(db).evaluate_scope_facts(
        user_id=current_user.id, scope="saving", facts=facts
    )
    result = {
        "pending_amount": decimal_to_string(pending),
        "months_required": months_required,
        "evaluation": evaluation.model_dump(mode="json"),
    }
    simulation = _store_simulation(db, current_user.id, "saving", payload.model_dump(), result)
    return ok(_with_simulation_id(simulation))


@router.post("/car")
def simulate_car(
    payload: CarSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    financed_amount = money(max(payload.vehicle_price - payload.down_payment, Decimal("0.00")))
    monthly_payment = loan_monthly_payment(
        financed_amount, payload.monthly_rate, payload.term_months
    )
    monthly_expenses = money(
        payload.insurance_monthly
        + payload.fuel_monthly
        + payload.maintenance_monthly
        + payload.parking_monthly
    )
    total_monthly = money(monthly_payment + monthly_expenses)
    facts = {
        "monthly_net_income": payload.monthly_net_income,
        "monthly_available": payload.monthly_net_income,
        "savings_rate": Decimal("0.000000"),
        "debt_payment_ratio": Decimal("0.000000"),
        "emergency_fund_months": Decimal("0.000000"),
        "remaining_after_goals": payload.monthly_net_income - total_monthly,
        "minimum_liquidity_buffer": payload.monthly_net_income * Decimal("0.10"),
        "car_loan_payment": monthly_payment,
        "car_monthly_expenses": monthly_expenses,
        "car_loan_payment_ratio": ratio(monthly_payment, payload.monthly_net_income),
        "car_total_monthly_ratio": ratio(total_monthly, payload.monthly_net_income),
        "goal_type": "BUY_CAR",
    }
    evaluation = RuleService(db).evaluate_scope_facts(
        user_id=current_user.id,
        scope="car",
        facts=facts,
    )
    result = {
        "financed_amount": f"{financed_amount:.2f}",
        "monthly_payment": f"{monthly_payment:.2f}",
        "monthly_extra_costs": f"{monthly_expenses:.2f}",
        "monthly_total_car_cost": f"{total_monthly:.2f}",
        "car_loan_payment_ratio": str(facts["car_loan_payment_ratio"]),
        "car_total_monthly_ratio": str(facts["car_total_monthly_ratio"]),
        "evaluation": evaluation.model_dump(mode="json"),
    }
    simulation = _store_simulation(
        db, current_user.id, "car_financing", payload.model_dump(), result
    )
    return ok(_with_simulation_id(simulation))


@router.post("/live-alone")
@router.post("/living-alone")
def simulate_live_alone(
    payload: LiveAloneSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    monthly_living_cost = money(
        payload.rent_amount
        + payload.utilities_amount
        + payload.food_amount
        + payload.transport_amount
        + payload.internet_amount
        + payload.personal_basics_amount
    )
    rent_range = healthy_rent_range(payload.monthly_net_income)
    emergency_required = money(monthly_living_cost * Decimal("3"))
    facts = {
        "monthly_net_income": payload.monthly_net_income,
        "monthly_available": payload.monthly_net_income - monthly_living_cost,
        "savings_rate": Decimal("0.000000"),
        "debt_payment_ratio": Decimal("0.000000"),
        "emergency_fund_amount": payload.emergency_fund_amount,
        "emergency_fund_months": ratio(payload.emergency_fund_amount, monthly_living_cost),
        "housing_cost_ratio": ratio(monthly_living_cost, payload.monthly_net_income),
        "rent_amount": payload.rent_amount,
        "remaining_after_goals": payload.monthly_net_income - monthly_living_cost,
        "minimum_liquidity_buffer": payload.monthly_net_income * Decimal("0.10"),
        "goal_type": "LIVE_ALONE",
    }
    evaluation = RuleService(db).evaluate_scope_facts(
        user_id=current_user.id,
        scope="housing",
        facts=facts,
        limits=[
            {
                "name": "arriendo_recomendado",
                "min": f"{rent_range['min']:.2f}",
                "ideal": f"{rent_range['ideal']:.2f}",
                "max": f"{rent_range['max']:.2f}",
            }
        ],
    )
    result = {
        "monthly_living_cost": f"{monthly_living_cost:.2f}",
        "moving_initial_cost": f"{payload.moving_initial_cost:.2f}",
        "emergency_fund_required": f"{emergency_required:.2f}",
        "housing_cost_ratio": str(facts["housing_cost_ratio"]),
        "emergency_fund_months": str(facts["emergency_fund_months"]),
        "evaluation": evaluation.model_dump(mode="json"),
    }
    simulation = _store_simulation(db, current_user.id, "housing", payload.model_dump(), result)
    return ok(_with_simulation_id(simulation))


@router.post("/travel")
def simulate_travel(
    payload: TravelSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_cost = money(
        payload.flights_amount
        + payload.lodging_amount
        + payload.food_amount
        + payload.extras_amount
    )
    pending = money(max(total_cost - payload.current_amount, Decimal("0.00")))
    months_until_trip = None
    if payload.travel_date:
        today = date.today()
        months_until_trip = max(
            (payload.travel_date.year - today.year) * 12 + payload.travel_date.month - today.month,
            1,
        )
    required_monthly = (
        pending if not months_until_trip else money(pending / Decimal(months_until_trip))
    )
    facts = {
        "monthly_net_income": payload.monthly_net_income,
        "monthly_available": payload.monthly_net_income,
        "goal_required_monthly": required_monthly,
        "remaining_after_goals": payload.monthly_net_income - required_monthly,
        "minimum_liquidity_buffer": payload.monthly_net_income * Decimal("0.10"),
        "savings_rate": ratio(required_monthly, payload.monthly_net_income),
        "debt_payment_ratio": Decimal("0.000000"),
        "emergency_fund_months": Decimal("0.000000"),
        "goal_type": "TRAVEL",
    }
    evaluation = RuleService(db).evaluate_scope_facts(
        user_id=current_user.id, scope="travel", facts=facts
    )
    result = {
        "destination": payload.destination,
        "total_cost": decimal_to_string(total_cost),
        "pending_amount": decimal_to_string(pending),
        "required_monthly": decimal_to_string(required_monthly),
        "months_until_trip": months_until_trip,
        "evaluation": evaluation.model_dump(mode="json"),
    }
    simulation = _store_simulation(db, current_user.id, "travel", payload.model_dump(), result)
    return ok(_with_simulation_id(simulation))


@router.get("/{simulation_id}")
def get_simulation(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    simulation = db.scalar(
        select(Simulation).where(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id,
        )
    )
    if simulation is None:
        raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
    return ok(
        {
            "id": str(simulation.id),
            "simulation_type": simulation.simulation_type,
            "input": simulation.input_payload,
            "result": simulation.result_payload,
            "created_at": simulation.created_at.isoformat(),
        }
    )


@router.post("/{simulation_id}/convert-to-goal")
def convert_simulation_to_goal(
    simulation_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    simulation = db.scalar(
        select(Simulation).where(
            Simulation.id == simulation_id,
            Simulation.user_id == current_user.id,
        )
    )
    if simulation is None:
        raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
    target_amount = simulation.result_payload.get("total_cost") or simulation.result_payload.get(
        "pending_amount"
    )
    if target_amount is None:
        target_amount = simulation.input_payload.get("target_amount") or "0.00"
    goal_type_map = {
        "saving": "saving",
        "housing": "live_alone",
        "car_financing": "buy_car",
        "travel": "travel",
    }
    goal_type = goal_type_map.get(simulation.simulation_type, "saving")
    goal = GoalService(db).create(
        current_user.id,
        GoalCreate(
            goal_type=goal_type,
            name=f"Meta desde simulacion {simulation.simulation_type}",
            target_amount=target_amount,
            parameters={"simulation_id": str(simulation.id)},
        ),
    )
    simulation.goal_id = goal.id
    db.commit()
    return ok({"goal_id": str(goal.id), "status": "created"})
