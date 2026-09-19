from typing import Any, cast

from app.middleware.request_logging import request_logging_middleware
from app.config import CORS_ORIGINS
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.services.auth_service import get_authenticated_user

from app.agent.agent import SentinelAgent
from app.agent.models import AgentRequest


from app.schemas.agent import (
    AgentRequestSchema,
    AgentResponseSchema,
)

from app.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
)

from app.schemas.llm import (
    SecurityEvent,
    LLMAnalysis,
)

from app.services.rate_limit_dependency import check_rate_limit

from app.services.llm_service import (
    analyze_security_event,
)
from app.services.metering_service import (
    can_use_ai,
    consume_credit,
    get_usage,
    get_or_create_user,
)

from app.schemas.security_analysis import (
    SecurityAnalysisRequest,
    SecurityAnalysisResponse,
)

from app.services.metered_security_service import (
    run_metered_security_analysis,
)

from app.services.payment_service import (
    create_payment,
    verify_payment,
)

from app.schemas.payment import (
    PaymentRequiredResponse,
    PaymentCreateResponse,
    PaymentVerifyResponse,
)

# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="SentinelL402 API",
    version="0.2.0",
)

app.middleware("http")(request_logging_middleware)

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "project": "SentinelL402",
        "status": "running",
        "version": "0.2.0",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
# ============================================================
# USAGE ENDPOINT
# ============================================================

@app.get("/api/usage/{user_id}")
def usage(
    user_id: str,
    authenticated_user_id: str = Security(
        get_authenticated_user
    ),
    db: Session = Depends(get_db),
):
    if user_id != authenticated_user_id:
        raise HTTPException(
            status_code=403,
            detail=(
                "You are not authorized to view "
                "this user's usage."
            ),
        )

    return get_usage(
        db,
        authenticated_user_id,
    )

@app.post(
    "/api/auth/register",
    response_model=RegisterResponse,
    status_code=201,
)
def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(models.User)
        .filter(
            models.User.user_id == request.user_id
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User already exists.",
        )

    user = get_or_create_user(
        db,
        request.user_id,
    )

    cast(Any, user).email = request.email

    db.commit()
    db.refresh(user)

    from app.services.api_key_service import create_api_key

    raw_api_key, api_key_record = create_api_key(
        db=db,
        user_id=request.user_id,
        name=request.api_key_name,
    )

    account = (
        db.query(models.Account)
        .filter(
            models.Account.user_id == user.id
        )
        .first()
    )

    return RegisterResponse(
        user_id=cast(str, user.user_id),
        email=cast(Any, user.email),
        api_key=raw_api_key,
        api_key_name=cast(str, api_key_record.name),
        initial_credits=(
            cast(int, account.credits)
            if account
            else 5
        ),
        message=(
            "Registration successful. "
            "Store this API key securely because "
            "it will not be shown again."
        ),
    )

# ============================================================
# BASIC AI ANALYSIS ENDPOINT
# ============================================================

@app.post(
    "/api/analyze",
    response_model=LLMAnalysis,
    responses={
        402: {
            "model": PaymentRequiredResponse,
            "description": "Lightning payment required",
        },
    },
)
def analyze(
    event: SecurityEvent,
    authenticated_user_id: str = Security(
        get_authenticated_user
    ),
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # AUTHORIZATION
    # --------------------------------------------------------

    if event.source != authenticated_user_id:
        raise HTTPException(
            status_code=403,
            detail=(
                "You are not authorized to analyze "
                "events for this user."
            ),
        )

    user_id = authenticated_user_id

    # --------------------------------------------------------
    # STEP 1: CHECK CREDITS
    # --------------------------------------------------------

    if not bool(can_use_ai(
        db,
        user_id,
    )):
        raise HTTPException(
            status_code=402,
            detail={
                "error": "payment_required",
                "message": "AI credits exhausted.",
                "payment_method": "lightning",
                "amount_sats": 10,
            },
        )

    # --------------------------------------------------------
    # STEP 2: CONSUME ONE CREDIT
    # --------------------------------------------------------

    success = consume_credit(
        db,
        user_id,
    )

    if not success:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "payment_required",
                "message": "Insufficient AI credits.",
                "payment_method": "lightning",
                "amount_sats": 10,
            },
        )

    # --------------------------------------------------------
    # STEP 3: RUN AI ANALYSIS
    # --------------------------------------------------------

    result = analyze_security_event(
        event.event_type,
        event.severity,
        event.description,
    )

    # --------------------------------------------------------
    # STEP 4: RETURN RESULT
    # --------------------------------------------------------

    return result


# ============================================================
# METERED SECURITY ANALYSIS ENDPOINT
# ============================================================
@app.post(
    "/api/security/analyze",
    response_model=SecurityAnalysisResponse,
    responses={
        402: {
            "model": PaymentRequiredResponse,
            "description": "Lightning payment required",
        },
    },
)
def security_analyze(
    request: SecurityAnalysisRequest,
    db: Session = Depends(get_db),
    authenticated_user: str = Depends(get_authenticated_user),
):
    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------
    # authenticated_user comes from the X-API-Key.
    # request.source is the security-data source
    # (for example: CIC-IDS2017), NOT the user identity.

    # --------------------------------------------------------
    # METERING + PAYMENT + ML ANALYSIS
    # --------------------------------------------------------

    return run_metered_security_analysis(
        db,
        request,
        authenticated_user,
    )

# ============================================================
# PAYMENT CREATION ENDPOINT
# ============================================================

@app.post(
    "/api/payment/create",
    response_model=PaymentCreateResponse,
)
def create_payment_endpoint(
    authenticated_user_id: str = Security(
        get_authenticated_user
    ),
    db: Session = Depends(get_db),
):
    payment = create_payment(
        db,
        authenticated_user_id,
    )

    return {
        "payment_id": payment.id,
        "user_id": authenticated_user_id,
        "amount_sats": payment.amount_sats,
        "invoice": payment.invoice,
        "payment_hash": payment.payment_hash,
        "status": payment.status,
        "credits_to_add": 5,
    }


# ============================================================
# PAYMENT VERIFICATION ENDPOINT
# ============================================================

@app.post(
    "/api/payment/verify/{payment_id}",
    response_model=PaymentVerifyResponse,
)
def payment_verify(
    payment_id: int,
    authenticated_user_id: str = Security(
        get_authenticated_user
    ),
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # STEP 1: FIND PAYMENT
    # --------------------------------------------------------

    payment_record = (
        db.query(models.Payment)
        .filter(
            models.Payment.id == payment_id
        )
        .first()
    )

    if not payment_record:
        raise HTTPException(
            status_code=404,
            detail="Payment not found.",
        )

    # --------------------------------------------------------
    # STEP 2: FIND PAYMENT OWNER
    # --------------------------------------------------------

    payment_owner = (
        db.query(models.User)
        .filter(
            models.User.id
            == payment_record.user_id
        )
        .first()
    )

    if not payment_owner:
        raise HTTPException(
            status_code=404,
            detail="Payment owner not found.",
        )

    # --------------------------------------------------------
    # STEP 3: AUTHORIZATION
    # --------------------------------------------------------

    if cast(str, payment_owner.user_id) != authenticated_user_id:
        raise HTTPException(
            status_code=403,
            detail=(
                "You are not authorized to verify "
                "this payment."
            ),
        )

    # --------------------------------------------------------
    # STEP 4: VERIFY LIGHTNING PAYMENT
    # --------------------------------------------------------

    payment = verify_payment(
        db,
        payment_id,
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found.",
        )

    # --------------------------------------------------------
    # STEP 5: GET USER ACCOUNT
    # --------------------------------------------------------

    account = (
        db.query(models.Account)
        .filter(
            models.Account.user_id
            == payment.user_id
        )
        .first()
    )

    # --------------------------------------------------------
    # STEP 6: RETURN PAYMENT STATUS
    # --------------------------------------------------------

    return {
        "payment_id": payment.id,
        "user_id": authenticated_user_id,
        "amount_sats": payment.amount_sats,
        "status": payment.status,
        "credits_added": payment.credits_granted,
        "credits_remaining": (
            account.credits
            if account
            else 0
        ),
    }


# ============================================================
# AGENT ENDPOINT
# ============================================================

@app.post(
    "/api/agent/run",
    response_model=AgentResponseSchema,
    responses={
        402: {
            "model": PaymentRequiredResponse,
            "description": "Lightning payment required",
        },
    },
)
def run_agent(
    request: AgentRequestSchema,
    authenticated_user_id: str = Security(
        get_authenticated_user
    ),
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # IMPORTANT:
    # Always use the authenticated user identity.
    # Do not trust request.user_id from the client.
    # --------------------------------------------------------

    agent_request = AgentRequest(
        user_id=authenticated_user_id,
        intent=request.intent,
        parameters=request.parameters,
    )

    # --------------------------------------------------------
    # CREATE AGENT
    # --------------------------------------------------------

    agent = SentinelAgent(db)

    # --------------------------------------------------------
    # RUN AGENT
    # --------------------------------------------------------

    result = agent.run(
        agent_request
    )

    # --------------------------------------------------------
    # RETURN AGENT RESPONSE
    # --------------------------------------------------------

    return AgentResponseSchema(
        action=result.action,
        tool=result.tool,
        result=result.result,
    )