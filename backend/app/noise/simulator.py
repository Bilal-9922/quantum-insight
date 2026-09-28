def analyze_noise(metrics):
    exposure = min(100, metrics["depth"] * 0.8 + metrics["two_qubit_ratio"] * 100)
    return {
        "noise_exposure_percent": round(exposure, 1),
        "method": "heuristic",
        "note": "Install and configure Aer noise models for physical/noise-model simulation."
    }
