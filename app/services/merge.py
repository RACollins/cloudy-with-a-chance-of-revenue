import pandas as pd

from app.domain.schemas import ValidationSummary
from app.services.weather import WEATHER_COLUMNS, fetch_daily_weather


def merge_weather(
    df: pd.DataFrame,
    summary: ValidationSummary,
    lat: float,
    lon: float,
) -> tuple[pd.DataFrame, ValidationSummary]:
    dt_col = summary.datetime_column
    start = pd.to_datetime(summary.start_date).date()
    end = pd.to_datetime(summary.end_date).date()
    weather = fetch_daily_weather(lat, lon, start, end)
    weather["merge_date"] = weather["date"].dt.normalize()
    merged = df.copy()
    merged["merge_date"] = pd.to_datetime(merged[dt_col]).dt.normalize()
    merged = merged.merge(weather.drop(columns=["date"]), on="merge_date", how="left")
    merged = merged.drop(columns=["merge_date"])

    updated = summary.model_copy(
        update={"weather_columns_added": list(WEATHER_COLUMNS)}
    )
    return merged, updated
