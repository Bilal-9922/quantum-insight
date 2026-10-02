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


# Expected number of arguments for each gate.
#
# This includes both parameter arguments and qubit arguments.
EXPECTED_ARGUMENTS = {
    "h": 1,
    "x": 1,
    "y": 1,
    "z": 1,
    "s": 1,
    "sdg": 1,
    "t": 1,
    "tdg": 1,
    "sx": 1,
    "sxdg": 1,
    "id": 1,
    "reset": 1,

    "measure": 2,

    "cx": 2,
    "cy": 2,
    "cz": 2,
    "ch": 2,
    "swap": 2,
    "iswap": 2,
    "ecr": 2,

    "ccx": 3,
    "cswap": 3,

    "rx": 2,
    "ry": 2,
    "rz": 2,
    "p": 2,
    "phase": 2,

    "u": 4,
    "u1": 2,
    "u2": 3,
    "u3": 4,
}


def run_qiskit_check(code: str):
    """
    Perform static Qiskit circuit validation.

    This does not execute arbitrary user Python.

    Checks:
    - Python syntax
    - QuantumCircuit size
    - QuantumCircuit variable names
    - undefined circuit variables
    - unsupported gates
    - incorrect gate argument counts
    - qubit indices
    - classical-bit indices
    - undefined variables used as indices
    - invalid string parameters
    """

    if not code or not code.strip():
        return {
            "success": False,
            "error_type": "GENERAL_ERROR",
            "error": "No code was supplied.",
        }

    # ---------------------------------------------------------
    # Python syntax
    # ---------------------------------------------------------

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {
            "success": False,
            "error_type": "SYNTAX_ERROR",
            "error": f"{e.msg}",
            "line": e.lineno,
            "column": e.offset,
        }

    # ---------------------------------------------------------
    # Collect variables defined in the source
    # ---------------------------------------------------------

    defined_names = _collect_defined_names(tree)

    # ---------------------------------------------------------
    # Find QuantumCircuit variables and sizes
    # ---------------------------------------------------------

    circuit_names = set()
    qubits = None
    classical_bits = 0

    for node in ast.walk(tree):

        if not isinstance(node, ast.Assign):
            continue

        if not isinstance(node.value, ast.Call):
            continue

        if not _is_quantum_circuit_call(node.value):
            continue

        # Example:
        #
        # qc = QuantumCircuit(2)
        #
        for target in node.targets:
            if isinstance(target, ast.Name):
                circuit_names.add(target.id)

        if node.value.args:

            first_value = _constant_int(node.value.args[0])

            if first_value is not None:
                qubits = first_value

        # QuantumCircuit(2, 2)
        #
        # Second positional argument represents
        # the number of classical bits.
        if len(node.value.args) >= 2:

            second_value = _constant_int(node.value.args[1])

            if second_value is not None:
                classical_bits = second_value

        # Handle keyword form:
        #
        # QuantumCircuit(2, 2, name="bell")
        #
        # No extra handling is needed for classical bits
        # because the first two positional arguments are
        # the normal Qiskit constructor form.

    # Also recognize:
    #
    # circuit = QuantumCircuit(2)
    #
    # even if the assignment is nested or unusual.
    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if not _is_quantum_circuit_call(node):
            continue

        if not node.args:
            continue

        value = _constant_int(node.args[0])

        if value is not None and qubits is None:
            qubits = value

        if len(node.args) >= 2:
            classical_value = _constant_int(node.args[1])

            if classical_value is not None:
                classical_bits = classical_value

    # If no circuit could be identified, let the route-level
    # Qiskit detection handle unsupported source.
    if qubits is None:
        return {
            "success": True,
            "error_type": None,
            "error": None,
            "qubits": None,
            "classical_bits": classical_bits,
            "message": (
                "Python syntax is valid, but the debugger could not "
                "determine the QuantumCircuit size."
            ),
        }

    # ---------------------------------------------------------
    # Find circuit operation calls
    # ---------------------------------------------------------

    gate_calls = []

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Attribute):
            continue

        gate_name = node.func.attr.lower()

        if gate_name not in SUPPORTED_GATES:
            continue

        if not isinstance(node.func.value, ast.Name):
            continue

        object_name = node.func.value.id

        gate_calls.append(
            {
                "gate": gate_name,
                "object": object_name,
                "args": node.args,
                "keywords": node.keywords,
                "line": getattr(node, "lineno", None),
            }
        )

    # ---------------------------------------------------------
    # Circuit variable validation
    # ---------------------------------------------------------

    for call in gate_calls:

        object_name = call["object"]

        # Example:
        #
        # circuit = QuantumCircuit(2)
        # qc.h(0)
        #
        # qc was never defined.
        if object_name not in circuit_names:

            return {
                "success": False,
                "error_type": "NAME_ERROR",
                "error": (
                    f"Name '{object_name}' is not defined as a "
                    f"QuantumCircuit."
                ),
                "line": call["line"],
                "name": object_name,
                "qubits": qubits,
                "classical_bits": classical_bits,
            }

    # ---------------------------------------------------------
    # Gate argument count validation
    # ---------------------------------------------------------

    for call in gate_calls:

        gate = call["gate"]

        # measure_all() has no required positional arguments.
        if gate == "measure_all":

            if len(call["args"]) != 0:

                return {
                    "success": False,
                    "error_type": "GATE_ARGUMENT_ERROR",
                    "error": (
                        "measure_all() does not accept positional "
                        "arguments."
                    ),
                    "line": call["line"],
                    "gate": gate,
                    "qubits": qubits,
                    "classical_bits": classical_bits,
                }

            continue

        expected = EXPECTED_ARGUMENTS.get(gate)

        if expected is None:
            continue

        actual = len(call["args"])

        if actual != expected:

            return {
                "success": False,
                "error_type": "GATE_ARGUMENT_ERROR",
                "error": (
                    f"Gate '{gate}' expects {expected} argument(s), "
                    f"but {actual} were provided."
                ),
                "line": call["line"],
                "gate": gate,
                "expected_arguments": expected,
                "actual_arguments": actual,
                "qubits": qubits,
                "classical_bits": classical_bits,
            }

    # ---------------------------------------------------------
    # Unsupported gate validation
    # ---------------------------------------------------------

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Attribute):
            continue

        gate_name = node.func.attr.lower()

        if gate_name in {
            "draw",
            "decompose",
            "depth",
            "count_ops",
            "remove_final_measurements",
            "remove_final_measurement",
        }:
            continue

        if not isinstance(node.func.value, ast.Name):
            continue

        object_name = node.func.value.id

        # Only inspect methods called on actual circuit variables.
        if object_name not in circuit_names:
            continue

        if gate_name not in SUPPORTED_GATES:

            return {
                "success": False,
                "error_type": "GATE_ERROR",
                "error": (
                    f"Unknown or unsupported gate '{gate_name}'."
                ),
                "line": getattr(node, "lineno", None),
                "gate": gate_name,
                "qubits": qubits,
                "classical_bits": classical_bits,
            }

    # ---------------------------------------------------------
    # Qubit index validation
    # ---------------------------------------------------------

    for call in gate_calls:

        gate = call["gate"]

        for position in _qubit_positions(gate):

            if position >= len(call["args"]):
                continue

            argument = call["args"][position]

            # Constant integer
            index = _constant_int(argument)

            if index is not None:

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
                        "classical_bits": classical_bits,
                    }

                continue

            # A variable such as:
            #
            # qc.x(qubit)
            #
            # should be checked.
            if isinstance(argument, ast.Name):

                variable_name = argument.id

                if variable_name not in defined_names:

                    return {
                        "success": False,
                        "error_type": "NAME_ERROR",
                        "error": (
                            f"Name '{variable_name}' is not defined."
                        ),
                        "line": call["line"],
                        "gate": gate,
                        "name": variable_name,
                        "qubits": qubits,
                        "classical_bits": classical_bits,
                    }

    # ---------------------------------------------------------
    # Classical-bit validation for measure()
    # ---------------------------------------------------------

    for call in gate_calls:

        if call["gate"] != "measure":
            continue

        if len(call["args"]) < 2:
            continue

        classical_argument = call["args"][1]

        classical_index = _constant_int(classical_argument)

        if classical_index is not None:

            if (
                classical_index < 0
                or classical_index >= classical_bits
            ):

                return {
                    "success": False,
                    "error_type": "CLASSICAL_BIT_INDEX_ERROR",
                    "error": (
                        f"Classical bit index {classical_index} "
                        f"is out of range for a circuit with "
                        f"{classical_bits} classical bit(s)."
                    ),
                    "line": call["line"],
                    "gate": "measure",
                    "classical_bit": classical_index,
                    "classical_bits": classical_bits,
                    "qubits": qubits,
                }

        elif isinstance(classical_argument, ast.Name):

            variable_name = classical_argument.id

            if variable_name not in defined_names:

                return {
                    "success": False,
                    "error_type": "NAME_ERROR",
                    "error": (
                        f"Name '{variable_name}' is not defined."
                    ),
                    "line": call["line"],
                    "gate": "measure",
                    "name": variable_name,
                    "qubits": qubits,
                    "classical_bits": classical_bits,
                }

    # ---------------------------------------------------------
    # Parameter validation
    # ---------------------------------------------------------

    for call in gate_calls:

        gate = call["gate"]

        for position in _parameter_positions(gate):

            if position >= len(call["args"]):
                continue

            parameter = call["args"][position]

            # Explicit string parameter
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
                        "classical_bits": classical_bits,
                    }

            # Undefined parameter variable
            if isinstance(parameter, ast.Name):

                variable_name = parameter.id

                if variable_name not in defined_names:

                    return {
                        "success": False,
                        "error_type": "NAME_ERROR",
                        "error": (
                            f"Name '{variable_name}' is not defined."
                        ),
                        "line": call["line"],
                        "gate": gate,
                        "name": variable_name,
                        "qubits": qubits,
                        "classical_bits": classical_bits,
                    }

    return {
        "success": True,
        "error_type": None,
        "error": None,
        "qubits": qubits,
        "classical_bits": classical_bits,
        "message": "No obvious Qiskit circuit error was detected.",
    }


# =============================================================
# Helper functions
# =============================================================

def _is_quantum_circuit_call(node):
    if not isinstance(node, ast.Call):
        return False

    if isinstance(node.func, ast.Name):
        return node.func.id == "QuantumCircuit"

    if isinstance(node.func, ast.Attribute):
        return (
            isinstance(node.func.value, ast.Name)
            and node.func.value.id == "qiskit"
            and node.func.attr == "QuantumCircuit"
        )

    return False


def _collect_defined_names(tree):
    """
    Collect names that have been defined in the submitted source.
    """

    names = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name):
                    names.add(target.id)

        elif isinstance(node, ast.AnnAssign):

            if isinstance(node.target, ast.Name):
                names.add(node.target.id)

        elif isinstance(node, ast.AugAssign):

            if isinstance(node.target, ast.Name):
                names.add(node.target.id)

        elif isinstance(node, ast.For):

            if isinstance(node.target, ast.Name):
                names.add(node.target.id)

        elif isinstance(node, ast.FunctionDef):
            names.add(node.name)

        elif isinstance(node, ast.ClassDef):
            names.add(node.name)

        elif isinstance(node, ast.Import):

            for alias in node.names:

                if alias.asname:
                    names.add(alias.asname)
                else:
                    names.add(alias.name.split(".")[0])

        elif isinstance(node, ast.ImportFrom):

            for alias in node.names:

                if alias.asname:
                    names.add(alias.asname)
                else:
                    names.add(alias.name)

    return names


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

        # Parameterized one-qubit gates have the
        # qubit argument after their parameters.
        if gate in {"rx", "ry", "rz", "p", "phase"}:
            return [1]

        if gate == "u":
            return [3]

        if gate == "u1":
            return [1]

        if gate == "u2":
            return [2]

        if gate == "u3":
            return [3]

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
