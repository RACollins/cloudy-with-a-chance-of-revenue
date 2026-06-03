"""Open-Meteo weather fetcher (stub-friendly for skeleton)."""

from datetime import date

import pandas as pd


WEATHER_COLUMNS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "windspeed_10m_max",
]


def fetch_daily_weather(
    lat: float,
    lon: float,
    start: date,
    end: date,
) -> pd.DataFrame:
    """Fetch daily historical weather. Returns skeleton stub when offline."""
    date_range = pd.date_range(start=start, end=end, freq="D")
    return pd.DataFrame(
        {
            "date": date_range,
            **{col: 0.0 for col in WEATHER_COLUMNS},
        }
    )


def fetch_daily_weather_live(
    lat: float,
    lon: float,
    start: date,
    end: date,
) -> pd.DataFrame:
    """Fetch real ERA5-backed data via Open-Meteo when network is available."""
    import openmeteo_requests
    import requests_cache
    from retry_requests import retry

    cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
    retry_session = retry(cache_session, retries=3, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": WEATHER_COLUMNS,
        "timezone": "UTC",
    }
    responses = openmeteo.weather_api(url, params=params)
    daily = responses[0].Daily()
    data = {"date": pd.date_range(
        start=pd.to_datetime(daily.Time(), unit="s", utc=True),
        periods=daily.Time().shape[0],
        freq="D",
    )}
    for idx, col in enumerate(WEATHER_COLUMNS):
        data[col] = daily.Variables(idx).ValuesAsNumpy()
    return pd.DataFrame(data)
