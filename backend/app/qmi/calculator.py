from __future__ import annotations

from typing import Any, Dict


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def _category(score: float) -> str:
    if score >= 85:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 50:
        return "Moderate"
    return "Difficult"


def calculate_qmi(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate the Quantum Maintainability Index (QMI).

    QMI measures how easy a quantum circuit is to understand,
    maintain, modify, and scale.

    Components:
        Readability      20%
        Gate Efficiency  20%
        Modularity       20%
        Scalability      15%
        Gate Diversity   15%
        Complexity       10%

    All component scores are normalized to 0-100.
    """

    qubits = max(
        1,
        int(_safe_float(metrics.get("qubits"), 1)),
    )

    gate_count = max(
        0,
        int(_safe_float(metrics.get("gate_count"), 0)),
    )

    depth = max(
        0,
        int(_safe_float(metrics.get("depth"), 0)),
    )

    two_qubit_gates = max(
        0,
        int(_safe_float(metrics.get("two_qubit_gates"), 0)),
    )

    one_qubit_gates = max(
        0,
        int(_safe_float(metrics.get("one_qubit_gates"), 0)),
    )

    gate_counts = metrics.get("gate_counts")

    if not isinstance(gate_counts, dict):
        gate_counts = {}

    # ---------------------------------------------------------
    # Derived metrics
    # ---------------------------------------------------------

    active_qubits = _safe_float(
        metrics.get("active_qubits"),
        qubits,
    )

    qubit_utilization = _safe_float(
        metrics.get("qubit_utilization"),
        active_qubits / qubits,
    )

    qubit_utilization = _clamp(
        qubit_utilization * 100.0
        if qubit_utilization <= 1
        else qubit_utilization
    )

    two_qubit_ratio = _safe_float(
        metrics.get("two_qubit_ratio"),
        two_qubit_gates / max(1, gate_count),
    )

    two_qubit_ratio = _clamp(
        two_qubit_ratio * 100.0
        if two_qubit_ratio <= 1
        else two_qubit_ratio
    )

    gate_density = _safe_float(
        metrics.get("gate_density"),
        gate_count / max(1, qubits * max(1, depth)),
    )

    cancellation_opportunities = max(
        0,
        int(
            _safe_float(
                metrics.get("cancellation_opportunities"),
                0,
            )
        ),
    )

    # ---------------------------------------------------------
    # 1. Readability Score — 20%
    # ---------------------------------------------------------
    #
    # Readability rewards:
    # - reasonable depth
    # - reasonable gate density
    # - organized gate structure
    #
    # Extremely deep/dense circuits become harder to understand.

    depth_penalty = min(
        60.0,
        max(0.0, depth - 10.0) * 1.5,
    )

    density_penalty = min(
        50.0,
        max(0.0, gate_density - 1.0) * 20.0,
    )

    readability = _clamp(
        100.0
        - depth_penalty
        - density_penalty
    )

    # ---------------------------------------------------------
    # 2. Gate Efficiency Score — 20%
    # ---------------------------------------------------------
    #
    # Rewards circuits that accomplish their work with fewer
    # unnecessary operations and limited cancellation potential.

    gate_per_qubit = gate_count / max(1, qubits)

    gate_efficiency = 100.0

    if gate_per_qubit > 5:
        gate_efficiency -= min(
            35.0,
            (gate_per_qubit - 5.0) * 4.0,
        )

    if depth > 10:
        gate_efficiency -= min(
            30.0,
            (depth - 10.0) * 1.5,
        )

    if gate_count > 0:
        cancellation_ratio = (
            cancellation_opportunities / gate_count
        )
        gate_efficiency -= min(
            25.0,
            cancellation_ratio * 100.0,
        )

    gate_efficiency = _clamp(gate_efficiency)

    # ---------------------------------------------------------
    # 3. Modularity Score — 20%
    # ---------------------------------------------------------
    #
    # A circuit that distributes operations across qubits in a
    # reasonably balanced way is easier to modify and maintain.

    if qubits <= 1:
        modularity = 100.0
    else:
        operations_per_qubit = (
            gate_count / qubits
        )

        if operations_per_qubit <= 2:
            modularity = 95.0
        elif operations_per_qubit <= 5:
            modularity = 90.0
        elif operations_per_qubit <= 10:
            modularity = 80.0
        elif operations_per_qubit <= 20:
            modularity = 68.0
        elif operations_per_qubit <= 40:
            modularity = 52.0
        else:
            modularity = 35.0

        # Very high two-qubit concentration can reduce
        # modular independence between qubit regions.
        modularity -= min(
            20.0,
            max(0.0, two_qubit_ratio - 40.0) * 0.25,
        )

    modularity = _clamp(modularity)

    # ---------------------------------------------------------
    # 4. Scalability Score — 15%
    # ---------------------------------------------------------
    #
    # Rewards circuits whose gate/depth requirements remain
    # manageable relative to the number of qubits.

    if qubits <= 5:
        scalability = 95.0
    elif qubits <= 10:
        scalability = 90.0
    elif qubits <= 20:
        scalability = 82.0
    elif qubits <= 50:
        scalability = 68.0
    elif qubits <= 100:
        scalability = 52.0
    else:
        scalability = 35.0

    gate_growth = gate_count / max(1, qubits)

    if gate_growth > 20:
        scalability -= min(
            25.0,
            (gate_growth - 20.0) * 0.7,
        )

    if depth > 30:
        scalability -= min(
            20.0,
            (depth - 30.0) * 0.7,
        )

    scalability = _clamp(scalability)

    # ---------------------------------------------------------
    # 5. Gate Diversity Score — 15%
    # ---------------------------------------------------------
    #
    # A moderate and purposeful variety of gate types improves
    # maintainability. Extremely high diversity can make a
    # circuit harder to understand and maintain.

    unique_gate_types = len(gate_counts)

    if unique_gate_types == 0:
        gate_diversity = 75.0
    elif unique_gate_types <= 3:
        gate_diversity = 95.0
    elif unique_gate_types <= 6:
        gate_diversity = 90.0
    elif unique_gate_types <= 10:
        gate_diversity = 78.0
    elif unique_gate_types <= 15:
        gate_diversity = 65.0
    else:
        gate_diversity = 50.0

    gate_diversity = _clamp(gate_diversity)

    # ---------------------------------------------------------
    # 6. Circuit Complexity Score — 10%
    # ---------------------------------------------------------
    #
    # Lower depth, fewer gates and fewer multi-qubit operations
    # produce a higher maintainability score.

    complexity_score = 100.0

    complexity_score -= min(
        35.0,
        gate_count * 0.35,
    )

    complexity_score -= min(
        30.0,
        depth * 1.2,
    )

    complexity_score -= min(
        25.0,
        two_qubit_gates * 0.25,
    )

    complexity_score = _clamp(complexity_score)

    # ---------------------------------------------------------
    # Weighted QMI
    # ---------------------------------------------------------

    weights = {
        "readability": 0.20,
        "gate_efficiency": 0.20,
        "modularity": 0.20,
        "scalability": 0.15,
        "gate_diversity": 0.15,
        "complexity": 0.10,
    }

    qmi = (
        readability * weights["readability"]
        + gate_efficiency * weights["gate_efficiency"]
        + modularity * weights["modularity"]
        + scalability * weights["scalability"]
        + gate_diversity * weights["gate_diversity"]
        + complexity_score * weights["complexity"]
    )

    qmi = round(_clamp(qmi), 1)

    components = {
        "readability": round(readability, 1),
        "gate_efficiency": round(gate_efficiency, 1),
        "modularity": round(modularity, 1),
        "scalability": round(scalability, 1),
        "gate_diversity": round(gate_diversity, 1),
        "complexity": round(complexity_score, 1),
    }

    return {
        "score": qmi,
        "category": _category(qmi),
        "components": components,
        "weights": weights,
        "basis": {
            "qubits": qubits,
            "gate_count": gate_count,
            "depth": depth,
            "one_qubit_gates": one_qubit_gates,
            "two_qubit_gates": two_qubit_gates,
            "two_qubit_ratio": round(
                two_qubit_ratio / 100.0,
                4,
            ),
            "gate_density": round(
                gate_density,
                4,
            ),
            "unique_gate_types": unique_gate_types,
            "cancellation_opportunities": cancellation_opportunities,
        },
    }
