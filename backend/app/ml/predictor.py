from app.ml.health_model import HealthModel
model = HealthModel()

def predict_health(components):
    return model.predict(components)
