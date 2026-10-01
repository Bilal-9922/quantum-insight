from typing import Any, Dict, List


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

    The recommendations are based on circuit-level characteristics and
    available noise analysis. This function does not use live backend
    availability, queue information, calibration data, or current hardware
    error rates.
    """

    noise = noise or {}

    # ---------------------------------------------------------
    # Circuit metrics
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Noise analysis
    # ---------------------------------------------------------

    # Existing analyzer returns noise_exposure_percent.
    # Example:
    # noise_exposure_percent = 69.1
    #
    # Convert percentage to a normalized 0-1 value.
    noise_exposure_percent = _safe_float(
        noise.get("noise_exposure_percent"),
        0.0,
    )

    noise_score = noise_exposure_percent / 100.0

    # Keep the value inside the expected 0-1 range.
    noise_score = max(0.0, min(1.0, noise_score))

    recommendations: List[Dict[str, Any]] = []

    # ---------------------------------------------------------
    # Qubit capacity
    # ---------------------------------------------------------

    if qubits <= 5:
        qubit_level = "low"
        qubit_message = (
            "Small qubit requirement. The circuit is suitable for "
            "small-scale hardware experiments and educational testing."
        )
    elif qubits <= 20:
        qubit_level = "moderate"
        qubit_message = (
            "Moderate qubit requirement. Consider hardware with enough "
            "available qubits while leaving routing and connectivity "
            "headroom."
        )
    else:
        qubit_level = "high"
        qubit_message = (
            "High qubit requirement. Prefer hardware with a sufficiently "
            "large qubit count and good connectivity to reduce routing "
            "overhead."
        )

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
    # Two-qubit connectivity
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
            f"Estimated noise exposure is high at "
            f"{noise_exposure_percent:.1f}%. Prefer lower-noise hardware "
            "and validate the circuit under a realistic noise model before "
            "hardware execution."
        )
    elif noise_score >= 0.40:
        noise_level = "moderate"
        noise_message = (
            f"Estimated noise exposure is moderate at "
            f"{noise_exposure_percent:.1f}%. Hardware calibration quality "
            "and gate fidelity should be considered before execution."
        )
    else:
        noise_level = "low"
        noise_message = (
            f"Estimated noise exposure is relatively low at "
            f"{noise_exposure_percent:.1f}% based on the available "
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
    # Hardware system profile
    # ---------------------------------------------------------

    # This is a hardware PROFILE recommendation, not a claim about
    # a currently available specific backend.
    #
    # The current analysis does not contain live backend information,
    # so we recommend a suitable hardware architecture rather than
    # inventing a specific backend name.

    if two_qubit_ratio > 0.50:
        hardware_system = "Superconducting QPU"
        hardware_system_reason = (
            "The circuit contains a high concentration of two-qubit "
            "operations, making reliable entangling gates and suitable "
            "qubit connectivity important."
        )
    elif depth > 20 or noise_score >= 0.70:
        hardware_system = "Low-noise quantum processor"
        hardware_system_reason = (
            "The circuit has significant execution or noise exposure, "
            "so low-noise operation and strong gate fidelity are important."
        )
    elif qubits <= 5 and depth <= 5:
        hardware_system = "Small-scale superconducting QPU"
        hardware_system_reason = (
            "The circuit requires few qubits and has low depth, making "
            "a small-scale quantum processor suitable for experimentation."
        )
    else:
        hardware_system = "Superconducting QPU"
        hardware_system_reason = (
            "The circuit requires a gate-based quantum processor with "
            "sufficient qubit capacity and reliable gate execution."
        )

    recommendations.insert(
        0,
        {
            "type": "hardware_system",
            "priority": "high",
            "title": "Recommended Hardware System",
            "message": (
                f"{hardware_system}. {hardware_system_reason}"
            ),
            "metric": qubits,
            "hardware_system": hardware_system,
        },
    )

    # ---------------------------------------------------------
    # Hardware characteristics
    # ---------------------------------------------------------

    if two_qubit_ratio > 0.50:
        connectivity_importance = "high"
    elif two_qubit_ratio > 0.20:
        connectivity_importance = "moderate"
    else:
        connectivity_importance = "low"

    if depth > 20 or two_qubit_ratio > 0.50:
        gate_fidelity_importance = "high"
    elif depth > 5 or two_qubit_ratio > 0.20:
        gate_fidelity_importance = "moderate"
    else:
        gate_fidelity_importance = "low"

    hardware_characteristics = {
        "minimum_qubits": qubits,
        "connectivity_importance": connectivity_importance,
        "gate_fidelity_importance": gate_fidelity_importance,
        "noise_sensitivity": noise_level,
        "recommended_hardware_system": hardware_system,
    }

    # ---------------------------------------------------------
    # Overall hardware execution risk
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
            "Hardware connectivity, gate fidelity, noise exposure, and "
            "transpilation should be reviewed before execution."
        )
    else:
        execution_level = "challenging"
        summary = (
            "The circuit has demanding hardware requirements. "
            "Circuit optimization, hardware-aware transpilation, and "
            "noise validation are recommended before execution."
        )

    # ---------------------------------------------------------
    # Return hardware recommendation data
    # ---------------------------------------------------------

    return {
        "available": True,

        "execution_level": execution_level,

        "summary": summary,

        "recommended_hardware": {
            "system": hardware_system,
            "reason": hardware_system_reason,
            "minimum_qubits": qubits,
            "connectivity_requirement": connectivity_importance,
            "gate_fidelity_requirement": gate_fidelity_importance,
            "noise_sensitivity": noise_level,
        },

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
            "noise_exposure_percent": round(
                noise_exposure_percent,
                1,
            ),
        },

        "disclaimer": (
            "Hardware system recommendations are based on circuit-level "
            "metrics and available noise analysis. They do not represent "
            "live hardware calibration, queue status, backend availability, "
            "or current hardware error rates."
        ),
    }
