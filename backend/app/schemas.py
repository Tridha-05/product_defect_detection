"""Shapes of the JSON the API sends back."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InspectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    prediction: str
    confidence: float
    normal_prob: float
    defective_prob: float
    created_at: datetime


class PredictionResponse(InspectionOut):
    heatmap_base64: str  # Grad-CAM overlay as base64 JPEG


class StatsOut(BaseModel):
    total: int
    normal: int
    defective: int
    defect_rate: float
    avg_confidence: float


class HealthOut(BaseModel):
    status: str
    model_loaded: bool
    device: str
    database: str
