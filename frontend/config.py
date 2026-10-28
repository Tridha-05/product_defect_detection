"""Frontend settings."""
import os

# Where the FastAPI backend lives. Change via environment variable when deployed.
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

GREEN = "#16a34a"
RED = "#dc2626"
