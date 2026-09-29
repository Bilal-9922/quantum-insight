from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.security import sanitize_code_input
from app.auth import current_user
from app.circuit.parser import parse_qiskit_code
from app.circuit.metrics import extract_metrics
from app.circuit.visualization import circuit_data
from app.circuit.validator import validate_python
from app.health.scoring import calculate_qhi
from app.ml.anomaly_detector import AnomalyDetector
from app.ml.predictor import predict_health
from app.ai.recommender import recommend
from app.ai.explainer import explain
from app.noise.simulator import analyze_noise

router = APIRouter(tags=["analysis"])
detector = AnomalyDetector()

class CodeRequest(BaseModel):
    code: str
    language: str = "python"

@router.post("/analyze")
def analyze(req: CodeRequest, user=Depends(current_user)):
    try:
        code = sanitize_code_input(req.code)
        validation = validate_python(code)
        circuit, mode = parse_qiskit_code(code)
        metrics = extract_metrics(circuit)
        health = calculate_qhi(metrics)
        model_health = predict_health(health["components"])
        anomaly = detector.predict(metrics)
        noise = analyze_noise(metrics)
        analysis = {
            "success": True,
            "validation": validation,
            "parser": mode,
            "metrics": metrics,
            "circuit": circuit_data(circuit),
            "health": health,
            "model_health": model_health,
            "anomaly": anomaly,
            "noise": noise,
        }
        analysis["recommendations"] = recommend(analysis)
        analysis["explanation"] = explain(analysis)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/noise-analysis")
def noise_analysis(req: CodeRequest, user=Depends(current_user)):
    circuit, _ = parse_qiskit_code(req.code)
    metrics = extract_metrics(circuit)
    return analyze_noise(metrics)

@router.post("/ai/recommend")
def ai_recommend(req: CodeRequest, user=Depends(current_user)):
    circuit, mode = parse_qiskit_code(req.code)
    metrics = extract_metrics(circuit)
    health = calculate_qhi(metrics)
    anomaly = detector.predict(metrics)
    data = {"metrics": metrics, "health": health, "anomaly": anomaly}
    return recommend(data)
