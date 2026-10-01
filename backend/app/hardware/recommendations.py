from typing import Any, Dict, List, Optional
import re


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _detect_hardware_target(
    source_code: Optional[str],
) -> Dict[str, Any]:
    """
    Detect hardware/provider information from submitted source code.

    This performs static source inspection only.
    It does not execute the submitted code and does not query
    live hardware availability.
    """

    code = source_code or ""
    code_lower = code.lower()

    detected_provider = None
    hardware_platform = None
    execution_target = None
    backend_name = None
    minimum_qubits = None
    backend_selection = None
    simulator_requested = None
    hardware_constraints: List[str] = []

    # ---------------------------------------------------------
    # IBM QUANTUM / QISKIT RUNTIME
    # ---------------------------------------------------------

    ibm_indicators = [
        "qiskit_ibm_runtime",
        "qiskitruntimeservice",
        "qiskitruntimeservice(",
        'channel="ibm_quantum"',
        "channel='ibm_quantum'",
        "ibm_quantum",
        "samplerv2",
    ]

    if any(indicator in code_lower for indicator in ibm_indicators):
        detected_provider = "IBM Quantum"
        hardware_platform = "IBM Quantum / Qiskit Runtime"

    # ---------------------------------------------------------
    # REAL HARDWARE VS SIMULATOR
    # ---------------------------------------------------------

    if "simulator=False" in code or "simulator = False" in code_lower:
        execution_target = "Real quantum hardware"
        simulator_requested = False

    elif "simulator=True" in code or "simulator = True" in code_lower:
        execution_target = "Quantum simulator"
        simulator_requested = True

    # ---------------------------------------------------------
    # IBM BACKEND SELECTION
    # ---------------------------------------------------------

    least_busy_match = re.search(
        r"least_busy\s*\((.*?)\)",
        code,
        flags=re.DOTALL,
    )

    if least_busy_match:
        backend_selection = "Least-busy backend"

    # ---------------------------------------------------------
    # MINIMUM QUBIT REQUIREMENT
    # ---------------------------------------------------------

    min_qubits_match = re.search(
        r"min_num_qubits\s*=\s*(\d+)",
        code,
        flags=re.IGNORECASE,
    )

    if min_qubits_match:
        minimum_qubits = int(min_qubits_match.group(1))

        hardware_constraints.append(
            f"Minimum backend size: {minimum_qubits} qubits"
        )

    # ---------------------------------------------------------
    # EXPLICIT BACKEND NAME
    # ---------------------------------------------------------

    backend_name_patterns = [
        r'backend\s*=\s*["\']([^"\']+)["\']',
        r'backend_name\s*=\s*["\']([^"\']+)["\']',
    ]

    for pattern in backend_name_patterns:
        match = re.search(
            pattern,
            code,
            flags=re.IGNORECASE,
        )

        if match:
            candidate = match.group(1).strip()

            if candidate:
                backend_name = candidate
                break

    # ---------------------------------------------------------
    # IBM CHANNEL
    # ---------------------------------------------------------

    ibm_channel_match = re.search(
        r'channel\s*=\s*["\']([^"\']+)["\']',
        code,
        flags=re.IGNORECASE,
    )

    if ibm_channel_match:
        channel = ibm_channel_match.group(1).strip()

        if channel.lower() == "ibm_quantum":
            detected_provider = "IBM Quantum"
            hardware_platform = "IBM Quantum / Qiskit Runtime"

    # ---------------------------------------------------------
    # HARDWARE CONSTRAINTS
    # ---------------------------------------------------------

    if simulator_requested is False:
        hardware_constraints.append(
            "Real hardware execution requested"
        )

    if backend_selection:
        hardware_constraints.append(
            "Backend selected dynamically"
        )

    if backend_name:
        hardware_constraints.append(
            f"Explicit backend: {backend_name}"
        )

    # ---------------------------------------------------------
    # DEFAULT / UNKNOWN
    # ---------------------------------------------------------

    if detected_provider:
        detection_status = "detected"
    else:
        detection_status = "not_detected"

    return {
        "detected": detection_status == "detected",
        "provider": detected_provider,
        "platform": hardware_platform,
        "execution_target": execution_target,
        "backend_name": backend_name,
        "minimum_qubits": minimum_qubits,
        "backend_selection": backend_selection,
        "simulator_requested": simulator_requested,
        "constraints": hardware_constraints,
    }


def generate_hardware_recommendations(
    metrics: Dict[str, Any],
    noise: Dict[str, Any] | None = None,
    source_code: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate hardware-oriented recommendations from circuit metrics,
    noise analysis, and detected hardware information in source code.

    The submitted source code is inspected statically. It is never
    executed by this function.

    Live backend availability, queue information, calibration data,
    and current hardware error rates are not queried here.
    """

    noise = noise or {}

    # =========================================================
    # CIRCUIT METRICS
    # =========================================================

    qubits = int(
        _safe_float(
            metrics.get("qubits"),
            0,
        )
    )

    gate_count = int(
        _safe_float(
            metrics.get("gate_count"),
            0,
        )
    )

    depth = int(
        _safe_float(
            metrics.get("depth"),
            0,
        )
    )

    two_qubit_gates = int(
        _safe_float(
            metrics.get("two_qubit_gates"),
            0,
        )
    )

    two_qubit_ratio = _safe_float(
        metrics.get("two_qubit_ratio"),
        two_qubit_gates / max(1, gate_count),
    )

    gate_density = _safe_float(
        metrics.get("gate_density"),
        gate_count / max(
            1,
            qubits * max(1, depth),
        ),
    )

    qubit_utilization = _safe_float(
        metrics.get("qubit_utilization"),
        0.0,
    )

    # =========================================================
    # NOISE ANALYSIS
    # =========================================================

    noise_exposure_percent = _safe_float(
        noise.get("noise_exposure_percent"),
        0.0,
    )

    noise_score = noise_exposure_percent / 100.0
    noise_score = max(
        0.0,
        min(1.0, noise_score),
    )

    # =========================================================
    # HARDWARE DETECTION
    # =========================================================

    hardware_target = _detect_hardware_target(
        source_code
    )

    detected_provider = hardware_target.get(
        "provider"
    )

    detected_platform = hardware_target.get(
        "platform"
    )

    execution_target = hardware_target.get(
        "execution_target"
    )

    detected_backend = hardware_target.get(
        "backend_name"
    )

    requested_minimum_qubits = hardware_target.get(
        "minimum_qubits"
    )

    backend_selection = hardware_target.get(
        "backend_selection"
    )

    # =========================================================
    # RECOMMENDATIONS
    # =========================================================

    recommendations: List[Dict[str, Any]] = []

    # =========================================================
    # QUBIT CAPACITY
    # =========================================================

    if qubits <= 5:
        qubit_level = "low"

        qubit_message = (
            "Small circuit qubit requirement. "
            "The circuit itself does not require a large "
            "quantum processor."
        )

    elif qubits <= 20:
        qubit_level = "moderate"

        qubit_message = (
            "Moderate qubit requirement. Consider hardware "
            "with enough available qubits while leaving "
            "routing and connectivity headroom."
        )

    else:
        qubit_level = "high"

        qubit_message = (
            "High qubit requirement. Prefer hardware with "
            "a sufficiently large qubit count and suitable "
            "connectivity to reduce routing overhead."
        )

    # If source code explicitly requires more qubits,
    # distinguish circuit requirement from requested hardware size.

    if (
        isinstance(requested_minimum_qubits, int)
        and requested_minimum_qubits > qubits
    ):
        qubit_message = (
            f"The circuit requires {qubits} qubits, but the "
            f"submitted code explicitly requests a backend "
            f"with at least {requested_minimum_qubits} qubits."
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

    # =========================================================
    # CIRCUIT DEPTH
    # =========================================================

    if depth <= 5:
        depth_level = "low"

        depth_message = (
            "Low circuit depth. The circuit has relatively "
            "limited sequential execution exposure."
        )

    elif depth <= 20:
        depth_level = "moderate"

        depth_message = (
            "Moderate circuit depth. Hardware with good "
            "gate fidelity and stable execution is recommended."
        )

    else:
        depth_level = "high"

        depth_message = (
            "High circuit depth. Prefer hardware with strong "
            "gate fidelity and low decoherence exposure, and "
            "consider circuit optimization before execution."
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

    # =========================================================
    # TWO-QUBIT CONNECTIVITY
    # =========================================================

    if two_qubit_ratio <= 0.20:
        two_qubit_level = "low"

        two_qubit_message = (
            "Low two-qubit gate concentration. Connectivity "
            "constraints are less likely to dominate execution."
        )

    elif two_qubit_ratio <= 0.50:
        two_qubit_level = "moderate"

        two_qubit_message = (
            "Moderate two-qubit gate concentration. Prefer "
            "hardware with good qubit connectivity and "
            "reliable entangling gates."
        )

    else:
        two_qubit_level = "high"

        two_qubit_message = (
            "High two-qubit gate concentration. Hardware "
            "connectivity and two-qubit gate fidelity are "
            "especially important for this circuit."
        )

    recommendations.append(
        {
            "type": "connectivity",
            "priority": two_qubit_level,
            "title": "Qubit Connectivity",
            "message": two_qubit_message,
            "metric": round(
                two_qubit_ratio,
                4,
            ),
        }
    )

    # =========================================================
    # GATE DENSITY
    # =========================================================

    if gate_density <= 0.50:
        density_level = "low"

        density_message = (
            "Low gate density. Hardware execution should "
            "generally have limited operation crowding."
        )

    elif gate_density <= 1.50:
        density_level = "moderate"

        density_message = (
            "Moderate gate density. Review gate scheduling "
            "and hardware execution constraints before "
            "running larger workloads."
        )

    else:
        density_level = "high"

        density_message = (
            "High gate density. Consider optimization and "
            "hardware-aware transpilation before execution."
        )

    recommendations.append(
        {
            "type": "gate_density",
            "priority": density_level,
            "title": "Gate Density",
            "message": density_message,
            "metric": round(
                gate_density,
                4,
            ),
        }
    )

    # =========================================================
    # NOISE EXPOSURE
    # =========================================================

    if noise_score >= 0.70:
        noise_level = "high"

        noise_message = (
            f"Estimated noise exposure is high at "
            f"{noise_exposure_percent:.1f}%. Prefer lower-noise "
            "hardware and validate the circuit under a realistic "
            "noise model before hardware execution."
        )

    elif noise_score >= 0.40:
        noise_level = "moderate"

        noise_message = (
            f"Estimated noise exposure is moderate at "
            f"{noise_exposure_percent:.1f}%. Hardware calibration "
            "quality and gate fidelity should be considered "
            "before execution."
        )

    else:
        noise_level = "low"

        noise_message = (
            f"Estimated noise exposure is relatively low at "
            f"{noise_exposure_percent:.1f}% based on the "
            "available circuit analysis."
        )

    recommendations.append(
        {
            "type": "noise_exposure",
            "priority": noise_level,
            "title": "Noise Exposure",
            "message": noise_message,
            "metric": round(
                noise_score,
                4,
            ),
        }
    )

    # =========================================================
    # HARDWARE SYSTEM RECOMMENDATION
    # =========================================================

    if detected_provider == "IBM Quantum":

        hardware_system = (
            "IBM Quantum-compatible superconducting QPU"
        )

        if requested_minimum_qubits:
            hardware_system_reason = (
                "IBM Quantum / Qiskit Runtime hardware was "
                "detected in the submitted source. The circuit "
                f"requires {qubits} qubits, while the code "
                f"requests a backend with at least "
                f"{requested_minimum_qubits} qubits."
            )
        else:
            hardware_system_reason = (
                "IBM Quantum / Qiskit Runtime hardware was "
                "detected in the submitted source. A compatible "
                "IBM Quantum superconducting QPU should be "
                "considered based on the circuit's qubit, "
                "connectivity and gate-fidelity requirements."
            )

        if backend_selection:
            hardware_system_reason += (
                " The code also uses dynamic least-busy backend "
                "selection."
            )

    elif two_qubit_ratio > 0.50:

        hardware_system = "Superconducting QPU"

        hardware_system_reason = (
            "The circuit contains a high concentration of "
            "two-qubit operations, making reliable entangling "
            "gates and suitable qubit connectivity important."
        )

    elif depth > 20 or noise_score >= 0.70:

        hardware_system = "Low-noise quantum processor"

        hardware_system_reason = (
            "The circuit has significant execution or noise "
            "exposure, so low-noise operation and strong gate "
            "fidelity are important."
        )

    elif qubits <= 5 and depth <= 5:

        hardware_system = "Small-scale superconducting QPU"

        hardware_system_reason = (
            "The circuit requires few qubits and has low depth, "
            "making a small-scale quantum processor suitable "
            "for experimentation."
        )

    else:

        hardware_system = "Superconducting QPU"

        hardware_system_reason = (
            "The circuit requires a gate-based quantum processor "
            "with sufficient qubit capacity and reliable "
            "gate execution."
        )

    recommendations.insert(
        0,
        {
            "type": "hardware_system",
            "priority": "high",
            "title": "Recommended Hardware System",
            "message": (
                f"{hardware_system}. "
                f"{hardware_system_reason}"
            ),
            "metric": qubits,
            "hardware_system": hardware_system,
        },
    )

    # =========================================================
    # HARDWARE CHARACTERISTICS
    # =========================================================

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

    # =========================================================
    # EXECUTION RISK
    # =========================================================

    risk_values = {
        "low": 0,
        "moderate": 1,
        "high": 2,
    }

    risk_score = (
        risk_values.get(
            qubit_level,
            0,
        )
        + risk_values.get(
            depth_level,
            0,
        )
        + risk_values.get(
            two_qubit_level,
            0,
        )
        + risk_values.get(
            density_level,
            0,
        )
        + risk_values.get(
            noise_level,
            0,
        )
    )

    if risk_score <= 3:

        execution_level = "favorable"

        summary = (
            "The circuit has relatively modest hardware "
            "requirements. Standard transpilation and "
            "validation should be sufficient before execution."
        )

    elif risk_score <= 6:

        execution_level = "moderate"

        summary = (
            "The circuit has moderate hardware requirements. "
            "Hardware connectivity, gate fidelity, noise "
            "exposure, and transpilation should be reviewed "
            "before execution."
        )

    else:

        execution_level = "challenging"

        summary = (
            "The circuit has demanding hardware requirements. "
            "Circuit optimization, hardware-aware transpilation, "
            "and noise validation are recommended before execution."
        )

    # =========================================================
    # SOURCE / HARDWARE DETECTION SUMMARY
    # =========================================================

    hardware_detection = {
        "detected": hardware_target.get(
            "detected",
            False,
        ),
        "provider": detected_provider,
        "platform": detected_platform,
        "execution_target": execution_target,
        "backend_name": detected_backend,
        "minimum_qubits": requested_minimum_qubits,
        "backend_selection": backend_selection,
        "simulator_requested": hardware_target.get(
            "simulator_requested"
        ),
        "constraints": hardware_target.get(
            "constraints",
            [],
        ),
    }

    # =========================================================
    # RETURN
    # =========================================================

    return {
        "available": True,

        "execution_level": execution_level,

        "summary": summary,

        "hardware_detection": hardware_detection,

        "recommended_hardware": {
            "system": hardware_system,
            "reason": hardware_system_reason,

            "minimum_qubits": qubits,

            "connectivity_requirement": (
                connectivity_importance
            ),

            "gate_fidelity_requirement": (
                gate_fidelity_importance
            ),

            "noise_sensitivity": noise_level,
        },

        "hardware_characteristics": (
            hardware_characteristics
        ),

        "recommendations": recommendations,

        "basis": {
            "qubits": qubits,
            "gate_count": gate_count,
            "depth": depth,
            "two_qubit_gates": two_qubit_gates,

            "two_qubit_ratio": round(
                two_qubit_ratio,
                4,
            ),

            "gate_density": round(
                gate_density,
                4,
            ),

            "qubit_utilization": round(
                qubit_utilization,
                4,
            ),

            "noise_score": round(
                noise_score,
                4,
            ),

            "noise_exposure_percent": round(
                noise_exposure_percent,
                1,
            ),
        },

        "disclaimer": (
            "Hardware recommendations combine circuit-level "
            "metrics with hardware information statically "
            "detected from the submitted source code. "
            "They do not represent live hardware calibration, "
            "queue status, backend availability, or current "
            "hardware error rates."
        ),
    }
