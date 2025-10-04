"""Smart reason generator for predicate failures.

Automatically generates human-readable failure reasons based on:
- Data type (number, boolean, string, array)
- Operator used
- Expected vs actual values
"""

from typing import Any, Optional


class ReasonGenerator:
    """Generates contextual failure reasons for predicate evaluations."""

    @staticmethod
    def generate_reason(
        field: str,
        operator: str,
        expected_value: Any,
        actual_value: Any,
        passed: bool,
        is_field_comparison: bool = False,
        compared_field: Optional[str] = None
    ) -> str:
        """Generate a contextual reason for a predicate evaluation.

        Args:
            field: The field name being evaluated
            operator: The comparison operator
            expected_value: The expected value from the predicate (or value of compared field)
            actual_value: The actual value from the payload
            passed: Whether the predicate passed or failed
            is_field_comparison: Whether this is comparing two fields
            compared_field: Name of the field being compared against (if field comparison)

        Returns:
            A human-readable reason string
        """
        if passed:
            return ReasonGenerator._generate_pass_reason(field, operator, expected_value, actual_value, is_field_comparison, compared_field)
        else:
            return ReasonGenerator._generate_fail_reason(field, operator, expected_value, actual_value, is_field_comparison, compared_field)

    @staticmethod
    def _generate_fail_reason(
        field: str,
        operator: str,
        expected_value: Any,
        actual_value: Any,
        is_field_comparison: bool = False,
        compared_field: Optional[str] = None
    ) -> str:
        """Generate a failure reason based on data type and operator."""

        if is_field_comparison and compared_field:
            return ReasonGenerator._generate_field_comparison_fail_reason(
                field, operator, compared_field, actual_value, expected_value
            )

        # Handle different operators
        if operator == "==":
            return ReasonGenerator._reason_for_equals_fail(field, expected_value, actual_value)

        elif operator == "!=":
            return ReasonGenerator._reason_for_not_equals_fail(field, expected_value, actual_value)

        elif operator in [">", ">=", "<", "<="]:
            return ReasonGenerator._reason_for_comparison_fail(field, operator, expected_value, actual_value)

        elif operator == "contains":
            return ReasonGenerator._reason_for_contains_fail(field, expected_value, actual_value)

        elif operator == "not_contains":
            return ReasonGenerator._reason_for_not_contains_fail(field, expected_value, actual_value)

        elif operator == "in":
            return ReasonGenerator._reason_for_in_fail(field, expected_value, actual_value)

        elif operator == "not_in":
            return ReasonGenerator._reason_for_not_in_fail(field, expected_value, actual_value)

        else:
            return f"{field} failed {operator} check (expected: {expected_value}, actual: {actual_value})"

    @staticmethod
    def _generate_pass_reason(
        field: str,
        operator: str,
        expected_value: Any,
        actual_value: Any,
        is_field_comparison: bool = False,
        compared_field: Optional[str] = None
    ) -> str:
        """Generate a success reason (optional, can be used for detailed logging)."""
        if is_field_comparison and compared_field:
            return f"{field} {operator} {compared_field} check passed"
        return f"{field} passed {operator} check"

    @staticmethod
    def _generate_field_comparison_fail_reason(
        field1: str,
        operator: str,
        field2: str,
        value1: Any,
        value2: Any
    ) -> str:
        """Generate reason for failed field-to-field comparison."""
        operator_text = {
            "==": "should equal",
            "!=": "should not equal",
            ">": "should be greater than",
            ">=": "should be greater than or equal to",
            "<": "should be less than",
            "<=": "should be less than or equal to"
        }

        comparison = operator_text.get(operator, f"failed {operator} check with")

        if isinstance(value1, str):
            v1_str = f"'{value1}'"
        else:
            v1_str = str(value1)

        if isinstance(value2, str):
            v2_str = f"'{value2}'"
        else:
            v2_str = str(value2)

        return f"{field1} ({v1_str}) {comparison} {field2} ({v2_str})"

    @staticmethod
    def _reason_for_equals_fail(field: str, expected: Any, actual: Any) -> str:
        """Generate reason for failed == comparison."""
        if isinstance(expected, bool):
            return f"Expected {field} to be {str(expected).lower()} but was {str(actual).lower()}"
        elif isinstance(expected, str):
            return f"Expected {field} to be '{expected}' but was '{actual}'"
        elif isinstance(expected, (int, float)):
            return f"Expected {field} to equal {expected} but was {actual}"
        else:
            return f"Expected {field} to be {expected} but was {actual}"

    @staticmethod
    def _reason_for_not_equals_fail(field: str, expected: Any, actual: Any) -> str:
        """Generate reason for failed != comparison."""
        if isinstance(expected, bool):
            return f"Expected {field} to not be {str(expected).lower()} but it was"
        elif isinstance(expected, str):
            return f"Expected {field} to not be '{expected}' but it was"
        else:
            return f"Expected {field} to not equal {expected} but it did"

    @staticmethod
    def _reason_for_comparison_fail(field: str, operator: str, expected: Any, actual: Any) -> str:
        """Generate reason for failed numeric comparison."""
        operator_text = {
            ">": "greater than",
            ">=": "greater than or equal to",
            "<": "less than",
            "<=": "less than or equal to"
        }

        comparison = operator_text.get(operator, operator)

        # Provide context about why it failed
        if operator == ">" and actual <= expected:
            return f"{field} ({actual}) must be greater than {expected}"
        elif operator == ">=" and actual < expected:
            return f"{field} ({actual}) must be at least {expected}"
        elif operator == "<" and actual >= expected:
            return f"{field} ({actual}) must be less than {expected}"
        elif operator == "<=" and actual > expected:
            return f"{field} ({actual}) must be at most {expected}"

        return f"{field} ({actual}) is not {comparison} {expected}"

    @staticmethod
    def _reason_for_contains_fail(field: str, expected: Any, actual: Any) -> str:
        """Generate reason for failed contains check."""
        if isinstance(actual, str):
            return f"Expected {field} to contain '{expected}' but it doesn't (actual: '{actual}')"
        elif isinstance(actual, list):
            return f"Expected {field} to contain '{expected}' but it doesn't (actual: {actual})"
        else:
            return f"Expected {field} to contain '{expected}'"

    @staticmethod
    def _reason_for_not_contains_fail(field: str, expected: Any, actual: Any) -> str:
        """Generate reason for failed not_contains check."""
        if isinstance(actual, str):
            return f"Expected {field} to not contain '{expected}' but it does (actual: '{actual}')"
        elif isinstance(actual, list):
            return f"Expected {field} to not contain '{expected}' but it does (actual: {actual})"
        else:
            return f"Expected {field} to not contain '{expected}' but it does"

    @staticmethod
    def _reason_for_in_fail(field: str, expected: Any, actual: Any) -> str:
        """Generate reason for failed 'in' check."""
        if isinstance(expected, list):
            # Format the list nicely
            if len(expected) <= 3:
                expected_str = str(expected)
            else:
                expected_str = f"[{', '.join(repr(x) for x in expected[:3])}, ... and {len(expected) - 3} more]"

            return f"Expected {field} to be one of {expected_str} but was '{actual}'"
        else:
            return f"Expected {field} to be in {expected} but was '{actual}'"

    @staticmethod
    def _reason_for_not_in_fail(field: str, expected: Any, actual: Any) -> str:
        """Generate reason for failed 'not_in' check."""
        if isinstance(expected, list):
            if len(expected) <= 3:
                expected_str = str(expected)
            else:
                expected_str = f"[{', '.join(repr(x) for x in expected[:3])}, ... and {len(expected) - 3} more]"

            return f"Expected {field} to not be in {expected_str} but it was '{actual}'"
        else:
            return f"Expected {field} to not be in {expected} but it was '{actual}'"

    @staticmethod
    def generate_error_reason(field: str, error_message: str) -> str:
        """Generate reason for evaluation errors (missing field, type mismatch, etc.)."""
        return f"{field}: {error_message}"

