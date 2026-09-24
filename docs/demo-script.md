# SentinelL402 — 5-Minute Project Demo Script

## 1. Introduction — 30 seconds

**What to say:**

> Good morning everyone. Today I am presenting my project **SentinelL402**, an AI-powered metered API system that combines Artificial Intelligence, network security analysis, Lightning payments, and the HTTP 402 payment protocol.
>
> The main idea is simple: users can access AI and security analysis services using API credits. When the user's credits are exhausted, the system automatically generates a Lightning payment request. After the payment is verified, credits are restored and the user can continue using the service.

---

## 2. Project Problem — 30 seconds

**What to say:**

> Traditional AI APIs usually use subscription-based or fixed billing models. SentinelL402 explores a different approach using **pay-per-use metering**.
>
> The system tracks API usage, consumes credits for each request, and uses the HTTP 402 Payment Required mechanism when the user needs additional credits.
>
> Lightning Network is used because it enables fast Bitcoin micropayments.

---

## 3. Architecture — 45 seconds

**Show:**

```text
User
  |
  v
FastAPI Backend
  |
  +---- API Key Authentication
  |
  +---- Usage / Credit Metering
  |
  +---- AI Agent
  |        |
  |        +---- Intent Classification
  |        |
  |        +---- Tool Selection
  |
  +---- Security Analysis Tool
  |        |
  |        +---- ML Model
  |        |
  |        +---- LLM Explanation
  |
  +---- HTTP 402
           |
           v
      Lightning / NWC
           |
           v
      Payment Verification
           |
           v
      Credits Restored
```

**What to say:**

> The backend is built using FastAPI. API requests first go through authentication and usage metering.
>
> The AI agent determines the user's intent and selects the appropriate tool. For network security analysis, the system uses a machine-learning model and then an LLM to generate a human-readable explanation.
>
> If credits are exhausted, the metering layer triggers the HTTP 402 payment flow.

---

## 4. Authentication Demo — 30 seconds

**Open:**

```text
http://127.0.0.1:8000/docs
```

**Show:**

`Authorize` → `X-API-Key`

**What to say:**

> SentinelL402 uses API-key authentication. The API key is stored securely as a hash in the database rather than storing the raw key.
>
> The client sends the key using the `X-API-Key` HTTP header.

**Important:**

Never show the actual API key during the presentation.

Use:

```text
<YOUR_API_KEY>
```

in screenshots or documentation.

---

## 5. Security Analysis Demo — 60 seconds

**Open Swagger:**

```text
http://127.0.0.1:8000/docs
```

Find:

```text
POST /api/security/analyze
```

Use the complete request stored in:

```text
backend/data/final_l402_request.json
```

**What to say:**

> This endpoint performs network security analysis.
>
> The request contains 78 network-flow features derived from the CIC-IDS2017 dataset.
>
> The machine-learning model analyzes these features and predicts whether the traffic is benign or malicious.

Example result:

```json
{
  "ml_prediction": 0,
  "ml_label": "BENIGN",
  "confidence": 1.0,
  "risk_level": "LOW"
}
```

Then explain:

> The ML result is combined with an LLM-generated explanation and recommendation so that the output is easier for a human operator to understand.

---

## 6. AI Agent Demo — 45 seconds

Find:

```text
POST /api/agent/run
```

Use the complete request stored in:

```text
backend/data/agent_security_request.json
```

**What to say:**

> Instead of directly calling the security-analysis endpoint, we can use the SentinelL402 AI agent.
>
> The agent first identifies the intent as a security-analysis request.
>
> It then selects the `analyze_network_security` tool.
>
> The tool validates the arguments, performs the machine-learning analysis, generates the LLM explanation, and returns the final result.

Show the response:

```text
action: analyze_security
tool: analyze_network_security
ml_label: BENIGN
risk_level: LOW
```

---

## 7. HTTP 402 + Lightning Demo — 60 seconds

This is the most important part of the demonstration.

**First explain:**

> Every successful security-analysis request consumes credits.

When credits reach zero:

```text
HTTP 402 Payment Required
```

is returned.

The response contains information such as:

```json
{
  "payment_id": 55,
  "amount_sats": 10,
  "credits_to_add": 5
}
```

**Do not display a real invoice or secret during a public presentation.**

**What to say:**

> Instead of simply rejecting the request, SentinelL402 generates a Lightning payment request.
>
> The user pays the required amount using the configured Lightning wallet.
>
> The backend then verifies the payment using Nostr Wallet Connect.

Show conceptually:

```text
Credits = 0
     |
     v
API Request
     |
     v
HTTP 402
     |
     v
Lightning Invoice
     |
     v
User Payment
     |
     v
Payment Verification
     |
     v
+5 Credits
     |
     v
API Request Works Again
```

---

## 8. Payment Verification Demo — 30 seconds

Use:

```text
POST /api/payment/verify/{payment_id}
```

**What to say:**

> After the Lightning payment is completed, the payment verification endpoint checks the payment status.
>
> When the payment is confirmed, the user's credits are restored.

Example safe presentation output:

```json
{
  "payment_id": 55,
  "status": "paid",
  "credits_added": 5,
  "credits_remaining": 4
}
```

---

## 9. Docker Demo — 20 seconds

Show the terminal:

```powershell
docker compose ps
```

Expected:

```text
sentinell402-api    Up    (healthy)
```

Then:

```powershell
curl.exe http://127.0.0.1:8000/health
```

Expected:

```json
{
  "status": "healthy"
}
```

Then:

```powershell
curl.exe http://127.0.0.1:8000/ready
```

Expected:

```json
{
  "status": "ready",
  "database": "ok"
}
```

**What to say:**

> The application is containerized using Docker. The API container runs as a non-root user and includes health and readiness checks.

---

## 10. Testing and CI — 20 seconds

Show:

```powershell
pytest backend/tests -q
```

Expected:

```text
94 passed
```

Then show GitHub Actions.

**What to say:**

> The project also includes automated tests and GitHub Actions CI. The backend test suite currently contains 94 passing tests, covering authentication, API behavior, payments, metering, agent functionality, and other components.

---

# Complete End-to-End Flow

The entire SentinelL402 workflow is:

```text
                    ┌─────────────────┐
                    │      User       │
                    └────────┬────────┘
                             │
                             v
                    ┌─────────────────┐
                    │   API Request   │
                    └────────┬────────┘
                             │
                             v
                    ┌─────────────────┐
                    │ API Key Auth    │
                    └────────┬────────┘
                             │
                             v
                    ┌─────────────────┐
                    │ Credit Check    │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
               Credits > 0       Credits = 0
                    │                 │
                    v                 v
             ┌────────────┐    ┌────────────┐
             │ AI Agent   │    │ HTTP 402   │
             └─────┬──────┘    └─────┬──────┘
                   │                  │
                   v                  v
          ┌────────────────┐   ┌───────────────┐
          │ Security Tool │   │ Lightning     │
          └───────┬────────┘   │ Payment       │
                  │             └───────┬───────┘
                  v                     │
          ┌────────────────┐            v
          │ ML Prediction  │      ┌────────────┐
          └───────┬────────┘      │ Verification│
                  │               └──────┬─────┘
                  v                      │
          ┌────────────────┐             v
          │ LLM Explanation│       Credits Added
          └───────┬────────┘             │
                  │                      │
                  └──────────┬───────────┘
                             v
                    ┌─────────────────┐
                    │ Final Response  │
                    └─────────────────┘
```

# Final Conclusion — 30 seconds

**What to say:**

> To conclude, SentinelL402 demonstrates how AI services can be combined with usage-based metering and Bitcoin Lightning micropayments.
>
> The project integrates FastAPI, API-key authentication, database-backed credit management, an AI agent, machine-learning security analysis, LLM explanations, HTTP 402, Lightning payments, Docker, automated testing, and CI.
>
> The main concept demonstrated by this project is **pay-per-use AI services powered by Lightning payments**.

# If the Examiner Asks: "What Is the Main Innovation?"

Answer:

> The main idea is combining HTTP 402 payment-required semantics with Lightning micropayments and AI API metering. Instead of requiring a traditional subscription, the service can request payment when the user's usage credits are exhausted.

# If the Examiner Asks: "Why Lightning?"

Answer:

> Lightning is suitable for this type of system because it is designed for fast Bitcoin payments and supports small-value payments, which fits a metered API or pay-per-use model.

# If the Examiner Asks: "Why HTTP 402?"

Answer:

> HTTP 402 Payment Required provides a natural protocol-level signal that a request cannot continue until payment requirements are satisfied.

# If the Examiner Asks: "Why Use an AI Agent?"

Answer:

> The agent provides an orchestration layer. It can understand the user's intent, select the appropriate tool, validate the arguments, and execute the required AI or security operation.

# If the Examiner Asks: "What Machine Learning Model Did You Use?"

Answer:

> The security-analysis pipeline uses a Random Forest classifier trained using network-flow features derived from the CIC-IDS2017 dataset.

# If the Examiner Asks: "What Does the LLM Do?"

Answer:

> The machine-learning model produces the security prediction, while the LLM converts that result into a more understandable security analysis and recommendation.

# If the Examiner Asks: "How Is Security Handled?"

Answer:

> The system uses API-key authentication, hashed API keys, authenticated-user-based credit metering, payment ownership checks, input validation, Docker security hardening, non-root execution, and automated tests.

# Important Presentation Security Rules

Never display:

```text
API keys
NWC connection strings
Lightning invoices
wallet credentials
database passwords
OpenAI API keys
Alby tokens
.env contents
```

Use placeholders:

```text
<YOUR_API_KEY>
<LIGHTNING_INVOICE>
<SECRET>
```

# Final One-Sentence Project Description

> **SentinelL402 is a metered AI security API that combines AI agents, machine-learning threat analysis, LLM explanations, HTTP 402, and Bitcoin Lightning micropayments to enable pay-per-use AI services.**
