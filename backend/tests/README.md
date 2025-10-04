# Test Suite

Comprehensive test suite for the Rekord Rules Evaluator expression language.

## Running Tests

### Install test dependencies:
```bash
pip install -r requirements-test.txt
```

### Run all tests:
```bash
cd backend
pytest tests/ -v
```

### Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run specific test file:
```bash
pytest tests/test_expression_parser.py -v
pytest tests/test_expression_evaluator.py -v
```

### Run specific test class:
```bash
pytest tests/test_expression_parser.py::TestExpressionParser -v
```

### Run specific test:
```bash
pytest tests/test_expression_parser.py::TestExpressionParser::test_simple_comparison -v
```

## Test Coverage

### Expression Parser Tests (`test_expression_parser.py`)
- ✅ Tokenization of all data types
- ✅ Parsing of all operators
- ✅ AND/OR logic
- ✅ Parentheses and nesting
- ✅ Operator precedence
- ✅ Error handling
- ✅ Complex real-world expressions
- ✅ Edge cases

### Expression Evaluator Tests (`test_expression_evaluator.py`)
- ✅ All comparison operators (==, !=, >, >=, <, <=)
- ✅ String operators (contains, not_contains)
- ✅ Membership operators (in, not_in)
- ✅ Boolean logic (AND, OR)
- ✅ Nested expressions
- ✅ Complex real-world scenarios
- ✅ All data types (int, float, string, boolean, null)
- ✅ Error handling
- ✅ Short-circuit evaluation
- ✅ Edge cases

## Test Statistics

- **Total Tests**: 100+
- **Test Files**: 2
- **Test Classes**: 20+
- **Code Coverage**: Aiming for 100% of expression parser/evaluator

## What's Tested

### Operators
- ✅ `==` (equals)
- ✅ `!=` (not equals)
- ✅ `>` (greater than)
- ✅ `>=` (greater than or equal)
- ✅ `<` (less than)
- ✅ `<=` (less than or equal)
- ✅ `contains` (string/list contains)
- ✅ `not_contains` (string/list not contains)
- ✅ `in` (value in list)
- ✅ `not_in` (value not in list)

### Boolean Logic
- ✅ AND (both conditions must be true)
- ✅ OR (at least one condition must be true)
- ✅ Parentheses for grouping
- ✅ Nested expressions
- ✅ Operator precedence (AND before OR)
- ✅ Short-circuit evaluation

### Data Types
- ✅ Integers
- ✅ Floats
- ✅ Strings (single and double quotes)
- ✅ Booleans (true/false)
- ✅ Arrays/Lists
- ✅ Null

### Error Cases
- ✅ Missing fields
- ✅ Type mismatches
- ✅ Invalid syntax
- ✅ Unclosed parentheses
- ✅ Missing operators/values

### Real-World Scenarios
- ✅ Financial eligibility
- ✅ Geographic restrictions
- ✅ Age verification with exceptions
- ✅ Fraud detection
- ✅ Multi-tier membership
- ✅ Complex nested logic

## Example Test Run

```bash
$ pytest tests/ -v

tests/test_expression_parser.py::TestExpressionTokenizer::test_simple_comparison PASSED
tests/test_expression_parser.py::TestExpressionTokenizer::test_string_values PASSED
tests/test_expression_parser.py::TestExpressionParser::test_simple_comparison PASSED
tests/test_expression_parser.py::TestExpressionParser::test_and_expression PASSED
tests/test_expression_parser.py::TestComplexExpressions::test_financial_eligibility PASSED
...
tests/test_expression_evaluator.py::TestBasicEvaluation::test_equals_true PASSED
tests/test_expression_evaluator.py::TestBooleanLogic::test_and_both_true PASSED
tests/test_expression_evaluator.py::TestComplexRealWorld::test_financial_eligibility PASSED
...

========== 100+ passed in 2.5s ==========
```

## Adding New Tests

When adding new operators or features:

1. Add tokenization tests in `test_expression_parser.py`
2. Add parsing tests in `test_expression_parser.py`
3. Add evaluation tests in `test_expression_evaluator.py`
4. Include edge cases and error handling tests
5. Add real-world scenario tests

## CI/CD Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r backend/requirements-test.txt
    pytest backend/tests/ --cov=backend/src
```

