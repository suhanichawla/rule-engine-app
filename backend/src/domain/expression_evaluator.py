"""Expression evaluator for rule evaluation.

Evaluates parsed expression ASTs against JSON payloads.
"""

from typing import Any, Dict, List, Union

from domain.exceptions import MissingFieldException, TypeMismatchException, EvaluationException
from domain.expression_parser import BinaryOpNode, ComparisonNode


class ExpressionEvaluator:
    """Evaluates expression ASTs against payloads."""

    def __init__(self, payload: Dict[str, Any]):
        self.payload = payload

    def evaluate(self, node: Union[ComparisonNode, BinaryOpNode]) -> bool:
        """Evaluate an AST node against the payload.

        Args:
            node: The AST node to evaluate

        Returns:
            Boolean result of the evaluation

        Raises:
            MissingFieldException: If a required field is missing
            TypeMismatchException: If types don't match for comparison
            EvaluationException: If evaluation fails
        """
        if isinstance(node, ComparisonNode):
            return self._evaluate_comparison(node)
        elif isinstance(node, BinaryOpNode):
            return self._evaluate_binary_op(node)
        else:
            raise EvaluationException(f"Unknown node type: {type(node)}")

    def _evaluate_comparison(self, node: ComparisonNode) -> bool:
        """Evaluate a comparison node."""
        if node.field not in self.payload:
            raise MissingFieldException(node.field)

        actual_value = self.payload[node.field]

        if node.is_field_comparison:
            if node.value not in self.payload:
                raise MissingFieldException(node.value)
            expected_value = self.payload[node.value]
        else:
            expected_value = node.value

        operator = node.operator

        try:
            if operator == '==':
                return actual_value == expected_value

            elif operator == '!=':
                return actual_value != expected_value

            elif operator == '>':
                return actual_value > expected_value

            elif operator == '>=':
                return actual_value >= expected_value

            elif operator == '<':
                return actual_value < expected_value

            elif operator == '<=':
                return actual_value <= expected_value

            elif operator == 'contains':
                if isinstance(actual_value, str):
                    return expected_value in actual_value
                elif isinstance(actual_value, list):
                    return expected_value in actual_value
                else:
                    raise TypeMismatchException(
                        node.field,
                        "string or list",
                        type(actual_value).__name__
                    )

            elif operator == 'not_contains':
                if isinstance(actual_value, str):
                    return expected_value not in actual_value
                elif isinstance(actual_value, list):
                    return expected_value not in actual_value
                else:
                    raise TypeMismatchException(
                        node.field,
                        "string or list",
                        type(actual_value).__name__
                    )

            elif operator == 'in':
                if isinstance(expected_value, list):
                    return actual_value in expected_value
                else:
                    raise TypeMismatchException(
                        node.field,
                        "expected value to be a list",
                        type(expected_value).__name__
                    )

            elif operator == 'not_in':
                if isinstance(expected_value, list):
                    return actual_value not in expected_value
                else:
                    raise TypeMismatchException(
                        node.field,
                        "expected value to be a list",
                        type(expected_value).__name__
                    )

            else:
                raise EvaluationException(f"Unsupported operator: {operator}")

        except TypeError:
            raise TypeMismatchException(
                node.field,
                str(type(expected_value).__name__),
                str(type(actual_value).__name__)
            )

    def _evaluate_binary_op(self, node: BinaryOpNode) -> bool:
        """Evaluate a binary operation node (AND/OR)."""
        # Always evaluate both sides - we want answers to all predicates
        left_result = self.evaluate(node.left)
        right_result = self.evaluate(node.right)

        if node.operator == 'AND':
            return left_result and right_result
        elif node.operator == 'OR':
            return left_result or right_result
        else:
            raise EvaluationException(f"Unknown binary operator: {node.operator}")


def evaluate_expression(
    expression_ast: Union[ComparisonNode, BinaryOpNode],
    payload: Dict[str, Any]
) -> bool:
    """Evaluate an expression AST against a payload.

    Args:
        expression_ast: The parsed expression AST
        payload: The data to evaluate against

    Returns:
        Boolean result of the evaluation
    """
    evaluator = ExpressionEvaluator(payload)
    return evaluator.evaluate(expression_ast)


class DetailedExpressionEvaluator(ExpressionEvaluator):
    """Evaluator that tracks detailed results for each comparison."""

    def __init__(self, payload: Dict[str, Any]):
        super().__init__(payload)
        self.comparison_results: List[Dict[str, Any]] = []

    def evaluate(self, node: Union[ComparisonNode, BinaryOpNode]) -> bool:
        """Evaluate an AST node and track comparison results.

        Args:
            node: The AST node to evaluate

        Returns:
            Boolean result of the evaluation
        """
        if isinstance(node, ComparisonNode):
            return self._evaluate_comparison_with_tracking(node)
        elif isinstance(node, BinaryOpNode):
            return self._evaluate_binary_op(node)
        else:
            raise EvaluationException(f"Unknown node type: {type(node)}")

    def _evaluate_comparison_with_tracking(self, node: ComparisonNode) -> bool:
        """Evaluate a comparison node and track its result."""
        try:
            if node.field not in self.payload:
                raise MissingFieldException(node.field)

            actual_value = self.payload[node.field]

            if node.is_field_comparison:
                if node.value not in self.payload:
                    raise MissingFieldException(node.value)
                expected_value = self.payload[node.value]
            else:
                expected_value = node.value

            passed = self._perform_comparison(node, actual_value)

            # Track the result
            self.comparison_results.append({
                "field": node.field,
                "operator": node.operator,
                "expected": expected_value,
                "actual": actual_value,
                "passed": passed,
                "is_field_comparison": node.is_field_comparison,
                "compared_field": node.value if node.is_field_comparison else None
            })

            return passed

        except (MissingFieldException, TypeMismatchException) as e:
            # Track the error
            expected_value = None
            if node.is_field_comparison:
                expected_value = self.payload.get(node.value)
            else:
                expected_value = node.value

            self.comparison_results.append({
                "field": node.field,
                "operator": node.operator,
                "expected": expected_value,
                "actual": self.payload.get(node.field),
                "passed": False,
                "error": str(e),
                "is_field_comparison": node.is_field_comparison,
                "compared_field": node.value if node.is_field_comparison else None
            })
            raise

    def _perform_comparison(self, node: ComparisonNode, actual_value: Any) -> bool:
        """Perform the actual comparison operation."""
        if node.is_field_comparison:
            expected_value = self.payload[node.value]
        else:
            expected_value = node.value
        operator = node.operator

        try:
            if operator == '==':
                return actual_value == expected_value
            elif operator == '!=':
                return actual_value != expected_value
            elif operator == '>':
                return actual_value > expected_value
            elif operator == '>=':
                return actual_value >= expected_value
            elif operator == '<':
                return actual_value < expected_value
            elif operator == '<=':
                return actual_value <= expected_value
            elif operator == 'contains':
                if isinstance(actual_value, (str, list)):
                    return expected_value in actual_value
                else:
                    raise TypeMismatchException(
                        node.field,
                        "string or list",
                        type(actual_value).__name__
                    )
            elif operator == 'not_contains':
                if isinstance(actual_value, (str, list)):
                    return expected_value not in actual_value
                else:
                    raise TypeMismatchException(
                        node.field,
                        "string or list",
                        type(actual_value).__name__
                    )
            elif operator == 'in':
                if isinstance(expected_value, list):
                    return actual_value in expected_value
                else:
                    raise TypeMismatchException(
                        node.field,
                        "expected value to be a list",
                        type(expected_value).__name__
                    )
            elif operator == 'not_in':
                if isinstance(expected_value, list):
                    return actual_value not in expected_value
                else:
                    raise TypeMismatchException(
                        node.field,
                        "expected value to be a list",
                        type(expected_value).__name__
                    )
            else:
                raise EvaluationException(f"Unsupported operator: {operator}")

        except TypeError:
            raise TypeMismatchException(
                node.field,
                str(type(expected_value).__name__),
                str(type(actual_value).__name__)
            )

    def get_comparison_results(self) -> List[Dict[str, Any]]:
        """Get all tracked comparison results."""
        return self.comparison_results


def evaluate_expression_detailed(
    expression_ast: Union[ComparisonNode, BinaryOpNode],
    payload: Dict[str, Any]
) -> tuple[bool, List[Dict[str, Any]]]:
    """Evaluate an expression and return detailed comparison results.

    Args:
        expression_ast: The parsed expression AST
        payload: The data to evaluate against

    Returns:
        Tuple of (overall_result, list of comparison results)
    """
    evaluator = DetailedExpressionEvaluator(payload)
    try:
        result = evaluator.evaluate(expression_ast)
        return result, evaluator.get_comparison_results()
    except (MissingFieldException, TypeMismatchException, EvaluationException):
        # Return False with whatever results we collected
        return False, evaluator.get_comparison_results()

