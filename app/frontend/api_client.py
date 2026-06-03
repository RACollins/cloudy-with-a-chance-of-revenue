import os

import httpx

API_BASE_URL = os.getenv("CLOUDY_API_URL", "http://127.0.0.1:8000")


def preprocess(payload: dict) -> dict:
    with httpx.Client(base_url=API_BASE_URL, timeout=60.0) as client:
        response = client.post("/preprocess", json=payload)
        response.raise_for_status()
        return response.json()


def get_status(job_id: str) -> dict:
    with httpx.Client(base_url=API_BASE_URL, timeout=30.0) as client:
        response = client.get(f"/status/{job_id}")
        response.raise_for_status()
        return response.json()


def approve_merge(job_id: str) -> dict:
    with httpx.Client(base_url=API_BASE_URL, timeout=60.0) as client:
        response = client.post("/approve-merge", json={"job_id": job_id})
        response.raise_for_status()
        return response.json()


def run_forecast(job_id: str, horizon: int = 7) -> dict:
    with httpx.Client(base_url=API_BASE_URL, timeout=120.0) as client:
        response = client.post("/forecast", json={"job_id": job_id, "horizon": horizon})
        response.raise_for_status()
        return response.json()
