from app.circuit.validator import validate_python
from app.debugger.qiskit_runner import run_qiskit_check


def verify(code):
    """
    Verify a proposed Qiskit fix.

    Verification has two stages:

    1. Python syntax validation.
    2. QuantumCircuit structural validation.

    The result is considered verified only when BOTH stages pass.
    """

    source = code or ""

    # ---------------------------------------------------------
    # 1. Python syntax
    # ---------------------------------------------------------

    syntax = validate_python(source)

    if not syntax.get("valid", False):
        return {
            "verified": False,
            "syntax": syntax,
            "circuit": {
                "valid": False,
                "success": False,
                "error": syntax.get("error"),
            },
        }

    # ---------------------------------------------------------
    # 2. Qiskit circuit validation
    # ---------------------------------------------------------

    circuit = run_qiskit_check(source)

    circuit_valid = bool(
        circuit.get("success", False)
    )

    return {
        "verified": circuit_valid,
        "syntax": syntax,
        "circuit": circuit,
    }
