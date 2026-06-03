from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.domain.job_status import JobStatus


class UserMetadata(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    business_name: str = Field(min_length=1, max_length=200)
    location_lat: float = Field(ge=-90, le=90)
    location_lon: float = Field(ge=-180, le=180)


class ValidationSummary(BaseModel):
    row_count: int
    datetime_column: str
    target_column: str
    start_date: str
    end_date: str
    missing_values: dict[str, int] = Field(default_factory=dict)
    weather_columns_added: list[str] = Field(default_factory=list)
    preview_rows: list[dict[str, Any]] = Field(default_factory=list, max_length=5)


class PreprocessRequest(BaseModel):
    user_metadata: UserMetadata
    csv_content: str
    datetime_column: str = "timestamp"
    target_column: str = "value"


class PreprocessResponse(BaseModel):
    job_id: str
    job_status: JobStatus
    validation_summary: ValidationSummary


class JobRecord(BaseModel):
    job_id: str
    job_status: JobStatus
    user_metadata: UserMetadata
    s3_raw_path: str | None = None
    s3_merged_path: str | None = None
    s3_model_path: str | None = None
    s3_feature_importance_path: str | None = None
    s3_forecast_path: str | None = None
    validation_summary: ValidationSummary | None = None
    sagemaker_training_job_name: str | None = None
    merge_approved_at: datetime | None = None
    forecast_approved_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ApproveMergeRequest(BaseModel):
    job_id: str


class ApproveForecastRequest(BaseModel):
    job_id: str
    horizon: int = Field(default=7, ge=1, le=90)


class ForecastRequest(BaseModel):
    job_id: str
    horizon: int = Field(default=7, ge=1, le=90)


class ForecastPoint(BaseModel):
    timestamp: str
    prediction: float


class ForecastResponse(BaseModel):
    job_id: str
    job_status: JobStatus
    forecast: list[ForecastPoint]


class FeatureImportanceItem(BaseModel):
    name: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    job_id: str
    features: list[FeatureImportanceItem]
