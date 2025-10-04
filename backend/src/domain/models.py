"""Domain models representing core business entities."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID


class OperatorType(str, Enum):
    """Supported comparison operators."""
    EQUALS = "=="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN = "in"
    NOT_IN = "not_in"


class RuleEffect(str, Enum):
    """Rule evaluation result."""
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class Predicate:
    """A single condition to be evaluated."""
    field: str
    operator: OperatorType
    value: Any

    def to_dict(self) -> Dict[str, Any]:
        """Convert predicate to dictionary representation."""
        return {
            "field": self.field,
            "operator": self.operator.value,
            "value": self.value
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Predicate":
        """Create predicate from dictionary representation."""
        return Predicate(
            field=data["field"],
            operator=OperatorType(data["operator"]),
            value=data["value"]
        )


@dataclass
class Rule:
    """A rule with either predicates or an expression.

    Rules can be defined in two ways:
    1. Predicates: List of conditions with configurable logic (AND/OR)
    2. Expression: A boolean expression string supporting complex logic

    Examples:
        - Predicates (AND): predicates=[...], logical_operator="AND"
        - Predicates (OR): predicates=[...], logical_operator="OR"
        - Expression: expression="age >= 18 AND (country == 'USA' OR country == 'Canada')"
    """
    id: UUID
    name: str
    description: str
    predicates: Optional[List[Predicate]] = None
    expression: Optional[str] = None
    logical_operator: str = "AND"  # "AND" or "OR" for predicates

    def __post_init__(self):
        """Validate that either predicates or expression is provided."""
        if self.predicates is None and self.expression is None:
            raise ValueError("Rule must have either predicates or expression")
        if self.predicates is not None and self.expression is not None:
            raise ValueError("Rule cannot have both predicates and expression")
        if self.logical_operator not in ["AND", "OR"]:
            raise ValueError("logical_operator must be 'AND' or 'OR'")

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary representation."""
        result = {
            "id": str(self.id),
            "name": self.name,
            "description": self.description
        }

        if self.predicates is not None:
            result["predicates"] = [p.to_dict() for p in self.predicates]
            result["logical_operator"] = self.logical_operator

        if self.expression is not None:
            result["expression"] = self.expression

        return result

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Rule":
        """Create rule from dictionary representation."""
        predicates = None
        if "predicates" in data:
            predicates = [Predicate.from_dict(p) for p in data["predicates"]]

        expression = data.get("expression")
        logical_operator = data.get("logical_operator", "AND")

        return Rule(
            id=UUID(data["id"]) if isinstance(data["id"], str) else data["id"],
            name=data["name"],
            description=data["description"],
            predicates=predicates,
            expression=expression,
            logical_operator=logical_operator
        )


@dataclass
class EvaluationResult:
    """Result of evaluating a payload against a rule."""
    rule_id: UUID
    rule_name: str
    result: RuleEffect
    reason: str
    predicate_results: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluation result to dictionary representation."""
        return {
            "rule_id": str(self.rule_id),
            "rule_name": self.rule_name,
            "result": self.result.value,
            "reason": self.reason,
            "predicate_results": self.predicate_results
        }


@dataclass
class EvaluationResponse:
    """Overall evaluation response for a payload."""
    result: RuleEffect
    reasons: List[str]
    details: List[EvaluationResult]

    def to_dict(self) -> Dict[str, Any]:
        """Convert evaluation response to dictionary representation."""
        return {
            "result": self.result.value,
            "reasons": self.reasons,
            "details": [d.to_dict() for d in self.details]
        }

