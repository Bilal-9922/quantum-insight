import ast


# Common Qiskit QuantumCircuit methods that represent
# supported circuit operations.
SUPPORTED_GATES = {
    "h",
    "x",
    "y",
    "z",
    "s",
    "sdg",
    "t",
    "tdg",
    "sx",
    "sxdg",
    "id",
    "reset",
    "measure",
    "measure_all",
    "barrier",
    "cx",
    "cy",
    "cz",
    "ch",
    "swap",
    "iswap",
    "ecr",
    "ccx",
    "cswap",
    "rx",
    "ry",
    "rz",
    "p",
    "phase",
    "u",
    "u1",
    "u2",
    "u3",
}


def run_qiskit_check(code: str):
    """
    Perform static Qiskit circuit validation.

    This does not execute arbitrary user Python.
    It checks:
    - Python syntax
    - QuantumCircuit size
    - unsupported gate names
    - qubit indices
    - invalid string parameters
    """

    if not code or not code.strip():
        return {
            "success": False,
            "error_type": "GENERAL_ERROR",
            "error": "No code was supplied.",
        }

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
    # Find QuantumCircuit size
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
    # Find gate calls
    # ---------------------------------------------------------

    gate_calls = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Attribute):
            continue

        gate_name = node.func.attr.lower()

        ignored_methods = {
            "draw",
            "decompose",
            "depth",
            "count_ops",
            "remove_final_measurements",
        }

        if gate_name in ignored_methods:
            continue

        # Only inspect methods called on an object.
        # This covers common code such as qc.h(...).
        if not isinstance(node.func.value, ast.Name):
            continue

        object_name = node.func.value.id.lower()

        if object_name not in {
            "qc",
            "circuit",
            "quantum_circuit",
        }:
            continue

        gate_calls.append({
            "gate": gate_name,
            "args": node.args,
            "line": getattr(node, "lineno", None),
        })

    # ---------------------------------------------------------
    # Gate validation
    # ---------------------------------------------------------

    for call in gate_calls:
        gate = call["gate"]

        if gate not in SUPPORTED_GATES:
            return {
                "success": False,
                "error_type": "GATE_ERROR",
                "error": (
                    f"Unknown or unsupported gate "
                    f"'{gate}'."
                ),
                "line": call["line"],
                "gate": gate,
                "qubits": qubits,
            }

    # ---------------------------------------------------------
    # Qubit index validation
    # ---------------------------------------------------------

    for call in gate_calls:
        gate = call["gate"]
        qubit_positions = _qubit_positions(gate)

        for position in qubit_positions:
            if position >= len(call["args"]):
                continue

            index = _constant_int(call["args"][position])

            if index is None:
                continue

            if index < 0 or index >= qubits:
                return {
                    "success": False,
                    "error_type": "QUBIT_INDEX_ERROR",
                    "error": (
                        f"Qubit index {index} is out of range "
                        f"for a circuit with {qubits} qubit(s)."
                    ),
                    "line": call["line"],
                    "gate": gate,
                    "qubit": index,
                    "qubits": qubits,
                }

    # ---------------------------------------------------------
    # Parameter validation
    # ---------------------------------------------------------

    for call in gate_calls:
        gate = call["gate"]
        parameter_positions = _parameter_positions(gate)

        for position in parameter_positions:
            if position >= len(call["args"]):
                continue

            parameter = call["args"][position]

            if isinstance(parameter, ast.Constant):
                if isinstance(parameter.value, str):
                    return {
                        "success": False,
                        "error_type": "PARAMETER_ERROR",
                        "error": (
                            f"Invalid parameter value for "
                            f"{gate} gate."
                        ),
                        "line": call["line"],
                        "gate": gate,
                        "qubits": qubits,
                    }

    return {
        "success": True,
        "error_type": None,
        "error": None,
        "qubits": qubits,
        "message": "No obvious Qiskit circuit error was detected.",
    }


def _qubit_positions(gate):
    single_qubit_gates = {
        "h",
        "x",
        "y",
        "z",
        "s",
        "sdg",
        "t",
        "tdg",
        "sx",
        "sxdg",
        "id",
        "reset",
        "measure",
    }

    two_qubit_gates = {
        "cx",
        "cy",
        "cz",
        "ch",
        "swap",
        "iswap",
        "ecr",
    }

    three_qubit_gates = {
        "ccx",
        "cswap",
    }

    parameterized_one_qubit_gates = {
        "rx",
        "ry",
        "rz",
        "p",
        "phase",
        "u",
        "u1",
        "u2",
        "u3",
    }

    if gate in single_qubit_gates:
        return [0]

    if gate in two_qubit_gates:
        return [0, 1]

    if gate in three_qubit_gates:
        return [0, 1, 2]

    if gate in parameterized_one_qubit_gates:
        return [1]

    return []


def _parameter_positions(gate):
    parameterized_gates = {
        "rx": [0],
        "ry": [0],
        "rz": [0],
        "p": [0],
        "phase": [0],
        "u": [0, 1, 2],
        "u1": [0],
        "u2": [0, 1],
        "u3": [0, 1, 2],
    }

    return parameterized_gates.get(gate, [])


def _constant_int(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, int):
            return node.value

    if isinstance(node, ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            value = _constant_int(node.operand)

            if value is not None:
                return -value

    return None
