"""All communication with the FastAPI backend lives here (no HTTP code in the UI files)."""
import base64
from typing import Optional

import requests

from config import API_URL

TIMEOUT = 60


class APIError(Exception):
    """Raised when the backend is unreachable or returns an error."""


def _handle(response: requests.Response):
    if response.ok:
        return response
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text
    raise APIError(f"{response.status_code}: {detail}")


def _request(method: str, path: str, **kwargs):
    try:
        return _handle(requests.request(method, f"{API_URL}{path}", timeout=TIMEOUT, **kwargs))
    except requests.exceptions.ConnectionError:
        raise APIError(f"Cannot reach the backend at {API_URL}. Is it running?")
    except requests.exceptions.Timeout:
        raise APIError("The backend took too long to respond.")


def get_health() -> Optional[dict]:
    try:
        return _request("GET", "/api/health").json()
    except APIError:
        return None


def predict_image(filename: str, data: bytes, content_type: str) -> dict:
    files = {"file": (filename, data, content_type)}
    result = _request("POST", "/api/predict", files=files).json()
    result["heatmap_bytes"] = base64.b64decode(result["heatmap_base64"])
    return result


def get_history(limit: int = 100) -> list:
    return _request("GET", "/api/history", params={"limit": limit}).json()


def get_stats() -> dict:
    return _request("GET", "/api/stats").json()


def get_image(inspection_id: int, kind: str) -> bytes:
    """kind = 'original' or 'heatmap'"""
    return _request("GET", f"/api/history/{inspection_id}/{kind}").content


def delete_inspection(inspection_id: int) -> None:
    _request("DELETE", f"/api/history/{inspection_id}")
