"""Lambda-compatible inference handler (skeleton)."""

import json
from typing import Any


def predict(model_artifact_path: str, horizon: int = 7) -> list[dict[str, Any]]:
    """Load model and predict. Stub returns synthetic series."""
    _ = model_artifact_path
    return [
        {"timestamp": f"day+{i}", "prediction": 100.0 + i}
        for i in range(1, horizon + 1)
    ]


def lambda_handler(event: dict, context: object) -> dict:
    body = json.loads(event.get("body", "{}"))
    horizon = int(body.get("horizon", 7))
    forecast = predict(body.get("model_path", ""), horizon=horizon)
    return {
        "statusCode": 200,
        "body": json.dumps({"forecast": forecast}),
    }
