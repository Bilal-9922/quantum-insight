from collections import Counter


SELF_INVERSE_GATES = {
    "x",
    "y",
    "z",
    "h",
    "cx",
    "cy",
    "cz",
    "ch",
    "swap",
    "iswap",
    "ccx",
    "cswap",
}


# These are quantum gates whose operation genuinely acts on
# two or more quantum bits.
#
# Measurement is intentionally NOT included because:
#
#     measure(qubit, classical_bit)
#
# contains one quantum bit and one classical bit.
MULTI_QUBIT_GATES = {
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
}


def extract_metrics(circuit):
    """
    Extract engineering metrics from a parsed circuit.

    Important:
    - A two-qubit gate is determined by quantum-qubit operands.
    - Measurements are never treated as two-qubit gates.
    - measure(qubit, classical_bit) therefore contributes one
      quantum operand only.
    """

    if isinstance(
        circuit,
        dict,
    ):

        gates = circuit["gates"]
        qubits = circuit["qubits"]

        depth = _light_depth(
            gates
        )

    else:

        gates = []

        for inst in circuit.data:

            op, qargs, _ = inst

            gates.append(
                {
                    "name": op.name,
                    "qubits": [
                        circuit.find_bit(q).index
                        for q in qargs
                    ],
                }
            )

        qubits = circuit.num_qubits
        depth = circuit.depth()

    # ---------------------------------------------------------
    # Normalize operation names.
    # ---------------------------------------------------------

    counts = Counter(
        g["name"].lower()
        for g in gates
    )

    gate_count = len(gates)

    # ---------------------------------------------------------
    # Single-qubit quantum gates
    #
    # Measurements are excluded because they are not quantum
    # gates.
    # ---------------------------------------------------------

    one_q = sum(
        1
        for g in gates
        if (
            g["name"].lower()
            not in {
                "measure",
                "measure_all",
            }
            and len(g["qubits"]) == 1
        )
    )

    # ---------------------------------------------------------
    # Genuine multi-qubit quantum gates
    #
    # This is intentionally based on gate identity AND quantum
    # operand count.
    #
    # A measurement must never enter this count.
    # ---------------------------------------------------------

    two_q = sum(
        1
        for g in gates
        if (
            g["name"].lower()
            in MULTI_QUBIT_GATES
            and len(g["qubits"]) >= 2
        )
    )

    # ---------------------------------------------------------
    # Measurement count
    # ---------------------------------------------------------

    measurement = sum(
        1
        for g in gates
        if g["name"].lower()
        in {
            "measure",
            "measure_all",
        }
    )

    # ---------------------------------------------------------
    # Active qubits
    # ---------------------------------------------------------

    active_qubits = set()

    for gate in gates:

        gate_name = gate["name"].lower()

        if gate_name in {
            "measure",
            "measure_all",
            "barrier",
        }:
            continue

        for qubit in gate["qubits"]:

            if 0 <= qubit < qubits:
                active_qubits.add(
                    qubit
                )

    active_qubit_count = len(
        active_qubits
    )

    qubit_utilization = (
        active_qubit_count
        / max(1, qubits)
    )

    # ---------------------------------------------------------
    # Gate cancellation opportunities
    # ---------------------------------------------------------

    cancellation_count = (
        _count_cancellation_opportunities(
            gates
        )
    )

    # ---------------------------------------------------------
    # Other circuit metrics
    # ---------------------------------------------------------

    density = (
        gate_count
        / max(
            1,
            qubits * max(
                1,
                depth,
            ),
        )
    )

    two_ratio = (
        two_q
        / max(
            1,
            gate_count,
        )
    )

    measurement_ratio = (
        measurement
        / max(
            1,
            gate_count,
        )
    )

    return {
        "qubits": qubits,
        "active_qubits": active_qubit_count,
        "qubit_utilization": round(
            qubit_utilization,
            4,
        ),
        "gate_count": gate_count,
        "depth": depth,
        "one_qubit_gates": one_q,
        "two_qubit_gates": two_q,
        "two_qubit_ratio": round(
            two_ratio,
            4,
        ),
        "gate_density": round(
            density,
            4,
        ),
        "measurement_ratio": round(
            measurement_ratio,
            4,
        ),
        "cancellation_opportunities": (
            cancellation_count
        ),
        "gate_counts": dict(
            counts
        ),
    }


def _count_cancellation_opportunities(gates):
    """
    Count adjacent identical self-inverse gates.

    Examples:

        x(0), x(0)
        h(0), h(0)
        cx(0, 1), cx(0, 1)

    These pairs cancel because:

        G * G = I

    for self-inverse gates.
    """

    count = 0

    for i in range(
        len(gates) - 1
    ):

        current = gates[i]
        following = gates[i + 1]

        current_name = (
            current["name"].lower()
        )

        following_name = (
            following["name"].lower()
        )

        if current_name != following_name:
            continue

        if (
            current_name
            not in SELF_INVERSE_GATES
        ):
            continue

        current_qubits = tuple(
            current["qubits"]
        )

        following_qubits = tuple(
            following["qubits"]
        )

        if (
            current_qubits
            == following_qubits
        ):
            count += 1

    return count


def _light_depth(gates):
    """
    Calculate a lightweight circuit depth.

    Operations are placed into the earliest layer where
    their quantum-qubit operands do not conflict.

    Measurement operations use their quantum-qubit list only.
    Classical-bit indices are never part of the list.
    """

    if not gates:
        return 0

    layers = []

    for gate in gates:

        used = set(
            gate["qubits"]
        )

        layer = 0

        while (
            layer < len(layers)
            and used.intersection(
                layers[layer]
            )
        ):
            layer += 1

        if layer == len(layers):
            layers.append(
                set()
            )

        layers[layer].update(
            used
        )

    return len(layers)


def circuit_to_gate_list(circuit):
    if isinstance(
        circuit,
        dict,
    ):
        return circuit["gates"]

    return []
