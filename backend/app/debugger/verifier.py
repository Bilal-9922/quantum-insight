from app.circuit.validator import validate_python
from app.debugger.qiskit_runner import run_qiskit_check


def verify(code):
    # Step 1: Check Python syntax
    syntax = validate_python(code)

    if not syntax["valid"]:
        return {
            "verified": False,
            "syntax": syntax,
            "circuit": {
                "valid": False,
                "error": syntax["error"],
            },
        }

    # Step 2: Check Qiskit-specific circuit structure
    circuit = run_qiskit_check(code)

    return {
        "verified": circuit.get("success", False),
        "syntax": syntax,
        "circuit": circuit,
    }
