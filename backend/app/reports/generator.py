def generate_report(analysis):
    return {
        "title": "QuantumInsight Circuit Analysis Report",
        "summary": analysis.get("health", {}),
        "metrics": analysis.get("metrics", {}),
        "anomaly": analysis.get("anomaly", {}),
        "recommendations": analysis.get("recommendations", {}),
    }
