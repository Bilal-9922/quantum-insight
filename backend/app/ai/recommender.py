def recommend(analysis):
    health = analysis.get("health", {})
    metrics = analysis.get("metrics", {})
    anomaly = analysis.get("anomaly", {})

    qhi = float(health.get("score", 0))
    category = health.get("category", "Unknown")
    components = health.get("components", {})

    # Circuit metrics
    qubits = int(metrics.get("qubits", 0))
    gates = int(metrics.get("gate_count", 0))
    depth = int(metrics.get("depth", 0))
    two_qubit_ratio = float(metrics.get("two_qubit_ratio", 0))

    two_qubit_gates = int(
        metrics.get(
            "two_qubit_gates",
            round(gates * two_qubit_ratio)
        )
    )

    cancellation_opportunities = int(
        metrics.get(
            "cancellation_opportunities",
            0
        )
    )

    # Health components
    depth_efficiency = float(
        components.get("depth_efficiency", 100)
    )

    gate_efficiency = float(
        components.get("gate_efficiency", 100)
    )

    qubit_utilization = float(
        components.get("qubit_utilization", 100)
    )

    two_qubit_efficiency = float(
        components.get("two_qubit_efficiency", 100)
    )

    noise_exposure = float(
        components.get("noise_exposure", 100)
    )

    optimization_potential = float(
        components.get("optimization_potential", 0)
    )

    recommendations = []

    # ---------------------------------------------------------
# Two-qubit operations
# ---------------------------------------------------------

if cancellation_opportunities > 0:

    plural = (
        "opportunity"
        if cancellation_opportunities == 1
        else "opportunities"
    )

    recommendations.append(
        f"Detected {cancellation_opportunities} adjacent "
        f"gate cancellation {plural}. Review repeated "
        "self-inverse gates such as CX, X, H, or similar "
        "operations because they may cancel and reduce "
        "circuit complexity."
    )

elif two_qubit_gates <= 1 and gates <= 5:

    recommendations.append(
        f"The circuit contains {two_qubit_gates} "
        "entangling operation in a very small workload. "
        "This is not necessarily an issue; preserve it "
        "unless backend constraints or transpilation "
        "introduce additional overhead."
    )

elif two_qubit_ratio >= 0.75:

    recommendations.append(
        f"Two-qubit operations are very high "
        f"({two_qubit_ratio * 100:.1f}% of gates). "
        "Review CX, CZ, and SWAP sequences for possible "
        "cancellation, fusion, or restructuring."
    )

elif two_qubit_ratio >= 0.50:

    recommendations.append(
        f"Two-qubit operations make up "
        f"{two_qubit_ratio * 100:.1f}% of gates. "
        "For larger circuits, review entangling sequences "
        "for unnecessary operations and possible cancellation."
    )

elif two_qubit_ratio >= 0.25:

    recommendations.append(
        f"The circuit contains a moderate two-qubit gate ratio "
        f"({two_qubit_ratio * 100:.1f}%). "
        "Check whether neighboring entangling operations "
        "can be simplified or cancelled."
    )

    # ---------------------------------------------------------
    # Circuit depth
    # ---------------------------------------------------------

    if depth >= 50:
        recommendations.append(
            f"Circuit depth is high at {depth}. "
            "Look for opportunities to parallelize independent "
            "operations and apply gate cancellation or fusion."
        )

    elif depth >= 20:
        recommendations.append(
            f"Circuit depth is {depth}. "
            "Consider gate fusion, cancellation, and "
            "backend-aware transpilation to reduce sequential layers."
        )

    elif depth_efficiency < 60:
        recommendations.append(
            f"Depth efficiency is {depth_efficiency:.1f}/100. "
            "Inspect sequential operations and determine whether "
            "independent gates can execute in parallel."
        )

    # ---------------------------------------------------------
    # Gate efficiency
    # ---------------------------------------------------------

    if gate_efficiency < 40:
        recommendations.append(
            f"Gate efficiency is low at {gate_efficiency:.1f}/100. "
            "Look for redundant gates, repeated operations, "
            "and neighbouring gates that can cancel."
        )

    elif gate_efficiency < 60:
        recommendations.append(
            f"Gate efficiency is moderate at {gate_efficiency:.1f}/100. "
            "Review repeated single-qubit operations and "
            "simplifiable gate sequences."
        )

    # ---------------------------------------------------------
    # Qubit utilization
    # ---------------------------------------------------------

    if qubit_utilization < 60:
        recommendations.append(
            f"Qubit utilization is {qubit_utilization:.1f}/100 "
            f"across {qubits} qubits. "
            "Check whether all allocated qubits are necessary."
        )

    # ---------------------------------------------------------
    # Two-qubit efficiency
    # ---------------------------------------------------------

    if two_qubit_efficiency < 50 and two_qubit_gates > 1:
        recommendations.append(
            f"Two-qubit gate efficiency is "
            f"{two_qubit_efficiency:.1f}/100. "
            "Review entangling-gate sequences for unnecessary "
            "operations and possible cancellation."
        )

    # ---------------------------------------------------------
    # Noise exposure
    # ---------------------------------------------------------

    if noise_exposure < 40:
        recommendations.append(
            f"Noise exposure score is low at "
            f"{noise_exposure:.1f}/100. "
            "Reducing circuit depth and two-qubit operations "
            "should be prioritized for execution on noisy hardware."
        )

    elif noise_exposure < 60:
        recommendations.append(
            f"Noise exposure score is moderate at "
            f"{noise_exposure:.1f}/100. "
            "Reducing depth and entangling operations could "
            "improve hardware robustness."
        )

    # ---------------------------------------------------------
    # Optimization potential
    # ---------------------------------------------------------

    if optimization_potential >= 70:
        recommendations.append(
            f"Optimization potential is high at "
            f"{optimization_potential:.1f}/100. "
            "The circuit has several opportunities for "
            "structural simplification."
        )

    elif optimization_potential >= 45:
        recommendations.append(
            f"Optimization potential is moderate at "
            f"{optimization_potential:.1f}/100. "
            "Compare the circuit before and after transpilation "
            "to identify useful reductions."
        )

    # ---------------------------------------------------------
    # Anomaly detection
    # ---------------------------------------------------------

    if anomaly.get("anomaly"):
        recommendations.append(
            "Anomaly detection flagged unusual circuit structure. "
            "Inspect the gate distribution, depth, and two-qubit "
            "operations for unexpected patterns."
        )

    # ---------------------------------------------------------
    # Fallback recommendation
    # ---------------------------------------------------------

    if not recommendations:

        if qhi >= 85:
            recommendations.append(
                "The circuit shows strong overall health with no "
                "major heuristic issue detected. Preserve the "
                "current structure and validate it on the intended backend."
            )

        elif qhi >= 70:
            recommendations.append(
                "The circuit is generally healthy. Focus optimization "
                "on the lowest-scoring health component rather than "
                "making broad structural changes."
            )

        else:
            recommendations.append(
                "No single dominant issue was detected. Review the "
                "lowest-scoring health components for targeted optimization."
            )

    # Keep the response concise.
    recommendations = recommendations[:4]

    return {
        "summary": f"QHI is {qhi:.1f}/100 ({category}).",
        "recommendations": recommendations,
        "provider": "deterministic-fallback",
    }
