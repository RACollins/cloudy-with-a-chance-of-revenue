from enum import StrEnum


class JobStatus(StrEnum):
    """Job lifecycle states with human-in-the-loop gates."""

    PROCESSING = "PROCESSING"
    AWAITING_MERGE_APPROVAL = "AWAITING_MERGE_APPROVAL"
    TRAINING = "TRAINING"
    AWAITING_FORECAST_APPROVAL = "AWAITING_FORECAST_APPROVAL"
    FORECASTING = "FORECASTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
