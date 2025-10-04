"""FastAPI router definitions for rule management and evaluation."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from application.services import EvaluationService, RuleService
from domain.exceptions import (
    DomainException,
    RuleNotFoundException,
    RuleValidationException,
    EvaluationException
)


class PredicateRequest(BaseModel):
    """Request model for a predicate."""
    field: str = Field(..., description="The field name to evaluate")
    operator: str = Field(..., description="The comparison operator (==, >, >=, <, <=, contains, etc.)")
    value: Any = Field(..., description="The value to compare against")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "age",
                "operator": ">=",
                "value": 18
            }
        }


class RuleCreateRequest(BaseModel):
    """Request model for creating a rule.

    Rules can be defined in two ways:
    1. Predicates: List of conditions with configurable logic (AND/OR)
    2. Expression: Boolean expression string with complex logic

    You must provide either predicates OR expression, but not both.

    """
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    predicates: Optional[List[PredicateRequest]] = Field(None, description="List of predicates")
    logical_operator: str = Field("AND", description="Logical operator for predicates: 'AND' or 'OR' (default: AND)")
    expression: Optional[str] = Field(None, description="Boolean expression (e.g., 'age >= 18 AND (country == \"USA\" OR country == \"Canada\")')")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "name": "Age Verification",
                    "description": "Must be 18+ and have good credit",
                    "predicates": [
                        {"field": "age", "operator": ">=", "value": 18},
                        {"field": "credit_score", "operator": ">=", "value": 650}
                    ],
                    "logical_operator": "AND"
                },
                {
                    "name": "Flexible Eligibility",
                    "description": "Pass if 18+ OR from USA",
                    "predicates": [
                        {"field": "age", "operator": ">=", "value": 18},
                        {"field": "country", "operator": "==", "value": "USA"}
                    ],
                    "logical_operator": "OR"
                },
                {
                    "name": "Complex Eligibility",
                    "description": "Complex eligibility with nested logic",
                    "expression": "(age >= 18 AND credit_score > 700) OR country == 'USA'"
                }
            ]
        }


class RuleUpdateRequest(BaseModel):
    """Request model for updating a rule.

    You must provide either predicates OR expression, but not both.
    """
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    predicates: Optional[List[PredicateRequest]] = Field(None, description="List of predicates")
    logical_operator: str = Field("AND", description="Logical operator for predicates: 'AND' or 'OR'")
    expression: Optional[str] = Field(None, description="Boolean expression")


class RuleResponse(BaseModel):
    """Response model for a rule.
    """
    id: str
    name: str
    description: str
    predicates: Optional[List[Dict[str, Any]]] = None
    logical_operator: Optional[str] = None
    expression: Optional[str] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Age Verification",
                    "description": "Must be 18+ and have good credit",
                    "predicates": [
                        {"field": "age", "operator": ">=", "value": 18},
                        {"field": "credit_score", "operator": ">=", "value": 650}
                    ],
                    "logical_operator": "AND"
                },
                {
                    "id": "223e4567-e89b-12d3-a456-426614174000",
                    "name": "Flexible Eligibility",
                    "description": "Pass if 18+ OR from USA",
                    "predicates": [
                        {"field": "age", "operator": ">=", "value": 18},
                        {"field": "country", "operator": "==", "value": "USA"}
                    ],
                    "logical_operator": "OR",
                },
                {
                    "id": "323e4567-e89b-12d3-a456-426614174000",
                    "name": "Complex Eligibility",
                    "description": "Complex eligibility with nested logic",
                    "expression": "(age >= 18 AND credit_score > 700) OR country == 'USA'",
                }
            ]
        }


class EvaluateRequest(BaseModel):
    """Request model for evaluation."""
    payload: Dict[str, Any] = Field(..., description="The JSON payload to evaluate")
    rule_ids: List[str] = Field(..., description="List of rule IDs to evaluate against")

    class Config:
        json_schema_extra = {
            "example": {
                "payload": {
                    "age": 25,
                    "country": "USA",
                    "credit_score": 720
                },
                "rule_ids": ["123e4567-e89b-12d3-a456-426614174000"]
            }
        }


class EvaluateResponse(BaseModel):
    """Response model for evaluation."""
    result: str = Field(..., description="Overall result (PASS or FAIL)")
    reasons: List[str] = Field(..., description="List of reasons for each rule")
    details: List[Dict[str, Any]] = Field(..., description="Detailed evaluation results")

    class Config:
        json_schema_extra = {
            "example": {
                "result": "PASS",
                "reasons": [
                    "Age Verification: User meets minimum age requirement"
                ],
                "details": [
                    {
                        "rule_id": "123e4567-e89b-12d3-a456-426614174000",
                        "rule_name": "Age Verification",
                        "result": "PASS",
                        "reason": "User meets minimum age requirement",
                        "predicate_results": [
                            {
                                "field": "age",
                                "operator": ">=",
                                "expected": 18,
                                "actual": 25,
                                "passed": True
                            }
                        ]
                    }
                ]
            }
        }


def create_rule_router(rule_service: RuleService, evaluation_service: EvaluationService) -> APIRouter:
    """Create and configure the API router."""

    router = APIRouter(prefix="/api/v1", tags=["rules"])

    @router.get(
        "/rules",
        response_model=List[RuleResponse],
        summary="List all rules",
        description="Retrieve all available rules"
    )
    async def list_rules():
        """List all rules."""
        rules = rule_service.get_all_rules()
        return [RuleResponse(**rule.to_dict()) for rule in rules]

    @router.get(
        "/rules/{rule_id}",
        response_model=RuleResponse,
        summary="Get a rule by ID",
        description="Retrieve a specific rule by its UUID"
    )
    async def get_rule(rule_id: UUID):
        """Get a specific rule."""
        try:
            rule = rule_service.get_rule(rule_id)
            return RuleResponse(**rule.to_dict())
        except RuleNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    @router.post(
        "/rules",
        response_model=RuleResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Create a new rule",
        description="Create a new rule with predicates or expression",
        responses={
            201: {"description": "Rule created successfully"},
            400: {
                "description": "Validation error",
                "content": {
                    "application/json": {
                        "examples": {
                            "invalid_expression": {
                                "summary": "Invalid expression syntax",
                                "value": {
                                    "detail": "Invalid expression syntax: Unexpected character '@' at position 8. Context: ...invalid @ expressi..."
                                }
                            },
                            "single_equals": {
                                "summary": "Single equals operator",
                                "value": {
                                    "detail": "Invalid expression syntax: Single '=' operator at position 4. Use '==' for equality comparison. Context: ...age = 18..."
                                }
                            },
                            "missing_operator": {
                                "summary": "Missing operator",
                                "value": {
                                    "detail": "Invalid expression syntax: Expected operator at position 6"
                                }
                            },
                            "unmatched_paren": {
                                "summary": "Unmatched parenthesis",
                                "value": {
                                    "detail": "Invalid expression syntax: Expected ')' at position 32"
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    async def create_rule(request: RuleCreateRequest):
        """Create a new rule."""
        try:
            predicates_dict = None
            if request.predicates:
                predicates_dict = [p.model_dump() for p in request.predicates]

            rule = rule_service.create_rule(
                name=request.name,
                description=request.description,
                predicates=predicates_dict,
                expression=request.expression,
                logical_operator=request.logical_operator
            )
            return RuleResponse(**rule.to_dict())
        except RuleValidationException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @router.put(
        "/rules/{rule_id}",
        response_model=RuleResponse,
        summary="Update a rule",
        description="Update an existing rule by its UUID",
        responses={
            200: {"description": "Rule updated successfully"},
            400: {
                "description": "Validation error",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Invalid expression syntax: Expected value at position 5"
                        }
                    }
                }
            },
            404: {"description": "Rule not found"}
        }
    )
    async def update_rule(rule_id: UUID, request: RuleUpdateRequest):
        """Update an existing rule."""
        try:
            predicates_dict = None
            if request.predicates:
                predicates_dict = [p.model_dump() for p in request.predicates]

            rule = rule_service.update_rule(
                rule_id=rule_id,
                name=request.name,
                description=request.description,
                predicates=predicates_dict,
                expression=request.expression,
                logical_operator=request.logical_operator
            )
            return RuleResponse(**rule.to_dict())
        except RuleNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except RuleValidationException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @router.delete(
        "/rules/{rule_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        summary="Delete a rule",
        description="Delete a rule by its UUID"
    )
    async def delete_rule(rule_id: UUID):
        """Delete a rule."""
        try:
            rule_service.delete_rule(rule_id)
        except RuleNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    @router.post(
        "/evaluate",
        response_model=EvaluateResponse,
        summary="Evaluate a payload against rules",
        description="Evaluate a JSON payload against one or more rules and get PASS/FAIL result with detailed reasoning"
    )
    async def evaluate(request: EvaluateRequest):
        """Evaluate a payload against specified rules."""
        try:
            result = evaluation_service.evaluate(request.payload, request.rule_ids)
            return EvaluateResponse(**result.to_dict())
        except RuleNotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except EvaluationException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return router

