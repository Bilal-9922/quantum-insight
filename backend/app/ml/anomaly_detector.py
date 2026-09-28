from sklearn.ensemble import IsolationForest
import numpy as np

class AnomalyDetector:
    def __init__(self):
        rng = np.random.default_rng(42)
        X = rng.normal(size=(500, 6))
        self.model = IsolationForest(random_state=42, contamination=0.06)
        self.model.fit(X)

    def predict(self, metrics):
        x = np.array([[
            metrics["qubits"],
            metrics["gate_count"] / 100,
            metrics["depth"] / 50,
            metrics["two_qubit_ratio"],
            metrics["gate_density"],
            metrics["measurement_ratio"],
        ]])
        pred = int(self.model.predict(x)[0])
        score = float(self.model.decision_function(x)[0])
        return {"anomaly": pred == -1, "score": round(score, 4)}
