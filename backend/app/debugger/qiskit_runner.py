import ast
import re


def run_qiskit_check(code: str):
    """
    Safely perform static Qiskit circuit validation.

    This does NOT execute arbitrary user Python.
    It inspects common QuantumCircuit construction patterns
    and detects invalid qubit references.
    """

    if not code or not code.strip():
        return {
            "success": False,
            "error_type": "GENERAL_ERROR",
            "error": "No code was supplied.",
        }

    # ---------------------------------------------------------
    # Step 1: Python syntax validation
    # ---------------------------------------------------------

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "success": False,
            "error_type": "SYNTAX_ERROR",
            "error": e.msg,
            "line": e.lineno,
        }

    # ---------------------------------------------------------
    # Step 2: Find QuantumCircuit size
    # ---------------------------------------------------------

    qubits = None

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Name):
            continue

        if node.func.id != "QuantumCircuit":
            continue

        if not node.args:
            continue

        value = _constant_int(node.args[0])

        if value is not None:
            qubits = value
            break

    if qubits is None:
        return {
            "success": True,
            "error_type": None,
            "error": None,
            "qubits": None,
            "message": (
                "Python syntax is valid, but the debugger could not "
                "determine the QuantumCircuit size."
            ),
        }

    # ---------------------------------------------------------
    # Step 3: Inspect gate calls
    # ---------------------------------------------------------

    gate_calls = []

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Attribute):
            continue

        gate_name = node.func.attr.lower()

        if gate_name in {
            "measure_all",
            "draw",
            "decompose",
            "depth",
            "count_ops",
        }:
            continue

        indices = []

        for arg in node.args:
            value = _constant_int(arg)

            if value is not None:
                indices.append(value)

        if not indices:
            continue

        gate_calls.append(
            {
                "gate": gate_name,
                "indices": indices,
                "line": getattr(node, "lineno", None),
            }
        )

    # ---------------------------------------------------------
    # Step 4: Detect invalid qubit indices
    # ---------------------------------------------------------

    for call in gate_calls:

        for index in call["indices"]:

            # Negative values are also invalid qubit indices.
            if index < 0 or index >= qubits:

                return {
                    "success": False,
                    "error_type": "QUBIT_INDEX_ERROR",
                    "error": (
                        f"Qubit index {index} is out of range "
                        f"for a circuit with {qubits} qubit(s)."
                    ),
                    "line": call["line"],
                    "gate": call["gate"],
                    "qubit": index,
                    "qubits": qubits,
                }

    # ---------------------------------------------------------
    # Step 5: Valid circuit structure
    # ---------------------------------------------------------

    return {
        "success": True,
        "error_type": None,
        "error": None,
        "qubits": qubits,
        "message": "No obvious qubit-index error was detected.",
    }


def _constant_int(node):
    """
    Return an integer for simple literal integer expressions.

    Supported:
        0
        1
        -1

    Other expressions are intentionally ignored.
    """

    if isinstance(node, ast.Constant):
        if isinstance(node.value, int):
            return node.value

    if isinstance(node, ast.UnaryOp):

        if isinstance(node.op, ast.USub):
            value = _constant_int(node.operand)

            if value is not None:
                return -value

    return None
