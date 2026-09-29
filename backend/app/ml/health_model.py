import numpy as np
from sklearn.ensemble import RandomForestClassifier

class HealthModel:
    def __init__(self):
        rng = np.random.default_rng(7)
        X = rng.uniform(0, 1, size=(1500, 6))
        y = np.where(X.mean(axis=1) > 0.68, 0, np.where(X.mean(axis=1) > 0.42, 1, 2))
        self.model = RandomForestClassifier(n_estimators=120, random_state=7)
        self.model.fit(X, y)

    def predict(self, components):
        vals = np.array([[components[k] / 100 for k in [
            "depth_efficiency", "gate_efficiency", "qubit_utilization",
            "two_qubit_efficiency", "noise_exposure", "optimization_potential"
        ]]])
        label = int(self.model.predict(vals)[0])
        names = {0: "Healthy", 1: "Moderate", 2: "Critical"}
        return {"category": names[label]}
