# SentinelL402

## Metered AI Cybersecurity Intelligence Agent

SentinelL402 is a real-world cybersecurity AI platform that combines:

- Machine Learning
- Large Language Models
- AI agents
- FastAPI
- API-key authentication
- Usage metering
- HTTP 402 Payment Required
- Bitcoin Lightning payments
- Payment verification
- Automatic retry after payment
- SQLite
- Web dashboard

The goal of SentinelL402 is to provide cybersecurity intelligence as a
metered AI service.

Users receive a limited number of AI credits. When credits are exhausted,
the API returns an HTTP 402 response containing a Bitcoin Lightning invoice.
After the invoice is paid and verified, additional credits are granted and
the user can retry the request.

---

# Project Vision

Traditional AI APIs usually charge through subscriptions or conventional
payment systems.

SentinelL402 explores a different model:

```text
AI capability
     +
usage metering
     +
HTTP 402
     +
Bitcoin Lightning micropayments