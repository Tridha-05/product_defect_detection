"""Database tables."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, LargeBinary, String

from app.database import Base


def _now():
    return datetime.now(timezone.utc)


class Inspection(Base):
    """One row = one image that a user inspected."""

    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    prediction = Column(String(20), nullable=False)       # "normal" or "defective"
    confidence = Column(Float, nullable=False)            # 0..1
    normal_prob = Column(Float, nullable=False)
    defective_prob = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, index=True)
    # Small JPEG copies stored INSIDE the database -> survive redeploys
    original_jpg = Column(LargeBinary, nullable=False)
    heatmap_jpg = Column(LargeBinary, nullable=False)
