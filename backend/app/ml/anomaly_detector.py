from sklearn.ensemble import IsolationForest
import numpy as np


class AnomalyDetector:
    def __init__(self):
        rng = np.random.default_rng(42)

        # Synthetic baseline representing typical quantum circuits.
        # Features:
        # 1. qubits
        # 2. gate_count / 100
        # 3. depth / 50
        # 4. two_qubit_ratio
        # 5. gate_density
        # 6. measurement_ratio
        X = np.column_stack(
            [
                rng.uniform(1, 20, 1000),       # qubits
                rng.uniform(0.01, 2.0, 1000),   # normalized gate count
                rng.uniform(0.01, 1.0, 1000),   # normalized depth
                rng.uniform(0.0, 0.6, 1000),    # 2Q ratio
                rng.uniform(0.01, 2.0, 1000),   # gate density
                rng.uniform(0.0, 1.0, 1000),    # measurement ratio
            ]
        )

        self.model = IsolationForest(
            n_estimators=200,
            contamination=0.06,
            random_state=42,
        )

        self.model.fit(X)

    def predict(self, metrics):
        x = np.array(
            [[
                float(metrics.get("qubits", 0)),
                float(metrics.get("gate_count", 0)) / 100.0,
                float(metrics.get("depth", 0)) / 50.0,
                float(metrics.get("two_qubit_ratio", 0)),
                float(metrics.get("gate_density", 0)),
                float(metrics.get("measurement_ratio", 0)),
            ]]
        )

        prediction = int(self.model.predict(x)[0])

        decision_score = float(
            self.model.decision_function(x)[0]
        )

        # Convert Isolation Forest's signed decision score
        # into an intuitive 0-100 anomaly score.
        #
        # Higher value = more anomalous.
        anomaly_score = 50.0 - (decision_score * 100.0)

        anomaly_score = float(
            np.clip(anomaly_score, 0.0, 100.0)
        )

        # Use the model prediction together with the
        # normalized anomaly score.
        is_anomaly = prediction == -1

        return {
            "anomaly": is_anomaly,
            "score": round(anomaly_score, 2),
        }
