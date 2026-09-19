# SentinelL402 — L402 Payment Flow

## 1. Overview

SentinelL402 uses HTTP 402 Payment Required as a payment boundary for metered AI functionality.

The core idea is:

```text
Use AI credits
      |
      v
Credits available?
      |
      +---- YES ----> Execute AI request
      |
      +---- NO -----> HTTP 402
                         |
                         v
                   Lightning invoice
                         |
                         v
                       Payment
                         |
                         v
                   Verification
                         |
                         v
                    Add credits
                         |
                         v
                       Retry
                         |
                         v
                    AI response