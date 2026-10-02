```python
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
    recognizable Qiskit quantum-circuit syntax.
    """
    pass


def parse_qiskit_code(code: str):
    """
    Parse common Qiskit syntax without executing user code.

    Supports:
    - QuantumCircuit(n)
    - direct gate calls such as qc.h(0)
    - two-qubit gates such as qc.cx(0, 1)
    - for loops using range()
    - simple arithmetic expressions such as q + 1
    - simple Qiskit measurement/reset/barrier operations

    Rejects:
    - C++
    - Java
    - JavaScript
    - ordinary Python
    - random text
    - source code without recognizable quantum-circuit syntax
    """

    if not isinstance(code, str) or not code.strip():
        raise UnsupportedQuantumCodeError(
            "Unsupported code. Please provide Qiskit quantum circuit code."
        )

    # ---------------------------------------------------------
    # First validate that the source looks like Qiskit code.
    # This prevents arbitrary languages or ordinary Python
    # from becoming an empty/default quantum circuit.
    # ---------------------------------------------------------
    if not _contains_qiskit_syntax(code):
        raise UnsupportedQuantumCodeError(
            "Unsupported code. QuantumInsight currently supports "
            "Qiskit quantum circuit code. The submitted source does "
            "not contain a recognizable quantum circuit."
        )

    try:
        tree = ast.parse(code)

        result = _static_ast_parse(tree)

        # A valid QuantumCircuit declaration is enough to accept
        # a circuit even when it currently contains zero gates.
        if _contains_quantum_circuit_constructor(tree):
            if result["qubits"] > 0 or result["gates"]:
                return result, "static-ast"

        # If recognizable Qiskit gate syntax exists, accept it.
        if result["gates"]:
            return result, "static-ast"

    except (SyntaxError, ValueError):
        pass

    # ---------------------------------------------------------
    # Regex fallback for simple Qiskit syntax.
    # ---------------------------------------------------------
    result = lightweight_parse(code)

    if result["qubits"] > 0 or result["gates"]:
        return result, "lightweight"

    # ---------------------------------------------------------
    # IMPORTANT:
    # Never silently convert unsupported code into:
    #
    #     {"qubits": 0, "gates": []}
    #
    # because downstream QHI/QMI/hardware analysis would then
    # treat invalid source as an empty quantum circuit.
    # ---------------------------------------------------------
    raise UnsupportedQuantumCodeError(
        "Unsupported code. QuantumInsight currently supports "
        "Qiskit quantum circuit code. The submitted source does "
        "not contain a recognizable quantum circuit."
    )


def _contains_qiskit_syntax(code: str):
    """
    Detect recognizable Qiskit quantum-circuit syntax without
    executing the submitted code.

    This is intentionally conservative.
    """

    # QuantumCircuit constructor
    if re.search(
        r"\bQuantumCircuit\s*\(",
        code,
    ):
        return True

    # Common Qiskit imports
    if re.search(
        r"\bfrom\s+qiskit\s+import\b",
        code,
    ):
        return True

    if re.search(
        r"\bimport\s+qiskit\b",
        code,
    ):
        return True

    # Common quantum gate calls.
    #
    # Examples:
    # qc.h(0)
    # circuit.cx(0, 1)
    # qc.measure_all()
    #
    gate_pattern = (
        r"\b[A-Za-z_][A-Za-z0-9_]*\."
        r"(?:" +
        "|".join(re.escape(name) for name in GATE_NAMES) +
        r")\s*\("
    )

    if re.search(gate_pattern, code, re.IGNORECASE):
        return True

    return False


def _contains_quantum_circuit_constructor(tree):
    """
    Check the AST for QuantumCircuit(...).
    """

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "QuantumCircuit"
        ):
            return True

    return False


def _static_ast_parse(tree):
    qubits = 0
    gates = []

    variables = {}

    # ---------------------------------------------------------
    # Discover QuantumCircuit(n)
    # ---------------------------------------------------------
    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "QuantumCircuit"
            ):

                if node.args:

                    value = _eval_int(
                        node.args[0],
                        variables,
                    )

                    if value is not None:
                        qubits = max(
                            qubits,
                            value,
                        )

    def visit(node, env):
        nonlocal qubits

        # -----------------------------------------------------
        # for i in range(...)
        # -----------------------------------------------------
        if isinstance(node, ast.For):

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
        if isinstance(node, ast.Assign):

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

            return

        # -----------------------------------------------------
        # Direct function/gate calls
        # -----------------------------------------------------
        if isinstance(node, ast.Expr):

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
                    # explicit indices in some Qiskit code.
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

    # Only walk top-level statements.
    for node in tree.body:

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
        qc.cx(q, q + 1)

    into:

        ("h", [0])
        ("cx", [q, q + 1])
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
    # Operations that do not necessarily require qubit indices.
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
    # Normal gate arguments.
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
    Extract a qubit index from an AST expression.

    Supports:

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

        if isinstance(
            node.value,
            int,
        ) and not isinstance(
            node.value,
            bool,
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
    """

    qubits = 0
    gates = []

    # ---------------------------------------------------------
    # QuantumCircuit(n)
    # ---------------------------------------------------------
    m = re.search(
        r"QuantumCircuit\s*\(\s*(\d+)",
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

        indices = [
            int(x)
            for x in re.findall(
                r"(?<![A-Za-z_])\d+(?![A-Za-z_])",
                args,
            )
        ]

        if indices:

            qubits = max(
                qubits,
                max(indices) + 1,
            )

            gates.append(
                {
                    "name": gate,
                    "qubits": indices,
                }
            )

    return {
        "qubits": qubits,
        "gates": gates,
    }


def circuit_to_gate_list(circuit):
    if isinstance(
        circuit,
        dict,
    ):
        return circuit["gates"]

    return []
```
