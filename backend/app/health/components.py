def health_components(m):
    depth_eff = max(0.0, 100 - min(100, m["depth"] * 2.0))
    gate_eff = max(0.0, 100 - min(100, m["gate_count"] * 0.55))
    qubit_util = min(100.0, 50 + min(50, m["qubits"] * 5))
    two_q_eff = max(0.0, 100 - min(100, m["two_qubit_ratio"] * 140))
    noise = max(0.0, 100 - min(100, m["two_qubit_ratio"] * 100 + m["depth"] * 0.8))
    opt = min(100.0, max(0.0, m["two_qubit_ratio"] * 100 + m["depth"] * 1.2))
    return {
        "depth_efficiency": round(depth_eff, 1),
        "gate_efficiency": round(gate_eff, 1),
        "qubit_utilization": round(qubit_util, 1),
        "two_qubit_efficiency": round(two_q_eff, 1),
        "noise_exposure": round(noise, 1),
        "optimization_potential": round(opt, 1),
    }
