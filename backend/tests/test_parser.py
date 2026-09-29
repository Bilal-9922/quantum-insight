from app.circuit.parser import lightweight_parse

def test_parser():
    c = lightweight_parse("from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0,1)")
    assert c["qubits"] == 2
