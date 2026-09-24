# SentinelL402

## AI + Lightning + HTTP 402 + APIs

SentinelL402 is a production-oriented, metered AI security API platform that combines **AI agents, machine-learning-based network security analysis, Bitcoin Lightning payments, HTTP 402 Payment Required, API authentication, usage metering, database persistence, Docker, automated testing, and CI/CD**.

The core idea is simple:

> **AI API usage is metered with credits. When credits are exhausted, SentinelL402 can return HTTP 402 and create a Bitcoin Lightning payment request. After payment verification, credits are restored and the client can continue using the AI service.**

The project demonstrates how **AI + Machine Learning + AI Agents + Bitcoin Lightning + HTTP 402 + API metering** can be combined into one real-world software system.

---

## 🚀 Project Overview

SentinelL402 contains four major systems:

1. **AI Agent Layer**
   Interprets requests, determines the requested operation, selects the appropriate tool, validates tool arguments, and executes the operation.

2. **ML-Based Network Security Analysis**
   Uses a trained Random Forest model to analyze network-security traffic features derived from the CIC-IDS2017 dataset.

3. **Lightning / L402 Payment Layer**
   Uses Bitcoin Lightning and Nostr Wallet Connect to provide metered payment functionality when API credits are exhausted.

4. **Production API Infrastructure**
   Provides API-key authentication, rate limiting, usage tracking, database persistence, migrations, logging, error handling, Docker hardening, automated testing, and GitHub Actions CI.

---

## 🏗️ High-Level Architecture

```text
                         ┌──────────────────────┐
                         │       Client         │
                         │ Swagger / Frontend   │
                         └──────────┬───────────┘
                                    │
                               X-API-Key
                                    │
                                    ▼
                    ┌───────────────────────────┐
                    │        FastAPI API        │
                    │ Authentication            │
                    │ Validation                │
                    │ Rate Limiting             │
                    │ Request Logging           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      Usage / Credits      │
                    │                           │
                    │ Check available credits   │
                    └─────────────┬─────────────┘
                                  │
                         Credits available?
                              /       \
                            YES        NO
                             │          │
                             │          ▼
                             │   ┌───────────────┐
                             │   │ HTTP 402      │
                             │   │ Payment       │
                             │   │ Required      │
                             │   └───────┬───────┘
                             │           │
                             │           ▼
                             │   ┌───────────────┐
                             │   │ Lightning     │
                             │   │ Invoice       │
                             │   └───────┬───────┘
                             │           │
                             │           ▼
                             │   ┌───────────────┐
                             │   │ NWC /         │
                             │   │ Lightning     │
                             │   └───────┬───────┘
                             │           │
                             │           ▼
                             │   ┌───────────────┐
                             │   │ Payment       │
                             │   │ Verification  │
                             │   └───────┬───────┘
                             │           │
                             │           ▼
                             │      +5 Credits
                             │           │
                             └─────┬─────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │     AI Agent      │
                         │ Intent Routing    │
                         │ Tool Selection    │
                         └─────────┬─────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ Security Tool     │
                         └─────────┬─────────┘
                                   │
                     ┌─────────────┴─────────────┐
                     │                           │
                     ▼                           ▼
            ┌──────────────────┐       ┌──────────────────┐
            │ Random Forest ML │       │      Ollama      │
            │ Security Model   │       │       LLM        │
            └────────┬─────────┘       └────────┬─────────┘
                     │                           │
                     └─────────────┬─────────────┘
                                   │
                                   ▼
                         ┌───────────────────┐
                         │ Security Analysis │
                         │ Result            │
                         └───────────────────┘
```

---

# ✨ Main Features

## 🤖 AI Agent

The SentinelL402 agent provides an orchestration layer between the API and AI tools.

The agent can:

* Receive an authenticated request.
* Determine the requested operation.
* Route the request to the appropriate tool.
* Validate tool arguments.
* Execute the security-analysis workflow.
* Use the ML security model.
* Use an LLM to generate analysis.
* Return a structured result.

The main agent endpoint is:

```http
POST /api/agent/run
```

---

## 🛡️ ML-Based Network Security Analysis

SentinelL402 includes a network-security analysis pipeline based on traffic features derived from the **CIC-IDS2017** dataset.

The system uses a trained **Random Forest** model to classify network traffic.

The analysis pipeline is:

```text
Network Traffic Features
          ↓
Feature Validation
          ↓
Preprocessing
          ↓
Random Forest Model
          ↓
Prediction
          ↓
Confidence / Probability
          ↓
Security Classification
          ↓
LLM Analysis
          ↓
Final Security Result
```

The security-analysis API is:

```http
POST /api/security/analyze
```

The system validates the required model features before running inference.

---

# 💳 Metered Usage Model

SentinelL402 uses a credit-based metering system.

The configured model is:

```text
10 sat Lightning payment
        ↓
5 credits
```

Credits are consumed by metered AI operations.

When sufficient credits are available:

```text
Authenticated Request
        ↓
Credit Check
        ↓
Consume Credit
        ↓
Execute AI Operation
        ↓
Return Result
```

When credits are exhausted:

```text
Authenticated Request
        ↓
Credits = 0
        ↓
HTTP 402 Payment Required
        ↓
Lightning Payment Request
```

After successful payment verification:

```text
Lightning Payment
        ↓
Payment Verification
        ↓
+5 Credits
        ↓
AI Request Can Continue
```

---

# ⚡ L402 / HTTP 402 Payment Flow

The core payment workflow is:

```text
1. Client sends authenticated AI request
                    ↓
2. SentinelL402 checks available credits
                    ↓
3. Credits are insufficient
                    ↓
4. API returns HTTP 402 Payment Required
                    ↓
5. Lightning payment is created
                    ↓
6. Client pays the Lightning invoice
                    ↓
7. SentinelL402 verifies the payment
                    ↓
8. Credits are restored
                    ↓
9. AI operation can continue
```

This connects:

```text
HTTP 402
    +
Bitcoin Lightning
    +
AI APIs
    +
Usage Metering
```

The implementation includes handling for:

* Pending payments
* Payment expiration
* Payment ownership
* Payment amount validation
* Payment state transitions
* Payment idempotency
* Database transaction handling
* Credit restoration

---

# 🔑 Authentication

Protected endpoints use the following HTTP header:

```http
X-API-Key: <your-api-key>
```

Authentication flow:

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

API keys are stored securely using hashing rather than storing the raw API key.

The application also supports API-key lifecycle operations including:

* API-key creation
* API-key validation
* API-key expiration
* API-key revocation
* Authenticated user identification

API keys and other credentials must remain outside Git.

---

# 📊 Usage Tracking

SentinelL402 tracks API usage and remaining credits.

The usage endpoint is:

```http
GET /api/usage/{user_id}
```

An authenticated user can access their own usage information.

Example response:

```json
{
  "user_id": "string",
  "credits_remaining": 4,
  "total_requests": 16
}
```

The exact values depend on the current account state.

---

# 🗂️ Project Structure

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
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
└── README.md
```

> `.env` is intentionally omitted because it contains local environment configuration and is excluded from Git.

---

# 🧰 Technology Stack

| Component           | Technology                           |
| ------------------- | ------------------------------------ |
| API Framework       | FastAPI                              |
| Language            | Python 3.13                          |
| API Documentation   | OpenAPI / Swagger                    |
| Authentication      | API Keys / `X-API-Key`               |
| Database            | SQLite for local development/testing |
| ORM                 | SQLAlchemy                           |
| Migrations          | Alembic                              |
| Payment Network     | Bitcoin Lightning                    |
| Wallet Connectivity | Nostr Wallet Connect                 |
| AI Agent            | Python-based agent layer             |
| LLM Runtime         | Ollama                               |
| Default LLM         | `llama3.2:3b`                        |
| Machine Learning    | Scikit-learn                         |
| Security Model      | Random Forest                        |
| Dataset             | CIC-IDS2017-derived network data     |
| Containerization    | Docker                               |
| Testing             | Pytest                               |
| CI/CD               | GitHub Actions                       |

---

# ⚙️ Local Development

## 1. Clone the repository

```bash
git clone https://github.com/trinesh1666/SentinelL402.git
cd SentinelL402
```

## 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
pip install -r backend\requirements.txt
```

## 4. Configure environment variables

Create a local:

```text
.env
```

Use:

```text
.env.example
```

as the configuration template.

Never commit `.env` to Git.

Sensitive values such as API keys, wallet credentials, NWC connection strings, and other secrets must never be placed in source code or committed to the repository.

---

# ▶️ Running the API

From the project root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
```

---

# ❤️ Health Checks

## Health

```http
GET /health
```

Expected:

```json
{
  "status": "healthy"
}
```

## Readiness

```http
GET /ready
```

Expected:

```json
{
  "status": "ready",
  "database": "ok"
}
```

These endpoints are also used by the Docker healthcheck configuration.

---

# 🐳 Docker

Build and start the API:

```powershell
docker compose up -d --build
```

Check the running container:

```powershell
docker compose ps
```

Expected state:

```text
sentinell402-api   Up ... (healthy)
```

Check readiness:

```powershell
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/ready).Content
```

Stop the services:

```powershell
docker compose down
```

---

# 🔒 Docker Security Hardening

The Docker deployment includes multiple security controls:

* Non-root container execution
* Read-only root filesystem
* Dedicated writable application-data volume
* Temporary writable `/tmp` filesystem
* `no-new-privileges`
* All Linux capabilities dropped
* CPU limit
* Memory limit
* Localhost-only host port binding
* Container healthcheck
* Automatic restart policy

Configured resource limits:

```text
Memory: 2 GB
CPU:    2 cores
```

The API is bound to:

```text
127.0.0.1:8000
```

rather than exposing the service directly on all host interfaces.

---

# 🗄️ Database Migrations

Alembic is the authoritative database migration system.

Check the current migration:

```powershell
alembic current
```

Check migration consistency:

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

# 🧪 Testing

Run the complete backend test suite:

```powershell
pytest backend\tests -q
```

Validated result:

```text
94 passed
```

Compile Python modules:

```powershell
python -m compileall backend\app alembic
```

Validate migrations:

```powershell
alembic check
```

The test suite covers areas including:

* Authentication
* API-key lifecycle
* Authorization
* Usage metering
* Security analysis
* Agent execution
* Lightning payment flow
* Payment verification
* Payment authorization
* Payment idempotency
* Payment state transitions
* Rate limiting
* Database integrity
* Error handling
* L402 end-to-end workflows

---

# 🔄 CI/CD

GitHub Actions validates changes pushed to `main` and pull requests targeting `main`.

The CI workflow performs:

```text
Git Push / Pull Request
        ↓
Checkout Repository
        ↓
Python 3.13
        ↓
Install Dependencies
        ↓
Compile Python
        ↓
Alembic Upgrade
        ↓
Alembic Current
        ↓
Alembic Check
        ↓
Run Backend Tests
        ↓
CI Result
```

Workflow file:

```text
.github/workflows/ci.yml
```

The project has been validated with a **green GitHub Actions CI run**.

---

# 📡 Important API Areas

The backend provides API functionality for:

* Authentication
* API-key management
* Usage tracking
* Security analysis
* AI-agent execution
* Lightning payment creation
* Lightning payment verification
* Health checks
* Readiness checks
* Rate limiting
* API-key lifecycle management

Interactive documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🧠 AI Security Analysis Pipeline

The security-analysis workflow combines machine learning and an LLM:

```text
Authenticated API Request
          ↓
Credit Validation
          ↓
Feature Validation
          ↓
ML Security Model
          ↓
Prediction + Confidence
          ↓
LLM Analysis
          ↓
Structured Security Response
          ↓
Credit / Usage Update
```

The ML model provides the security classification, while the LLM can provide additional natural-language analysis.

---

# 🛡️ Security Considerations

SentinelL402 implements several security controls:

* API-key authentication
* API-key hashing
* API-key expiration
* API-key revocation
* User-scoped authorization
* Rate limiting
* Payment ownership validation
* Payment expiration handling
* Payment idempotency
* Exact payment amount verification
* Database transaction handling
* Structured logging
* Error-handling middleware
* Docker container hardening
* Non-root container execution
* Read-only container filesystem
* Environment-based configuration
* `.env` exclusion through `.gitignore`

Sensitive credentials must remain outside Git.

Never commit:

```text
.env
API keys
NWC connection strings
Wallet secrets
Private keys
Database passwords
LLM provider secrets
```

---

# 🔬 Production Validation

The core system has been validated through automated and live checks.

```text
Python compilation                 ✅
Automated test suite              ✅
94 tests passed                    ✅
Alembic migration validation      ✅
Docker container                  ✅
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
X-API-Key authentication          ✅
OpenAPI authentication schema     ✅
Unauthenticated request rejected  ✅
Lightning payment flow            ✅
HTTP 402 payment flow              ✅
AI agent workflow                 ✅
ML security analysis              ✅
LLM integration                   ✅
Test database isolation           ✅
GitHub Actions CI                 ✅ GREEN
Git working tree                  ✅ CLEAN
```

---

# 🎯 Project Goals

SentinelL402 demonstrates how modern technologies can be combined into a single real-world metered AI system:

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
Database
        +
Docker
        +
Automated Testing
        +
CI/CD
```

The project focuses on building a complete AI service infrastructure rather than only training a machine-learning model.

---

# 👨‍💻 Development Philosophy

The project follows several software-engineering principles:

* Environment-driven configuration
* Explicit database migrations
* Automated testing
* Defensive error handling
* Secure authentication
* User-scoped authorization
* Payment-state validation
* Idempotent payment operations
* Structured operational logging
* Container security
* CI validation before integration
* Separation of application, service, agent, and ML layers

---

# 📌 Project Status

## Core SentinelL402 Implementation: Complete

The core implementation has been developed and validated across:

* FastAPI backend
* API authentication
* Usage metering
* Credit management
* AI agent orchestration
* Random Forest network-security analysis
* Ollama LLM integration
* Bitcoin Lightning payments
* HTTP 402 payment flow
* Payment verification
* Database migrations
* Automated testing
* Docker deployment
* Docker security hardening
* GitHub Actions CI/CD

### Optional future work

Future improvements may include:

* Web frontend/dashboard
* Cloud deployment
* Production monitoring
* External production database
* Additional AI-agent tools
* Additional ML models
* Advanced observability
* Distributed rate limiting
* Production secret management
* Metrics and tracing

---

# 📄 License

Add the project's chosen license before distributing the repository for broader reuse.

---

# 👨‍💻 Project Author

**Trinesh Vardhan**

SentinelL402 was developed as a practical project demonstrating the integration of **AI agents, machine learning, Bitcoin Lightning, HTTP 402, API metering, and production-oriented backend engineering**.
