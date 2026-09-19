from sqlalchemy.orm import Session

from app.schemas.security_analysis import (
    SecurityAnalysisRequest,
    SecurityAnalysisResponse
)

from app.ml.predictor import predict_attack

from app.services.metering_service import (
    get_usage
)


def perform_security_analysis(
    db: Session,
    request: SecurityAnalysisRequest
) -> SecurityAnalysisResponse:

    # Run Random Forest
    ml_result = predict_attack(
        request.features
    )

    label = ml_result["label"]

    confidence = ml_result.get(
        "confidence"
    )

    probabilities = ml_result.get(
        "probabilities"
    )

    # Determine risk
    if label == "DDoS":

        risk_level = "HIGH"

        explanation = (
            "The machine learning detector "
            "identified the network flow as DDoS traffic."
        )

        recommendation = (
            "Investigate the source immediately "
            "and apply traffic filtering or "
            "rate-limiting controls."
        )

    else:

        risk_level = "LOW"

        explanation = (
            "The machine learning detector "
            "classified the network flow as benign."
        )

        recommendation = (
            "No immediate malicious activity "
            "was detected. Continue monitoring "
            "the network flow."
        )

    # Get remaining credits
    usage = get_usage(
        db,
        request.source
    )

    return SecurityAnalysisResponse(

        source=request.source,

        event_type=request.event_type,

        ml_prediction=ml_result["prediction"],

        ml_label=label,

        confidence=confidence,

        probabilities=probabilities,

        risk_level=risk_level,

        explanation=explanation,

        recommendation=recommendation,

        credits_remaining=usage[
            "credits_remaining"
        ]
    )