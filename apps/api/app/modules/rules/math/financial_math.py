from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal

MONEY_Q = Decimal("0.01")
RATIO_Q = Decimal("0.000001")


def money(value: Decimal | str | int) -> Decimal:
    if isinstance(value, float):
        raise TypeError("Money values must not be floats")
    return Decimal(str(value)).quantize(MONEY_Q, rounding=ROUND_HALF_UP)


def ratio(numerator: Decimal, denominator: Decimal) -> Decimal:
    if denominator <= Decimal("0"):
        return Decimal("0.000000")
    return (numerator / denominator).quantize(RATIO_Q, rounding=ROUND_HALF_UP)


def percent_of(base: Decimal, percent: Decimal) -> Decimal:
    return money(base * percent)


def monthly_available(
    income: Decimal,
    fixed_expenses: Decimal,
    variable_expenses: Decimal,
    debt_payments: Decimal,
    mandatory_savings: Decimal,
) -> Decimal:
    return money(income - fixed_expenses - variable_expenses - debt_payments - mandatory_savings)


def months_to_goal(
    target: Decimal, current_saved: Decimal, monthly_contribution: Decimal
) -> int | None:
    remaining = target - current_saved
    if remaining <= Decimal("0"):
        return 0
    if monthly_contribution <= Decimal("0"):
        return None
    return int((remaining / monthly_contribution).to_integral_value(rounding=ROUND_CEILING))


def required_monthly_contribution(
    target: Decimal,
    current_saved: Decimal,
    months_until_deadline: int,
) -> Decimal | None:
    if months_until_deadline <= 0:
        return None
    remaining = max(target - current_saved, Decimal("0.00"))
    return money(remaining / Decimal(months_until_deadline))


def loan_monthly_payment(principal: Decimal, monthly_rate: Decimal, months: int) -> Decimal:
    if principal <= Decimal("0"):
        return Decimal("0.00")
    if months <= 0:
        raise ValueError("months_must_be_positive")
    if monthly_rate < Decimal("0"):
        raise ValueError("monthly_rate_must_be_non_negative")
    if monthly_rate == Decimal("0"):
        return money(principal / Decimal(months))
    one = Decimal("1")
    factor = (one + monthly_rate) ** months
    return money(principal * (monthly_rate * factor) / (factor - one))


def financeable_principal(payment: Decimal, monthly_rate: Decimal, months: int) -> Decimal:
    if payment <= Decimal("0"):
        return Decimal("0.00")
    if months <= 0:
        raise ValueError("months_must_be_positive")
    if monthly_rate < Decimal("0"):
        raise ValueError("monthly_rate_must_be_non_negative")
    if monthly_rate == Decimal("0"):
        return money(payment * Decimal(months))
    one = Decimal("1")
    principal = payment * (one - (one + monthly_rate) ** Decimal(-months)) / monthly_rate
    return money(principal)


def max_car_price_by_payment(
    max_payment: Decimal,
    monthly_rate: Decimal,
    months: int,
    down_payment: Decimal,
) -> Decimal:
    return money(financeable_principal(max_payment, monthly_rate, months) + down_payment)


def emergency_fund_months(emergency_fund: Decimal, essential_monthly_expenses: Decimal) -> Decimal:
    return ratio(emergency_fund, essential_monthly_expenses)


def healthy_rent_range(income: Decimal) -> dict[str, Decimal]:
    return {
        "min": percent_of(income, Decimal("0.20")),
        "ideal": percent_of(income, Decimal("0.25")),
        "max": percent_of(income, Decimal("0.30")),
    }
