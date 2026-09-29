from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.security import sanitize_code_input
from app.auth import current_user
from app.core.supabase import supabase

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
        # -----------------------------
        # 1. Sanitize and validate code
        # -----------------------------
        code = sanitize_code_input(req.code)
        validation = validate_python(code)

        # -----------------------------
        # 2. Parse quantum circuit
        # -----------------------------
        circuit, mode = parse_qiskit_code(code)

        # -----------------------------
        # 3. Extract circuit metrics
        # -----------------------------
        metrics = extract_metrics(circuit)

        # -----------------------------
        # 4. Calculate Quantum Health
        # -----------------------------
        health = calculate_qhi(metrics)

        # -----------------------------
        # 5. ML health prediction
        # -----------------------------
        model_health = predict_health(health["components"])

        # -----------------------------
        # 6. Detect anomalies
        # -----------------------------
        anomaly = detector.predict(metrics)

        # -----------------------------
        # 7. Analyze noise
        # -----------------------------
        noise = analyze_noise(metrics)

        # -----------------------------
        # 8. Build analysis result
        # -----------------------------
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

        # -----------------------------
        # 9. Generate recommendations
        # -----------------------------
        analysis["recommendations"] = recommend(analysis)

        # -----------------------------
        # 10. Generate explanation
        # -----------------------------
        analysis["explanation"] = explain(analysis)

        # -----------------------------
        # 11. Save analysis to Supabase
        # -----------------------------
        try:
            saved_result = (
                supabase
                .table("analysis_history")
                .insert({
                    "circuit": code,
                    "metrics": metrics,
                    "health_score": health.get("score"),
                    "health_category": health.get("category"),
                    "anomaly_score": anomaly.get("score")
                    if isinstance(anomaly, dict)
                    else None,
                    "recommendations": analysis["recommendations"],
                    "explanation": analysis["explanation"],
                })
                .execute()
            )

            if saved_result.data:
                analysis["database"] = {
                    "saved": True,
                    "id": saved_result.data[0].get("id"),
                }
            else:
                analysis["database"] = {
                    "saved": False,
                    "id": None,
                }

        except Exception as db_error:
            # Database failure should not prevent the analysis
            # itself from being returned.
            analysis["database"] = {
                "saved": False,
                "error": str(db_error),
            }

        return analysis

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post("/noise-analysis")
def noise_analysis(req: CodeRequest, user=Depends(current_user)):
    try:
        circuit, _ = parse_qiskit_code(req.code)
        metrics = extract_metrics(circuit)
        return analyze_noise(metrics)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post("/ai/recommend")
def ai_recommend(req: CodeRequest, user=Depends(current_user)):
    try:
        circuit, mode = parse_qiskit_code(req.code)
        metrics = extract_metrics(circuit)
        health = calculate_qhi(metrics)
        anomaly = detector.predict(metrics)

        data = {
            "metrics": metrics,
            "health": health,
            "anomaly": anomaly,
        }

        return recommend(data)

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
