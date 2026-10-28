"""POST /api/predict  -> upload an image, get normal/defective + confidence + Grad-CAM."""
import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.config import ALLOWED_TYPES, MAX_UPLOAD_MB
from app.database import get_db
from app.ml.predictor import predictor
from app.models import Inspection
from app.schemas import PredictionResponse
from app.utils import to_base64, to_jpeg_bytes

router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=PredictionResponse)
def predict(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type '{file.content_type}'. Upload a PNG or JPG image.")

    data = file.file.read()
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File too large (max {MAX_UPLOAD_MB} MB).")

    try:
        image = Image.open(io.BytesIO(data)).convert("RGB")
    except (UnidentifiedImageError, OSError):
        raise HTTPException(400, "That file is not a valid image.")

    if not predictor.is_loaded:
        raise HTTPException(503, "Model is not trained yet. Train it first (see README).")

    result = predictor.predict(image)

    original_jpg = to_jpeg_bytes(image)
    heatmap_jpg = to_jpeg_bytes(Image.fromarray(result.heatmap_rgb))

    record = Inspection(
        filename=file.filename or "uploaded_image",
        prediction=result.label,
        confidence=result.confidence,
        normal_prob=result.normal_prob,
        defective_prob=result.defective_prob,
        original_jpg=original_jpg,
        heatmap_jpg=heatmap_jpg,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return PredictionResponse(
        id=record.id,
        filename=record.filename,
        prediction=record.prediction,
        confidence=record.confidence,
        normal_prob=record.normal_prob,
        defective_prob=record.defective_prob,
        created_at=record.created_at,
        heatmap_base64=to_base64(heatmap_jpg),
    )
