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
    Detect whether the submitted source contains a real
    Qiskit QuantumCircuit reference.

    Important:
    We must NOT use simple substring matching for
    "QuantumCircuit(" because fake classes such as:

        PseudoQuantumCircuit

    would incorrectly match it.

    The debugger intentionally uses recognition instead of
    full parsing here so malformed Qiskit code can still reach
    the debugger and be diagnosed as a syntax error.
    """

    import re

    source = code or ""

    # ---------------------------------------------------------
    # 1. Real Qiskit imports
    # ---------------------------------------------------------

    import_patterns = [
        r"\bfrom\s+qiskit\s+import\s+QuantumCircuit\b",
        r"\bimport\s+qiskit\b",
        r"\bfrom\s+qiskit\s+import\b",
    ]

    for pattern in import_patterns:
        if re.search(pattern, source):
            return True

    # ---------------------------------------------------------
    # 2. Real Qiskit QuantumCircuit constructor
    # ---------------------------------------------------------
    #
    # Match:
    #
    # QuantumCircuit(...)
    #
    # qiskit.QuantumCircuit(...)
    #
    # But DO NOT match:
    #
    # PseudoQuantumCircuit(...)
    # MyQuantumCircuit(...)
    # FakeQuantumCircuit(...)
    #
    constructor_patterns = [
        r"(?<![A-Za-z0-9_])QuantumCircuit\s*\(",
        r"\bqiskit\.QuantumCircuit\s*\(",
    ]

    for pattern in constructor_patterns:
        if re.search(pattern, source):
            return True

    return False


@router.post("/debug")
def debug(
    req: DebugRequest,
    user=Depends(current_user),
):

    # ---------------------------------------------------------
    # 1. Reject clearly non-Qiskit / pseudo quantum code
    # ---------------------------------------------------------
    #
    # We intentionally DO NOT call parse_qiskit_code() here.
    #
    # The Debugger must be able to receive malformed Qiskit
    # code such as:
    #
    #     qc.h(0
    #
    # and diagnose it as a syntax error.
    #
    # Therefore, this first stage only determines whether the
    # submitted code appears to contain real Qiskit code.
    # ---------------------------------------------------------

    if not contains_qiskit_circuit_code(req.code):

        message = (
            "Unsupported code. QuantumInsight currently supports "
            "valid Python code containing a real Qiskit QuantumCircuit."
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
    # analyze_ast() can detect Python syntax problems.
    #
    # This information is preserved even if the code contains
    # a syntax error.
    # ---------------------------------------------------------

    try:
        ast_result = analyze_ast(req.code)

    except Exception as exc:
        ast_result = {
            "success": False,
            "error": str(exc),
        }

    # ---------------------------------------------------------
    # 3. Run Qiskit validation / debugging checks
    # ---------------------------------------------------------
    #
    # This stage detects:
    #
    # - Syntax errors
    # - Qubit index errors
    # - Classical bit errors
    # - Gate argument errors
    # - Undefined variables
    # - Unsupported gates
    # - Parameter problems
    # - Other Qiskit-related errors
    # ---------------------------------------------------------

    rdetected_error = runner_result.get("error")
    runner_success = runner_result.get("success") is True
    
    # ---------------------------------------------------------
    # The Qiskit runner is the authoritative validation layer.
    #
    # If Qiskit successfully validates the submitted circuit,
    # do not allow a manually supplied/stale error message to
    # turn a valid circuit into GENERAL_ERROR.
    # ---------------------------------------------------------


    # ---------------------------------------------------------
    # 4. Determine the error type
    # ---------------------------------------------------------

    if runner_success and not detected_error:
        error_message = None
        error_type = "NO_ERROR"
    
    else:
        error_message = detected_error or req.error
    
        error_type = runner_result.get("error_type")
    
        if not error_type:
            error_type = classify(error_message)

    # ---------------------------------------------------------
    # 5. AI diagnosis
    # ---------------------------------------------------------

    diagnosis = diagnose(
        req.code,
        error_message,
    )

    # ---------------------------------------------------------
    # 6. Generate suggested correction
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
    # 8. Return complete debugger response
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
