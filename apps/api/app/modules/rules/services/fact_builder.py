import uuid
from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.finance.repository import TransactionRepository
from app.modules.goals.repository import GoalRepository
from app.modules.rules.domain.facts import FinancialFacts
from app.modules.rules.math.financial_math import (
    emergency_fund_months,
    healthy_rent_range,
    monthly_available,
    ratio,
    required_monthly_contribution,
)


class FactBuilder:
    def __init__(self, db: Session):
        self.db = db
        self.transactions = TransactionRepository(db)
        self.goals = GoalRepository(db)

    def build_profile(self, user_id: uuid.UUID, period_month: date | None = None) -> FinancialFacts:
        month_start = (period_month or date.today()).replace(day=1)
        month_end = month_start.replace(day=monthrange(month_start.year, month_start.month)[1])
        totals = self.transactions.monthly_totals(user_id, month_start, month_end)
        income = totals.get("income", Decimal("0.00"))
        expenses = totals.get("expense", Decimal("0.00"))
        debt = totals.get("debt_payment", Decimal("0.00"))
        savings = totals.get("saving", Decimal("0.00"))
        available = monthly_available(income, expenses, Decimal("0.00"), debt, savings)
        essential = expenses + debt
        emergency_amount = self._emergency_fund_amount(user_id)
        return FinancialFacts(
            monthly_net_income=income,
            fixed_expenses_total=expenses,
            variable_expenses_avg=Decimal("0.00"),
            debt_payment_total=debt,
            mandatory_savings_total=savings,
            monthly_available=available,
            savings_rate=ratio(savings, income),
            debt_payment_ratio=ratio(debt, income),
            emergency_fund_amount=emergency_amount,
            emergency_fund_months=emergency_fund_months(emergency_amount, essential),
            remaining_after_goals=available,
            minimum_liquidity_buffer=income * Decimal("0.10"),
            goal_type="GENERAL",
        )

    def build_goal(
        self,
        user_id: uuid.UUID,
        goal_id: uuid.UUID,
        period_month: date | None = None,
    ) -> FinancialFacts:
        goal = self.goals.get_owned(user_id, goal_id)
        if goal is None:
            from app.core.errors import AppError

            raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
        profile = self.build_profile(user_id, period_month)
        months_until_deadline = self._months_until(goal.target_date)
        required = (
            required_monthly_contribution(
                goal.target_amount,
                goal.current_amount,
                months_until_deadline,
            )
            if months_until_deadline
            else Decimal("0.00")
        )
        rent_amount = Decimal(str(goal.parameters.get("rent_amount", "0.00")))
        car_payment = Decimal(str(goal.parameters.get("car_loan_payment", "0.00")))
        car_expenses = Decimal(str(goal.parameters.get("car_monthly_expenses", "0.00")))
        housing_total = Decimal(str(goal.parameters.get("housing_monthly_total", rent_amount)))
        facts = profile.as_dict()
        facts.update(
            {
                "housing_cost_ratio": ratio(housing_total, profile.monthly_net_income),
                "rent_amount": rent_amount,
                "car_loan_payment": car_payment,
                "car_monthly_expenses": car_expenses,
                "car_loan_payment_ratio": ratio(car_payment, profile.monthly_net_income),
                "car_total_monthly_ratio": ratio(
                    car_payment + car_expenses,
                    profile.monthly_net_income,
                ),
                "target_amount": goal.target_amount,
                "current_saved": goal.current_amount,
                "monthly_contribution": goal.monthly_contribution,
                "goal_required_monthly": required or Decimal("0.00"),
                "goal_progress_ratio": ratio(goal.current_amount, goal.target_amount),
                "remaining_after_goals": profile.monthly_available - goal.monthly_contribution,
                "goal_type": goal.goal_type.upper(),
                "status": goal.status.upper(),
            }
        )
        return FinancialFacts(**facts)

    def ui_limits(self, facts: FinancialFacts) -> list[dict[str, str]]:
        limits = []
        if facts.monthly_net_income > Decimal("0.00"):
            rent = healthy_rent_range(facts.monthly_net_income)
            limits.append(
                {
                    "name": "arriendo_recomendado",
                    "min": f"{rent['min']:.2f}",
                    "ideal": f"{rent['ideal']:.2f}",
                    "max": f"{rent['max']:.2f}",
                }
            )
            limits.append(
                {
                    "name": "cuota_carro",
                    "ideal": f"{facts.monthly_net_income * Decimal('0.10'):.2f}",
                    "max": f"{facts.monthly_net_income * Decimal('0.15'):.2f}",
                }
            )
        return limits

    def _emergency_fund_amount(self, user_id: uuid.UUID) -> Decimal:
        active_goals = self.goals.list(user_id, limit=100, offset=0)
        for goal in active_goals:
            if goal.parameters.get("is_emergency_fund") is True:
                return goal.current_amount
        return Decimal("0.00")

    @staticmethod
    def _months_until(target_date: date | None) -> int | None:
        if target_date is None:
            return None
        today = date.today()
        months = (target_date.year - today.year) * 12 + target_date.month - today.month
        return max(months, 0)
