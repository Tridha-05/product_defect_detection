"""History + stats endpoints (reads from the database)."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Inspection
from app.schemas import InspectionOut, StatsOut

router = APIRouter(tags=["History"])


@router.get("/history", response_model=List[InspectionOut])
def list_history(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Inspection)
        .order_by(Inspection.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return rows


@router.get("/history/{inspection_id}", response_model=InspectionOut)
def get_one(inspection_id: int, db: Session = Depends(get_db)):
    row = db.get(Inspection, inspection_id)
    if not row:
        raise HTTPException(404, "Inspection not found")
    return row


@router.get("/history/{inspection_id}/original")
def get_original(inspection_id: int, db: Session = Depends(get_db)):
    row = db.get(Inspection, inspection_id)
    if not row:
        raise HTTPException(404, "Inspection not found")
    return Response(content=row.original_jpg, media_type="image/jpeg")


@router.get("/history/{inspection_id}/heatmap")
def get_heatmap(inspection_id: int, db: Session = Depends(get_db)):
    row = db.get(Inspection, inspection_id)
    if not row:
        raise HTTPException(404, "Inspection not found")
    return Response(content=row.heatmap_jpg, media_type="image/jpeg")


@router.delete("/history/{inspection_id}")
def delete_one(inspection_id: int, db: Session = Depends(get_db)):
    row = db.get(Inspection, inspection_id)
    if not row:
        raise HTTPException(404, "Inspection not found")
    db.delete(row)
    db.commit()
    return {"deleted": inspection_id}


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Inspection.id)).scalar() or 0
    defective = (
        db.query(func.count(Inspection.id)).filter(Inspection.prediction == "defective").scalar() or 0
    )
    avg_conf = db.query(func.avg(Inspection.confidence)).scalar() or 0.0
    return StatsOut(
        total=total,
        normal=total - defective,
        defective=defective,
        defect_rate=(defective / total) if total else 0.0,
        avg_confidence=float(avg_conf),
    )
