import io
from dataclasses import dataclass

import pandas as pd

from app.domain.schemas import ValidationSummary


@dataclass
class ValidationResult:
    dataframe: pd.DataFrame
    summary: ValidationSummary


class ValidationError(Exception):
    pass


def validate_csv(
    csv_content: str,
    datetime_column: str,
    target_column: str,
) -> ValidationResult:
    try:
        df = pd.read_csv(io.StringIO(csv_content))
    except Exception as exc:
        raise ValidationError(f"Could not parse CSV: {exc}") from exc

    if datetime_column not in df.columns:
        raise ValidationError(f"Missing datetime column: {datetime_column}")
    if target_column not in df.columns:
        raise ValidationError(f"Missing target column: {target_column}")

    df[datetime_column] = pd.to_datetime(df[datetime_column], errors="coerce")
    if df[datetime_column].isna().all():
        raise ValidationError(f"Column {datetime_column} has no valid timestamps")

    df = df.dropna(subset=[datetime_column]).sort_values(datetime_column)
    if df.empty:
        raise ValidationError("No rows remain after datetime parsing")

    missing = {col: int(df[col].isna().sum()) for col in df.columns}
    preview = df.head(5).astype(str).to_dict(orient="records")

    summary = ValidationSummary(
        row_count=len(df),
        datetime_column=datetime_column,
        target_column=target_column,
        start_date=str(df[datetime_column].min()),
        end_date=str(df[datetime_column].max()),
        missing_values=missing,
        preview_rows=preview,
    )
    return ValidationResult(dataframe=df, summary=summary)
