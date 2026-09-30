from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.debugger.ast_analyzer import analyze_ast
from app.auth import current_user
from app.debugger.classifier import classify
from app.debugger.ai_debugger import diagnose
from app.debugger.patch_generator import generate_patch
from app.debugger.verifier import verify
from app.debugger.qiskit_runner import run_qiskit_check

router = APIRouter(tags=["debugger"])

class DebugRequest(BaseModel):
    code: str
    error: str | None = None
    language: str = "python"

@router.post("/debug")
def debug(req: DebugRequest, user=Depends(current_user)):
    # Analyze the Python structure
    ast_result = analyze_ast(req.code)

    # Run static Qiskit-specific validation
    runner_result = run_qiskit_check(req.code)

    # Prefer the error discovered from the submitted code.
    # Fall back to the manually supplied error when necessary.
    detected_error = runner_result.get("error")

    error_message = detected_error or req.error

    eerror_type = runner_result.get("error_type")

    if not error_type:
        if (
            not error_message
            and runner_result.get("success") is True
        ):
            error_type = "NO_ERROR"
        else:
            error_type = classify(error_message)

    # Generate diagnosis using the detected error
    diagnosis = diagnose(
        req.code,
        error_message
    )

    # Generate patch
    patch = generate_patch(
        req.code,
        error_message
    )

    # Verify the resulting code
    verification = verify(
        patch["fixed_code"]
    )

    return {
        "success": True,
        "ast": ast_result,
        "runner": runner_result,
        "error": {
            "type": error_type,
            "message": error_message,
        },
        **diagnosis,
        **patch,
        **verification,
    }
