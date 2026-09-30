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


def parse_qiskit_code(code: str):
    """
    Parse common Qiskit syntax without executing user code.

    Supports:
    - direct gate calls
    - for loops using range()
    - simple arithmetic expressions such as q + 1
    - QuantumCircuit(n)
    """

    try:
        tree = ast.parse(code)
        result = _static_ast_parse(tree)

        if result["gates"]:
            return result, "static-ast"

    except (SyntaxError, ValueError):
        pass

    return lightweight_parse(code), "lightweight"


def _static_ast_parse(tree):
    qubits = 0
    gates = []

    variables = {}

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            # QuantumCircuit(n)
            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "QuantumCircuit"
            ):
                if node.args:
                    value = _eval_int(node.args[0], variables)

                    if value is not None:
                        qubits = max(qubits, value)

    def visit(node, env):
        nonlocal qubits

        if isinstance(node, ast.For):

            loop_values = _range_values(node.iter, env)

            if loop_values is None:
                return

            target = _target_name(node.target)

            if target is None:
                return

            for value in loop_values:
                child_env = dict(env)
                child_env[target] = value

                for child in node.body:
                    visit(child, child_env)

            return

        if isinstance(node, ast.Assign):

            value = _eval_int(node.value, env)

            if value is not None:

                for target in node.targets:

                    name = _target_name(target)

                    if name:
                        env[name] = value

            return

        if isinstance(node, ast.Expr):

            if isinstance(node.value, ast.Call):

                gate_data = _parse_gate_call(
                    node.value,
                    env
                )

                if gate_data is not None:

                    name, indices = gate_data

                    if name == "measure_all":

                        if qubits > 0:
                            indices = list(range(qubits))

                    if indices:

                        valid_indices = [
                            i
                            for i in indices
                            if i >= 0
                        ]

                        if valid_indices:

                            qubits = max(
                                qubits,
                                max(valid_indices) + 1
                            )

                            gates.append(
                                {
                                    "name": name,
                                    "qubits": valid_indices,
                                }
                            )

            return

        for child in ast.iter_child_nodes(node):

            visit(child, dict(env))

    for node in tree.body:

        visit(node, variables)

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

    if not isinstance(call.func, ast.Attribute):
        return None

    gate = call.func.attr.lower()

    if gate not in GATE_NAMES:
        return None

    if gate in {
        "measure_all",
        "barrier",
        "reset",
    }:
        indices = []

        for arg in call.args:

            value = _eval_int(arg, env)

            if value is not None:
                indices.append(value)

        return gate, indices

    indices = []

    for arg in call.args:

        value = _extract_qubit_index(arg, env)

        if value is not None:
            indices.append(value)

    if not indices:
        return None

    # Parameterized gates may contain a parameter
    # before the qubit index, e.g.:
    #
    # qc.ry(3.1415, 0)
    #
    # Only actual integer qubit expressions should
    # be included here.

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

    return _eval_int(node, env)


def _eval_int(node, env):
    if isinstance(node, ast.Constant):

        if isinstance(node.value, int):
            return node.value

        return None

    if isinstance(node, ast.Name):
        return env.get(node.id)

    if isinstance(node, ast.UnaryOp):

        value = _eval_int(node.operand, env)

        if value is None:
            return None

        if isinstance(node.op, ast.USub):
            return -value

        if isinstance(node.op, ast.UAdd):
            return value

        return None

    if isinstance(node, ast.BinOp):

        left = _eval_int(node.left, env)
        right = _eval_int(node.right, env)

        if left is None or right is None:
            return None

        if isinstance(node.op, ast.Add):
            return left + right

        if isinstance(node.op, ast.Sub):
            return left - right

        if isinstance(node.op, ast.Mult):
            return left * right

        if isinstance(node.op, ast.FloorDiv):
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

    if not isinstance(node, ast.Call):
        return None

    if not isinstance(node.func, ast.Name):
        return None

    if node.func.id != "range":
        return None

    values = []

    for arg in node.args:

        value = _eval_int(arg, env)

        if value is None:
            return None

        values.append(value)

    try:

        if len(values) == 1:
            return range(values[0])

        if len(values) == 2:
            return range(values[0], values[1])

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
    if isinstance(node, ast.Name):
        return node.id

    return None


def lightweight_parse(code: str):
    """
    Regex fallback parser for simple Qiskit code.
    """

    qubits = 0
    gates = []

    m = re.search(
        r"QuantumCircuit\s*\(\s*(\d+)",
        code
    )

    if m:
        qubits = int(m.group(1))

    for line in code.splitlines():

        line = line.split("#", 1)[0].strip()

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

        gate = call.group("gate").lower()
        args = call.group("args")

        if gate not in GATE_NAMES:
            continue

        if gate == "measure_all":

            gates.append(
                {
                    "name": gate,
                    "qubits": list(range(qubits)),
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
    if isinstance(circuit, dict):
        return circuit["gates"]

    return []
