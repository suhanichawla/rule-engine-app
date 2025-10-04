"""Comprehensive tests for expression parser."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from domain.expression_parser import (
    ExpressionTokenizer,
    ExpressionParser,
    parse_expression,
    extract_fields_from_ast,
    ComparisonNode,
    BinaryOpNode
)


class TestExpressionTokenizer:
    """Test expression tokenization."""

    def test_simple_comparison(self):
        """Test tokenizing a simple comparison."""
        tokenizer = ExpressionTokenizer("age >= 18")
        tokens = tokenizer.tokenize()

        assert tokens[0].value == "age"
        assert tokens[1].value == ">="
        assert tokens[2].value == 18

    def test_string_values(self):
        """Test tokenizing string values."""
        tokenizer = ExpressionTokenizer("country == 'USA'")
        tokens = tokenizer.tokenize()

        assert tokens[0].value == "country"
        assert tokens[1].value == "=="
        assert tokens[2].value == "USA"

    def test_double_quotes(self):
        """Test tokenizing double-quoted strings."""
        tokenizer = ExpressionTokenizer('status == "active"')
        tokens = tokenizer.tokenize()

        assert tokens[2].value == "active"

    def test_boolean_operators(self):
        """Test tokenizing AND/OR operators."""
        tokenizer = ExpressionTokenizer("age >= 18 AND status == 'active'")
        tokens = tokenizer.tokenize()

        assert any(t.value == "AND" for t in tokens)

    def test_parentheses(self):
        """Test tokenizing parentheses."""
        tokenizer = ExpressionTokenizer("(age >= 18)")
        tokens = tokenizer.tokenize()

        assert tokens[0].value == "("
        assert tokens[4].value == ")"

    def test_array_values(self):
        """Test tokenizing array values."""
        tokenizer = ExpressionTokenizer("country in ['USA', 'Canada']")
        tokens = tokenizer.tokenize()

        assert tokens[2].value == ["USA", "Canada"]

    def test_numeric_array(self):
        """Test tokenizing numeric arrays."""
        tokenizer = ExpressionTokenizer("score in [100, 200, 300]")
        tokens = tokenizer.tokenize()

        assert tokens[2].value == [100, 200, 300]

    def test_float_values(self):
        """Test tokenizing float values."""
        tokenizer = ExpressionTokenizer("price >= 99.99")
        tokens = tokenizer.tokenize()

        assert tokens[2].value == 99.99

    def test_negative_numbers(self):
        """Test tokenizing negative numbers."""
        tokenizer = ExpressionTokenizer("balance > -100")
        tokens = tokenizer.tokenize()

        assert tokens[2].value == -100

    def test_boolean_values(self):
        """Test tokenizing boolean values."""
        tokenizer = ExpressionTokenizer("active == true")
        tokens = tokenizer.tokenize()

        assert tokens[2].value is True

    def test_null_values(self):
        """Test tokenizing null values."""
        tokenizer = ExpressionTokenizer("value == null")
        tokens = tokenizer.tokenize()

        assert tokens[2].value is None


class TestExpressionParser:
    """Test expression parsing."""

    def test_simple_comparison(self):
        """Test parsing a simple comparison."""
        ast = parse_expression("age >= 18")

        assert isinstance(ast, ComparisonNode)
        assert ast.field == "age"
        assert ast.operator == ">="
        assert ast.value == 18

    def test_and_expression(self):
        """Test parsing AND expression."""
        ast = parse_expression("age >= 18 AND score > 100")

        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "AND"
        assert isinstance(ast.left, ComparisonNode)
        assert isinstance(ast.right, ComparisonNode)

    def test_or_expression(self):
        """Test parsing OR expression."""
        ast = parse_expression("age >= 18 OR country == 'USA'")

        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "OR"

    def test_nested_and_or(self):
        """Test parsing nested AND/OR."""
        ast = parse_expression("age >= 18 AND (country == 'USA' OR country == 'Canada')")

        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "AND"
        assert isinstance(ast.right, BinaryOpNode)
        assert ast.right.operator == "OR"

    def test_multiple_and(self):
        """Test parsing multiple AND conditions."""
        ast = parse_expression("a == 1 AND b == 2 AND c == 3")

        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "AND"
        # Should be left-associative: ((a AND b) AND c)
        assert isinstance(ast.left, BinaryOpNode)

    def test_multiple_or(self):
        """Test parsing multiple OR conditions."""
        ast = parse_expression("a == 1 OR b == 2 OR c == 3")

        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "OR"

    def test_complex_nested(self):
        """Test parsing complex nested expression."""
        ast = parse_expression("(age >= 21 AND score >= 700) OR income > 100000")

        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "OR"
        assert isinstance(ast.left, BinaryOpNode)
        assert ast.left.operator == "AND"

    def test_operator_precedence(self):
        """Test that AND has higher precedence than OR."""
        # a OR b AND c should be parsed as: a OR (b AND c)
        ast = parse_expression("a == 1 OR b == 2 AND c == 3")

        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "OR"
        assert isinstance(ast.right, BinaryOpNode)
        assert ast.right.operator == "AND"

    def test_all_comparison_operators(self):
        """Test all comparison operators."""
        operators = ["==", "!=", ">", ">=", "<", "<=", "contains", "not_contains", "in", "not_in"]

        for op in operators:
            if op in ["in", "not_in"]:
                ast = parse_expression(f"value {op} [1, 2, 3]")
            else:
                ast = parse_expression(f"value {op} 10")
            assert isinstance(ast, ComparisonNode)
            assert ast.operator == op

    def test_invalid_syntax_missing_operator(self):
        """Test that invalid syntax raises error."""
        with pytest.raises(ValueError):
            parse_expression("age 18")

    def test_invalid_syntax_missing_value(self):
        """Test that missing value raises error."""
        with pytest.raises(ValueError):
            parse_expression("age >=")

    def test_invalid_syntax_single_equals(self):
        """Test that single = operator raises helpful error."""
        with pytest.raises(ValueError) as exc_info:
            parse_expression("age = 18")

        assert "Single '=' operator" in str(exc_info.value)
        assert "==" in str(exc_info.value)

    def test_invalid_syntax_unclosed_parenthesis(self):
        """Test that unclosed parenthesis raises error."""
        with pytest.raises(ValueError):
            parse_expression("(age >= 18")

    def test_empty_expression(self):
        """Test that empty expression raises error."""
        with pytest.raises(Exception):
            parse_expression("")


class TestComplexExpressions:
    """Test complex real-world expressions."""

    def test_financial_eligibility(self):
        """Test complex financial eligibility expression."""
        expr = "(age >= 21 AND credit_score >= 700 AND debt_ratio < 0.4) OR net_worth > 1000000"
        ast = parse_expression(expr)

        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "OR"

    def test_geographic_rules(self):
        """Test geographic eligibility with multiple countries."""
        expr = "country in ['USA', 'Canada', 'UK'] AND age >= 18"
        ast = parse_expression(expr)

        assert isinstance(ast, BinaryOpNode)

    def test_multi_tier_membership(self):
        """Test multi-tier membership logic."""
        expr = "(status == 'premium' AND years >= 5) OR status == 'vip' OR lifetime_value > 50000"
        ast = parse_expression(expr)

        assert isinstance(ast, BinaryOpNode)

    def test_fraud_detection(self):
        """Test fraud detection logic with field-to-field comparison."""
        expr = "login_attempts <= 3 AND ip_country == account_country AND notes not_contains 'fraud'"
        ast = parse_expression(expr)

        assert isinstance(ast, BinaryOpNode)

        # The middle comparison should be field-to-field
        # Navigate the AST: AND(AND(login_attempts<=3, ip_country==account_country), notes not_contains 'fraud')
        left_and = ast.left
        assert isinstance(left_and, BinaryOpNode)
        ip_country_comparison = left_and.right
        assert isinstance(ip_country_comparison, ComparisonNode)
        assert ip_country_comparison.field == "ip_country"
        assert ip_country_comparison.operator == "=="
        assert ip_country_comparison.value == "account_country"
        assert ip_country_comparison.is_field_comparison is True

    def test_deeply_nested(self):
        """Test deeply nested expression."""
        expr = "((a == 1 AND b == 2) OR (c == 3 AND d == 4)) AND (e == 5 OR f == 6)"
        ast = parse_expression(expr)

        assert isinstance(ast, BinaryOpNode)

    def test_age_with_exceptions(self):
        """Test age verification with parental consent exception."""
        expr = "age >= 21 OR (age >= 18 AND parental_consent == true)"
        ast = parse_expression(expr)

        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "OR"

    def test_regional_credit_requirements(self):
        """Test regional rules with credit requirements."""
        expr = "(country in ['USA', 'Canada']) OR (country in ['UK', 'Germany'] AND credit_score >= 650)"
        ast = parse_expression(expr)

        assert isinstance(ast, BinaryOpNode)

    def test_string_operations(self):
        """Test string containment operations."""
        expr = "tags contains 'premium' AND notes not_contains 'fraud'"
        ast = parse_expression(expr)

        assert isinstance(ast, BinaryOpNode)

    def test_mixed_types(self):
        """Test expression with mixed data types."""
        expr = "age >= 18 AND active == true AND status in ['active', 'pending'] AND balance > 0.0"
        ast = parse_expression(expr)

        assert isinstance(ast, BinaryOpNode)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_character_field_name(self):
        """Test single character field names."""
        ast = parse_expression("a >= 1")
        assert ast.field == "a"

    def test_field_with_underscores(self):
        """Test field names with underscores."""
        ast = parse_expression("annual_income >= 50000")
        assert ast.field == "annual_income"

    def test_field_with_numbers(self):
        """Test field names with numbers."""
        ast = parse_expression("account_id_123 == 456")
        assert ast.field == "account_id_123"

    def test_zero_value(self):
        """Test comparison with zero."""
        ast = parse_expression("balance >= 0")
        assert ast.value == 0

    def test_very_large_number(self):
        """Test very large numbers."""
        ast = parse_expression("value >= 999999999")
        assert ast.value == 999999999

    def test_very_small_decimal(self):
        """Test very small decimal numbers."""
        ast = parse_expression("rate >= 0.001")
        assert ast.value == 0.001

    def test_empty_string(self):
        """Test empty string value."""
        ast = parse_expression("value == ''")
        assert ast.value == ""

    def test_string_with_spaces(self):
        """Test string with spaces."""
        ast = parse_expression("name == 'John Doe'")
        assert ast.value == "John Doe"

    def test_empty_array(self):
        """Test empty array."""
        ast = parse_expression("value in []")
        assert ast.value == []

    def test_single_element_array(self):
        """Test single element array."""
        ast = parse_expression("value in [1]")
        assert ast.value == [1]

    def test_whitespace_tolerance(self):
        """Test that extra whitespace is handled."""
        expr1 = "age>=18"
        expr2 = "age  >=  18"
        expr3 = "  age >= 18  "

        ast1 = parse_expression(expr1)
        ast2 = parse_expression(expr2)
        ast3 = parse_expression(expr3)

        # All should parse to the same structure
        assert ast1.field == ast2.field == ast3.field == "age"
        assert ast1.value == ast2.value == ast3.value == 18

    def test_field_names_containing_operator_keywords(self):
        """Test field names that contain operator keywords like 'in', 'contains', 'not_in'."""
        ast1 = parse_expression("income > 100000")
        assert ast1.field == "income"
        assert ast1.operator == ">"
        assert ast1.value == 100000

        ast2 = parse_expression("im_not_in_class == false")
        assert ast2.field == "im_not_in_class"
        assert ast2.operator == "=="
        assert ast2.value is False

        ast3 = parse_expression("container > 10")
        assert ast3.field == "container"
        assert ast3.operator == ">"
        assert ast3.value == 10

        ast4 = parse_expression("insurance_type == 'premium'")
        assert ast4.field == "insurance_type"
        assert ast4.operator == "=="
        assert ast4.value == "premium"

    def test_complex_expression_with_operator_keyword_fields(self):
        """Test complex expression with multiple field names containing operator keywords."""
        expr = "(age >= 21 AND score > 700) OR income > 100000 AND im_not_in_class==false and greeting in ['hi', 'bye']"
        ast = parse_expression(expr)

        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "OR"

        assert isinstance(ast.left, BinaryOpNode)

        # Right side: income > 100000 AND im_not_in_class==false AND greeting in ['hi', 'bye']
        # (AND has higher precedence than OR)
        assert isinstance(ast.right, BinaryOpNode)

    def test_extract_fields_from_simple_expression(self):
        """Test extracting field names from a simple comparison."""
        ast = parse_expression("age >= 18")
        fields = extract_fields_from_ast(ast)
        assert fields == ["age"]

    def test_extract_fields_from_and_expression(self):
        """Test extracting field names from AND expression."""
        ast = parse_expression("age >= 18 AND score > 100")
        fields = extract_fields_from_ast(ast)
        assert set(fields) == {"age", "score"}

    def test_extract_fields_from_complex_expression(self):
        """Test extracting all field names from complex expression."""
        expr = "(age >= 21 AND score > 700) OR income > 100000 AND im_not_in_class==false and greeting in ['hi', 'bye']"
        ast = parse_expression(expr)
        fields = extract_fields_from_ast(ast)

        # Should extract all 5 unique field names
        expected_fields = {"age", "score", "income", "im_not_in_class", "greeting"}
        assert set(fields) == expected_fields

    def test_extract_fields_with_duplicates(self):
        """Test that duplicate field names are returned only once."""
        ast = parse_expression("age >= 18 AND age <= 65")
        fields = extract_fields_from_ast(ast)
        assert fields == ["age"]

    def test_field_to_field_comparison_simple(self):
        """Test parsing simple field-to-field comparison."""
        expr = "password == confirm_password"
        ast = parse_expression(expr)

        assert isinstance(ast, ComparisonNode)
        assert ast.field == "password"
        assert ast.operator == "=="
        assert ast.value == "confirm_password"
        assert ast.is_field_comparison is True

    def test_field_to_field_comparison_numeric(self):
        """Test field-to-field comparison with numeric operators."""
        expr = "current_balance >= minimum_balance"
        ast = parse_expression(expr)

        assert isinstance(ast, ComparisonNode)
        assert ast.field == "current_balance"
        assert ast.operator == ">="
        assert ast.value == "minimum_balance"
        assert ast.is_field_comparison is True

    def test_field_to_field_comparison_in_expression(self):
        """Test field-to-field comparison within complex expression."""
        expr = "(start_date < end_date) AND status == 'active'"
        ast = parse_expression(expr)

        assert isinstance(ast, BinaryOpNode)
        assert ast.operator == "AND"

        # Left side: field-to-field
        left = ast.left
        assert isinstance(left, ComparisonNode)
        assert left.field == "start_date"
        assert left.operator == "<"
        assert left.value == "end_date"
        assert left.is_field_comparison is True

        # Right side: field-to-literal
        right = ast.right
        assert isinstance(right, ComparisonNode)
        assert right.field == "status"
        assert right.value == "active"
        assert right.is_field_comparison is False

    def test_extract_fields_from_field_comparison(self):
        """Test that extract_fields includes both fields in field-to-field comparison."""
        expr = "password == confirm_password"
        ast = parse_expression(expr)
        fields = extract_fields_from_ast(ast)

        assert len(fields) == 2
        assert "password" in fields
        assert "confirm_password" in fields

    def test_extract_fields_from_complex_with_field_comparison(self):
        """Test field extraction from complex expression with field comparisons."""
        expr = "ip_country == account_country AND login_attempts <= 3"
        ast = parse_expression(expr)
        fields = extract_fields_from_ast(ast)

        assert len(fields) == 3
        assert "ip_country" in fields
        assert "account_country" in fields
        assert "login_attempts" in fields


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

