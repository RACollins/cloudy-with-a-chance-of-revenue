"""Export AutoGluon feature importance to JSON contract."""


def export_feature_importance_stub(job_id: str) -> dict:
    return {
        "job_id": job_id,
        "features": [
            {"name": "temperature_2m_max", "importance": 0.35},
            {"name": "precipitation_sum", "importance": 0.28},
            {"name": "windspeed_10m_max", "importance": 0.15},
            {"name": "temperature_2m_min", "importance": 0.12},
            {"name": "value_lag_7", "importance": 0.10},
        ],
    }


def export_feature_importance(predictor, job_id: str) -> dict:
    """Real implementation: call predictor.feature_importance() and normalize."""
    importance = predictor.feature_importance()
    features = [
        {"name": str(name), "importance": float(value)}
        for name, value in importance.items()
    ]
    return {"job_id": job_id, "features": features}
