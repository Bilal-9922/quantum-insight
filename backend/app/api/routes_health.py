from fastapi import APIRouter
from pydantic import BaseModel
from app.health.scoring import calculate_qhi

router = APIRouter(tags=["health"])

class MetricsRequest(BaseModel):
    metrics: dict

@router.post("/health")
def health(req: MetricsRequest):
    return calculate_qhi(req.metrics)
