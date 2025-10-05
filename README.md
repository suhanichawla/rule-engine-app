# Rekord Rule Evaluator System - Summary

## Overview

The **Rekord Rule Evaluator System** is a transparent, containerized decision-making platform designed for regulated entities that require clear, auditable rule evaluation. The system provides a RESTful API for creating, managing, and evaluating complex business rules against JSON payloads, returning clear PASS/FAIL results with detailed reasoning for each decision.

**Key Capabilities:**
- Define rules using either simple predicates (either ANDing or ORing them) or complex expressions
- Evaluate JSON payloads against multiple rules simultaneously
- Receive detailed, human-readable explanations for every decision
- Support for both AND/OR logical operators in predicates
- Field-to-field comparisons possible in expressions
- Complete CRUD operations for rule management
- Modern web UI for interactive rule management

---

## Technology Stack

**Backend:**
- **Python 3.11**
- **FastAPI**: for the server
- **Pydantic**: for data validation and serialization
- **Swagger**: for api docs

There is a frontend to interact easily with the app, hosted on port 8080

**Frontend:**
- **Vanilla JavaScript**: No framework dependencies, lightweight
- **Modern CSS**: CSS variables, responsive design
- **Nginx**: Production-ready web server

**Infrastructure:**
- **Docker & Docker Compose**: Containerization and orchestration
- **JSON File Storage**: Simple, portable persistence layer

---

## Features

### 1. **Flexible Rule Definition**

Rules can be defined in two powerful ways:

#### A. Predicate-Based Rules
Simple list of conditions with configurable AND/OR logic:
```json
{
  "name": "Premium User Check",
  "description": "User must meet all premium criteria",
  "predicates": [
    {"field": "account_type", "operator": "==", "value": "premium"},
    {"field": "subscription_months", "operator": ">=", "value": 12}
  ],
  "logical_operator": "AND" //can also be OR
}
```
AND is also the default if no logical_operator is specified

#### B. Expression-Based Rules
Complex boolean expressions with nested logic:
```json
{
  "name": "Financial Eligibility",
  "description": "Complex eligibility check",
  "expression": "(age >= 21 AND credit_score >= 700) OR net_worth > 1000000"
}
```
One of the main features in this system is the parsing of the complex expressions. This is done by first tokenizing them and then converting them into an AST and then evaluating the AST.

### 2. **Rich Operator Support**

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equals | `age == 18` |
| `!=` | Not equals | `status != "banned"` |
| `>` | Greater than | `score > 100` |
| `>=` | Greater than or equal | `age >= 21` |
| `<` | Less than | `debt < 1000` |
| `<=` | Less than or equal | `attempts <= 3` |
| `contains` | String/list contains | `tags contains "premium"` |
| `not_contains` | String/list does not contain | `notes not_contains "fraud"` |
| `in` | Value in list | `country in ["USA", "Canada"]` |
| `not_in` | Value not in list | `status not_in ["banned", "suspended"]` |

### 3. **Advanced Expression Features**

- **Boolean Logic**: Support for `AND`, `OR` operators with proper precedence
- **Parentheses**: Group expressions for complex nested logic
- **Field-to-Field Comparison**: Compare payload fields to each other
  ```javascript
  ip_country == account_country
  password == confirm_password
  start_date < end_date
  current_balance >= minimum_balance
  ```
- **Type Support**: Numbers (int/float), strings, booleans, null, arrays
- **Expression Validation**: Syntax errors caught at rule creation time

### 4. **Transparent Decision-Making**

Every evaluation returns:
- **Overall Result**: PASS or FAIL
- **Detailed Reasons**: Human-readable explanations for each condition
- **Predicate-Level Results**: See exactly which conditions passed/failed
- **Actual vs Expected Values**: Full transparency for auditing

Note that the predicate level results will be returned even if it is an chain of ORs. This is because we want the user to be aware of every failing predicate. For example, if this was a banking application and they had the option of providing either a utility bill + RTB letter or providing the lease as an option and they only provided the RTB letter, we need to tell them they are missing a utility bill as well as a lease. If they provided just the lease, the rule will PASS but will tell them if there are any failing predicates.

### 5. **Complete CRUD API**

- `GET /api/v1/rules` - List all rules
- `GET /api/v1/rules/{id}` - Get specific rule
- `POST /api/v1/rules` - Create new rule
- `PUT /api/v1/rules/{id}` - Update existing rule
- `DELETE /api/v1/rules/{id}` - Delete rule
- `POST /api/v1/evaluate` - Evaluate payload against rules


### 6. **Interactive Documentation**

- **Swagger UI**: http://localhost:8000/docs
- Auto-generated from code with examples

---

## Rules Format and Evaluation Strategy

Rules can be defined using either **predicates** or **expressions**:

**Predicates**: Simple conditions combined with AND/OR logic
- Multiple predicates evaluated independently
- AND logic: ALL predicates must pass
- OR logic: At least ONE predicate must pass
- Each predicate tracked for detailed reporting

**Expressions**: Complex boolean expressions with nested logic
- Supports AND, OR, parentheses for grouping
- Field-to-field comparisons
- Operator precedence: Parentheses → Comparisons → AND → OR
- Parsed into Abstract Syntax Tree (AST) for evaluation

For detailed technical information about the expression parser implementation, AST structure, and evaluation algorithms, see [technical_architecture.md](./docs/technical_architecture.md).

---

## Docker Setup

### Single Command Startup

```bash
# From project root
docker-compose up -d
```

This command will:
1. Build the backend Docker image
2. Start the backend container on port 8000
3. Start the frontend container on port 8080
4. Create a Docker network for service communication
5. Mount the `backend/data` directory for persistence


Once you run the docker command, the following services should become available

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend UI**: http://localhost:8080

## Demo

### Video Walkthrough


### Live Demo
The current setup is hosted on an ec2
- **Frontend**: http://ec2-13-61-145-69.eu-north-1.compute.amazonaws.com:8080
- **Backend API**: http://ec2-13-61-145-69.eu-north-1.compute.amazonaws.com:8000

---

## Sample curl Requests

The system comes pre-loaded with several example rules. Here are some practical curl examples using these rules:

### Example 1: PASS Scenario ✓

**Rule**: Financial Eligibility
**Expression**: `(age >= 21 AND credit_score >= 700 AND debt_ratio < 0.4) OR net_worth > 1000000`
**Scenario**: User meets all criteria in the first branch (age, credit score, debt ratio)

```bash
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "age": 25,
      "credit_score": 750,
      "debt_ratio": 0.3,
      "net_worth": 500000
    },
    "rule_ids": ["0f825fa8-e97d-435e-90ff-311900d1ad4a"]
  }'
```

**Response:**
```json
{
  "result": "PASS",
  "reasons": [
    "Financial Eligibility: Financial Eligibility passed all conditions"
  ],
  "details": [
    {
      "rule_id": "0f825fa8-e97d-435e-90ff-311900d1ad4a",
      "rule_name": "Financial Eligibility",
      "result": "PASS",
      "reason": "Financial Eligibility passed all conditions",
      "predicate_results": [
        {
          "field": "age",
          "operator": ">=",
          "expected": 21,
          "actual": 25,
          "passed": true,
          "reason": "age passed >= check"
        },
        {
          "field": "credit_score",
          "operator": ">=",
          "expected": 700,
          "actual": 750,
          "passed": true,
          "reason": "credit_score passed >= check"
        },
        {
          "field": "debt_ratio",
          "operator": "<",
          "expected": 0.4,
          "actual": 0.3,
          "passed": true,
          "reason": "debt_ratio passed < check"
        },
        {
          "field": "net_worth",
          "operator": ">",
          "expected": 1000000,
          "actual": 500000,
          "passed": false,
          "reason": "net_worth (500000) must be greater than 1000000"
        }
      ]
    }
  ]
}
```

**Note**: Even though `net_worth` check failed, the rule passes because the first branch of the OR expression (age AND credit_score AND debt_ratio) succeeded. This demonstrates the transparency feature - all predicate results are shown even when the rule passes.

### Example 2: FAIL Scenario ✗

**Rule**: Financial Eligibility
**Expression**: `(age >= 21 AND credit_score >= 700 AND debt_ratio < 0.4) OR net_worth > 1000000`
**Scenario**: User fails multiple criteria - doesn't meet any branch of the OR expression

```bash
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "age": 20,
      "credit_score": 650,
      "debt_ratio": 0.5,
      "net_worth": 50000
    },
    "rule_ids": ["0f825fa8-e97d-435e-90ff-311900d1ad4a"]
  }'
```

**Response:**
```json
{
  "result": "FAIL",
  "reasons": [
    "Financial Eligibility: age (20) must be at least 21; credit_score (650) must be at least 700; debt_ratio (0.5) must be less than 0.4; net_worth (50000) must be greater than 1000000"
  ],
  "details": [
    {
      "rule_id": "0f825fa8-e97d-435e-90ff-311900d1ad4a",
      "rule_name": "Financial Eligibility",
      "result": "FAIL",
      "reason": "age (20) must be at least 21; credit_score (650) must be at least 700; debt_ratio (0.5) must be less than 0.4; net_worth (50000) must be greater than 1000000",
      "predicate_results": [
        {
          "field": "age",
          "operator": ">=",
          "expected": 21,
          "actual": 20,
          "passed": false,
          "reason": "age (20) must be at least 21"
        },
        {
          "field": "credit_score",
          "operator": ">=",
          "expected": 700,
          "actual": 650,
          "passed": false,
          "reason": "credit_score (650) must be at least 700"
        },
        {
          "field": "debt_ratio",
          "operator": "<",
          "expected": 0.4,
          "actual": 0.5,
          "passed": false,
          "reason": "debt_ratio (0.5) must be less than 0.4"
        },
        {
          "field": "net_worth",
          "operator": ">",
          "expected": 1000000,
          "actual": 50000,
          "passed": false,
          "reason": "net_worth (50000) must be greater than 1000000"
        }
      ]
    }
  ]
}
```

**Note**: All four predicates failed, showing detailed reasons for each. The user needs to either: (1) meet all three criteria in the first branch, OR (2) have net_worth > $1M.

### Example 3: Multiple Rules Evaluation

**Rules**:
1. Geographic Eligibility: `(country in ['USA', 'Canada']) OR (country in ['UK', 'Germany'] AND credit_score >= 650)`
2. Fraud Detection: `login_attempts <= 3 AND ip_country == account_country AND notes not_contains 'fraud'`

**Scenario**: Evaluate a payload against two rules simultaneously

```bash
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "country": "Canada",
      "credit_score": 720,
      "login_attempts": 2,
      "ip_country": "Canada",
      "account_country": "Canada",
      "notes": "Active user"
    },
    "rule_ids": [
      "c3bf418d-d5c3-4fdd-984d-4cff14e9627b",
      "d1963b85-007f-447f-a74e-d1f1ab2d9dbe"
    ]
  }'
```

**Result**: Both rules will PASS - user is from Canada (allowed country) and passes all fraud checks.

### Example 4: Field-to-Field Comparison (PASS)

**Rule**: Password and Security Check
**Expression**: `password == confirm_password AND password_length >= 8`
**Scenario**: Demonstrates field-to-field comparison where password must match confirm_password

```bash
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "password": "SecurePass123",
      "confirm_password": "SecurePass123",
      "password_length": 13
    },
    "rule_ids": ["7e936fcb-5c09-4085-9e37-b9e7019a593b"]
  }'
```

**Response:**
```json
{
  "result": "PASS",
  "reasons": [
    "Password and Security Check: Password and Security Check passed all conditions"
  ],
  "details": [
    {
      "rule_id": "7e936fcb-5c09-4085-9e37-b9e7019a593b",
      "rule_name": "Password and Security Check",
      "result": "PASS",
      "reason": "Password and Security Check passed all conditions",
      "predicate_results": [
        {
          "field": "password",
          "operator": "==",
          "expected": "SecurePass123",
          "actual": "SecurePass123",
          "passed": true,
          "reason": "password == confirm_password check passed"
        },
        {
          "field": "password_length",
          "operator": ">=",
          "expected": 8,
          "actual": 13,
          "passed": true,
          "reason": "password_length passed >= check"
        }
      ]
    }
  ]
}
```

**Note**: The first comparison shows field-to-field validation where `password` field is compared to `confirm_password` field.

### Example 5: Missing Fields (FAIL)

**Rule**: Financial Eligibility
**Expression**: `(age >= 21 AND credit_score >= 700 AND debt_ratio < 0.4) OR net_worth > 1000000`
**Scenario**: Payload is missing required fields - demonstrates clear error messaging

```bash
curl -X POST http://localhost:8000/api/v1/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "payload": {
      "age": 25
    },
    "rule_ids": ["0f825fa8-e97d-435e-90ff-311900d1ad4a"]
  }'
```

**Response:**
```json
{
  "result": "FAIL",
  "reasons": [
    "Financial Eligibility: Missing required fields: debt_ratio, net_worth, credit_score"
  ],
  "details": [
    {
      "rule_id": "0f825fa8-e97d-435e-90ff-311900d1ad4a",
      "rule_name": "Financial Eligibility",
      "result": "FAIL",
      "reason": "Missing required fields: debt_ratio, net_worth, credit_score",
      "predicate_results": [
        {
          "error": "Missing required fields: debt_ratio, net_worth, credit_score",
          "passed": false
        }
      ]
    }
  ]
}
```

**Note**: The system identifies all missing fields upfront before attempting evaluation, providing clear feedback to the user.


## Assumptions and Design Decisions

The system is built on several key assumptions and design decisions that balance simplicity, maintainability, and production-readiness:

- **File-Based Storage**: JSON file storage for simplicity and portability
- **Smart Reason Generation**: Auto-generated human-readable explanations
- **Every predicate reasoning**: Each predicate decision is sent back in the api and no short circuiting happens for OR chains
- **Expression Validation**: Fail-fast validation at rule creation time if the expression is invalid
- **Immutable Domain Models**: Ensures evaluation reproducibility
- **No Authentication**: Assuming auth is not a priority here as its a demo project
- **Non AI solution**: Because the use case is to give a deterministic answer for every check, i decided to go with a simple logic based solution, so that same payload gives you the same response every time. Thats not to say its not possible with AI (and structured outputs) but made a design decision to use a non ai solution here.

---

## Edge Cases Handled

The system handles numerous edge cases to ensure robust operation:

- Missing fields in payloads
- Type mismatches between expected and actual values
- Invalid expression syntax with helpful error messages
- Field-to-field comparisons with missing fields
- Boolean and null value handling
- Array comparison validations

---

## What's Next?

Since this is a take home, I made a few design decisions that i wouldnt neccesarily make in production. here are some short term and long term improvements for this project

**Immediate Improvements:**
- Database integration instead of fetching from a file
- Enhanced testing coverage
- Logging wherever required
- A slightly nicer UI :)

**Long-Term Features:**
- Adding AI for the user to be able to add a natural language prompt and for an LLM to transform it into the format our api requires
- we can also do the decision making using an LLM with structured outputs. This will however come with an eval system to ensure as much determinism as we can
- Derived fields or formulas: currently you cannot specify `income-expenditure<300` type expressions. We can introduce a concept for users to specify a derived field like `savings` for the above example, which is computed as `income-expenditure`. Then if the request payload doesnt have savings but has income and expenditure fields, that should still be evaluated succesfully


---

**Technical Details**: [technical_architecture.md](./docs/technical_architecture.md)
