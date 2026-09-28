def recommend(analysis):
    qhi = analysis["health"]["score"]
    recs = []
    if analysis["metrics"]["two_qubit_ratio"] > 0.25:
        recs.append("Reduce unnecessary two-qubit operations where circuit semantics allow.")
    if analysis["metrics"]["depth"] > 20:
        recs.append("Reduce circuit depth using cancellation, fusion, and backend-aware transpilation.")
    if analysis["anomaly"]["anomaly"]:
        recs.append("Inspect the unusual circuit structure flagged by anomaly detection.")
    if not recs:
        recs.append("The circuit has no major heuristic issue; validate behavior under a realistic backend/noise model.")
    return {
        "summary": f"QHI is {qhi}/100 ({analysis['health']['category']}).",
        "recommendations": recs,
        "provider": "deterministic-fallback"
    }
