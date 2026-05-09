from app.modules.rules.domain.entities import RuleResult
from app.modules.rules.domain.enums import EvaluationStatus, RuleSeverity, RuleStatus


class RecommendationBuilder:
    def build(
        self,
        results: list[RuleResult],
        limits: list[dict[str, str]] | None = None,
    ) -> dict:
        triggered = [result for result in results if result.triggered]
        if any(result.status == RuleStatus.BLOCK for result in triggered):
            overall_status = EvaluationStatus.INSUFFICIENT_DATA
        elif any(
            result.status == RuleStatus.FAIL
            or result.severity
            in {RuleSeverity.CRITICAL, RuleSeverity.BLOCKING, RuleSeverity.HIGH_RISK}
            for result in triggered
        ):
            overall_status = EvaluationStatus.RISKY
        elif triggered:
            overall_status = EvaluationStatus.VIABLE_WITH_WARNINGS
        else:
            overall_status = EvaluationStatus.VIABLE

        score = self._score(triggered)
        alerts = [
            {
                "code": result.rule_code,
                "severity": result.severity.value,
                "message": result.message or "",
            }
            for result in triggered
            if result.message
        ]
        suggestions = []
        for result in triggered:
            for suggestion in result.suggestions:
                if suggestion not in suggestions:
                    suggestions.append(suggestion)
        headline = self._headline(overall_status)
        summary = (
            alerts[0]["message"]
            if alerts
            else "Tus indicadores evaluados están dentro del rango esperado."
        )
        return {
            "overall_status": overall_status,
            "score": score,
            "currency": "COP",
            "headline": headline,
            "summary": summary,
            "limits": limits or [],
            "alerts": alerts,
            "suggestions": suggestions[:3],
            "charts_data": {"budget_distribution": []},
        }

    @staticmethod
    def _score(triggered: list[RuleResult]) -> int:
        score = 100
        for result in triggered:
            if result.status == RuleStatus.BLOCK:
                score -= 35
            elif result.severity in {
                RuleSeverity.CRITICAL,
                RuleSeverity.BLOCKING,
                RuleSeverity.HIGH_RISK,
            }:
                score -= 25
            elif result.status == RuleStatus.WARN:
                score -= 10
            else:
                score -= 5
        return max(score, 0)

    @staticmethod
    def _headline(status: EvaluationStatus) -> str:
        return {
            EvaluationStatus.VIABLE: "Tu plan luce viable.",
            EvaluationStatus.VIABLE_WITH_WARNINGS: "Tu plan es viable, pero requiere ajustes.",
            EvaluationStatus.RISKY: "Tu plan tiene riesgos financieros importantes.",
            EvaluationStatus.NOT_VIABLE: "Tu plan no es recomendable en este momento.",
            EvaluationStatus.INSUFFICIENT_DATA: "Faltan datos para evaluar con seguridad.",
        }[status]
