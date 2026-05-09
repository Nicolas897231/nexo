from enum import StrEnum


class GoalScope(StrEnum):
    GENERAL = "general"
    SAVING = "saving"
    HOUSING = "housing"
    CAR = "car"
    TRAVEL = "travel"


class RuleStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    BLOCK = "BLOCK"
    INFO = "INFO"


class RuleSeverity(StrEnum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    BLOCKING = "BLOCKING"
    HIGH_RISK = "HIGH_RISK"


class EvaluationStatus(StrEnum):
    VIABLE = "VIABLE"
    VIABLE_WITH_WARNINGS = "VIABLE_WITH_WARNINGS"
    RISKY = "RISKY"
    NOT_VIABLE = "NOT_VIABLE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
