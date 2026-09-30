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


def extract_metrics(circuit):
    if isinstance(circuit, dict):
        gates = circuit["gates"]
        qubits = circuit["qubits"]
        depth = _light_depth(gates)
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

    counts = Counter(g["name"] for g in gates)

    gate_count = len(gates)

    one_q = sum(
        1
        for g in gates
        if len(g["qubits"]) == 1
    )

    two_q = sum(
        1
        for g in gates
        if len(g["qubits"]) == 2
    )

    measurement = sum(
        1
        for g in gates
        if g["name"] in {
            "measure",
            "measure_all",
        }
    )

    # ---------------------------------------------------------
    # Active qubits
    # ---------------------------------------------------------

    active_qubits = set()

    for gate in gates:

        if gate["name"].lower() in {
            "measure",
            "measure_all",
            "barrier",
        }:
            continue

        for qubit in gate["qubits"]:

            if 0 <= qubit < qubits:
                active_qubits.add(qubit)

    active_qubit_count = len(active_qubits)

    qubit_utilization = (
        active_qubit_count / max(1, qubits)
    )

    # ---------------------------------------------------------
    # Gate cancellation opportunities
    # ---------------------------------------------------------

    cancellation_count = _count_cancellation_opportunities(
        gates
    )

    # ---------------------------------------------------------
    # Other circuit metrics
    # ---------------------------------------------------------

    density = (
        gate_count
        / max(
            1,
            qubits * max(1, depth)
        )
    )

    two_ratio = (
        two_q
        / max(1, gate_count)
    )

    measurement_ratio = (
        measurement
        / max(1, gate_count)
    )

    return {
        "qubits": qubits,
        "active_qubits": active_qubit_count,
        "qubit_utilization": round(
            qubit_utilization,
            4
        ),
        "gate_count": gate_count,
        "depth": depth,
        "one_qubit_gates": one_q,
        "two_qubit_gates": two_q,
        "two_qubit_ratio": round(
            two_ratio,
            4
        ),
        "gate_density": round(
            density,
            4
        ),
        "measurement_ratio": round(
            measurement_ratio,
            4
        ),
        "cancellation_opportunities": cancellation_count,
        "gate_counts": dict(counts),
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

    for i in range(len(gates) - 1):

        current = gates[i]
        following = gates[i + 1]

        current_name = current["name"].lower()
        following_name = following["name"].lower()

        if current_name != following_name:
            continue

        if current_name not in SELF_INVERSE_GATES:
            continue

        current_qubits = tuple(
            current["qubits"]
        )

        following_qubits = tuple(
            following["qubits"]
        )

        if current_qubits == following_qubits:
            count += 1

    return count


def _light_depth(gates):
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
            layers.append(set())

        layers[layer].update(used)

    return len(layers)


def circuit_to_gate_list(circuit):
    if isinstance(circuit, dict):
        return circuit["gates"]

    return []
