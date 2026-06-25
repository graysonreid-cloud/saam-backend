from fastapi import APIRouter
from app.engine.perceptron_predict import load_model

router = APIRouter()

@router.get("/saam/model")
def inspect_model():
    """
    Returns perceptron weights, bias, and feature importance.
    Helps explain how SAAM makes decisions.
    """
    model = load_model()

    weights = model.coef_[0].tolist()
    bias = float(model.intercept_[0])

    features = ["comments", "assignments", "transitions"]
    feature_importance = {
        feature: weight for feature, weight in zip(features, weights)
    }

    return {
        "model_type": "Perceptron",
        "weights": feature_importance,
        "bias": bias,
        "decision_rule": (
            "label = 1 (healthy) if dot(weights, features) + bias > 0 "
            "else 0 (low_collaboration)"
        )
    }
