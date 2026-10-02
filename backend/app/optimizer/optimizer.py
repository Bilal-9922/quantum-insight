from app.optimizer.rules import rule_optimize
from app.circuit.metrics import extract_metrics
from app.circuit.parser import parse_qiskit_code


# Gates that can be safely regenerated from the
# static parser representation.
SINGLE_QUBIT_GATES = {
    "h",
    "x",
    "y",
    "z",
    "s",
    "sdg",
    "t",
    "tdg",
}

TWO_QUBIT_GATES = {
    "cx",
    "cy",
    "cz",
    "ch",
    "swap",
    "iswap",
}

THREE_QUBIT_GATES = {
    "ccx",
    "cswap",
}


def _generate_optimized_code(qubits, gates):
    """
    Generate readable Qiskit code from the optimized
    static gate representation.

    This does NOT execute user-submitted code.
    """

    lines = [
        "from qiskit import QuantumCircuit",
        "",
        f"qc = QuantumCircuit({qubits})",
        "",
    ]

    for gate in gates:
        name = gate.get("name", "").lower()
        gate_qubits = gate.get("qubits", [])

        if name in SINGLE_QUBIT_GATES:
            if len(gate_qubits) != 1:
                continue

            lines.append(
                f"qc.{name}({gate_qubits[0]})"
            )

        elif name in TWO_QUBIT_GATES:
            if len(gate_qubits) != 2:
                continue

            lines.append(
                f"qc.{name}("
                f"{gate_qubits[0]}, "
                f"{gate_qubits[1]})"
            )

        elif name in THREE_QUBIT_GATES:
            if len(gate_qubits) != 3:
                continue

            lines.append(
                f"qc.{name}("
                f"{gate_qubits[0]}, "
                f"{gate_qubits[1]}, "
                f"{gate_qubits[2]})"
            )

        elif name == "measure_all":
            lines.append("qc.measure_all()")

        elif name == "barrier":
            lines.append("qc.barrier()")

        elif name == "reset":
            if len(gate_qubits) == 1:
                lines.append(
                    f"qc.reset({gate_qubits[0]})"
                )

    lines.append("")

    return "\n".join(lines)


def optimize_code(code):
    """
    Analyze and optimize a Qiskit circuit without
    executing the submitted source code.
    """

    circuit, mode = parse_qiskit_code(code)

    optimized_code = code
    optimization_applied = False

    # -------------------------------------------------
    # Static AST / lightweight parser mode
    # -------------------------------------------------

    if isinstance(circuit, dict):
        original = extract_metrics(circuit)

        optimized_gates = rule_optimize(
            circuit["gates"]
        )

        optimized = {
            "qubits": circuit["qubits"],
            "gates": optimized_gates,
        }

        result = extract_metrics(optimized)

        optimized_code = _generate_optimized_code(
            circuit["qubits"],
            optimized_gates,
        )

        optimization_applied = (
            len(optimized_gates)
            != len(circuit["gates"])
        )

    # -------------------------------------------------
    # Real Qiskit circuit mode
    # -------------------------------------------------

    else:
        original = extract_metrics(circuit)

        try:
            from app.optimizer.transpiler import transpile_circuit

            opt = transpile_circuit(circuit)

            result = extract_metrics(opt)

        except Exception:
            result = original

    # -------------------------------------------------
    # Percentage calculation
    # -------------------------------------------------

    def pct(a, b):
        return round(
            (a - b) / max(1, a) * 100,
            1,
        )

    # -------------------------------------------------
    # Result
    # -------------------------------------------------

    return {
        "mode": mode,

        "original": original,

        "optimized": result,

        "improvement": {
            "gate_reduction_percent": pct(
                original["gate_count"],
                result["gate_count"],
            ),
            "depth_reduction_percent": pct(
                original["depth"],
                result["depth"],
            ),
            "two_qubit_reduction_percent": pct(
                original["two_qubit_gates"],
                result["two_qubit_gates"],
            ),
        },

        "optimization_applied": optimization_applied,

        "optimized_code": optimized_code,
    }
