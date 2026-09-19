from app.ml.feature_processor import get_required_features
from app.ml.predictor import predict_attack


def create_test_features():
    return {
        feature: 0.0
        for feature in get_required_features()
    }


def test_feature_count():
    features = get_required_features()

    assert len(features) == 78


def test_prediction_returns_valid_result():
    features = create_test_features()

    result = predict_attack(features)

    assert "prediction" in result
    assert "label" in result
    assert "confidence" in result
    assert "probabilities" in result

    assert result["prediction"] in [0, 1]
    assert result["label"] in ["BENIGN", "DDoS"]

    assert 0.0 <= result["confidence"] <= 1.0

    assert len(result["probabilities"]) == 2