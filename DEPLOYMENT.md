# SentinelL402 Deployment Guide

## 1. Overview

SentinelL402 is currently designed as a local development and demonstration system.

The current deployment stack consists of:

- FastAPI backend
- Python virtual environment
- SQLite database
- Ollama local LLM
- Random Forest ML model
- Lightning / Nostr Wallet Connect integration
- HTML/CSS/JavaScript frontend

The current development architecture is:

```text
Browser
   |
   v
Frontend
   |
   v
FastAPI API
   |
   +--------------------+
   |                    |
   v                    v
Authentication       Sentinel Agent
   |                    |
   |                    +----> LLM Router
   |                    |
   |                    +----> Security Tool
   |                               |
   |                               v
   |                         ML Security Model
   |
   +----> Metering
   |
   +----> Payment Service
               |
               v
        Lightning / NWC
               |
               v
        Payment Verification
               |
               v
          Credit Grant