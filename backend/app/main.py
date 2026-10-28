"""FastAPI entry point.  Run:  uvicorn app.main:app --reload"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app import models  # noqa: F401  (makes sure tables are registered)
from app.config import ALLOWED_ORIGINS
from app.database import Base, SessionLocal, engine
from app.ml.predictor import predictor
from app.routers import history, predict
from app.schemas import HealthOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)   # creates the tables automatically if missing
    predictor.load()                        # loads the trained ResNet50 (if it exists)
    yield


app = FastAPI(
    title="AI Product Defect Detection API",
    description="Upload a product image -> Normal / Defective + confidence + Grad-CAM.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, prefix="/api")
app.include_router(history.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Defect Detection API is running. Open /docs for the interactive docs."}


@app.get("/api/health", response_model=HealthOut, tags=["Health"])
def health():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:  # pragma: no cover
        db_status = f"error: {exc}"
    return HealthOut(
        status="ok",
        model_loaded=predictor.is_loaded,
        device=str(predictor.device),
        database=db_status,
    )
