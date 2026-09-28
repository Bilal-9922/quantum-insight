from app.health.scoring import calculate_qhi

def test_qhi_range():
    result = calculate_qhi({
        "qubits": 2, "gate_count": 4, "depth": 3,
        "one_qubit_gates": 3, "two_qubit_gates": 1,
        "two_qubit_ratio": .25, "gate_density": .6,
        "measurement_ratio": 0
    })
    assert 0 <= result["score"] <= 100
