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
    score = sum(c[k] * w for k, w in WEIGHTS.items())
    score = round(max(0, min(100, score)), 1)
    category = "Healthy" if score >= 75 else "Moderate" if score >= 50 else "Critical"
    return {"score": score, "category": category, "components": c, "weights": WEIGHTS}
