def health_components(m):
    qubits = max(1, int(m.get("qubits", 0)))
    gate_count = max(0, int(m.get("gate_count", 0)))
    depth = max(0, int(m.get("depth", 0)))
    one_q = max(0, int(m.get("one_qubit_gates", 0)))
    two_q = max(0, int(m.get("two_qubit_gates", 0)))

    two_ratio = float(m.get("two_qubit_ratio", 0.0))
    gate_density = float(m.get("gate_density", 0.0))
    measurement_ratio = float(m.get("measurement_ratio", 0.0))

    # ---------------------------------------------------------
    # 1. Depth efficiency
    # ---------------------------------------------------------
    # Penalize deep circuits, but scale the penalty relative
    # to the number of qubits.
    depth_per_qubit = depth / qubits

    if depth_per_qubit <= 1:
        depth_eff = 100.0
    elif depth_per_qubit <= 3:
        depth_eff = 90.0 - (depth_per_qubit - 1) * 10.0
    elif depth_per_qubit <= 6:
        depth_eff = 70.0 - (depth_per_qubit - 3) * 8.0
    else:
        depth_eff = 46.0 - min(46.0, (depth_per_qubit - 6) * 5.0)

    depth_eff = max(0.0, min(100.0, depth_eff))

    # ---------------------------------------------------------
    # 2. Gate efficiency
    # ---------------------------------------------------------
    # Gate count alone should not determine health.
    # We compare gates against circuit size.
    gates_per_qubit = gate_count / qubits

    if gates_per_qubit <= 2:
        gate_eff = 100.0
    elif gates_per_qubit <= 5:
        gate_eff = 100.0 - (gates_per_qubit - 2) * 10.0
    elif gates_per_qubit <= 10:
        gate_eff = 70.0 - (gates_per_qubit - 5) * 6.0
    else:
        gate_eff = 40.0 - min(40.0, (gates_per_qubit - 10) * 3.0)

    gate_eff = max(0.0, min(100.0, gate_eff))

    # ---------------------------------------------------------
    # 3. Qubit utilization
    # ---------------------------------------------------------
    # Estimate active qubits from the parsed gate structure.
    # The metrics extractor does not currently return the exact
    # active-qubit set, so use gate participation as a proxy.
    #
    # For a circuit with gates, higher gate density means more
    # of the allocated qubits are likely being utilized.
    # Use the exact active-qubit calculation from metrics.py.
    qubit_utilization = float(
        m.get("qubit_utilization", 0.0)
    )
    
    qubit_util = (
        qubit_utilization * 100.0
    )
    
    qubit_util = max(
        0.0,
        min(100.0, qubit_util)
    )

    qubit_util = max(0.0, min(100.0, qubit_util))

    # ---------------------------------------------------------
    # 4. Two-qubit efficiency
    # ---------------------------------------------------------
    # Two-qubit gates are generally more expensive/noise-sensitive
    # than single-qubit operations.
    if two_q == 0:
        two_q_eff = 100.0
    elif two_ratio <= 0.10:
        two_q_eff = 98.0
    elif two_ratio <= 0.25:
        two_q_eff = 95.0 - (two_ratio - 0.10) * 60.0
    elif two_ratio <= 0.50:
        two_q_eff = 86.0 - (two_ratio - 0.25) * 48.0
    elif two_ratio <= 0.75:
        two_q_eff = 74.0 - (two_ratio - 0.50) * 56.0
    else:
        two_q_eff = 60.0 - min(
            60.0,
            (two_ratio - 0.75) * 80.0
        )
    
    two_q_eff = max(
        0.0,
        min(100.0, two_q_eff)
    )

    two_q_eff = max(0.0, min(100.0, two_q_eff))

    # ---------------------------------------------------------
    # 5. Noise exposure
    # ---------------------------------------------------------
    # Depth and two-qubit operations are the main contributors.
    depth_factor = min(100.0, depth_per_qubit * 8.0)
    two_q_factor = min(100.0, two_ratio * 100.0)

    noise_penalty = (
        depth_factor * 0.55
        + two_q_factor * 0.45
    )

    # Excessive measurement operations can also add overhead.
    if measurement_ratio > 0.20:
        noise_penalty += min(
            15.0,
            (measurement_ratio - 0.20) * 30.0
        )

    noise_exposure = 100.0 - min(100.0, noise_penalty)
    noise_exposure = max(0.0, min(100.0, noise_exposure))

    # ---------------------------------------------------------
    # 6. Optimization potential
    # ---------------------------------------------------------
    # Higher depth, density and two-qubit usage indicate more
    # possible opportunities for optimization.
    depth_opportunity = min(40.0, depth_per_qubit * 5.0)
    gate_opportunity = min(30.0, gates_per_qubit * 2.5)
    two_q_opportunity = min(30.0, two_ratio * 60.0)

    opt = (
        depth_opportunity
        + gate_opportunity
        + two_q_opportunity
    )

    # Very small/simple circuits should not be classified as
    # highly optimizable merely because of their structure.
    if gate_count <= qubits:
        opt *= 0.5

    opt = max(0.0, min(100.0, opt))

    return {
        "depth_efficiency": round(depth_eff, 1),
        "gate_efficiency": round(gate_eff, 1),
        "qubit_utilization": round(qubit_util, 1),
        "two_qubit_efficiency": round(two_q_eff, 1),
        "noise_exposure": round(noise_exposure, 1),
        "optimization_potential": round(opt, 1),
    }
