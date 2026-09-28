from app.circuit.metrics import extract_metrics

def test_metrics():
    c = {"qubits": 2, "gates": [{"name":"h","qubits":[0]}, {"name":"cx","qubits":[0,1]}]}
    m = extract_metrics(c)
    assert m["qubits"] == 2
    assert m["gate_count"] == 2
    assert m["two_qubit_gates"] == 1
