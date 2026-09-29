from app.optimizer.gate_cancellation import cancel_adjacent

def test_x_x_cancel():
    gates = [{"name":"x","qubits":[0]}, {"name":"x","qubits":[0]}]
    assert cancel_adjacent(gates) == []
