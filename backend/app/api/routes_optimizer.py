from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.optimizer.optimizer import optimize_code
from app.auth import current_user

router = APIRouter(tags=["optimizer"])

class OptimizeRequest(BaseModel):
    code: str

@router.post("/optimize")
def optimize(req: OptimizeRequest, user=Depends(current_user)):
    try:
        return optimize_code(req.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
