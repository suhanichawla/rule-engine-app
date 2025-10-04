"""Application configuration."""

import os
from pathlib import Path


class Config:
    """Application configuration settings."""

    APP_NAME: str = "Rekord Rules Evaluator"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = """
    Rekord Rules Evaluator - A transparent decision-making platform for regulated entities.

    This service provides:
    * CRUD operations for rule management
    * Rule evaluation against JSON payloads
    * Clear PASS/FAIL results with detailed reasoning
    * Option to use predicates or expression for rule definition

    ## Supported Operators

    * `==` - Equals
    * `!=` - Not equals
    * `>` - Greater than
    * `>=` - Greater than or equal
    * `<` - Less than
    * `<=` - Less than or equal
    * `contains` - String/list contains (checks if value is in the field)
    * `not_contains` - String/list does not contain
    * `in` - Field value is in the provided list
    * `not_in` - Field value is not in the provided list

    ## Predicate Logic

    Multiple predicates in a rule are combined with **AND** logic by default.
    All predicates must pass for the rule to evaluate to its specified effect.

    ## Expression Logic

    Expression is a string that is parsed and evaluated to determine if the rule passes or fails.
    It supports complex logic and field-to-field comparisons. It also gets validated when creating a rule.
    If the validation fails, the rule will not be created.
    """

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8080",
        "http://ec2-13-61-145-69.eu-north-1.compute.amazonaws.com:8080",
        "*",  # Allow all origins for EC2 deployment
    ]

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RULES_FILE: str = str(DATA_DIR / "rules.json")

    @classmethod
    def ensure_data_directory(cls):
        """Ensure data directory exists."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)


config = Config()

