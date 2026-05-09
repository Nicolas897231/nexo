from decimal import Decimal, InvalidOperation
from typing import Any

from app.core.errors import AppError
from app.modules.rules.domain.entities import Rule, RuleResult
from app.modules.rules.domain.enums import RuleSeverity, RuleStatus
from app.modules.rules.math.financial_math import money, percent_of, ratio

ALLOWED_FACTS = {
    "monthly_net_income",
    "fixed_expenses_total",
    "variable_expenses_avg",
    "debt_payment_total",
    "mandatory_savings_total",
    "monthly_available",
    "savings_rate",
    "debt_payment_ratio",
    "emergency_fund_amount",
    "emergency_fund_months",
    "housing_cost_ratio",
    "rent_amount",
    "car_loan_payment",
    "car_monthly_expenses",
    "car_loan_payment_ratio",
    "car_total_monthly_ratio",
    "target_amount",
    "current_saved",
    "monthly_contribution",
    "goal_required_monthly",
    "goal_progress_ratio",
    "remaining_after_goals",
    "minimum_liquidity_buffer",
    "goal_type",
    "status",
    "category",
}

ALLOWED_OPERATORS = {"eq", "neq", "gt", "gte", "lt", "lte", "between", "in"}
ALLOWED_FORMULAS = {"percent_of", "sum", "subtract", "multiply", "divide"}
UNSAFE_TOKENS = {"eval", "exec", "import", "lambda", "__", "open(", "subprocess", "os.", "sys."}


class RuleEngine:
    def validate_condition(self, condition: dict[str, Any]) -> None:
        self._reject_unsafe_tokens(condition)
        if "all" in condition:
            self._validate_group(condition, "all")
            return
        if "any" in condition:
            self._validate_group(condition, "any")
            return
        if "left" in condition or "right" in condition:
            self._validate_expression_condition(condition)
            return
        self._validate_leaf(condition)

    def evaluate(self, rule: Rule | dict[str, Any], facts: dict[str, Decimal | str]) -> RuleResult:
        normalized_rule = self._normalize_rule(rule)
        self.validate_condition(normalized_rule.condition_json)
        triggered, snapshot = self._evaluate_condition(normalized_rule.condition_json, facts)
        action = normalized_rule.action_json
        status = self._status_for(triggered, action)
        severity = self._severity_for(triggered, action, normalized_rule.severity)
        message = action.get("user_message") or action.get("message")
        suggestions = action.get("suggestions") or []
        if recommendation := action.get("recommendation"):
            suggestions = [recommendation, *suggestions]
        return RuleResult(
            rule_id=normalized_rule.id,
            rule_code=normalized_rule.code,
            rule_version=normalized_rule.version,
            status=status,
            severity=severity,
            triggered=triggered,
            message=message if triggered else None,
            developer_message=action.get("developer_message"),
            suggestions=[str(item) for item in suggestions[:3]],
            details={
                "source": normalized_rule.source,
                "scope": normalized_rule.scope,
                "priority": str(normalized_rule.priority),
            },
            facts_snapshot=snapshot,
        )

    def _evaluate_condition(
        self,
        condition: dict[str, Any],
        facts: dict[str, Decimal | str],
    ) -> tuple[bool, dict[str, Decimal | str]]:
        if "all" in condition:
            snapshots: dict[str, Decimal | str] = {}
            results = []
            for child in condition["all"]:
                result, snapshot = self._evaluate_condition(child, facts)
                snapshots.update(snapshot)
                results.append(result)
            return all(results), snapshots
        if "any" in condition:
            snapshots = {}
            results = []
            for child in condition["any"]:
                result, snapshot = self._evaluate_condition(child, facts)
                snapshots.update(snapshot)
                results.append(result)
            return any(results), snapshots
        if "left" in condition or "right" in condition:
            left = self._resolve_expression(condition["left"], facts)
            right = self._resolve_expression(condition["right"], facts)
            return self._compare(left, condition["operator"], right), {
                "left": self._snapshot_value(left),
                "right": self._snapshot_value(right),
            }
        fact_name = condition.get("fact") or condition.get("field")
        if fact_name not in facts:
            raise AppError("INSUFFICIENT_DATA", "Faltan datos para evaluar la regla.", 409)
        left = facts[fact_name]
        if condition["operator"] == "between":
            right = [self._parse_decimal(condition["min"]), self._parse_decimal(condition["max"])]
        elif condition["operator"] == "in":
            right = condition["value"]
        else:
            right = condition["value"]
            if isinstance(left, Decimal):
                right = self._parse_decimal(right)
        return self._compare(left, condition["operator"], right), {fact_name: left}

    def _validate_group(self, condition: dict[str, Any], key: str) -> None:
        children = condition.get(key)
        if not isinstance(children, list) or not 1 <= len(children) <= 10:
            raise AppError(
                "RULE_INVALID_CONDITION", "La regla debe tener entre 1 y 10 condiciones.", 400
            )
        for child in children:
            if not isinstance(child, dict):
                raise AppError(
                    "RULE_INVALID_CONDITION", "La condición de la regla no es válida.", 400
                )
            self.validate_condition(child)

    def _validate_expression_condition(self, condition: dict[str, Any]) -> None:
        operator = condition.get("operator")
        if operator not in ALLOWED_OPERATORS - {"in", "between"}:
            raise AppError("RULE_INVALID_OPERATOR", "La condición de la regla no es válida.", 400)
        if "left" not in condition or "right" not in condition:
            raise AppError("RULE_INVALID_CONDITION", "La regla requiere left y right.", 400)
        self._validate_expression(condition["left"])
        self._validate_expression(condition["right"])

    def _validate_leaf(self, condition: dict[str, Any]) -> None:
        fact = condition.get("fact") or condition.get("field")
        operator = condition.get("operator")
        if fact not in ALLOWED_FACTS:
            raise AppError(
                "RULE_UNSAFE_EXPRESSION", "La regla contiene un campo no permitido.", 400
            )
        if operator not in ALLOWED_OPERATORS:
            raise AppError("RULE_INVALID_OPERATOR", "La condición de la regla no es válida.", 400)
        if operator == "between":
            if "min" not in condition or "max" not in condition:
                raise AppError("RULE_INVALID_OPERATOR", "La regla between requiere min y max.", 400)
            self._parse_decimal(condition["min"])
            self._parse_decimal(condition["max"])
            return
        if operator == "in":
            values = condition.get("value")
            if not isinstance(values, list) or not 1 <= len(values) <= 20:
                raise AppError(
                    "RULE_INVALID_OPERATOR", "La regla in requiere una lista válida.", 400
                )
            return
        if "value" not in condition:
            raise AppError("RULE_INVALID_OPERATOR", "La regla requiere value.", 400)
        if fact not in {"goal_type", "status", "category"}:
            self._parse_decimal(condition["value"])

    def _validate_expression(self, expression: Any) -> None:
        if not isinstance(expression, dict):
            raise AppError("RULE_INVALID_CONDITION", "La expresión de la regla no es válida.", 400)
        formula = expression.get("formula")
        if formula is not None:
            if formula not in ALLOWED_FORMULAS:
                raise AppError(
                    "RULE_UNSAFE_EXPRESSION", "La fórmula de la regla no está permitida.", 400
                )
            if formula == "percent_of":
                fact = expression.get("field") or expression.get("fact")
                if fact not in ALLOWED_FACTS:
                    raise AppError(
                        "RULE_UNSAFE_EXPRESSION", "La regla contiene un campo no permitido.", 400
                    )
                self._parse_decimal(expression.get("value"))
                return
            if formula == "sum":
                fields = expression.get("fields")
                if not isinstance(fields, list) or not 1 <= len(fields) <= 10:
                    raise AppError("RULE_INVALID_CONDITION", "La fórmula sum requiere fields.", 400)
                if any(field not in ALLOWED_FACTS for field in fields):
                    raise AppError(
                        "RULE_UNSAFE_EXPRESSION", "La regla contiene un campo no permitido.", 400
                    )
                return
            for key in ("left", "right"):
                self._validate_expression(expression.get(key))
            return
        if "fact" in expression or "field" in expression:
            fact = expression.get("fact") or expression.get("field")
            if fact not in ALLOWED_FACTS:
                raise AppError(
                    "RULE_UNSAFE_EXPRESSION", "La regla contiene un campo no permitido.", 400
                )
            return
        if "value" in expression:
            self._parse_decimal(expression["value"])
            return
        raise AppError("RULE_INVALID_CONDITION", "La expresión de la regla no es válida.", 400)

    def _resolve_expression(
        self,
        expression: dict[str, Any],
        facts: dict[str, Decimal | str],
    ) -> Decimal | str:
        if "formula" in expression:
            formula = expression["formula"]
            if formula == "percent_of":
                fact = expression.get("field") or expression.get("fact")
                if fact not in facts:
                    raise AppError("INSUFFICIENT_DATA", "Faltan datos para evaluar la regla.", 409)
                return percent_of(
                    self._ensure_decimal(facts[fact]), self._parse_decimal(expression["value"])
                )
            if formula == "sum":
                return money(
                    sum(self._ensure_decimal(facts[field]) for field in expression["fields"])
                )
            left = self._ensure_decimal(self._resolve_expression(expression["left"], facts))
            right = self._ensure_decimal(self._resolve_expression(expression["right"], facts))
            if formula == "subtract":
                return money(left - right)
            if formula == "multiply":
                return money(left * right)
            if formula == "divide":
                return ratio(left, right)
            raise AppError(
                "RULE_UNSAFE_EXPRESSION", "La fórmula de la regla no está permitida.", 400
            )
        if "fact" in expression or "field" in expression:
            fact = expression.get("fact") or expression.get("field")
            if fact not in facts:
                raise AppError("INSUFFICIENT_DATA", "Faltan datos para evaluar la regla.", 409)
            return facts[fact]
        if "value" in expression:
            return self._parse_decimal(expression["value"])
        raise AppError("RULE_INVALID_CONDITION", "La expresión de la regla no es válida.", 400)

    def _compare(self, left: Decimal | str, operator: str, right: Any) -> bool:
        if operator == "between":
            return right[0] <= self._ensure_decimal(left) <= right[1]
        if operator == "in":
            return str(left) in {str(item) for item in right}
        if isinstance(left, Decimal):
            right = self._ensure_decimal(right)
        else:
            right = str(right)
        if operator == "eq":
            return left == right
        if operator == "neq":
            return left != right
        if operator == "gt":
            return left > right
        if operator == "gte":
            return left >= right
        if operator == "lt":
            return left < right
        if operator == "lte":
            return left <= right
        raise AppError("RULE_INVALID_OPERATOR", "La condición de la regla no es válida.", 400)

    @staticmethod
    def _normalize_rule(rule: Rule | dict[str, Any]) -> Rule:
        if isinstance(rule, Rule):
            return rule
        return Rule(
            id=rule.get("id"),
            code=rule.get("code", "CUSTOM_RULE"),
            scope=rule.get("scope", "general"),
            name=rule.get("name", rule.get("code", "Regla")),
            priority=int(rule.get("priority", 100)),
            condition_json=rule["condition_json"],
            action_json=rule.get("action_json", {}),
            severity=rule.get("severity", rule.get("action_json", {}).get("severity", "INFO")),
            version=int(rule.get("version", 1)),
            source=rule.get("source", "inline"),
        )

    @staticmethod
    def _status_for(triggered: bool, action: dict[str, Any]) -> RuleStatus:
        if not triggered:
            return RuleStatus.PASS
        status = action.get("status", "WARN")
        if status not in {item.value for item in RuleStatus}:
            raise AppError("RULE_INVALID_ACTION", "La acción de la regla no es válida.", 400)
        return RuleStatus(status)

    @staticmethod
    def _severity_for(triggered: bool, action: dict[str, Any], fallback: str) -> RuleSeverity:
        if not triggered:
            return RuleSeverity.SUCCESS
        severity = action.get("severity", fallback)
        if severity not in {item.value for item in RuleSeverity}:
            raise AppError("RULE_INVALID_ACTION", "La severidad de la regla no es válida.", 400)
        return RuleSeverity(severity)

    @staticmethod
    def _parse_decimal(value: Any) -> Decimal:
        if isinstance(value, float):
            raise AppError(
                "RULE_INVALID_VALUE", "Los valores numéricos deben ser string decimal.", 400
            )
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError) as exc:
            raise AppError("RULE_INVALID_VALUE", "El valor de la regla no es válido.", 400) from exc

    def _ensure_decimal(self, value: Any) -> Decimal:
        if not isinstance(value, Decimal):
            return self._parse_decimal(value)
        return value

    @staticmethod
    def _snapshot_value(value: Decimal | str) -> Decimal | str:
        return value if isinstance(value, str) else Decimal(str(value))

    def _reject_unsafe_tokens(self, value: Any) -> None:
        if isinstance(value, dict):
            for item in value.values():
                self._reject_unsafe_tokens(item)
            return
        if isinstance(value, list):
            for item in value:
                self._reject_unsafe_tokens(item)
            return
        if isinstance(value, str):
            lowered = value.lower()
            if any(token in lowered for token in UNSAFE_TOKENS):
                raise AppError(
                    "RULE_UNSAFE_EXPRESSION",
                    "La regla contiene una expresión no permitida.",
                    400,
                )
