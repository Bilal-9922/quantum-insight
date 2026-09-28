def circuit_data(circuit):
    if isinstance(circuit, dict):
        return {
            "qubits": circuit["qubits"],
            "gates": circuit["gates"],
        }
    return {
        "qubits": circuit.num_qubits,
        "gates": [
            {"name": op.name, "qubits": [circuit.find_bit(q).index for q in qargs]}
            for op, qargs, _ in circuit.data
        ],
    }
