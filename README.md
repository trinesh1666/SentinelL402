# SentinelL402

## AI + Lightning + HTTP 402 + APIs

SentinelL402 is a production-oriented AI security API platform that combines **AI agents, machine-learning-based network security analysis, Lightning payments, HTTP 402 payment requirements, API authentication, usage metering, and Docker-based deployment**.

The system is designed around a metered API model: authenticated clients can use security-analysis capabilities while credits are available. When additional credits are required, the API can return an **HTTP 402 Payment Required** response and create a Lightning payment request. After the Lightning payment is verified, credits are restored and the requested operation can continue.

---

## 🚀 Project Overview

SentinelL402 combines four major areas:

* **AI Agent** — interprets requests and selects the appropriate tool.
* **ML Security Analysis** — analyzes network-security data using a trained machine-learning model.
* **Lightning / L402 Payments** — provides a payment mechanism for metered API usage.
* **Production API Infrastructure** — authentication, rate limiting, database persistence, logging, error handling, Docker hardening, migrations, automated tests, and CI/CD.

### High-level architecture

```text
                    ┌─────────────────────┐
                    │       Client        │
                    └──────────┬──────────┘
                               │
                               │ X-API-Key
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │       API           │
                    └──────────┬──────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
          Authentication   Rate Limiting   Request Logging
                │
                ▼
          Usage / Credits
                │
                ▼
          ┌─────────────┐
          │  HTTP 402   │
          │  if needed  │
          └──────┬──────┘
                 │
                 ▼
        Lightning Invoice
                 │
                 ▼
          NWC / Lightning
                 │
                 ▼
        Payment Verification
                 │
                 ▼
          Credits Granted
                 │
                 ▼
             AI Agent
                 │
                 ▼
        Security Analysis Tool
                 │
                 ▼
          ML Security Model
                 │
                 ▼
          Security Result
```

---

## ✨ Main Features

### 🔐 API Authentication

SentinelL402 uses API-key authentication through the:

```text
X-API-Key
```

header.

The system supports API-key lifecycle operations including creation, authentication, expiration handling, listing, and revocation.

---

### ⚡ Lightning + HTTP 402

The application implements a metered payment flow based on HTTP 402.

When a user does not have sufficient credits:

```text
Client
  ↓
Security API
  ↓
Insufficient credits
  ↓
HTTP 402 Payment Required
  ↓
Lightning invoice
  ↓
Payment
  ↓
Payment verification
  ↓
Credits granted
  ↓
Request continues
```

The Lightning integration uses **Nostr Wallet Connect (NWC)**.

---

### 🤖 AI Agent

The SentinelL402 agent provides an intent-routing layer between the API and available tools.

The agent can:

1. Receive an authenticated request.
2. Determine the requested operation.
3. Select the appropriate tool.
4. Validate tool arguments.
5. Execute the metered operation.
6. Return the result.

The authenticated identity is maintained separately from user-provided request data.

---

### 🧠 LLM Integration

The project integrates with a local Ollama LLM.

Default configuration:

```text
Model: llama3.2:3b
```

The LLM service communicates with Ollama through its generation API.

LLM configuration is environment-driven and can be changed without modifying application code.

---

### 🛡️ ML-Based Security Analysis

SentinelL402 includes a network-security analysis pipeline based on machine-learning features derived from network traffic data.

The security-analysis API accepts the required security features and uses the trained model to produce an analysis result.

The project includes a Random Forest security model and associated model-loading functionality.

---

## 💳 Metered Usage Model

The project uses credits to control access to metered operations.

The configured payment model grants:

```text
1 Lightning payment
        ↓
5 credits
```

The configured payment amount is:

```text
10 sats
```

Payment invoices have an expiration period configured by the application.

The payment system also handles:

* Pending payments
* Expired payments
* Payment verification
* Payment ownership
* Exact invoice amount verification
* Idempotent payment handling
* Transaction errors
* Payment state transitions

---

## 🔑 Authentication Flow

A protected request uses:

```http
X-API-Key: <your-api-key>
```

The authentication process is:

```text
Client
  ↓
X-API-Key
  ↓
API-key validation
  ↓
User identification
  ↓
Authenticated request
```

API keys are not logged by the application.

---

## 🏗️ Project Structure

```text
SentinelL402/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── alembic/
│   └── versions/
│       ├── 5973593e9cbf_baseline_existing_schema.py
│       ├── 73105a708303_add_payment_description.py
│       └── b278622c3c1d_add_api_key_expiration.py
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── logging_config.py
│   │   │
│   │   ├── agent/
│   │   │
│   │   ├── middleware/
│   │   │   ├── request_logging.py
│   │   │   ├── database_errors.py
│   │   │   └── error_handling.py
│   │   │
│   │   ├── ml/
│   │   │   └── models/
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   └── api_key.py
│   │   │
│   │   └── services/
│   │       ├── api_key_service.py
│   │       ├── auth_service.py
│   │       ├── health_service.py
│   │       ├── lightning_service.py
│   │       ├── llm_service.py
│   │       ├── payment_service.py
│   │       ├── rate_limit_dependency.py
│   │       └── rate_limit_service.py
│   │
│   ├── tests/
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
└── README.md
```

---

## 🛠️ Technology Stack

| Component           | Technology               |
| ------------------- | ------------------------ |
| API                 | FastAPI                  |
| Language            | Python 3.13              |
| Database            | SQLite                   |
| ORM                 | SQLAlchemy               |
| Migrations          | Alembic                  |
| Authentication      | API Keys                 |
| Payment             | Bitcoin Lightning        |
| Wallet connectivity | Nostr Wallet Connect     |
| AI Agent            | Python-based agent layer |
| LLM                 | Ollama                   |
| Default LLM         | `llama3.2:3b`            |
| ML                  | Scikit-learn             |
| Security model      | Random Forest            |
| Containerization    | Docker                   |
| CI/CD               | GitHub Actions           |
| Testing             | Pytest                   |

---

## ⚙️ Local Development

### 1. Clone the repository

```bash
git clone https://github.com/trinesh1666/SentinelL402.git
cd SentinelL402
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r backend\requirements.txt
```

### 4. Configure environment variables

Create:

```text
.env
```

Use `.env.example` as the configuration template.

Do not commit `.env`.

---

## ▶️ Running the API

From the project root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

The API can then be accessed through:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## ❤️ Health Checks

### Health

```http
GET /health
```

Expected response:

```json
{
  "status": "healthy"
}
```

### Readiness

```http
GET /ready
```

Expected response:

```json
{
  "status": "ready",
  "database": "ok"
}
```

---

## 🐳 Docker

The project includes Docker configuration for the API.

Build and start:

```powershell
docker compose up -d --build
```

Check containers:

```powershell
docker compose ps
```

Check application readiness:

```powershell
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/ready).Content
```

Expected:

```json
{
  "status": "ready",
  "database": "ok"
}
```

Stop the services:

```powershell
docker compose down
```

---

## 🔒 Docker Security

The API container includes several hardening controls:

* Runs as a non-root user.
* Read-only root filesystem.
* Writable application data through the mounted data directory.
* Writable `/tmp` through a temporary filesystem.
* `no-new-privileges`.
* All Linux capabilities dropped.
* Memory limit.
* CPU limit.
* Localhost-only host port binding.
* Container healthcheck.

The configured limits are:

```text
Memory: 2 GB
CPU:    2 cores
```

---

## 🗄️ Database Migrations

Alembic is the authoritative database migration system.

Check the current migration:

```powershell
alembic current
```

Check for schema differences:

```powershell
alembic check
```

Apply migrations:

```powershell
alembic upgrade head
```

The validated migration head is:

```text
b278622c3c1d
```

---

## 🧪 Testing

Run the complete backend test suite:

```powershell
pytest backend\tests -q
```

The project has been validated with:

```text
94 passed
```

Compilation check:

```powershell
python -m compileall backend\app alembic
```

Migration validation:

```powershell
alembic check
```

---

## 🔄 CI/CD

GitHub Actions automatically validates changes pushed to `main` and pull requests targeting `main`.

Workflow:

```text
Git push / Pull Request
        ↓
GitHub Actions
        ↓
Checkout repository
        ↓
Python 3.13
        ↓
Install dependencies
        ↓
Compile Python
        ↓
Run backend tests
        ↓
Check Alembic migrations
        ↓
CI result
```

Workflow file:

```text
.github/workflows/ci.yml
```

The CI pipeline has been successfully validated with a green GitHub Actions run.

---

## 📡 Important API Areas

The backend includes API functionality for:

* Authentication
* API-key management
* Usage tracking
* Security analysis
* Payment creation
* Payment verification
* AI-agent execution
* Health and readiness
* API-key lifecycle management

Interactive API documentation is available through FastAPI Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## ⚡ L402 Payment Flow

The core metered-payment workflow is:

```text
1. Client sends authenticated request
                ↓
2. API checks available credits
                ↓
3. Credits insufficient
                ↓
4. API returns HTTP 402
                ↓
5. Lightning payment is created
                ↓
6. Client pays invoice
                ↓
7. Payment is verified
                ↓
8. Credits are granted
                ↓
9. Requested operation can proceed
```

This creates the connection between:

```text
HTTP 402
+
Lightning
+
AI API
+
Usage Metering
```

---

## 🛡️ Security Considerations

The project includes:

* API-key authentication.
* API-key expiration.
* API-key revocation.
* Rate limiting.
* Payment ownership validation.
* Payment expiry handling.
* Payment idempotency.
* Exact payment amount verification.
* Database transaction handling.
* Structured operational logging.
* Error-handling middleware.
* Docker container hardening.
* Non-root container execution.
* Read-only container filesystem.
* Secret exclusion through `.gitignore`.
* Environment-based configuration.

Sensitive credentials should always remain in environment configuration and must never be committed to Git.

---

## 📊 Production Validation

The project has completed the following validation:

```text
Python compilation                 ✅
Automated test suite              ✅
94 tests passed                    ✅
Alembic current                   ✅
Alembic schema check              ✅
Docker health                     ✅
Docker readiness                  ✅
Read-only filesystem              ✅
Writable application data         ✅
Writable /tmp                     ✅
2 GB memory limit                 ✅
2 CPU limit                       ✅
Capabilities dropped              ✅
No-new-privileges                 ✅
Localhost-only port binding       ✅
Git secret scan                    ✅
Git whitespace validation         ✅
GitHub Actions CI                 ✅ GREEN
```

---

## 🎯 Project Goals

SentinelL402 demonstrates how several modern technologies can be combined into a single real-world system:

```text
Artificial Intelligence
        +
Machine Learning
        +
AI Agents
        +
Bitcoin Lightning
        +
HTTP 402
        +
API Metering
        +
FastAPI
        +
Docker
        +
Automated Testing
        +
CI/CD
```

The project is intended as a practical demonstration of building a secure, metered AI API rather than only a machine-learning model.

---

## 👨‍💻 Development Philosophy

The project follows several engineering principles:

* Environment-driven configuration.
* Explicit database migrations.
* Automated testing.
* Defensive error handling.
* Secure authentication.
* Payment-state validation.
* Idempotent payment operations.
* Structured operational logging.
* Container security.
* CI validation before integration.

---

## 📌 Project Status

**Core SentinelL402 implementation: Complete**

The core backend, Lightning payment flow, AI-agent integration, security-analysis pipeline, testing, Docker hardening, database migrations, and CI/CD pipeline have been implemented and validated.

Future optional work can include:

* Web frontend/dashboard.
* Cloud deployment.
* Production monitoring.
* External production database.
* Additional AI-agent tools.
* Additional ML models.
* Advanced observability.

---

## 📄 License

Add the project's chosen license here before publishing the repository for broader reuse.

---

## ⭐ SentinelL402

**AI + Lightning + HTTP 402 + APIs**

A metered AI security API combining machine learning, AI agents, and Bitcoin Lightning payments.
