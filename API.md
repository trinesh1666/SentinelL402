# SentinelL402 API Documentation

## 1. Overview

SentinelL402 exposes a FastAPI-based HTTP API for:

- Network security analysis
- AI-agent execution
- API-key authentication
- Usage metering
- Lightning payment creation
- Lightning payment verification
- Credit management

Base URL during local development:

```text
http://127.0.0.1:8000

## L402 Payment Flow

SentinelL402 uses HTTP 402 Payment Required when a user's AI credits are exhausted.

### 1. Make an AI request

The authenticated client sends a request to:

`POST /api/security/analyze`

or:

`POST /api/agent/run`

The API identifies the user from the `X-API-Key` header.

The client-supplied `user_id` is not authoritative for authentication.

### 2. Credits available

If the authenticated user has at least one credit:

```text
Request
  ↓
Authentication
  ↓
Credit check
  ↓
Security analysis / Agent
  ↓
Consume 1 credit
  ↓
HTTP 200