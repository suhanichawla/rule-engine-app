"""Comprehensive tests for expression evaluator."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from domain.expression_parser import parse_expression
from domain.expression_evaluator import evaluate_expression
from domain.exceptions import MissingFieldException, TypeMismatchException


class TestBasicEvaluation:
    """Test basic expression evaluation."""

    def test_equals_true(self):
        """Test equality that is true."""
        ast = parse_expression("age == 18")
        result = evaluate_expression(ast, {"age": 18})
        assert result is True

    def test_equals_false(self):
        """Test equality that is false."""
        ast = parse_expression("age == 18")
        result = evaluate_expression(ast, {"age": 25})
        assert result is False

    def test_not_equals(self):
        """Test not equals operator."""
        ast = parse_expression("status != 'banned'")
        assert evaluate_expression(ast, {"status": "active"}) is True
        assert evaluate_expression(ast, {"status": "banned"}) is False

    def test_greater_than(self):
        """Test greater than operator."""
        ast = parse_expression("age > 18")
        assert evaluate_expression(ast, {"age": 19}) is True
        assert evaluate_expression(ast, {"age": 18}) is False
        assert evaluate_expression(ast, {"age": 17}) is False

    def test_greater_than_or_equal(self):
        """Test greater than or equal operator."""
        ast = parse_expression("age >= 18")
        assert evaluate_expression(ast, {"age": 19}) is True
        assert evaluate_expression(ast, {"age": 18}) is True
        assert evaluate_expression(ast, {"age": 17}) is False

    def test_less_than(self):
        """Test less than operator."""
        ast = parse_expression("age < 65")
        assert evaluate_expression(ast, {"age": 64}) is True
        assert evaluate_expression(ast, {"age": 65}) is False
        assert evaluate_expression(ast, {"age": 66}) is False

    def test_less_than_or_equal(self):
        """Test less than or equal operator."""
        ast = parse_expression("age <= 65")
        assert evaluate_expression(ast, {"age": 64}) is True
        assert evaluate_expression(ast, {"age": 65}) is True
        assert evaluate_expression(ast, {"age": 66}) is False


class TestStringOperators:
    """Test string-specific operators."""

    def test_string_contains_true(self):
        """Test string contains - true case."""
        ast = parse_expression("tags contains 'premium'")
        result = evaluate_expression(ast, {"tags": "premium_gold"})
        assert result is True

    def test_string_contains_false(self):
        """Test string contains - false case."""
        ast = parse_expression("tags contains 'premium'")
        result = evaluate_expression(ast, {"tags": "basic"})
        assert result is False

    def test_string_not_contains_true(self):
        """Test string not contains - true case."""
        ast = parse_expression("notes not_contains 'fraud'")
        result = evaluate_expression(ast, {"notes": "clean record"})
        assert result is True

    def test_string_not_contains_false(self):
        """Test string not contains - false case."""
        ast = parse_expression("notes not_contains 'fraud'")
        result = evaluate_expression(ast, {"notes": "suspected fraud"})
        assert result is False

    def test_list_contains_true(self):
        """Test list contains - true case."""
        ast = parse_expression("tags contains 'vip'")
        result = evaluate_expression(ast, {"tags": ["premium", "vip", "gold"]})
        assert result is True

    def test_list_contains_false(self):
        """Test list contains - false case."""
        ast = parse_expression("tags contains 'vip'")
        result = evaluate_expression(ast, {"tags": ["premium", "gold"]})
        assert result is False


class TestMembershipOperators:
    """Test membership operators (in/not_in)."""

    def test_in_operator_true(self):
        """Test 'in' operator - value is in list."""
        ast = parse_expression("country in ['USA', 'Canada', 'UK']")
        assert evaluate_expression(ast, {"country": "USA"}) is True
        assert evaluate_expression(ast, {"country": "Canada"}) is True
        assert evaluate_expression(ast, {"country": "UK"}) is True

    def test_in_operator_false(self):
        """Test 'in' operator - value is not in list."""
        ast = parse_expression("country in ['USA', 'Canada']")
        assert evaluate_expression(ast, {"country": "France"}) is False

    def test_not_in_operator_true(self):
        """Test 'not_in' operator - value is not in list."""
        ast = parse_expression("status not_in ['banned', 'suspended']")
        assert evaluate_expression(ast, {"status": "active"}) is True

    def test_not_in_operator_false(self):
        """Test 'not_in' operator - value is in list."""
        ast = parse_expression("status not_in ['banned', 'suspended']")
        assert evaluate_expression(ast, {"status": "banned"}) is False

    def test_numeric_in_operator(self):
        """Test 'in' operator with numbers."""
        ast = parse_expression("score in [100, 200, 300]")
        assert evaluate_expression(ast, {"score": 200}) is True
        assert evaluate_expression(ast, {"score": 150}) is False


class TestBooleanLogic:
    """Test AND/OR boolean logic."""

    def test_and_both_true(self):
        """Test AND when both conditions are true."""
        ast = parse_expression("age >= 18 AND score > 100")
        result = evaluate_expression(ast, {"age": 25, "score": 150})
        assert result is True

    def test_and_first_false(self):
        """Test AND when first condition is false."""
        ast = parse_expression("age >= 18 AND score > 100")
        result = evaluate_expression(ast, {"age": 16, "score": 150})
        assert result is False

    def test_and_second_false(self):
        """Test AND when second condition is false."""
        ast = parse_expression("age >= 18 AND score > 100")
        result = evaluate_expression(ast, {"age": 25, "score": 50})
        assert result is False

    def test_and_both_false(self):
        """Test AND when both conditions are false."""
        ast = parse_expression("age >= 18 AND score > 100")
        result = evaluate_expression(ast, {"age": 16, "score": 50})
        assert result is False

    def test_or_both_true(self):
        """Test OR when both conditions are true."""
        ast = parse_expression("age >= 18 OR score > 100")
        result = evaluate_expression(ast, {"age": 25, "score": 150})
        assert result is True

    def test_or_first_true(self):
        """Test OR when first condition is true."""
        ast = parse_expression("age >= 18 OR score > 100")
        result = evaluate_expression(ast, {"age": 25, "score": 50})
        assert result is True

    def test_or_second_true(self):
        """Test OR when second condition is true."""
        ast = parse_expression("age >= 18 OR score > 100")
        result = evaluate_expression(ast, {"age": 16, "score": 150})
        assert result is True

    def test_or_both_false(self):
        """Test OR when both conditions are false."""
        ast = parse_expression("age >= 18 OR score > 100")
        result = evaluate_expression(ast, {"age": 16, "score": 50})
        assert result is False

    def test_multiple_and(self):
        """Test multiple AND conditions."""
        ast = parse_expression("a == 1 AND b == 2 AND c == 3")
        assert evaluate_expression(ast, {"a": 1, "b": 2, "c": 3}) is True
        assert evaluate_expression(ast, {"a": 1, "b": 2, "c": 4}) is False

    def test_multiple_or(self):
        """Test multiple OR conditions."""
        ast = parse_expression("a == 1 OR b == 2 OR c == 3")
        assert evaluate_expression(ast, {"a": 1, "b": 0, "c": 0}) is True
        assert evaluate_expression(ast, {"a": 0, "b": 2, "c": 0}) is True
        assert evaluate_expression(ast, {"a": 0, "b": 0, "c": 3}) is True
        assert evaluate_expression(ast, {"a": 0, "b": 0, "c": 0}) is False


class TestNestedLogic:
    """Test nested AND/OR logic with parentheses."""

    def test_nested_or_in_and(self):
        """Test (A OR B) AND C."""
        ast = parse_expression("(age >= 18 OR parental_consent == true) AND verified == true")

        # Age ok, verified
        assert evaluate_expression(ast, {"age": 25, "parental_consent": False, "verified": True}) is True

        # Consent ok, verified
        assert evaluate_expression(ast, {"age": 16, "parental_consent": True, "verified": True}) is True

        # Age ok, not verified
        assert evaluate_expression(ast, {"age": 25, "parental_consent": False, "verified": False}) is False

        # Neither ok
        assert evaluate_expression(ast, {"age": 16, "parental_consent": False, "verified": True}) is False

    def test_nested_and_in_or(self):
        """Test (A AND B) OR C."""
        ast = parse_expression("(age >= 21 AND credit_score >= 700) OR income > 100000")

        # Both age and credit ok
        assert evaluate_expression(ast, {"age": 25, "credit_score": 750, "income": 50000}) is True

        # Income ok
        assert evaluate_expression(ast, {"age": 19, "credit_score": 600, "income": 120000}) is True

        # Nothing ok
        assert evaluate_expression(ast, {"age": 19, "credit_score": 600, "income": 50000}) is False

    def test_deeply_nested(self):
        """Test deeply nested logic."""
        ast = parse_expression("((a == 1 AND b == 2) OR (c == 3 AND d == 4)) AND e == 5")

        # First branch + e
        assert evaluate_expression(ast, {"a": 1, "b": 2, "c": 0, "d": 0, "e": 5}) is True

        # Second branch + e
        assert evaluate_expression(ast, {"a": 0, "b": 0, "c": 3, "d": 4, "e": 5}) is True

        # Branch ok but not e
        assert evaluate_expression(ast, {"a": 1, "b": 2, "c": 0, "d": 0, "e": 6}) is False


class TestComplexRealWorld:
    """Test complex real-world scenarios."""

    def test_financial_eligibility(self):
        """Test complex financial eligibility."""
        ast = parse_expression("(age >= 21 AND credit_score >= 700 AND debt_ratio < 0.4) OR net_worth > 1000000")

        # Meets all criteria
        payload = {"age": 30, "credit_score": 750, "debt_ratio": 0.3, "net_worth": 500000}
        assert evaluate_expression(ast, payload) is True

        # High net worth only
        payload = {"age": 25, "credit_score": 600, "debt_ratio": 0.5, "net_worth": 2000000}
        assert evaluate_expression(ast, payload) is True

        # Fails all
        payload = {"age": 20, "credit_score": 600, "debt_ratio": 0.5, "net_worth": 100000}
        assert evaluate_expression(ast, payload) is False

    def test_geographic_eligibility(self):
        """Test geographic eligibility rules."""
        ast = parse_expression("(country in ['USA', 'Canada']) OR (country in ['UK', 'Germany'] AND credit_score >= 650)")

        # North America
        assert evaluate_expression(ast, {"country": "USA", "credit_score": 500}) is True

        # Europe with good credit
        assert evaluate_expression(ast, {"country": "UK", "credit_score": 700}) is True

        # Europe with bad credit
        assert evaluate_expression(ast, {"country": "UK", "credit_score": 600}) is False

        # Other country
        assert evaluate_expression(ast, {"country": "France", "credit_score": 800}) is False

    def test_fraud_detection(self):
        """Test fraud detection logic."""
        ast = parse_expression("login_attempts <= 3 AND ip_country == account_country AND notes not_contains 'fraud'")

        # All good
        payload = {"login_attempts": 2, "ip_country": "USA", "account_country": "USA", "notes": "normal activity"}
        assert evaluate_expression(ast, payload) is True

        # Too many attempts
        payload = {"login_attempts": 5, "ip_country": "USA", "account_country": "USA", "notes": "normal activity"}
        assert evaluate_expression(ast, payload) is False

        # IP mismatch
        payload = {"login_attempts": 2, "ip_country": "RU", "account_country": "USA", "notes": "normal activity"}
        assert evaluate_expression(ast, payload) is False

        # Fraud note
        payload = {"login_attempts": 2, "ip_country": "USA", "account_country": "USA", "notes": "potential fraud"}
        assert evaluate_expression(ast, payload) is False


class TestDataTypes:
    """Test different data types."""

    def test_integer_comparison(self):
        """Test integer comparisons."""
        ast = parse_expression("count > 10")
        assert evaluate_expression(ast, {"count": 15}) is True
        assert evaluate_expression(ast, {"count": 5}) is False

    def test_float_comparison(self):
        """Test float comparisons."""
        ast = parse_expression("price >= 99.99")
        assert evaluate_expression(ast, {"price": 100.00}) is True
        assert evaluate_expression(ast, {"price": 99.98}) is False

    def test_string_comparison(self):
        """Test string comparisons."""
        ast = parse_expression("status == 'active'")
        assert evaluate_expression(ast, {"status": "active"}) is True
        assert evaluate_expression(ast, {"status": "inactive"}) is False

    def test_boolean_comparison(self):
        """Test boolean comparisons."""
        ast = parse_expression("verified == true")
        assert evaluate_expression(ast, {"verified": True}) is True
        assert evaluate_expression(ast, {"verified": False}) is False

    def test_null_comparison(self):
        """Test null comparisons."""
        ast = parse_expression("optional_field == null")
        assert evaluate_expression(ast, {"optional_field": None}) is True
        assert evaluate_expression(ast, {"optional_field": "value"}) is False


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_missing_field(self):
        """Test that missing field raises exception."""
        ast = parse_expression("age >= 18")
        with pytest.raises(MissingFieldException):
            evaluate_expression(ast, {"name": "John"})

    def test_type_mismatch_comparison(self):
        """Test type mismatch in comparison."""
        ast = parse_expression("age > 18")
        with pytest.raises(TypeMismatchException):
            evaluate_expression(ast, {"age": "twenty"})

    def test_contains_on_non_string(self):
        """Test contains on non-string/list."""
        ast = parse_expression("value contains 'test'")
        with pytest.raises(TypeMismatchException):
            evaluate_expression(ast, {"value": 123})

    def test_in_on_non_list(self):
        """Test 'in' operator with non-list value."""
        ast = parse_expression("value in 'not_a_list'")
        with pytest.raises(TypeMismatchException):
            evaluate_expression(ast, {"value": "test"})


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_value(self):
        """Test comparisons with zero."""
        ast = parse_expression("balance >= 0")
        assert evaluate_expression(ast, {"balance": 0}) is True
        assert evaluate_expression(ast, {"balance": -1}) is False

    def test_negative_numbers(self):
        """Test negative number comparisons."""
        ast = parse_expression("temperature > -10")
        assert evaluate_expression(ast, {"temperature": -5}) is True
        assert evaluate_expression(ast, {"temperature": -15}) is False

    def test_empty_string(self):
        """Test empty string."""
        ast = parse_expression("value == ''")
        assert evaluate_expression(ast, {"value": ""}) is True
        assert evaluate_expression(ast, {"value": "text"}) is False

    def test_empty_list_in(self):
        """Test 'in' with empty list."""
        ast = parse_expression("value in []")
        assert evaluate_expression(ast, {"value": "anything"}) is False

    def test_single_element_list(self):
        """Test 'in' with single element list."""
        ast = parse_expression("value in [1]")
        assert evaluate_expression(ast, {"value": 1}) is True
        assert evaluate_expression(ast, {"value": 2}) is False

    def test_case_sensitive_strings(self):
        """Test that string comparison is case-sensitive."""
        ast = parse_expression("status == 'ACTIVE'")
        assert evaluate_expression(ast, {"status": "ACTIVE"}) is True
        assert evaluate_expression(ast, {"status": "active"}) is False


class TestNoShortCircuitEvaluation:
    """Test that ALL predicates are evaluated (no short-circuiting)."""

    def test_and_evaluates_both_sides(self):
        """Test that AND evaluates both sides even when left is false."""
        ast = parse_expression("exists == false AND other_field == 1")

        # Even though first condition (exists == false) fails when exists=True,
        # the second condition (other_field == 1) should still be evaluated
        result = evaluate_expression(ast, {"exists": True, "other_field": 1})
        assert result is False

        # This should fail if other_field is missing, proving it was evaluated
        with pytest.raises(MissingFieldException) as exc_info:
            evaluate_expression(ast, {"exists": True})
        assert "other_field" in str(exc_info.value)

    def test_or_evaluates_both_sides(self):
        """Test that OR evaluates both sides even when left is true."""
        ast = parse_expression("exists == true OR other_field == 1")

        # Even though first condition passes, second should still be evaluated
        result = evaluate_expression(ast, {"exists": True, "other_field": 1})
        assert result is True

        # This should fail if other_field is missing, proving it was evaluated
        with pytest.raises(MissingFieldException) as exc_info:
            evaluate_expression(ast, {"exists": True})
        assert "other_field" in str(exc_info.value)

    def test_detailed_evaluator_tracks_all_comparisons(self):
        """Test that detailed evaluator captures all comparison results."""
        from domain.expression_evaluator import evaluate_expression_detailed

        # Expression with OR where first condition passes
        ast = parse_expression("age >= 18 OR score > 100")
        result, comparisons = evaluate_expression_detailed(ast, {
            "age": 25,
            "score": 50
        })

        # Should pass (age >= 18 is true)
        assert result is True

        # Should have captured BOTH comparisons
        assert len(comparisons) == 2
        assert comparisons[0]["field"] == "age"
        assert comparisons[0]["passed"] is True
        assert comparisons[1]["field"] == "score"
        assert comparisons[1]["passed"] is False  # This was evaluated even though not needed!


class TestFieldToFieldComparisons:
    """Test field-to-field comparisons."""

    def test_field_equals_field_pass(self):
        """Test field-to-field equality that passes."""
        ast = parse_expression("password == confirm_password")
        result = evaluate_expression(ast, {"password": "secret123", "confirm_password": "secret123"})
        assert result is True

    def test_field_equals_field_fail(self):
        """Test field-to-field equality that fails."""
        ast = parse_expression("password == confirm_password")
        result = evaluate_expression(ast, {"password": "secret123", "confirm_password": "different"})
        assert result is False

    def test_field_greater_than_field_pass(self):
        """Test field-to-field greater than that passes."""
        ast = parse_expression("current_balance >= minimum_balance")
        result = evaluate_expression(ast, {"current_balance": 1000, "minimum_balance": 500})
        assert result is True

    def test_field_greater_than_field_fail(self):
        """Test field-to-field greater than that fails."""
        ast = parse_expression("current_balance >= minimum_balance")
        result = evaluate_expression(ast, {"current_balance": 400, "minimum_balance": 500})
        assert result is False

    def test_field_less_than_field_pass(self):
        """Test field-to-field less than that passes."""
        ast = parse_expression("start_date < end_date")
        result = evaluate_expression(ast, {"start_date": "2024-01-01", "end_date": "2024-12-31"})
        assert result is True

    def test_field_comparison_missing_first_field(self):
        """Test that missing left field raises error."""
        ast = parse_expression("password == confirm_password")
        with pytest.raises(MissingFieldException) as exc_info:
            evaluate_expression(ast, {"confirm_password": "secret123"})
        assert "password" in str(exc_info.value)

    def test_field_comparison_missing_second_field(self):
        """Test that missing right field raises error."""
        ast = parse_expression("password == confirm_password")
        with pytest.raises(MissingFieldException) as exc_info:
            evaluate_expression(ast, {"password": "secret123"})
        assert "confirm_password" in str(exc_info.value)

    def test_fraud_detection_with_field_comparison(self):
        """Test real-world fraud detection scenario."""
        ast = parse_expression("login_attempts <= 3 AND ip_country == account_country")

        # Should pass: login attempts OK and countries match
        result = evaluate_expression(ast, {
            "login_attempts": 2,
            "ip_country": "USA",
            "account_country": "USA"
        })
        assert result is True

        # Should fail: countries don't match
        result = evaluate_expression(ast, {
            "login_attempts": 2,
            "ip_country": "USA",
            "account_country": "RU"
        })
        assert result is False

        # Should fail: too many login attempts
        result = evaluate_expression(ast, {
            "login_attempts": 5,
            "ip_country": "USA",
            "account_country": "USA"
        })
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

