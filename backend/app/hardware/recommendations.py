from typing import Any, Dict, List


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def generate_hardware_recommendations(
    metrics: Dict[str, Any],
    noise: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Generate hardware-oriented recommendations from circuit metrics.

    This module does not claim live backend availability or live calibration
    data. Recommendations are based on structural circuit characteristics
    such as qubit count, depth, two-qubit operations, gate density, and
    estimated noise exposure.
    """

    noise = noise or {}

    qubits = int(_safe_float(metrics.get("qubits"), 0))
    gate_count = int(_safe_float(metrics.get("gate_count"), 0))
    depth = int(_safe_float(metrics.get("depth"), 0))
    two_qubit_gates = int(
        _safe_float(metrics.get("two_qubit_gates"), 0)
    )

    two_qubit_ratio = _safe_float(
        metrics.get("two_qubit_ratio"),
        two_qubit_gates / max(1, gate_count),
    )

    gate_density = _safe_float(
        metrics.get("gate_density"),
        gate_count / max(1, qubits * max(1, depth)),
    )

    qubit_utilization = _safe_float(
        metrics.get("qubit_utilization"),
        0.0,
    )

    noise_score = _safe_float(
        noise.get("score")
        if isinstance(noise, dict)
        else None,
        0.0,
    )

    recommendations: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # Qubit requirements
    # ---------------------------------------------------------
    if qubits <= 5:
        qubit_message = (
            "Small qubit requirement. The circuit is suitable for "
            "small-scale hardware experiments and educational testing."
        )
        qubit_level = "low"
    elif qubits <= 20:
        qubit_message = (
            "Moderate qubit requirement. Consider hardware with enough "
            "available qubits while leaving some routing and connectivity "
            "headroom."
        )
        qubit_level = "moderate"
    else:
        qubit_message = (
            "High qubit requirement. Prefer hardware with a sufficiently "
            "large qubit count and good connectivity to reduce routing "
            "overhead."
        )
        qubit_level = "high"

    recommendations.append(
        {
            "type": "qubit_capacity",
            "priority": qubit_level,
            "title": "Qubit Capacity",
            "message": qubit_message,
            "metric": qubits,
        }
    )

    # ---------------------------------------------------------
    # Circuit depth
    # ---------------------------------------------------------
    if depth <= 5:
        depth_level = "low"
        depth_message = (
            "Low circuit depth. The circuit has relatively limited "
            "sequential execution exposure."
        )
    elif depth <= 20:
        depth_level = "moderate"
        depth_message = (
            "Moderate circuit depth. Hardware with good gate fidelity "
            "and stable execution is recommended."
        )
    else:
        depth_level = "high"
        depth_message = (
            "High circuit depth. Prefer hardware with strong gate fidelity "
            "and low decoherence exposure, and consider circuit optimization "
            "before execution."
        )

    recommendations.append(
        {
            "type": "circuit_depth",
            "priority": depth_level,
            "title": "Circuit Depth",
            "message": depth_message,
            "metric": depth,
        }
    )

    # ---------------------------------------------------------
    # Two-qubit gates
    # ---------------------------------------------------------
    if two_qubit_ratio <= 0.20:
        two_qubit_level = "low"
        two_qubit_message = (
            "Low two-qubit gate concentration. Connectivity constraints "
            "are less likely to dominate circuit execution."
        )
    elif two_qubit_ratio <= 0.50:
        two_qubit_level = "moderate"
        two_qubit_message = (
            "Moderate two-qubit gate concentration. Prefer hardware with "
            "good qubit connectivity and reliable entangling gates."
        )
    else:
        two_qubit_level = "high"
        two_qubit_message = (
            "High two-qubit gate concentration. Hardware connectivity and "
            "two-qubit gate fidelity are especially important for this circuit."
        )

    recommendations.append(
        {
            "type": "connectivity",
            "priority": two_qubit_level,
            "title": "Qubit Connectivity",
            "message": two_qubit_message,
            "metric": round(two_qubit_ratio, 4),
        }
    )

    # ---------------------------------------------------------
    # Gate density
    # ---------------------------------------------------------
    if gate_density <= 0.50:
        density_level = "low"
        density_message = (
            "Low gate density. Hardware execution should generally have "
            "limited operation crowding."
        )
    elif gate_density <= 1.50:
        density_level = "moderate"
        density_message = (
            "Moderate gate density. Review gate scheduling and hardware "
            "execution constraints before running larger workloads."
        )
    else:
        density_level = "high"
        density_message = (
            "High gate density. Consider optimization and transpilation "
            "before execution to reduce unnecessary hardware operations."
        )

    recommendations.append(
        {
            "type": "gate_density",
            "priority": density_level,
            "title": "Gate Density",
            "message": density_message,
            "metric": round(gate_density, 4),
        }
    )

    # ---------------------------------------------------------
    # Noise exposure
    # ---------------------------------------------------------
    if noise_score >= 0.70:
        noise_level = "high"
        noise_message = (
            "Estimated noise exposure is high. Prefer lower-noise hardware "
            "and validate the circuit under a realistic noise model before "
            "hardware execution."
        )
    elif noise_score >= 0.40:
        noise_level = "moderate"
        noise_message = (
            "Estimated noise exposure is moderate. Hardware calibration "
            "quality and gate fidelity should be considered before execution."
        )
    else:
        noise_level = "low"
        noise_message = (
            "Estimated noise exposure is relatively low from the available "
            "circuit analysis."
        )

    recommendations.append(
        {
            "type": "noise_exposure",
            "priority": noise_level,
            "title": "Noise Exposure",
            "message": noise_message,
            "metric": round(noise_score, 4),
        }
    )

    # ---------------------------------------------------------
    # Overall hardware guidance
    # ---------------------------------------------------------
    risk_values = {
        "low": 0,
        "moderate": 1,
        "high": 2,
    }

    risk_score = (
        risk_values.get(qubit_level, 0)
        + risk_values.get(depth_level, 0)
        + risk_values.get(two_qubit_level, 0)
        + risk_values.get(density_level, 0)
        + risk_values.get(noise_level, 0)
    )

    if risk_score <= 3:
        execution_level = "favorable"
        summary = (
            "The circuit has relatively modest hardware requirements. "
            "Standard transpilation and validation should be sufficient "
            "before execution."
        )
    elif risk_score <= 6:
        execution_level = "moderate"
        summary = (
            "The circuit has moderate hardware requirements. "
            "Hardware connectivity, gate fidelity, and transpilation "
            "should be reviewed before execution."
        )
    else:
        execution_level = "challenging"
        summary = (
            "The circuit has demanding hardware requirements. "
            "Circuit optimization, hardware-aware transpilation, and "
            "noise validation are recommended before execution."
        )

    # ---------------------------------------------------------
    # Hardware characteristics
    # ---------------------------------------------------------
    hardware_characteristics = {
        "minimum_qubits": qubits,
        "connectivity_importance": (
            "high"
            if two_qubit_ratio > 0.50
            else "moderate"
            if two_qubit_ratio > 0.20
            else "low"
        ),
        "gate_fidelity_importance": (
            "high"
            if depth > 20 or two_qubit_ratio > 0.50
            else "moderate"
            if depth > 5 or two_qubit_ratio > 0.20
            else "low"
        ),
        "noise_sensitivity": noise_level,
    }

    return {
        "available": True,
        "execution_level": execution_level,
        "summary": summary,
        "hardware_characteristics": hardware_characteristics,
        "recommendations": recommendations,
        "basis": {
            "qubits": qubits,
            "gate_count": gate_count,
            "depth": depth,
            "two_qubit_gates": two_qubit_gates,
            "two_qubit_ratio": round(two_qubit_ratio, 4),
            "gate_density": round(gate_density, 4),
            "qubit_utilization": round(qubit_utilization, 4),
            "noise_score": round(noise_score, 4),
        },
        "disclaimer": (
            "These recommendations are based on circuit-level metrics "
            "and available noise analysis. They do not represent live "
            "hardware calibration, queue, or backend availability data."
        ),
    }
