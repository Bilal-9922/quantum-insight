import ast
import re


GATE_NAMES = {
    "h",
    "x",
    "y",
    "z",
    "s",
    "sdg",
    "t",
    "tdg",
    "rx",
    "ry",
    "rz",
    "p",
    "u",
    "u1",
    "u2",
    "u3",
    "cx",
    "cy",
    "cz",
    "ch",
    "swap",
    "iswap",
    "ccx",
    "cswap",
    "crx",
    "cry",
    "crz",
    "cp",
    "rxx",
    "ryy",
    "rzz",
    "measure",
    "measure_all",
    "barrier",
    "reset",
}


class UnsupportedQuantumCodeError(ValueError):
    """
    Raised when submitted source code does not contain
    recognizable Qiskit QuantumCircuit syntax.
    """

    pass


def parse_qiskit_code(code: str):
    """
    Parse supported Qiskit QuantumCircuit source code
    without executing user code.

    Supported examples:

        from qiskit import QuantumCircuit

        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)

    Also supports:

    - QuantumCircuit(n)
    - QuantumCircuit(n, m)
    - common Qiskit gate calls
    - two-qubit gates
    - simple for/range loops
    - simple integer expressions
    - measurement operations
    - measure_all()
    - barrier()
    - reset()

    Important:
    - Only actual QuantumCircuit construction is accepted.
    - Arbitrary objects such as fake.cx(0, 1) are rejected.
    - measure(qubit, classical_bit) records only the quantum bit.
    - Submitted code is NEVER executed.
    """

    if not isinstance(code, str) or not code.strip():
        raise UnsupportedQuantumCodeError(
            "Unsupported code. Please provide Qiskit quantum circuit code."
        )

    # ---------------------------------------------------------
    # Parse Python syntax first.
    # ---------------------------------------------------------

    try:
        tree = ast.parse(code)
    except SyntaxError:
        raise UnsupportedQuantumCodeError(
            "Unsupported code. QuantumInsight currently supports "
            "valid Python code containing a Qiskit QuantumCircuit."
        )

    # ---------------------------------------------------------
    # Strict Qiskit validation.
    #
    # QuantumInsight is intentionally Qiskit-only.
    # A Qiskit import by itself is NOT sufficient.
    #
    # The source must contain an actual QuantumCircuit(...)
    # constructor.
    # ---------------------------------------------------------

    if not _contains_quantum_circuit_constructor(tree):
        raise UnsupportedQuantumCodeError(
            "Unsupported code. QuantumInsight currently supports "
            "Qiskit quantum circuit code. The submitted source does "
            "not contain a recognizable Qiskit QuantumCircuit."
        )

    # ---------------------------------------------------------
    # Static AST parser.
    #
    # No submitted code is executed.
    # ---------------------------------------------------------

    try:
        result = _static_ast_parse(tree)

        # A valid QuantumCircuit declaration is enough to accept
        # a circuit even when it currently contains zero gates.
        if _contains_quantum_circuit_constructor(tree):
            if result["qubits"] > 0 or result["gates"]:
                return result, "static-ast"

    except (SyntaxError, ValueError, TypeError):
        pass

    # ---------------------------------------------------------
    # Regex fallback for simple Qiskit syntax.
    # ---------------------------------------------------------

    result = lightweight_parse(code)

    if result["qubits"] > 0 or result["gates"]:
        return result, "lightweight"

    # ---------------------------------------------------------
    # Never silently convert unsupported code into an empty
    # quantum circuit.
    # ---------------------------------------------------------

    raise UnsupportedQuantumCodeError(
        "Unsupported code. QuantumInsight currently supports "
        "Qiskit quantum circuit code. The submitted source does "
        "not contain a recognizable quantum circuit."
    )


def _contains_quantum_circuit_constructor(tree):
    """
    Check whether the AST contains an actual QuantumCircuit(...)
    constructor.

    Accepted:

        QuantumCircuit(2)
        qc = QuantumCircuit(3)
        circuit = QuantumCircuit(2, 2)

    Rejected:

        fake.cx(0, 1)
        simulator = FakeQuantumCircuit(...)
        print("QuantumCircuit")
    """

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        # Direct constructor:
        #
        # QuantumCircuit(...)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "QuantumCircuit"
        ):
            return True

        # Also allow:
        #
        # qiskit.QuantumCircuit(...)
        #
        # from qiskit import QuantumCircuit
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "QuantumCircuit"
        ):
            if isinstance(
                node.func.value,
                ast.Name,
            ):
                if node.func.value.id in {
                    "qiskit",
                    "circuit",
                }:
                    return True

    return False


def _contains_qiskit_import(tree):
    """
    Detect actual Qiskit imports.

    This function is intentionally separate from the main
    validation rule.

    Importing Qiskit alone does NOT make a source file a
    valid QuantumInsight circuit. A QuantumCircuit constructor
    is still required.
    """

    for node in ast.walk(tree):

        if isinstance(
            node,
            ast.Import,
        ):

            for alias in node.names:

                if alias.name == "qiskit":
                    return True

        if isinstance(
            node,
            ast.ImportFrom,
        ):

            if node.module == "qiskit":
                return True

            if (
                node.module
                and node.module.startswith("qiskit.")
            ):
                return True

    return False


def _static_ast_parse(tree):
    """
    Extract Qiskit circuit structure from the AST.

    The submitted code is never executed.
    """

    qubits = 0
    gates = []

    variables = {}

    # ---------------------------------------------------------
    # Discover QuantumCircuit(...)
    # ---------------------------------------------------------

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        is_constructor = False

        # QuantumCircuit(...)
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "QuantumCircuit"
        ):
            is_constructor = True

        # qiskit.QuantumCircuit(...)
        elif (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "QuantumCircuit"
            and isinstance(
                node.func.value,
                ast.Name,
            )
            and node.func.value.id in {
                "qiskit",
                "circuit",
            }
        ):
            is_constructor = True

        if not is_constructor:
            continue

        # First positional argument is the number
        # of quantum bits for the supported static parser.
        if node.args:

            value = _eval_int(
                node.args[0],
                variables,
            )

            if value is not None and value >= 0:

                qubits = max(
                    qubits,
                    value,
                )

    def visit(node, env):
        nonlocal qubits

        # -----------------------------------------------------
        # for i in range(...)
        # -----------------------------------------------------

        if isinstance(
            node,
            ast.For,
        ):

            loop_values = _range_values(
                node.iter,
                env,
            )

            if loop_values is None:
                return

            target = _target_name(
                node.target
            )

            if target is None:
                return

            for value in loop_values:

                child_env = dict(env)

                child_env[target] = value

                for child in node.body:
                    visit(
                        child,
                        child_env,
                    )

            return

        # -----------------------------------------------------
        # Variable assignments
        # -----------------------------------------------------

        if isinstance(
            node,
            ast.Assign,
        ):

            value = _eval_int(
                node.value,
                env,
            )

            if value is not None:

                for target in node.targets:

                    name = _target_name(
                        target
                    )

                    if name:
                        env[name] = value

            # Continue looking for circuit operations
            # in assignments such as:
            #
            # qc = QuantumCircuit(2)
            #
            for child in ast.iter_child_nodes(node):
                if isinstance(
                    child,
                    ast.Call,
                ):
                    continue

            return

        # -----------------------------------------------------
        # Direct function/gate calls
        # -----------------------------------------------------

        if isinstance(
            node,
            ast.Expr,
        ):

            if isinstance(
                node.value,
                ast.Call,
            ):

                gate_data = _parse_gate_call(
                    node.value,
                    env,
                )

                if gate_data is not None:

                    name, indices = gate_data

                    # measure_all() acts on all circuit qubits.
                    if name == "measure_all":

                        if qubits > 0:
                            indices = list(
                                range(qubits)
                            )

                    # barrier() and reset() may not contain
                    # explicit indices.
                    if name in {
                        "barrier",
                        "reset",
                    } and not indices:

                        if qubits > 0:
                            indices = list(
                                range(qubits)
                            )

                    if indices:

                        valid_indices = [
                            i
                            for i in indices
                            if i >= 0
                        ]

                        if valid_indices:

                            qubits = max(
                                qubits,
                                max(valid_indices) + 1,
                            )

                            gates.append(
                                {
                                    "name": name,
                                    "qubits": valid_indices,
                                }
                            )

            return

        # -----------------------------------------------------
        # Recursively inspect child nodes.
        # -----------------------------------------------------

        for child in ast.iter_child_nodes(node):

            visit(
                child,
                dict(env),
            )

    # ---------------------------------------------------------
    # Only inspect top-level statements.
    # ---------------------------------------------------------

    for node in tree.body:

        # Don't treat imports as circuit operations.
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        ):
            continue

        visit(
            node,
            variables,
        )

    return {
        "qubits": qubits,
        "gates": gates,
    }


def _parse_gate_call(call, env):
    """
    Convert:

        qc.h(0)
        qc.cx(0, 1)

    into:

        ("h", [0])
        ("cx", [0, 1])

    Measurement is handled specially:

        qc.measure(0, 0)

    becomes:

        ("measure", [0])

    The second value is a classical-bit index and is NEVER
    treated as a quantum-bit index.
    """

    if not isinstance(
        call.func,
        ast.Attribute,
    ):
        return None

    gate = call.func.attr.lower()

    if gate not in GATE_NAMES:
        return None

    # ---------------------------------------------------------
    # Measurement
    #
    # Qiskit:
    #
    # qc.measure(qubit, classical_bit)
    #
    # Only the first argument is a quantum-bit index.
    # ---------------------------------------------------------

    if gate == "measure":

        if not call.args:
            return None

        qubit_index = _extract_qubit_index(
            call.args[0],
            env,
        )

        if qubit_index is None:
            return None

        return gate, [qubit_index]

    # ---------------------------------------------------------
    # Operations that do not necessarily require explicit
    # qubit indices.
    # ---------------------------------------------------------

    if gate in {
        "measure_all",
        "barrier",
        "reset",
    }:

        indices = []

        for arg in call.args:

            value = _eval_int(
                arg,
                env,
            )

            if value is not None:
                indices.append(value)

        return gate, indices

    # ---------------------------------------------------------
    # Normal quantum gate arguments.
    # ---------------------------------------------------------

    indices = []

    for arg in call.args:

        value = _extract_qubit_index(
            arg,
            env,
        )

        if value is not None:
            indices.append(value)

    if not indices:
        return None

    return gate, indices


def _extract_qubit_index(node, env):
    """
    Extract a qubit index from a simple AST expression.

    Supported:

        0
        q
        q + 1
        q - 1
    """

    return _eval_int(
        node,
        env,
    )


def _eval_int(node, env):
    """
    Safely evaluate simple integer expressions.

    No arbitrary Python code is executed.
    """

    if isinstance(
        node,
        ast.Constant,
    ):

        if (
            isinstance(node.value, int)
            and not isinstance(node.value, bool)
        ):
            return node.value

        return None

    if isinstance(
        node,
        ast.Name,
    ):

        return env.get(
            node.id
        )

    if isinstance(
        node,
        ast.UnaryOp,
    ):

        value = _eval_int(
            node.operand,
            env,
        )

        if value is None:
            return None

        if isinstance(
            node.op,
            ast.USub,
        ):
            return -value

        if isinstance(
            node.op,
            ast.UAdd,
        ):
            return value

        return None

    if isinstance(
        node,
        ast.BinOp,
    ):

        left = _eval_int(
            node.left,
            env,
        )

        right = _eval_int(
            node.right,
            env,
        )

        if left is None or right is None:
            return None

        if isinstance(
            node.op,
            ast.Add,
        ):
            return left + right

        if isinstance(
            node.op,
            ast.Sub,
        ):
            return left - right

        if isinstance(
            node.op,
            ast.Mult,
        ):
            return left * right

        if isinstance(
            node.op,
            ast.FloorDiv,
        ):

            if right == 0:
                return None

            return left // right

        return None

    return None


def _range_values(node, env):
    """
    Safely evaluate:

        range(10)
        range(1, 10)
        range(0, 10, 2)

    without executing arbitrary Python.
    """

    if not isinstance(
        node,
        ast.Call,
    ):
        return None

    if not isinstance(
        node.func,
        ast.Name,
    ):
        return None

    if node.func.id != "range":
        return None

    values = []

    for arg in node.args:

        value = _eval_int(
            arg,
            env,
        )

        if value is None:
            return None

        values.append(value)

    try:

        if len(values) == 1:
            return range(
                values[0]
            )

        if len(values) == 2:
            return range(
                values[0],
                values[1],
            )

        if len(values) == 3:
            return range(
                values[0],
                values[1],
                values[2],
            )

    except ValueError:
        return None

    return None


def _target_name(node):
    if isinstance(
        node,
        ast.Name,
    ):
        return node.id

    return None


def lightweight_parse(code: str):
    """
    Regex fallback parser for simple Qiskit code.

    This fallback is still Qiskit-only because
    parse_qiskit_code() requires a QuantumCircuit(...)
    constructor before calling this function.

    Important:
    measure(qubit, classical_bit) records only the qubit.
    """

    qubits = 0
    gates = []

    # ---------------------------------------------------------
    # QuantumCircuit(n)
    # ---------------------------------------------------------

    m = re.search(
        r"\bQuantumCircuit\s*\(\s*(\d+)",
        code,
    )

    if m:
        qubits = int(
            m.group(1)
        )

    # ---------------------------------------------------------
    # Parse individual lines.
    # ---------------------------------------------------------

    for line in code.splitlines():

        line = line.split(
            "#",
            1,
        )[0].strip()

        if not line:
            continue

        if line.startswith(
            (
                "from ",
                "import ",
            )
        ):
            continue

        call = re.match(
            r"^(?:\w+\.)?"
            r"(?P<gate>[a-zA-Z][a-zA-Z0-9_]*)"
            r"\s*\((?P<args>.*)\)\s*$",
            line,
        )

        if not call:
            continue

        gate = call.group(
            "gate"
        ).lower()

        args = call.group(
            "args"
        )

        if gate not in GATE_NAMES:
            continue

        # -----------------------------------------------------
        # measure_all()
        # -----------------------------------------------------

        if gate == "measure_all":

            gates.append(
                {
                    "name": gate,
                    "qubits": list(
                        range(qubits)
                    ),
                }
            )

            continue

        # -----------------------------------------------------
        # measure(qubit, classical_bit)
        #
        # Only the first numeric argument is the quantum bit.
        # -----------------------------------------------------

        if gate == "measure":

            measurement_indices = re.findall(
                r"(?<![A-Za-z_])[-+]?\d+(?![A-Za-z_])",
                args,
            )

            if not measurement_indices:
                continue

            indices = [
                int(
                    measurement_indices[0]
                )
            ]

        else:

            indices = [
                int(x)
                for x in re.findall(
                    r"(?<![A-Za-z_])[-+]?\d+(?![A-Za-z_])",
                    args,
                )
            ]

        if indices:

            valid_indices = [
                i
                for i in indices
                if i >= 0
            ]

            if not valid_indices:
                continue

            qubits = max(
                qubits,
                max(valid_indices) + 1,
            )

            gates.append(
                {
                    "name": gate,
                    "qubits": valid_indices,
                }
            )

    return {
        "qubits": qubits,
        "gates": gates,
    }


def circuit_to_gate_list(circuit):
    """
    Return the normalized gate list from a parsed circuit.
    """

    if isinstance(
        circuit,
        dict,
    ):
        return circuit["gates"]

    return []
