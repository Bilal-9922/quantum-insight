from app.health.components import health_components


WEIGHTS = {
    "depth_efficiency": 0.22,
    "gate_efficiency": 0.18,
    "qubit_utilization": 0.12,
    "two_qubit_efficiency": 0.20,
    "noise_exposure": 0.16,
    "optimization_potential": 0.12,
}


def calculate_qhi(metrics):
    c = health_components(metrics)

    # All components except optimization_potential
    # are health scores where higher is better.
    #
    # optimization_potential is different:
    # higher = more room for optimization.
    # Therefore it is inverted when contributing to QHI.
    optimization_score = 100.0 - c["optimization_potential"]

    score = (
        c["depth_efficiency"] * WEIGHTS["depth_efficiency"]
        + c["gate_efficiency"] * WEIGHTS["gate_efficiency"]
        + c["qubit_utilization"] * WEIGHTS["qubit_utilization"]
        + c["two_qubit_efficiency"] * WEIGHTS["two_qubit_efficiency"]
        + c["noise_exposure"] * WEIGHTS["noise_exposure"]
        + optimization_score * WEIGHTS["optimization_potential"]
    )

    score = round(
        max(0.0, min(100.0, score)),
        1
    )

    if score >= 75:
        category = "Healthy"
    elif score >= 50:
        category = "Moderate"
    else:
        category = "Critical"

    return {
        "score": score,
        "category": category,
        "components": c,
        "weights": WEIGHTS,
    }
