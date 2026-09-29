from collections import Counter

def extract_metrics(circuit):
    if isinstance(circuit, dict):
        gates = circuit["gates"]
        qubits = circuit["qubits"]
        depth = _light_depth(gates)
    else:
        gates = []
        for inst in circuit.data:
            op, qargs, _ = inst
            gates.append({"name": op.name, "qubits": [circuit.find_bit(q).index for q in qargs]})
        qubits = circuit.num_qubits
        depth = circuit.depth()

    counts = Counter(g["name"] for g in gates)
    gate_count = len(gates)
    one_q = sum(1 for g in gates if len(g["qubits"]) == 1)
    two_q = sum(1 for g in gates if len(g["qubits"]) == 2)
    measurement = sum(1 for g in gates if g["name"] in {"measure", "measure_all"})

    density = gate_count / max(1, qubits * max(1, depth))
    two_ratio = two_q / max(1, gate_count)
    measurement_ratio = measurement / max(1, gate_count)

    return {
        "qubits": qubits,
        "gate_count": gate_count,
        "depth": depth,
        "one_qubit_gates": one_q,
        "two_qubit_gates": two_q,
        "two_qubit_ratio": round(two_ratio, 4),
        "gate_density": round(density, 4),
        "measurement_ratio": round(measurement_ratio, 4),
        "gate_counts": dict(counts),
    }

def _light_depth(gates):
    if not gates:
        return 0
    layers = []
    for gate in gates:
        used = set(gate["qubits"])
        layer = 0
        while layer < len(layers) and used.intersection(layers[layer]):
            layer += 1
        if layer == len(layers):
            layers.append(set())
        layers[layer].update(used)
    return len(layers)
