# SentinelL402 Architecture

## 1. Project Overview

SentinelL402 is an AI-powered metered API platform that combines:

- FastAPI
- API-key authentication
- Usage and credit metering
- HTTP 402 Payment Required
- Lightning Network payments
- Nostr Wallet Connect (NWC)
- AI agent intent routing
- Machine-learning-based network security detection
- Local LLM analysis using Ollama
- SQLite/PostgreSQL database support
- Docker
- Alembic migrations
- Automated testing and GitHub Actions CI

The project demonstrates how AI API usage can be connected to
machine-to-machine Lightning payments through the HTTP 402/L402
payment flow.

---

## 2. High-Level Architecture

```text
Client
   |
   | X-API-Key
   v
FastAPI API
   |
   +----------------------+
   |                      |
   v                      v
Authentication       Credit Metering
   |                      |
   +----------+-----------+
              |
              v
        SentinelL402 Agent
              |
              +-------------------+
              |                   |
              v                   v
       Intent Classification   Tool Selection
                                  |
                                  v
                       Security Analysis Tool
                                  |
                                  v
                       78 Network Features
                                  |
                                  v
                       ML Security Detector
                                  |
                                  v
                         Random Forest
                                  |
                                  v
                         ML Prediction
                                  |
                                  v
                           Local LLM
                            Ollama
                                  |
                                  v
                    Explanation + Recommendation