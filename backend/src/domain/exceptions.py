"""Domain-specific exceptions."""


class DomainException(Exception):
    """Base exception for domain errors."""
    pass


class RuleNotFoundException(DomainException):
    """Raised when a rule is not found."""
    def __init__(self, rule_id: str):
        self.rule_id = rule_id
        super().__init__(f"Rule with id '{rule_id}' not found")


class RuleValidationException(DomainException):
    """Raised when a rule fails validation."""
    pass


class EvaluationException(DomainException):
    """Raised when evaluation fails."""
    pass


class InvalidOperatorException(DomainException):
    """Raised when an unsupported operator is used."""
    def __init__(self, operator: str):
        self.operator = operator
        super().__init__(f"Operator '{operator}' is not supported")


class MissingFieldException(DomainException):
    """Raised when a required field is missing from payload."""
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"Required field '{field}' is missing from payload")


class TypeMismatchException(DomainException):
    """Raised when a field type doesn't match expected type."""
    def __init__(self, field: str, expected_type: str, actual_type: str):
        self.field = field
        self.expected_type = expected_type
        self.actual_type = actual_type
        super().__init__(
            f"Type mismatch for field '{field}': expected {expected_type}, got {actual_type}"
        )

