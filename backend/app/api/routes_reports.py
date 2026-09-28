from fastapi import APIRouter
from pydantic import BaseModel
from app.reports.generator import generate_report

router = APIRouter(tags=["reports"])

class ReportRequest(BaseModel):
    analysis: dict

@router.post("/report")
def report(req: ReportRequest):
    return generate_report(req.analysis)
