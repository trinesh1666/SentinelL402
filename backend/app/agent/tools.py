from typing import Any, Dict

from app.schemas.security_analysis import (
    SecurityAnalysisRequest,
)
from app.services.metered_security_service import (
    run_metered_security_analysis,
)


def analyze_network_security(
    db,
    authenticated_user: str,
    source: str,
    event_type: str,
    severity: str,
    description: str,
    features: Dict[str, float],
) -> Dict[str, Any]:

    request = SecurityAnalysisRequest(
        source=source,
        event_type=event_type,
        severity=severity,
        description=description,
        features=features,
    )

    # Run the existing metered ML security analysis.
    result = run_metered_security_analysis(
        db,
        request,
        authenticated_user,
    )

    result_data = result.model_dump()

    # Generate grounded LLM analysis using the ML result.
    from app.services.llm_service import analyze_security_event

    llm_response = analyze_security_event(
        event_type=event_type,
        severity=severity,
        description=description,
        ml_prediction=result_data["ml_prediction"],
        ml_label=result_data["ml_label"],
        confidence=result_data["confidence"],
        risk_level=result_data["risk_level"],
        ml_explanation=result_data["explanation"],
        ml_recommendation=result_data["recommendation"],
    )

    result_data["llm_analysis"] = llm_response

    return result_data