from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.optimizer.optimizer import optimize_code

router = APIRouter(tags=["optimizer"])

class OptimizeRequest(BaseModel):
    code: str

@router.post("/optimize")
def optimize(req: OptimizeRequest):
    try:
        return optimize_code(req.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
