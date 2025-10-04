# 🎯 Rekord Rules Evaluator

A transparent, containerized rules evaluation service for regulated entities. This platform provides clear decision-making through well-defined rules with comprehensive reasoning.

## 🌟 Features

- **Rule Management**: Complete CRUD operations for rule definitions
- **Transparent Evaluation**: Clear PASS/FAIL results with detailed reasoning
- **Multiple Operators**: Support for comparison, containment, and membership operators
- **RESTful API**: Clean, well-documented API with OpenAPI/Swagger
- **Modern UI**: Simple, intuitive web interface for rule management and evaluation
- **Containerized**: Docker-based deployment with single-command startup
- **Clean Architecture**: Hexagonal (Ports & Adapters) architecture for maintainability

## 🏗️ Architecture

This project follows **Hexagonal Architecture** (Ports and Adapters pattern):

```
backend/
├── src/
│   ├── domain/           # Core business logic
│   │   ├── models.py     # Domain entities (Rule, Predicate, etc.)
│   │   └── exceptions.py # Domain-specific exceptions
│   ├── application/      # Use cases and business orchestration
│   │   ├── ports.py      # Interface definitions (RuleRepository)
│   │   └── services.py   # Business logic (RuleService, EvaluationService)
│   ├── adapters/         # External interfaces
│   │   ├── inbound/      # API endpoints (FastAPI routes)
│   │   └── outbound/     # External services (FileRepository)
│   ├── infrastructure/   # Configuration and setup
│   └── main.py          # Application entry point
└── data/
    └── rules.json       # Persistent rule storage
```

### Why Hexagonal Architecture?

- **Testability**: Business logic is independent of external dependencies
- **Flexibility**: Easy to swap implementations (e.g., file storage → database)
- **Maintainability**: Clear separation of concerns
- **Domain-Driven**: Business rules at the center, infrastructure at the edges

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Ports 8000 (backend) and 8080 (frontend) available

### Running the Application

```bash
# Clone the repository (if applicable)
cd rekord

# Start the services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the services
docker-compose down
```

The services will be available at:
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend UI**: http://localhost:8080

## 📚 API Documentation

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `==` | Equals | `{"field": "age", "operator": "==", "value": 18}` |
| `!=` | Not equals | `{"field": "status", "operator": "!=", "value": "rejected"}` |
| `>` | Greater than | `{"field": "score", "operator": ">", "value": 100}` |
| `>=` | Greater than or equal | `{"field": "age", "operator": ">=", "value": 21}` |
| `<` | Less than | `{"field": "debt", "operator": "<", "value": 1000}` |
| `<=` | Less than or equal | `{"field": "attempts", "operator": "<=", "value": 3}` |
| `contains` | String/list contains value | `{"field": "tags", "operator": "contains", "value": "premium"}` |
| `not_contains` | String/list does not contain | `{"field": "notes", "operator": "not_contains", "value": "fraud"}` |
| `in` | Value in list | `{"field": "country", "operator": "in", "value": ["USA", "Canada"]}` |
| `not_in` | Value not in list | `{"field": "status", "operator": "not_in", "value": ["banned", "suspended"]}` |

### Predicate Logic

- Multiple predicates in a rule are combined with **AND** logic
- All predicates must evaluate to `true` for the rule to pass
- If any predicate fails, the entire rule fails

### API Endpoints

#### List All Rules
```http
GET /api/v1/rules
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Age Verification",
    "description": "Verify minimum age requirement",
    "predicates": [
      {
        "field": "age",
        "operator": ">=",
        "value": 18
      }
    ],
    "effect": "PASS",
    "reason": "Applicant meets minimum age requirement"
  }
]
```

#### Get Rule by ID
```http
GET /api/v1/rules/{rule_id}
```

#### Create Rule
```http
POST /api/v1/rules
Content-Type: application/json

{
  "name": "Credit Score Check",
  "description": "Verify acceptable credit score",
  "predicates": [
    {
      "field": "credit_score",
      "operator": ">=",
      "value": 650
    }
  ],
  "effect": "PASS",
  "reason": "Credit score meets minimum threshold"
}
```

**Response:** `201 Created` with the created rule (including generated UUID)

#### Update Rule
```http
PUT /api/v1/rules/{rule_id}
Content-Type: application/json

{
  "name": "Updated Rule Name",
  "description": "Updated description",
  "predicates": [...],
  "effect": "PASS",
  "reason": "Updated reason"
}
```

#### Delete Rule
```http
DELETE /api/v1/rules/{rule_id}
```

**Response:** `204 No Content`

#### Evaluate Payload
```http
POST /api/v1/evaluate
Content-Type: application/json

{
  "payload": {
    "age": 25,
    "credit_score": 720,
    "country": "USA"
  },
  "rule_ids": [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ]
}
```

**Response:**
```json
{
  "result": "PASS",
  "reasons": [
    "Age Verification: Applicant meets minimum age requirement",
    "Credit Score Check: Credit score meets minimum threshold"
  ],
  "details": [
    {
      "rule_id": "550e8400-e29b-41d4-a716-446655440001",
      "rule_name": "Age Verification",
      "result": "PASS",
      "reason": "Applicant meets minimum age requirement",
      "predicate_results": [
        {
          "field": "age",
          "operator": ">=",
          "expected": 18,
          "actual": 25,
          "passed": true
        }
      ]
    }
  ]
}
```

## 🧪 Example Use Cases

### Example 1: Simple Age Check

**Rule:**
```json
{
  "name": "Age Verification",
  "description": "Must be 18 or older",
  "predicates": [
    {"field": "age", "operator": ">=", "value": 18}
  ],
  "effect": "PASS",
  "reason": "Applicant is of legal age"
}
```

**Payload:**
```json
{"age": 25}
```

**Result:** `PASS` ✓

### Example 2: Multi-Criteria Evaluation

**Rule:**
```json
{
  "name": "Premium Eligibility",
  "description": "Premium tier requirements",
  "predicates": [
    {"field": "age", "operator": ">=", "value": 21},
    {"field": "credit_score", "operator": ">=", "value": 700},
    {"field": "annual_income", "operator": ">", "value": 50000}
  ],
  "effect": "PASS",
  "reason": "Meets all premium criteria"
}
```

**Payload:**
```json
{
  "age": 30,
  "credit_score": 750,
  "annual_income": 75000
}
```

**Result:** `PASS` ✓ (all predicates satisfied)

### Example 3: Geographic Restriction

**Rule:**
```json
{
  "name": "Geographic Check",
  "description": "Service available in specific countries",
  "predicates": [
    {
      "field": "country",
      "operator": "in",
      "value": ["USA", "Canada", "UK"]
    }
  ],
  "effect": "PASS",
  "reason": "Service available in applicant's region"
}
```

## 🛠️ Development

### Local Development (without Docker)

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd src
python main.py

# Frontend (serve with any static server)
cd frontend
python -m http.server 8080
```

### Project Structure

```
rekord/
├── backend/
│   ├── src/
│   │   ├── domain/          # Business entities and logic
│   │   ├── application/     # Use cases and ports
│   │   ├── adapters/        # External interfaces
│   │   ├── infrastructure/  # Configuration
│   │   └── main.py         # Application entry
│   ├── data/
│   │   └── rules.json      # Rule persistence
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── docker-compose.yml
└── README.md
```

### Technology Stack

**Backend:**
- Python 3.11
- FastAPI (modern, fast web framework)
- Pydantic (data validation)
- Uvicorn (ASGI server)

**Frontend:**
- Vanilla JavaScript (no framework dependencies)
- Modern CSS with CSS variables
- Responsive design

**Infrastructure:**
- Docker & Docker Compose
- Nginx (frontend server)

## 🔧 Configuration

### Environment Variables

- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)

### Data Persistence

Rules are persisted in `backend/data/rules.json`. This file is:
- Automatically created on first run if it doesn't exist
- Mounted as a Docker volume for persistence across container restarts
- Thread-safe with file locking

## 🧹 Best Practices Implemented

1. **Clean Architecture**: Separation of concerns with hexagonal architecture
2. **Type Safety**: Pydantic models for request/response validation
3. **Error Handling**: Comprehensive exception handling with meaningful messages
4. **Thread Safety**: File operations protected with locks
5. **API Documentation**: Auto-generated OpenAPI/Swagger documentation
6. **CORS Support**: Configured for cross-origin requests
7. **Health Checks**: Endpoint for monitoring service health
8. **Deterministic**: Same input always produces same output
9. **Immutability**: Domain models designed to be immutable
10. **Single Responsibility**: Each class/module has one clear purpose

## 📝 Design Decisions

1. **File-based Storage**: Simple JSON file storage for ease of setup and portability. Can easily be replaced with database via repository pattern.

2. **UUID for IDs**: Universally unique identifiers prevent collisions and enable distributed scenarios.

3. **AND Logic**: Multiple predicates use AND by default for strict validation. This is the most common use case in compliance scenarios.

4. **Explicit Effects**: Rules explicitly declare their effect (PASS/FAIL) rather than implicit success/failure for clarity.

5. **Detailed Reasoning**: Every evaluation includes predicate-level results for full transparency and auditability.

## 🚨 Error Handling

The API provides clear error messages:

- `400 Bad Request`: Invalid input, validation errors
- `404 Not Found`: Rule ID not found
- `500 Internal Server Error`: Unexpected server errors

Example error response:
```json
{
  "detail": "Rule with id '123' not found"
}
```

## 📈 Future Enhancements

Potential improvements for production use:

- Database support (PostgreSQL, MongoDB)
- OR logic support for predicates
- Nested predicate groups
- Rule versioning and history
- Authentication and authorization
- Rate limiting
- Audit logging
- Batch evaluation
- Rule testing/simulation
- Import/export functionality

## 📄 License

This is a demonstration project for technical assessment purposes.

---

**Built with ❤️ for Rekord**

