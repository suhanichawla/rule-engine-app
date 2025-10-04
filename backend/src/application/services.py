"""Application services implementing business use cases."""

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from application.ports import RuleRepository
from domain.exceptions import (
    EvaluationException,
    MissingFieldException,
    RuleNotFoundException,
    RuleValidationException,
    TypeMismatchException
)
from domain.expression_evaluator import evaluate_expression_detailed
from domain.expression_parser import parse_expression, extract_fields_from_ast
from domain.models import (
    EvaluationResponse,
    EvaluationResult,
    OperatorType,
    Predicate,
    Rule,
    RuleEffect
)
from domain.reason_generator import ReasonGenerator

logger = logging.getLogger(__name__)


class RuleService:
    """Service for managing rule definitions."""

    def __init__(self, repository: RuleRepository):
        self.repository = repository

    def get_all_rules(self) -> List[Rule]:
        """Retrieve all rules."""
        return self.repository.get_all()

    def get_rule(self, rule_id: UUID) -> Rule:
        """Retrieve a specific rule by ID."""
        rule = self.repository.get_by_id(rule_id)
        if not rule:
            raise RuleNotFoundException(str(rule_id))
        return rule

    def create_rule(
        self,
        name: str,
        description: str,
        predicates: Optional[List[Dict[str, Any]]] = None,
        expression: Optional[str] = None,
        logical_operator: str = "AND"
    ) -> Rule:
        """Create a new rule with either predicates or expression.

        """
        self._validate_rule_data(name, predicates, expression, logical_operator)

        predicate_objects = None
        if predicates:
            predicate_objects = [Predicate.from_dict(p) for p in predicates]

        rule = Rule(
            id=uuid4(),
            name=name,
            description=description,
            predicates=predicate_objects,
            expression=expression,
            logical_operator=logical_operator
        )

        return self.repository.create(rule)

    def update_rule(
        self,
        rule_id: UUID,
        name: str,
        description: str,
        predicates: Optional[List[Dict[str, Any]]] = None,
        expression: Optional[str] = None,
        logical_operator: str = "AND"
    ) -> Rule:
        """Update an existing rule.

        All rules default to PASS effect. Failure reasons are auto-generated.
        """
        existing_rule = self.repository.get_by_id(rule_id)
        if not existing_rule:
            raise RuleNotFoundException(str(rule_id))

        self._validate_rule_data(name, predicates, expression, logical_operator)

        predicate_objects = None
        if predicates:
            predicate_objects = [Predicate.from_dict(p) for p in predicates]

        updated_rule = Rule(
            id=rule_id,
            name=name,
            description=description,
            predicates=predicate_objects,
            expression=expression,
            logical_operator=logical_operator
        )

        return self.repository.update(updated_rule)

    def delete_rule(self, rule_id: UUID) -> bool:
        """Delete a rule."""
        deleted = self.repository.delete(rule_id)
        if not deleted:
            raise RuleNotFoundException(str(rule_id))
        return deleted

    def _validate_rule_data(
        self,
        name: str,
        predicates: Optional[List[Dict[str, Any]]] = None,
        expression: Optional[str] = None,
        logical_operator: str = "AND"
    ) -> None:
        """Validate rule data."""
        if not name or not name.strip():
            raise RuleValidationException("Rule name cannot be empty")

        # Must have either predicates or expression
        if predicates is None and expression is None:
            raise RuleValidationException("Rule must have either predicates or expression")

        if predicates is not None and expression is not None:
            raise RuleValidationException("Rule cannot have both predicates and expression")

        if logical_operator not in ["AND", "OR"]:
            raise RuleValidationException(f"logical_operator must be 'AND' or 'OR', got: {logical_operator}")

        if expression is not None:
            try:
                parse_expression(expression)
            except ValueError as e:
                raise RuleValidationException(f"Invalid expression syntax: {str(e)}")
            except Exception as e:
                raise RuleValidationException(f"Failed to parse expression: {str(e)}")

        if predicates is not None:
            if len(predicates) == 0:
                raise RuleValidationException("Rule must have at least one predicate")

            for predicate in predicates:
                if "field" not in predicate or "operator" not in predicate or "value" not in predicate:
                    raise RuleValidationException("Each predicate must have field, operator, and value")

                try:
                    OperatorType(predicate["operator"])
                except ValueError:
                    raise RuleValidationException(f"Invalid operator: {predicate['operator']}")

        if expression is not None:
            if not expression.strip():
                raise RuleValidationException("Expression cannot be empty")

            try:
                # Parse the expression to validate syntax
                parse_expression(expression)
            except Exception as e:
                raise RuleValidationException(f"Invalid expression syntax: {str(e)}")


class EvaluationService:
    """Service for evaluating payloads against rules."""

    def __init__(self, repository: RuleRepository):
        self.repository = repository

    def evaluate(self, payload: Dict[str, Any], rule_ids: List[str]) -> EvaluationResponse:
        """
        Evaluate a payload against specified rules.

        Args:
            payload: The JSON payload to evaluate
            rule_ids: List of rule IDs to evaluate against

        Returns:
            EvaluationResponse with overall result and detailed reasons
        """
        if not rule_ids:
            raise EvaluationException("At least one rule_id must be provided")

        rules_to_evaluate = []
        for rule_id_str in rule_ids:
            try:
                rule_id = UUID(rule_id_str)
            except ValueError:
                raise EvaluationException(f"Invalid UUID format: {rule_id_str}")

            rule = self.repository.get_by_id(rule_id)
            if not rule:
                raise RuleNotFoundException(rule_id_str)
            rules_to_evaluate.append(rule)

        evaluation_results = []
        all_passed = True
        reasons = []

        for rule in rules_to_evaluate:
            result = self._evaluate_rule(rule, payload)
            evaluation_results.append(result)

            if result.result == RuleEffect.FAIL:
                all_passed = False

            reasons.append(f"{rule.name}: {result.reason}")

        overall_result = RuleEffect.PASS if all_passed else RuleEffect.FAIL

        return EvaluationResponse(
            result=overall_result,
            reasons=reasons,
            details=evaluation_results
        )

    def _evaluate_rule(self, rule: Rule, payload: Dict[str, Any]) -> EvaluationResult:
        """Evaluate a single rule against the payload."""
        if rule.expression:
            return self._evaluate_expression_rule(rule, payload)

        return self._evaluate_predicate_rule(rule, payload)

    def _evaluate_expression_rule(self, rule: Rule, payload: Dict[str, Any]) -> EvaluationResult:
        """Evaluate a rule with an expression."""
        try:
            expression_ast = parse_expression(rule.expression)

            # Check that all fields referenced in the expression exist in the payload
            required_fields = extract_fields_from_ast(expression_ast)
            missing_fields = [field for field in required_fields if field not in payload]

            if missing_fields:
                missing_fields_str = ", ".join(missing_fields)
                return EvaluationResult(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    result=RuleEffect.FAIL,
                    reason=f"Missing required fields: {missing_fields_str}",
                    predicate_results=[{
                        "error": f"Missing required fields: {missing_fields_str}",
                        "passed": False
                    }]
                )

            passed, comparison_results = evaluate_expression_detailed(expression_ast, payload)

            # Generate smart reasons for each comparison
            predicate_results = []
            failed_reasons = []

            for comp_result in comparison_results:
                # Check if there's an error
                if "error" in comp_result:
                    reason = ReasonGenerator.generate_error_reason(
                        comp_result["field"],
                        comp_result["error"]
                    )
                else:
                    reason = ReasonGenerator.generate_reason(
                        field=comp_result["field"],
                        operator=comp_result["operator"],
                        expected_value=comp_result["expected"],
                        actual_value=comp_result["actual"],
                        passed=comp_result["passed"],
                        is_field_comparison=comp_result.get("is_field_comparison", False),
                        compared_field=comp_result.get("compared_field")
                    )

                predicate_results.append({
                    "field": comp_result["field"],
                    "operator": comp_result["operator"],
                    "expected": comp_result["expected"],
                    "actual": comp_result["actual"],
                    "passed": comp_result["passed"],
                    "reason": reason,
                    "error": comp_result.get("error")
                })

                if not comp_result["passed"]:
                    failed_reasons.append(reason)

            result_effect = RuleEffect.PASS if passed else RuleEffect.FAIL

            # Use smart reasons for failures, generate pass reason dynamically
            if passed:
                result_reason = f"{rule.name} passed all conditions"
            else:
                if failed_reasons:
                    if len(failed_reasons) == 1:
                        result_reason = failed_reasons[0]
                    else:
                        result_reason = "; ".join(failed_reasons)
                else:
                    result_reason = f"Rule {rule.name} failed"

            return EvaluationResult(
                rule_id=rule.id,
                rule_name=rule.name,
                result=result_effect,
                reason=result_reason,
                predicate_results=predicate_results
            )
        except (MissingFieldException, TypeMismatchException, EvaluationException) as e:
            return EvaluationResult(
                rule_id=rule.id,
                rule_name=rule.name,
                result=RuleEffect.FAIL,
                reason=str(e),
                predicate_results=[{
                    "expression": rule.expression,
                    "error": str(e),
                    "passed": False
                }]
            )

    def _evaluate_predicate_rule(self, rule: Rule, payload: Dict[str, Any]) -> EvaluationResult:
        """Evaluate a rule with predicates."""
        predicate_results = []
        passed_count = 0
        failed_count = 0
        failed_predicate_reasons = []

        for predicate in rule.predicates:
            try:
                passed = self._evaluate_predicate(predicate, payload)
                actual_value = payload.get(predicate.field)

                # Auto-generate smart reason
                reason = ReasonGenerator.generate_reason(
                    field=predicate.field,
                    operator=predicate.operator.value,
                    expected_value=predicate.value,
                    actual_value=actual_value,
                    passed=passed
                )

                predicate_results.append({
                    "field": predicate.field,
                    "operator": predicate.operator.value,
                    "expected": predicate.value,
                    "actual": actual_value,
                    "passed": passed,
                    "reason": reason
                })

                if passed:
                    passed_count += 1
                else:
                    failed_count += 1
                    failed_predicate_reasons.append(reason)

            except (MissingFieldException, TypeMismatchException) as e:
                # Auto-generate error reason
                error_reason = ReasonGenerator.generate_error_reason(
                    predicate.field, str(e)
                )

                predicate_results.append({
                    "field": predicate.field,
                    "operator": predicate.operator.value,
                    "expected": predicate.value,
                    "error": str(e),
                    "passed": False,
                    "reason": error_reason
                })
                failed_count += 1
                failed_predicate_reasons.append(error_reason)

        # Determine if rule passed based on logical operator
        if rule.logical_operator == "AND":
            # All predicates must pass
            rule_passed = failed_count == 0
        else:  # OR
            # At least one predicate must pass
            rule_passed = passed_count > 0

        result_effect = RuleEffect.PASS if rule_passed else RuleEffect.FAIL

        # Use specific predicate reason(s) if available, generate pass reason dynamically
        if rule_passed:
            result_reason = f"{rule.name} passed all conditions"
        else:
            if failed_predicate_reasons:
                # Return the specific predicate reason(s)
                if len(failed_predicate_reasons) == 1:
                    result_reason = failed_predicate_reasons[0]
                else:
                    result_reason = "; ".join(failed_predicate_reasons)
            else:
                result_reason = f"Rule {rule.name} failed"

        return EvaluationResult(
            rule_id=rule.id,
            rule_name=rule.name,
            result=result_effect,
            reason=result_reason,
            predicate_results=predicate_results
        )

    def _evaluate_predicate(self, predicate: Predicate, payload: Dict[str, Any]) -> bool:
        """Evaluate a single predicate against the payload."""
        if predicate.field not in payload:
            raise MissingFieldException(predicate.field)

        actual_value = payload[predicate.field]
        expected_value = predicate.value

        try:
            if predicate.operator == OperatorType.EQUALS:
                return actual_value == expected_value

            elif predicate.operator == OperatorType.NOT_EQUALS:
                return actual_value != expected_value

            elif predicate.operator == OperatorType.GREATER_THAN:
                return actual_value > expected_value

            elif predicate.operator == OperatorType.GREATER_THAN_OR_EQUAL:
                return actual_value >= expected_value

            elif predicate.operator == OperatorType.LESS_THAN:
                return actual_value < expected_value

            elif predicate.operator == OperatorType.LESS_THAN_OR_EQUAL:
                return actual_value <= expected_value

            elif predicate.operator == OperatorType.CONTAINS:
                if isinstance(actual_value, str):
                    return expected_value in actual_value
                elif isinstance(actual_value, list):
                    return expected_value in actual_value
                else:
                    raise TypeMismatchException(
                        predicate.field,
                        "string or list",
                        type(actual_value).__name__
                    )

            elif predicate.operator == OperatorType.NOT_CONTAINS:
                if isinstance(actual_value, str):
                    return expected_value not in actual_value
                elif isinstance(actual_value, list):
                    return expected_value not in actual_value
                else:
                    raise TypeMismatchException(
                        predicate.field,
                        "string or list",
                        type(actual_value).__name__
                    )

            elif predicate.operator == OperatorType.IN:
                if isinstance(expected_value, list):
                    return actual_value in expected_value
                else:
                    raise TypeMismatchException(
                        predicate.field,
                        "expected value to be a list",
                        type(expected_value).__name__
                    )

            elif predicate.operator == OperatorType.NOT_IN:
                if isinstance(expected_value, list):
                    return actual_value not in expected_value
                else:
                    raise TypeMismatchException(
                        predicate.field,
                        "expected value to be a list",
                        type(expected_value).__name__
                    )

            else:
                raise EvaluationException(f"Unsupported operator: {predicate.operator}")

        except TypeError:
            raise TypeMismatchException(
                predicate.field,
                str(type(expected_value).__name__),
                str(type(actual_value).__name__)
            )

