# SentinelL402 Architecture

## 1. Overview

SentinelL402 is a metered AI cybersecurity platform.

The system combines:

- FastAPI
- API-key authentication
- AI agent routing
- Local LLM inference
- Machine-learning security detection
- Usage metering
- HTTP 402 Payment Required
- Bitcoin Lightning payments
- Payment verification
- SQLite
- Web frontend

The architecture is designed around a payment-gated AI service model.

---

# 2. High-Level Architecture

```text
                         ┌─────────────────────┐
                         │       Client        │
                         │                     │
                         │ Frontend / API      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │      Gateway        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Authentication      │
                         │     X-API-Key       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Sentinel Agent   │
                         │                     │
                         │ Intent + Tool       │
                         │ Routing             │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Tool Validation   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Metering Layer    │
                         │                     │
                         │ Check AI credits    │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
              Credits available                 Credits exhausted
                    │                                │
                    ▼                                ▼
          ┌──────────────────┐             ┌──────────────────┐
          │ Security        │             │ HTTP 402         │
          │ Analysis        │             │ Payment Required │
          └────────┬─────────┘             └────────┬─────────┘
                   │                                │
                   │                                ▼
                   │                         Lightning Invoice
                   │                                │
                   │                                ▼
                   │                         Lightning Payment
                   │                                │
                   │                                ▼
                   │                         Payment Verification
                   │                                │
                   │                                ▼
                   │                           +5 Credits
                   │                                │
                   │                                ▼
                   │                              Retry
                   │
                   ▼
          ┌──────────────────┐
          │ Random Forest    │
          │ Security Model   │
          └────────┬─────────┘
                   │
                   ▼
             ML Prediction
                   │
                   ▼
          ┌──────────────────┐
          │ Security Result  │
          └────────┬─────────┘
                   │
                   ▼
                Client