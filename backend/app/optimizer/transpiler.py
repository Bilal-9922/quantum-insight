def transpile_circuit(circuit, optimization_level=3):
    try:
        from qiskit import transpile
        return transpile(circuit, optimization_level=optimization_level)
    except Exception:
        return circuit
