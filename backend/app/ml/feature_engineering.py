import numpy as np

FEATURES = ["qubits", "gate_count", "depth", "one_qubit_gates", "two_qubit_gates", "two_qubit_ratio", "gate_density", "measurement_ratio"]

def vector(metrics):
    return np.array([[metrics.get(k, 0) for k in FEATURES]], dtype=float)
