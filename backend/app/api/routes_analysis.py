from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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

from app.hardware.recommendations import generate_hardware_recommendations

from app.qmi.calculator import calculate_qmi


router = APIRouter(tags=["analysis"])


detector = AnomalyDetector()


security = HTTPBearer()


class CodeRequest(BaseModel):
    code: str
    language: str = "python"


def authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return current_user(f"Bearer {credentials.credentials}")


@router.post("/analyze")
def analyze(
    req: CodeRequest,
    user=Depends(authenticated_user),
):
    try:
        code = sanitize_code_input(req.code)

        validation = validate_python(code)

        circuit, mode = parse_qiskit_code(code)

        metrics = extract_metrics(circuit)

        # -----------------------------------------------------
        # Quantum Health Index
        # -----------------------------------------------------

        health = calculate_qhi(metrics)

        # -----------------------------------------------------
        # ML Health Prediction
        # -----------------------------------------------------

        model_health = predict_health(
            health["components"]
        )

        # -----------------------------------------------------
        # Anomaly Detection
        # -----------------------------------------------------

        anomaly = detector.predict(metrics)

        # -----------------------------------------------------
        # Noise Analysis
        # -----------------------------------------------------

        noise = analyze_noise(metrics)

        # -----------------------------------------------------
        # Hardware Recommendations
        # -----------------------------------------------------

        hardware_recommendations = (
            generate_hardware_recommendations(
                metrics=metrics,
                noise=noise,
            )
        )

        # -----------------------------------------------------
        # Quantum Maintainability Index
        # -----------------------------------------------------

        qmi = calculate_qmi(metrics)

        # -----------------------------------------------------
        # Base Analysis Result
        # -----------------------------------------------------

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

            "hardware_recommendations": (
                hardware_recommendations
            ),

            "qmi": qmi,
        }

        # -----------------------------------------------------
        # AI Recommendations
        # -----------------------------------------------------

        analysis["recommendations"] = recommend(
            analysis
        )

        # -----------------------------------------------------
        # AI Explanation
        # -----------------------------------------------------

        analysis["explanation"] = explain(
            analysis
        )

        # -----------------------------------------------------
        # Save Analysis History
        # -----------------------------------------------------

        try:
            saved_result = (
                supabase
                .table("analysis_history")
                .insert(
                    {
                        "user_id": user["id"],
                        "circuit": code,
                        "metrics": metrics,
                        "health_score": health.get(
                            "score"
                        ),
                        "health_category": health.get(
                            "category"
                        ),
                        "anomaly_score": (
                            anomaly.get("score")
                            if isinstance(
                                anomaly,
                                dict,
                            )
                            else None
                        ),
                        "recommendations": (
                            analysis[
                                "recommendations"
                            ]
                        ),
                        "explanation": (
                            analysis[
                                "explanation"
                            ]
                        ),
                    }
                )
                .execute()
            )

            if saved_result.data:
                analysis["database"] = {
                    "saved": True,
                    "id": saved_result.data[0].get(
                        "id"
                    ),
                }
            else:
                analysis["database"] = {
                    "saved": False,
                    "id": None,
                }

        except Exception as db_error:
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
def noise_analysis(
    req: CodeRequest,
    user=Depends(authenticated_user),
):
    try:
        circuit, _ = parse_qiskit_code(
            req.code
        )

        metrics = extract_metrics(
            circuit
        )

        return analyze_noise(
            metrics
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post("/ai/recommend")
def ai_recommend(
    req: CodeRequest,
    user=Depends(authenticated_user),
):
    try:
        circuit, mode = parse_qiskit_code(
            req.code
        )

        metrics = extract_metrics(
            circuit
        )

        health = calculate_qhi(
            metrics
        )

        anomaly = detector.predict(
            metrics
        )

        data = {
            "metrics": metrics,
            "health": health,
            "anomaly": anomaly,
        }

        return recommend(
            data
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
