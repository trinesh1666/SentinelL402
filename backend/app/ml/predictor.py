from typing import Dict, Any

import pandas as pd

from app.ml.model_loader import load_random_forest
from app.ml.feature_processor import (
    build_feature_vector,
    get_required_features
)
from app.ml.class_mapping import get_class_name


MODEL = load_random_forest()


def predict_attack(
    features: Dict[str, float]
) -> Dict[str, Any]:
    """
    Run the trained Random Forest model
    using the exact 78 feature names.
    """

    feature_names = get_required_features()

    feature_vector = build_feature_vector(
        features
    )

    X = pd.DataFrame(
        [feature_vector],
        columns=feature_names
    )

    prediction = MODEL.predict(X)

    prediction_number = int(
        prediction[0]
    )

    result = {
        "prediction": prediction_number,
        "label": get_class_name(
            prediction_number
        )
    }

    if hasattr(MODEL, "predict_proba"):

        probabilities = MODEL.predict_proba(X)

        result["probabilities"] = (
            probabilities[0].tolist()
        )

        result["confidence"] = float(
            probabilities[0].max()
        )

    return result