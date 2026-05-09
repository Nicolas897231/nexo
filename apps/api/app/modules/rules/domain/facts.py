from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class FinancialFacts:
    monthly_net_income: Decimal
    fixed_expenses_total: Decimal = Decimal("0.00")
    variable_expenses_avg: Decimal = Decimal("0.00")
    debt_payment_total: Decimal = Decimal("0.00")
    mandatory_savings_total: Decimal = Decimal("0.00")
    monthly_available: Decimal = Decimal("0.00")
    savings_rate: Decimal = Decimal("0.000000")
    debt_payment_ratio: Decimal = Decimal("0.000000")
    emergency_fund_amount: Decimal = Decimal("0.00")
    emergency_fund_months: Decimal = Decimal("0.000000")
    housing_cost_ratio: Decimal = Decimal("0.000000")
    rent_amount: Decimal = Decimal("0.00")
    car_loan_payment: Decimal = Decimal("0.00")
    car_monthly_expenses: Decimal = Decimal("0.00")
    car_loan_payment_ratio: Decimal = Decimal("0.000000")
    car_total_monthly_ratio: Decimal = Decimal("0.000000")
    target_amount: Decimal = Decimal("0.00")
    current_saved: Decimal = Decimal("0.00")
    monthly_contribution: Decimal = Decimal("0.00")
    goal_required_monthly: Decimal = Decimal("0.00")
    goal_progress_ratio: Decimal = Decimal("0.000000")
    remaining_after_goals: Decimal = Decimal("0.00")
    minimum_liquidity_buffer: Decimal = Decimal("0.00")
    goal_type: str = "GENERAL"
    status: str = "OPEN"
    category: str = ""
    extra: dict[str, Decimal | str] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Decimal | str]:
        data = {
            "monthly_net_income": self.monthly_net_income,
            "fixed_expenses_total": self.fixed_expenses_total,
            "variable_expenses_avg": self.variable_expenses_avg,
            "debt_payment_total": self.debt_payment_total,
            "mandatory_savings_total": self.mandatory_savings_total,
            "monthly_available": self.monthly_available,
            "savings_rate": self.savings_rate,
            "debt_payment_ratio": self.debt_payment_ratio,
            "emergency_fund_amount": self.emergency_fund_amount,
            "emergency_fund_months": self.emergency_fund_months,
            "housing_cost_ratio": self.housing_cost_ratio,
            "rent_amount": self.rent_amount,
            "car_loan_payment": self.car_loan_payment,
            "car_monthly_expenses": self.car_monthly_expenses,
            "car_loan_payment_ratio": self.car_loan_payment_ratio,
            "car_total_monthly_ratio": self.car_total_monthly_ratio,
            "target_amount": self.target_amount,
            "current_saved": self.current_saved,
            "monthly_contribution": self.monthly_contribution,
            "goal_required_monthly": self.goal_required_monthly,
            "goal_progress_ratio": self.goal_progress_ratio,
            "remaining_after_goals": self.remaining_after_goals,
            "minimum_liquidity_buffer": self.minimum_liquidity_buffer,
            "goal_type": self.goal_type,
            "status": self.status,
            "category": self.category,
        }
        data.update(self.extra)
        return data
