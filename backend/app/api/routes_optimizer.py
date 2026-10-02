from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.optimizer.optimizer import optimize_code
from app.auth import current_user

from app.circuit.parser import (
    parse_qiskit_code,
    UnsupportedQuantumCodeError,
)


router = APIRouter(tags=["optimizer"])


class OptimizeRequest(BaseModel):
    code: str


@router.post("/optimize")
def optimize(req: OptimizeRequest, user=Depends(current_user)):

    # ---------------------------------------------------------
    # Validate that the submitted source is real Qiskit code
    # ---------------------------------------------------------

    try:
        parse_qiskit_code(req.code)

    except UnsupportedQuantumCodeError as exc:
        return {
            "success": False,
            "error": {
                "type": "UNSUPPORTED_QUANTUM_CODE",
                "message": str(exc),
            },
            "message": str(exc),
        }

    # ---------------------------------------------------------
    # Run the optimizer only for valid Qiskit code
    # ---------------------------------------------------------

    try:
        result = optimize_code(req.code)

        # Make sure the response always identifies
        # the request as a successful optimization.
        if isinstance(result, dict):
            result.setdefault("success", True)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
