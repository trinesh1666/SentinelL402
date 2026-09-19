from typing import Dict, List

from app.ml.model_loader import load_random_forest


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

MODEL = load_random_forest()


# ============================================================
# GET EXACT MODEL FEATURES
# ============================================================

def get_required_features() -> List[str]:
    """
    Return the exact 78 features expected by
    the trained Random Forest model.
    """

    if not hasattr(MODEL, "feature_names_in_"):
        raise RuntimeError(
            "Random Forest model does not contain "
            "feature names."
        )

    return list(MODEL.feature_names_in_)


# ============================================================
# VALIDATE FEATURES
# ============================================================

def validate_features(
    features: Dict[str, float]
) -> None:
    """
    Check whether all required model features
    are present.
    """

    required_features = get_required_features()

    missing_features = [
        feature
        for feature in required_features
        if feature not in features
    ]

    if missing_features:

        raise ValueError(
            "Missing required ML features:\n"
            + "\n".join(missing_features)
        )


# ============================================================
# BUILD FEATURE VECTOR
# ============================================================

def build_feature_vector(
    features: Dict[str, float]
) -> List[float]:
    """
    Convert feature dictionary into the exact
    feature order expected by Random Forest.
    """

    validate_features(features)

    required_features = get_required_features()

    return [
        float(features[feature])
        for feature in required_features
    ]