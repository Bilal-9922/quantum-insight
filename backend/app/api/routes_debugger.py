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


def contains_qiskit_circuit_code(code: str) -> bool:
    """
    Detect whether the submitted source appears to be intended
    as real Qiskit QuantumCircuit code.

    This is intentionally a lightweight check.

    We do NOT parse the code here because the Debugger must be
    able to receive syntactically invalid Qiskit code and diagnose
    the syntax error.
    """

    qiskit_markers = [
        "from qiskit import QuantumCircuit",
        "from qiskit import",
        "import qiskit",
        "QuantumCircuit(",
        "qiskit.QuantumCircuit(",
    ]

    return any(marker in code for marker in qiskit_markers)


@router.post("/debug")
def debug(req: DebugRequest, user=Depends(current_user)):

    # ---------------------------------------------------------
    # 1. Reject clearly non-Qiskit / pseudo quantum code
    # ---------------------------------------------------------
    #
    # IMPORTANT:
    # We only perform a lightweight recognition check here.
    #
    # We intentionally DO NOT call parse_qiskit_code().
    #
    # This allows malformed Qiskit code such as:
    #
    #     qc.h(0
    #
    # to reach the debugger and be diagnosed as a syntax error.
    #
    if not contains_qiskit_circuit_code(req.code):
        message = (
            "Unsupported code. QuantumInsight currently supports "
            "valid Python code containing a Qiskit QuantumCircuit."
        )

        return {
            "success": False,
            "error": {
                "type": "UNSUPPORTED_QUANTUM_CODE",
                "message": message,
            },
            "message": message,
        }

    # ---------------------------------------------------------
    # 2. Analyze the submitted source
    # ---------------------------------------------------------
    #
    # analyze_ast() may detect syntax problems. That information
    # is intentionally preserved for the debugger pipeline.
    #
    try:
        ast_result = analyze_ast(req.code)
    except Exception as exc:
        ast_result = {
            "success": False,
            "error": str(exc),
        }

    # ---------------------------------------------------------
    # 3. Run the Qiskit validation / execution check
    # ---------------------------------------------------------
    #
    # This is where syntax errors and other Qiskit/Python
    # problems should be detected.
    #
    runner_result = run_qiskit_check(req.code)

    detected_error = runner_result.get("error")
    error_message = detected_error or req.error
    error_type = runner_result.get("error_type")

    # ---------------------------------------------------------
    # 4. Determine the error type
    # ---------------------------------------------------------
    if not error_type:

        if not error_message and runner_result.get("success") is True:
            error_type = "NO_ERROR"

        else:
            error_type = classify(error_message)

    # ---------------------------------------------------------
    # 5. AI diagnosis
    # ---------------------------------------------------------
    diagnosis = diagnose(
        req.code,
        error_message,
    )

    # ---------------------------------------------------------
    # 6. Generate correction
    # ---------------------------------------------------------
    patch = generate_patch(
        req.code,
        error_message,
    )

    # ---------------------------------------------------------
    # 7. Verify generated correction
    # ---------------------------------------------------------
    verification = verify(
        patch["fixed_code"]
    )

    # ---------------------------------------------------------
    # 8. Return normal debugger response
    # ---------------------------------------------------------
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
