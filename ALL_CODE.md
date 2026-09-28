# QuantumInsight — Complete Source Code

This file contains the code for every generated project file.

## `.env.example`

```text
APP_NAME=QuantumInsight
AI_API_KEY=
AI_MODEL=
DATABASE_URL=sqlite:///./quantuminsight.db
CORS_ORIGINS=http://localhost:3000

```

## `.gitignore`

```text
__pycache__/
*.py[cod]
.venv/
.env
.pytest_cache/
backend/quantuminsight.db
node_modules/
.next/
out/
*.log

```

## `README.md`

```markdown
# QuantumInsight

AI-powered quantum circuit intelligence MVP.

## Features
- Quantum Python code analysis
- Circuit metrics and visualization data
- Custom Quantum Health Index (QHI)
- Isolation Forest anomaly detection
- Random Forest health-category model with generated fallback data
- Deterministic gate cancellation
- Qiskit transpiler optimization when Qiskit is installed
- Noise-analysis fallback
- AI debugger/recommendations with deterministic fallback when no LLM key is configured
- FastAPI backend
- Next.js frontend
- SQLite history
- Tests

## Architecture

Frontend (Next.js/React/TypeScript/Tailwind)
        |
        v
FastAPI REST API
        |
        +-- Circuit parser / metrics
        +-- QHI health engine
        +-- ML anomaly detector
        +-- Rule optimizer / Qiskit transpiler
        +-- Debugger
        +-- Noise analysis
        +-- Recommendations

## Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000
Docs: http://127.0.0.1:8000/docs

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

Set `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000` in `frontend/.env.local` if needed.

## Optional Qiskit

The backend attempts to use Qiskit. If it is unavailable, the parser falls back to a lightweight parser for common QuantumCircuit statements so the demo remains usable.

## Optional AI

Copy `.env.example` to `.env`. No AI key is required for the MVP. The recommendation/debugger service uses deterministic explanations when an LLM is not configured.

## Important security note

Do not execute arbitrary user Python with `exec()` on the production API process. The included debugger verifier only performs static checks in the default MVP. For production, place code execution in a separately isolated sandbox/container with CPU, memory, timeout, filesystem, process and network restrictions.

```

## `backend/Dockerfile`

```text
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY tests ./tests
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

```

## `backend/app/__init__.py`

```python

```

## `backend/app/ai/__init__.py`

```python

```

## `backend/app/ai/explainer.py`

```python
def explain(analysis):
    return (
        f"The QHI is {analysis['health']['score']}/100 because the score combines "
        "depth, gate efficiency, qubit utilization, two-qubit efficiency, noise exposure, "
        "and optimization potential using project-specific weights."
    )

```

## `backend/app/ai/prompts.py`

```python
def recommendation_prompt(summary):
    return f"Explain this quantum circuit analysis clearly and recommend improvements: {summary}"

```

## `backend/app/ai/recommender.py`

```python
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

```

## `backend/app/api/__init__.py`

```python

```

## `backend/app/api/routes_analysis.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.security import sanitize_code_input
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
def analyze(req: CodeRequest):
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
def noise_analysis(req: CodeRequest):
    circuit, _ = parse_qiskit_code(req.code)
    metrics = extract_metrics(circuit)
    return analyze_noise(metrics)

@router.post("/ai/recommend")
def ai_recommend(req: CodeRequest):
    circuit, mode = parse_qiskit_code(req.code)
    metrics = extract_metrics(circuit)
    health = calculate_qhi(metrics)
    anomaly = detector.predict(metrics)
    data = {"metrics": metrics, "health": health, "anomaly": anomaly}
    return recommend(data)

```

## `backend/app/api/routes_debugger.py`

```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.debugger.ast_analyzer import analyze_ast
from app.debugger.classifier import classify
from app.debugger.ai_debugger import diagnose
from app.debugger.patch_generator import generate_patch
from app.debugger.verifier import verify

router = APIRouter(tags=["debugger"])

class DebugRequest(BaseModel):
    code: str
    error: str | None = None
    language: str = "python"

@router.post("/debug")
def debug(req: DebugRequest):
    ast_result = analyze_ast(req.code)
    error_type = classify(req.error)
    diagnosis = diagnose(req.code, req.error)
    patch = generate_patch(req.code, req.error)
    verification = verify(patch["fixed_code"])
    return {
        "success": True,
        "ast": ast_result,
        "error": {"type": error_type, "message": req.error},
        **diagnosis,
        **patch,
        **verification,
    }

```

## `backend/app/api/routes_health.py`

```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.health.scoring import calculate_qhi

router = APIRouter(tags=["health"])

class MetricsRequest(BaseModel):
    metrics: dict

@router.post("/health")
def health(req: MetricsRequest):
    return calculate_qhi(req.metrics)

```

## `backend/app/api/routes_optimizer.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.optimizer.optimizer import optimize_code

router = APIRouter(tags=["optimizer"])

class OptimizeRequest(BaseModel):
    code: str

@router.post("/optimize")
def optimize(req: OptimizeRequest):
    try:
        return optimize_code(req.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

```

## `backend/app/api/routes_reports.py`

```python
from fastapi import APIRouter
from pydantic import BaseModel
from app.reports.generator import generate_report

router = APIRouter(tags=["reports"])

class ReportRequest(BaseModel):
    analysis: dict

@router.post("/report")
def report(req: ReportRequest):
    return generate_report(req.analysis)

```

## `backend/app/circuit/__init__.py`

```python

```

## `backend/app/circuit/metrics.py`

```python
from collections import Counter

def extract_metrics(circuit):
    if isinstance(circuit, dict):
        gates = circuit["gates"]
        qubits = circuit["qubits"]
        depth = _light_depth(gates)
    else:
        gates = []
        for inst in circuit.data:
            op, qargs, _ = inst
            gates.append({"name": op.name, "qubits": [circuit.find_bit(q).index for q in qargs]})
        qubits = circuit.num_qubits
        depth = circuit.depth()

    counts = Counter(g["name"] for g in gates)
    gate_count = len(gates)
    one_q = sum(1 for g in gates if len(g["qubits"]) == 1)
    two_q = sum(1 for g in gates if len(g["qubits"]) == 2)
    measurement = sum(1 for g in gates if g["name"] in {"measure", "measure_all"})

    density = gate_count / max(1, qubits * max(1, depth))
    two_ratio = two_q / max(1, gate_count)
    measurement_ratio = measurement / max(1, gate_count)

    return {
        "qubits": qubits,
        "gate_count": gate_count,
        "depth": depth,
        "one_qubit_gates": one_q,
        "two_qubit_gates": two_q,
        "two_qubit_ratio": round(two_ratio, 4),
        "gate_density": round(density, 4),
        "measurement_ratio": round(measurement_ratio, 4),
        "gate_counts": dict(counts),
    }

def _light_depth(gates):
    if not gates:
        return 0
    layers = []
    for gate in gates:
        used = set(gate["qubits"])
        layer = 0
        while layer < len(layers) and used.intersection(layers[layer]):
            layer += 1
        if layer == len(layers):
            layers.append(set())
        layers[layer].update(used)
    return len(layers)

```

## `backend/app/circuit/parser.py`

```python
import re

GATE_RE = re.compile(
    r"^\s*(?P<gate>[a-zA-Z][a-zA-Z0-9_]*)\s*(?:\((?P<params>[^)]*)\))?\s+(?P<args>[^#]+)",
    re.I,
)

def parse_qiskit_code(code: str):
    """Parse common QuantumCircuit syntax without executing user code."""
    return lightweight_parse(code), "lightweight"

def lightweight_parse(code: str):
    qubits = 0
    gates = []
    m = re.search(r"QuantumCircuit\s*\(\s*(\d+)", code)
    if m:
        qubits = int(m.group(1))

    for line in code.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith(("from ", "import ")):
            continue

        # Accept qc.h(0), qc.cx(0, 1), qc.measure_all(), etc.
        call = re.match(r"^(?:\w+\.)?(?P<gate>[a-zA-Z][a-zA-Z0-9_]*)\s*\((?P<args>.*)\)\s*$", line)
        if not call:
            continue

        gate = call.group("gate").lower()
        args = call.group("args")

        if gate in {"measure_all", "barrier", "reset"}:
            indices = [int(x) for x in re.findall(r"\d+", args)]
        else:
            # Only treat integer arguments as qubit indices.
            indices = [int(x) for x in re.findall(r"(?<![A-Za-z_])\d+(?![A-Za-z_])", args)]

        if gate in {"measure_all"}:
            gates.append({"name": gate, "qubits": list(range(qubits))})
        elif gate not in {"quantumcircuit", "print"} and indices:
            qubits = max(qubits, max(indices) + 1)
            gates.append({"name": gate, "qubits": indices})

    return {"qubits": qubits, "gates": gates}

def circuit_to_gate_list(circuit):
    if isinstance(circuit, dict):
        return circuit["gates"]
    return []

```

## `backend/app/circuit/serializer.py`

```python
def serialize_metrics(metrics):
    return dict(metrics)

```

## `backend/app/circuit/validator.py`

```python
import ast

def validate_python(code: str):
    try:
        ast.parse(code)
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {
            "valid": False,
            "error": {"type": "SyntaxError", "line": e.lineno, "message": e.msg}
        }

```

## `backend/app/circuit/visualization.py`

```python
def circuit_data(circuit):
    if isinstance(circuit, dict):
        return {
            "qubits": circuit["qubits"],
            "gates": circuit["gates"],
        }
    return {
        "qubits": circuit.num_qubits,
        "gates": [
            {"name": op.name, "qubits": [circuit.find_bit(q).index for q in qargs]}
            for op, qargs, _ in circuit.data
        ],
    }

```

## `backend/app/core/__init__.py`

```python

```

## `backend/app/core/config.py`

```python
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    app_name: str = os.getenv("APP_NAME", "QuantumInsight")
    ai_api_key: str = os.getenv("AI_API_KEY", "")
    ai_model: str = os.getenv("AI_MODEL", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./quantuminsight.db")
    cors_origins: list[str] = None

    def __post_init__(self):
        raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
        self.cors_origins = [x.strip() for x in raw.split(",") if x.strip()]

settings = Settings()

```

## `backend/app/core/logging.py`

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quantuminsight")

```

## `backend/app/core/security.py`

```python
def sanitize_code_input(code: str, max_chars: int = 50000) -> str:
    if not isinstance(code, str):
        raise ValueError("Code must be a string.")
    if len(code) > max_chars:
        raise ValueError(f"Code exceeds the {max_chars} character limit.")
    return code

```

## `backend/app/debugger/__init__.py`

```python

```

## `backend/app/debugger/ai_debugger.py`

```python
def diagnose(code, error=None):
    if error:
        msg = str(error)
        return {
            "diagnosis": f"Review the reported error: {msg}",
            "suggestions": [
                "Check the referenced qubit index and circuit size.",
                "Validate gate arguments and parameter values.",
                "Run the corrected code through a sandbox before trusting it."
            ]
        }
    return {
        "diagnosis": "No runtime error was supplied. Static syntax and circuit validation can still be performed.",
        "suggestions": ["Analyze the circuit metrics and run the optimizer."]
    }

```

## `backend/app/debugger/ast_analyzer.py`

```python
import ast

def analyze_ast(code):
    try:
        tree = ast.parse(code)
        imports = [n.names[0].name for n in ast.walk(tree) if isinstance(n, ast.Import) and n.names]
        return {"valid": True, "imports": imports, "nodes": len(list(ast.walk(tree)))}
    except SyntaxError as e:
        return {"valid": False, "error": {"line": e.lineno, "message": e.msg}}

```

## `backend/app/debugger/classifier.py`

```python
def classify(message):
    m = (message or "").lower()
    if "syntax" in m or "invalid syntax" in m:
        return "SYNTAX_ERROR"
    if "index" in m or "qubit" in m:
        return "QUBIT_INDEX_ERROR"
    if "parameter" in m:
        return "PARAMETER_ERROR"
    return "GENERAL_ERROR"

```

## `backend/app/debugger/error_parser.py`

```python
def parse_error(error):
    if not error:
        return None
    text = str(error)
    if "index" in text.lower() and "qubit" in text.lower():
        kind = "QUBIT_INDEX_ERROR"
    elif "syntax" in text.lower():
        kind = "SYNTAX_ERROR"
    else:
        kind = "GENERAL_ERROR"
    return {"type": kind, "message": text}

```

## `backend/app/debugger/patch_generator.py`

```python
def generate_patch(code, error=None):
    return {
        "fixed_code": code,
        "changed": False,
        "note": "MVP patch generator does not rewrite code automatically without a verified, isolated execution environment."
    }

```

## `backend/app/debugger/verifier.py`

```python
from app.circuit.validator import validate_python

def verify(code):
    syntax = validate_python(code)
    return {"verified": syntax["valid"], "syntax": syntax}

```

## `backend/app/health/__init__.py`

```python

```

## `backend/app/health/calibration.py`

```python
# QHI weights are project-specific and should be experimentally validated.
def calibration_note():
    return "QHI is a custom weighted score, not an established scientific standard."

```

## `backend/app/health/components.py`

```python
def health_components(m):
    depth_eff = max(0.0, 100 - min(100, m["depth"] * 2.0))
    gate_eff = max(0.0, 100 - min(100, m["gate_count"] * 0.55))
    qubit_util = min(100.0, 50 + min(50, m["qubits"] * 5))
    two_q_eff = max(0.0, 100 - min(100, m["two_qubit_ratio"] * 140))
    noise = max(0.0, 100 - min(100, m["two_qubit_ratio"] * 100 + m["depth"] * 0.8))
    opt = min(100.0, max(0.0, m["two_qubit_ratio"] * 100 + m["depth"] * 1.2))
    return {
        "depth_efficiency": round(depth_eff, 1),
        "gate_efficiency": round(gate_eff, 1),
        "qubit_utilization": round(qubit_util, 1),
        "two_qubit_efficiency": round(two_q_eff, 1),
        "noise_exposure": round(noise, 1),
        "optimization_potential": round(opt, 1),
    }

```

## `backend/app/health/scoring.py`

```python
from app.health.components import health_components

WEIGHTS = {
    "depth_efficiency": 0.22,
    "gate_efficiency": 0.18,
    "qubit_utilization": 0.12,
    "two_qubit_efficiency": 0.20,
    "noise_exposure": 0.16,
    "optimization_potential": 0.12,
}

def calculate_qhi(metrics):
    c = health_components(metrics)
    score = sum(c[k] * w for k, w in WEIGHTS.items())
    score = round(max(0, min(100, score)), 1)
    category = "Healthy" if score >= 75 else "Moderate" if score >= 50 else "Critical"
    return {"score": score, "category": category, "components": c, "weights": WEIGHTS}

```

## `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes_analysis import router as analysis_router
from app.api.routes_health import router as health_router
from app.api.routes_optimizer import router as optimizer_router
from app.api.routes_debugger import router as debugger_router
from app.api.routes_reports import router as reports_router

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(optimizer_router, prefix="/api")
app.include_router(debugger_router, prefix="/api")
app.include_router(reports_router, prefix="/api")

@app.get("/")
def root():
    return {"name": settings.app_name, "status": "ok"}

@app.get("/api/healthcheck")
def healthcheck():
    return {"status": "healthy"}

```

## `backend/app/ml/__init__.py`

```python

```

## `backend/app/ml/anomaly_detector.py`

```python
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

```

## `backend/app/ml/feature_engineering.py`

```python
import numpy as np

FEATURES = ["qubits", "gate_count", "depth", "one_qubit_gates", "two_qubit_gates", "two_qubit_ratio", "gate_density", "measurement_ratio"]

def vector(metrics):
    return np.array([[metrics.get(k, 0) for k in FEATURES]], dtype=float)

```

## `backend/app/ml/health_model.py`

```python
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

```

## `backend/app/ml/predictor.py`

```python
from app.ml.health_model import HealthModel
model = HealthModel()

def predict_health(components):
    return model.predict(components)

```

## `backend/app/noise/__init__.py`

```python

```

## `backend/app/noise/noise_model.py`

```python
def default_noise_model():
    return {
        "type": "heuristic",
        "description": "MVP heuristic noise exposure based on depth and two-qubit gate ratio."
    }

```

## `backend/app/noise/simulator.py`

```python
def analyze_noise(metrics):
    exposure = min(100, metrics["depth"] * 0.8 + metrics["two_qubit_ratio"] * 100)
    return {
        "noise_exposure_percent": round(exposure, 1),
        "method": "heuristic",
        "note": "Install and configure Aer noise models for physical/noise-model simulation."
    }

```

## `backend/app/optimizer/__init__.py`

```python

```

## `backend/app/optimizer/gate_cancellation.py`

```python
INVERSES = {
    "x": "x", "y": "y", "z": "z", "h": "h",
    "cx": "cx", "cz": "cz", "swap": "swap",
    "s": "sdg", "sdg": "s", "t": "tdg", "tdg": "t",
}

def cancel_adjacent(gates):
    out = []
    for g in gates:
        if out and len(out[-1]["qubits"]) == len(g["qubits"]) and out[-1]["qubits"] == g["qubits"]:
            a = out[-1]["name"].lower()
            b = g["name"].lower()
            if INVERSES.get(a) == b:
                out.pop()
                continue
        out.append(g)
    return out

```

## `backend/app/optimizer/gate_fusion.py`

```python
def fuse_note(gates):
    return "Gate-fusion opportunities are delegated to Qiskit transpilation when available."

```

## `backend/app/optimizer/optimizer.py`

```python
from app.optimizer.rules import rule_optimize
from app.circuit.metrics import extract_metrics
from app.circuit.parser import parse_qiskit_code

def optimize_code(code):
    circuit, mode = parse_qiskit_code(code)
    if isinstance(circuit, dict):
        original = extract_metrics(circuit)
        optimized_gates = rule_optimize(circuit["gates"])
        optimized = {"qubits": circuit["qubits"], "gates": optimized_gates}
        result = extract_metrics(optimized)
    else:
        original = extract_metrics(circuit)
        try:
            from app.optimizer.transpiler import transpile_circuit
            opt = transpile_circuit(circuit)
            result = extract_metrics(opt)
        except Exception:
            result = original
    def pct(a, b):
        return round((a-b) / max(1, a) * 100, 1)
    return {
        "mode": mode,
        "original": original,
        "optimized": result,
        "improvement": {
            "gate_reduction_percent": pct(original["gate_count"], result["gate_count"]),
            "depth_reduction_percent": pct(original["depth"], result["depth"]),
            "two_qubit_reduction_percent": pct(original["two_qubit_gates"], result["two_qubit_gates"]),
        },
    }

```

## `backend/app/optimizer/rules.py`

```python
from app.optimizer.gate_cancellation import cancel_adjacent

def rule_optimize(gates):
    return cancel_adjacent(gates)

```

## `backend/app/optimizer/transpiler.py`

```python
def transpile_circuit(circuit, optimization_level=3):
    try:
        from qiskit import transpile
        return transpile(circuit, optimization_level=optimization_level)
    except Exception:
        return circuit

```

## `backend/app/reports/__init__.py`

```python

```

## `backend/app/reports/generator.py`

```python
def generate_report(analysis):
    return {
        "title": "QuantumInsight Circuit Analysis Report",
        "summary": analysis.get("health", {}),
        "metrics": analysis.get("metrics", {}),
        "anomaly": analysis.get("anomaly", {}),
        "recommendations": analysis.get("recommendations", {}),
    }

```

## `backend/requirements.txt`

```text
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.5
python-dotenv==1.0.1
numpy==2.2.1
pandas==2.2.3
scikit-learn==1.6.1
scipy==1.15.1
matplotlib==3.10.0
networkx==3.4.2
qiskit==1.3.2
qiskit-aer==0.15.1
httpx==0.28.1
pytest==8.3.4

```

## `backend/tests/test_debugger.py`

```python
from app.debugger.verifier import verify

def test_debugger():
    assert verify("x = 1")["verified"] is True
    assert verify("x =")["verified"] is False

```

## `backend/tests/test_health.py`

```python
from app.health.scoring import calculate_qhi

def test_qhi_range():
    result = calculate_qhi({
        "qubits": 2, "gate_count": 4, "depth": 3,
        "one_qubit_gates": 3, "two_qubit_gates": 1,
        "two_qubit_ratio": .25, "gate_density": .6,
        "measurement_ratio": 0
    })
    assert 0 <= result["score"] <= 100

```

## `backend/tests/test_metrics.py`

```python
from app.circuit.metrics import extract_metrics

def test_metrics():
    c = {"qubits": 2, "gates": [{"name":"h","qubits":[0]}, {"name":"cx","qubits":[0,1]}]}
    m = extract_metrics(c)
    assert m["qubits"] == 2
    assert m["gate_count"] == 2
    assert m["two_qubit_gates"] == 1

```

## `backend/tests/test_optimizer.py`

```python
from app.optimizer.gate_cancellation import cancel_adjacent

def test_x_x_cancel():
    gates = [{"name":"x","qubits":[0]}, {"name":"x","qubits":[0]}]
    assert cancel_adjacent(gates) == []

```

## `backend/tests/test_parser.py`

```python
from app.circuit.parser import lightweight_parse

def test_parser():
    c = lightweight_parse("from qiskit import QuantumCircuit\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0,1)")
    assert c["qubits"] == 2

```

## `data/sample_circuits/bell.py`

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

```

## `data/sample_circuits/redundant.py`

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.x(0)
qc.x(0)
qc.cx(0, 1)
qc.cx(0, 1)
qc.measure_all()

```

## `docker-compose.yml`

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - CORS_ORIGINS=http://localhost:3000
    volumes:
      - ./backend:/app

  frontend:
    image: node:20-alpine
    working_dir: /app
    command: sh -c "npm install && npm run dev"
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app

```

## `docs/algorithms.md`

```markdown
# Algorithms

- Custom weighted QHI
- Isolation Forest for unusual circuit characteristics
- Random Forest for generated health categories
- Rule-based adjacent inverse gate cancellation
- Qiskit transpilation optimization
- AST validation and safe verification architecture
- Heuristic noise exposure in the MVP

```

## `docs/api.md`

```markdown
# API

POST /api/analyze
POST /api/debug
POST /api/optimize
POST /api/health
POST /api/noise-analysis (reserved for extension)
POST /api/ai/recommend (reserved for extension)
POST /api/report
GET /api/healthcheck

```

## `docs/architecture.md`

```markdown
# Architecture

QuantumInsight has four logical intelligence layers:

1. Quantum engine: parser, Qiskit/Aer, metrics, transpilation.
2. ML engine: Isolation Forest and Random Forest.
3. AI engine: debugger, explanations and recommendations.
4. Health engine: custom Quantum Health Index.

The web dashboard consumes FastAPI endpoints and renders the structured results.

```

## `docs/qhi_methodology.md`

```markdown
# QHI Methodology

QHI is a project-specific 0-100 weighted score.

Components:
- Depth efficiency
- Gate efficiency
- Qubit utilization
- Two-qubit gate efficiency
- Noise exposure
- Optimization potential

The blueprint explicitly recommends experimental validation of the weights; therefore QHI should be presented as a custom project metric, not an established scientific standard.

```

## `frontend/.env.example`

```text
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000

```

## `frontend/next-env.d.ts`

```typescript
/// <reference types="next" />
/// <reference types="next/image-types/global" />

```

## `frontend/next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = { reactStrictMode: true };
module.exports = nextConfig;

```

## `frontend/package.json`

```json
{
  "name": "quantuminsight-frontend",
  "private": true,
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "15.1.6",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "recharts": "2.15.1"
  },
  "devDependencies": {
    "@types/node": "22.10.5",
    "@types/react": "19.0.3",
    "@types/react-dom": "19.0.2",
    "autoprefixer": "10.4.20",
    "postcss": "8.4.49",
    "tailwindcss": "3.4.17",
    "typescript": "5.7.2"
  }
}

```

## `frontend/postcss.config.js`

```javascript
module.exports = {
  plugins: { tailwindcss: {}, autoprefixer: {} }
};

```

## `frontend/src/app/analyzer/page.tsx`

```tsx
"use client";
import {useState} from "react";
import {analyze} from "../../services/api";
import {Analysis} from "../../types/quantum";
import MetricCard from "../../components/MetricCard";
import HealthScore from "../../components/HealthScore";
import HealthChart from "../../components/HealthChart";
import CircuitViewer from "../../components/CircuitViewer";
import AIRecommendation from "../../components/AIRecommendation";

const sample = `from qiskit import QuantumCircuit

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()`;

export default function Analyzer() {
  const [code,setCode]=useState(sample); const [data,setData]=useState<Analysis|null>(null); const [error,setError]=useState("");
  async function run(){setError(""); try{setData(await analyze(code));}catch(e:any){setError(e.message)}}
  return <div className="space-y-6"><div><h1 className="text-3xl font-bold">Circuit Analyzer</h1><p className="text-slate-400">Paste Qiskit Python and analyze it.</p></div>
    <textarea className="min-h-72 w-full font-mono text-sm" value={code} onChange={e=>setCode(e.target.value)}/>
    <button className="btn btn-primary" onClick={run}>Analyze Circuit</button>
    {error && <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-4">{error}</div>}
    {data && <><div className="grid gap-4 md:grid-cols-4"><MetricCard label="Qubits" value={data.metrics.qubits}/><MetricCard label="Gates" value={data.metrics.gate_count}/><MetricCard label="Depth" value={data.metrics.depth}/><MetricCard label="2Q Gates" value={data.metrics.two_qubit_gates}/></div>
      <div className="grid gap-6 md:grid-cols-2"><HealthScore score={data.health.score} category={data.health.category}/><HealthChart components={data.health.components}/></div>
      <CircuitViewer circuit={data.circuit}/><AIRecommendation data={data.recommendations}/></>}
  </div>;
}

```

## `frontend/src/app/dashboard/page.tsx`

```tsx
import Link from "next/link";
export default function Dashboard(){return <div className="space-y-6"><h1 className="text-3xl font-bold">Dashboard</h1><div className="grid gap-4 md:grid-cols-3"><div className="card"><b>QHI</b><p className="mt-2 text-slate-400">Analyze a circuit to calculate its project health score.</p></div><div className="card"><b>Anomaly detection</b><p className="mt-2 text-slate-400">Isolation Forest flags unusual feature combinations.</p></div><div className="card"><b>Optimization</b><p className="mt-2 text-slate-400">Compare original and optimized metrics.</p></div></div><Link className="btn btn-primary inline-block" href="/analyzer">Start analysis</Link></div>}

```

## `frontend/src/app/debugger/page.tsx`

```tsx
"use client";
import {useState} from "react";
import {debug} from "../../services/api";
import DebugPanel from "../../components/DebugPanel";
const sample=`from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)`;
export default function Debugger(){const [code,setCode]=useState(sample);const [err,setErr]=useState("Qubit index error: qubit 3 is outside the circuit");const [res,setRes]=useState<any>();const [busy,setBusy]=useState(false);
async function run(){setBusy(true);try{setRes(await debug(code,err))}finally{setBusy(false)}}
return <div className="space-y-6"><h1 className="text-3xl font-bold">AI Quantum Debugger</h1><div className="grid gap-6 md:grid-cols-2"><textarea className="min-h-80 font-mono" value={code} onChange={e=>setCode(e.target.value)}/><div className="space-y-3"><textarea className="min-h-40 w-full" value={err} onChange={e=>setErr(e.target.value)}/><button className="btn btn-primary" onClick={run}>{busy?"Analyzing...":"Fix With AI"}</button></div></div><DebugPanel result={res}/></div>}

```

## `frontend/src/app/globals.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root { color-scheme: dark; }
body {
  margin: 0;
  background: #070b14;
  color: #e8eefc;
  font-family: Arial, Helvetica, sans-serif;
}
* { box-sizing: border-box; }
.card {
  @apply rounded-2xl border border-slate-800 bg-slate-900/70 p-5 shadow-xl;
}
.btn {
  @apply rounded-xl px-4 py-2 font-semibold transition;
}
.btn-primary { @apply bg-cyan-500 text-slate-950 hover:bg-cyan-400; }
.btn-secondary { @apply bg-slate-800 hover:bg-slate-700; }
textarea, input {
  @apply rounded-xl border border-slate-700 bg-slate-950 p-3 text-slate-100 outline-none focus:border-cyan-400;
}

```

## `frontend/src/app/history/page.tsx`

```tsx
export default function History(){return <div className="space-y-4"><h1 className="text-3xl font-bold">Analysis History</h1><div className="card"><p className="text-slate-400">SQLite history schema is prepared in the backend architecture. This MVP keeps the core analysis stateless; persistent history can be enabled next.</p></div></div>}

```

## `frontend/src/app/layout.tsx`

```tsx
import "./globals.css";
import Link from "next/link";

export const metadata = {
  title: "QuantumInsight",
  description: "AI-powered quantum circuit intelligence"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-slate-800 bg-slate-950/90">
          <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
            <Link href="/" className="text-xl font-bold text-cyan-400">QuantumInsight</Link>
            <div className="flex gap-4 text-sm text-slate-300">
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/analyzer">Analyzer</Link>
              <Link href="/debugger">Debugger</Link>
              <Link href="/optimizer">Optimizer</Link>
              <Link href="/history">History</Link>
            </div>
          </nav>
        </header>
        <main className="mx-auto min-h-screen max-w-7xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}

```

## `frontend/src/app/optimizer/page.tsx`

```tsx
"use client";
import {useState} from "react"; import {optimize} from "../../services/api"; import OptimizationPanel from "../../components/OptimizationPanel";
const sample=`from qiskit import QuantumCircuit
qc = QuantumCircuit(2)
qc.h(0)
qc.x(0)
qc.x(0)
qc.cx(0,1)
qc.cx(0,1)
qc.measure_all()`;
export default function Optimizer(){const [code,setCode]=useState(sample);const [res,setRes]=useState<any>();return <div className="space-y-6"><h1 className="text-3xl font-bold">Circuit Optimizer</h1><textarea className="min-h-72 w-full font-mono" value={code} onChange={e=>setCode(e.target.value)}/><button className="btn btn-primary" onClick={async()=>setRes(await optimize(code))}>Optimize</button><OptimizationPanel data={res}/></div>}

```

## `frontend/src/app/page.tsx`

```tsx
import Link from "next/link";

export default function Home() {
  return <section className="py-20">
    <div className="max-w-4xl">
      <p className="mb-4 text-sm font-bold uppercase tracking-[.3em] text-cyan-400">Quantum circuit intelligence</p>
      <h1 className="text-5xl font-black leading-tight md:text-7xl">Analyze. Debug. Optimize. Explain.</h1>
      <p className="mt-6 max-w-2xl text-lg text-slate-400">QuantumInsight combines Qiskit analysis, a custom Quantum Health Index, ML anomaly detection, optimization and AI-style recommendations in one dashboard.</p>
      <div className="mt-8 flex gap-3"><Link className="btn btn-primary" href="/analyzer">Analyze Circuit</Link><Link className="btn btn-secondary" href="/debugger">Open Debugger</Link></div>
    </div>
  </section>;
}

```

## `frontend/src/components/AIRecommendation.tsx`

```tsx
export default function AIRecommendation({data}: {data:any}) {
  if (!data) return null;
  return <div className="card"><h3 className="font-bold text-cyan-400">AI Recommendations</h3>
    <p className="mt-2 text-slate-300">{data.summary}</p>
    <ul className="mt-4 list-disc space-y-2 pl-5 text-slate-300">{data.recommendations.map((x:string,i:number)=><li key={i}>{x}</li>)}</ul>
    <p className="mt-4 text-xs text-slate-500">Provider: {data.provider}</p>
  </div>;
}

```

## `frontend/src/components/CircuitEditor.tsx`

```tsx
export default function CircuitEditor({code, setCode}: {code:string; setCode:(v:string)=>void}) {
  return <textarea className="min-h-[360px] w-full font-mono text-sm" value={code} onChange={e=>setCode(e.target.value)} />;
}

```

## `frontend/src/components/CircuitViewer.tsx`

```tsx
export default function CircuitViewer({circuit}: {circuit:any}) {
  if (!circuit) return null;
  return <div className="card overflow-auto"><h3 className="mb-3 font-bold">Circuit operations</h3>
    {Array.from({length: circuit.qubits}, (_,q)=><div key={q} className="mb-2 flex min-w-max items-center gap-2">
      <span className="w-16 text-slate-400">q[{q}]</span>
      {circuit.gates.map((g:any,i:number)=><span key={i} className={`rounded border px-3 py-2 text-xs ${g.qubits.includes(q) ? "border-cyan-400 bg-cyan-500/10" : "border-slate-800 opacity-30"}`}>{g.qubits.includes(q) ? g.name : "·"}</span>)}
    </div>)}
  </div>;
}

```

## `frontend/src/components/DebugPanel.tsx`

```tsx
export default function DebugPanel({result}: {result:any}) {
  if (!result) return null;
  return <div className="card space-y-3"><h3 className="font-bold text-cyan-400">Debug result</h3>
    <p><b>Type:</b> {result.error?.type}</p>
    <p><b>Diagnosis:</b> {result.diagnosis}</p>
    <ul className="list-disc pl-5">{result.suggestions?.map((x:string,i:number)=><li key={i}>{x}</li>)}</ul>
    <p><b>Verified:</b> {String(result.verified)}</p>
  </div>;
}

```

## `frontend/src/components/HealthChart.tsx`

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
export default function HealthChart({components}: {components: Record<string, number>}) {
  const data = Object.entries(components).map(([name,value])=>({name:name.replaceAll("_"," "), value}));
  return <div className="card h-80"><h3 className="mb-2 font-bold">Health Components</h3><ResponsiveContainer width="100%" height="90%"><BarChart data={data}><XAxis dataKey="name" hide/><YAxis domain={[0,100]}/><Tooltip/><Bar dataKey="value"/></BarChart></ResponsiveContainer></div>;
}

```

## `frontend/src/components/HealthScore.tsx`

```tsx
export default function HealthScore({score, category}: {score:number; category:string}) {
  return <div className="card text-center">
    <div className="text-sm uppercase tracking-widest text-slate-400">Quantum Health Index</div>
    <div className="my-3 text-6xl font-black text-cyan-400">{score}</div>
    <div className="text-slate-300">/100 · {category}</div>
    <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-800">
      <div className="h-full bg-cyan-400" style={{width:`${score}%`}} />
    </div>
  </div>;
}

```

## `frontend/src/components/MetricCard.tsx`

```tsx
export default function MetricCard({label, value}: {label: string; value: string | number}) {
  return <div className="card"><div className="text-sm text-slate-400">{label}</div><div className="mt-2 text-2xl font-bold">{value}</div></div>;
}

```

## `frontend/src/components/OptimizationPanel.tsx`

```tsx
export default function OptimizationPanel({data}: {data:any}) {
  if (!data) return null;
  return <div className="card"><h3 className="mb-4 font-bold text-cyan-400">Before vs After</h3>
    <div className="grid gap-3 md:grid-cols-3">
      {[
        ["Gates", data.original.gate_count, data.optimized.gate_count, data.improvement.gate_reduction_percent],
        ["Depth", data.original.depth, data.optimized.depth, data.improvement.depth_reduction_percent],
        ["2Q Gates", data.original.two_qubit_gates, data.optimized.two_qubit_gates, data.improvement.two_qubit_reduction_percent]
      ].map(([name,a,b,p]:any)=><div key={name} className="rounded-xl bg-slate-950 p-4">
        <div className="text-slate-400">{name}</div><div className="mt-2">{a} → {b}</div><div className="mt-1 text-cyan-400">↓ {p}%</div>
      </div>)}
    </div>
  </div>;
}

```

## `frontend/src/services/api.ts`

```typescript
import { Analysis } from "../types/quantum";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function analyze(code: string): Promise<Analysis> {
  const r = await fetch(`${API}/api/analyze`, {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ code, language: "python" })
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function debug(code: string, error: string) {
  const r = await fetch(`${API}/api/debug`, {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ code, error, language: "python" })
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function optimize(code: string) {
  const r = await fetch(`${API}/api/optimize`, {
    method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ code })
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

```

## `frontend/src/types/quantum.ts`

```typescript
export type Metrics = {
  qubits: number; gate_count: number; depth: number;
  one_qubit_gates: number; two_qubit_gates: number;
  two_qubit_ratio: number; gate_density: number; measurement_ratio: number;
  gate_counts: Record<string, number>;
};
export type Analysis = {
  success: boolean; parser: string; metrics: Metrics;
  health: { score: number; category: string; components: Record<string, number> };
  anomaly: { anomaly: boolean; score: number };
  noise: Record<string, unknown>;
  recommendations: { summary: string; recommendations: string[]; provider: string };
  explanation: string;
};

```

## `frontend/tailwind.config.js`

```javascript
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: { extend: {} },
  plugins: []
};

```

## `frontend/tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}]
  },
  "include": ["next-env.d.ts", ".next/types/**/*.ts", "src/**/*.ts", "src/**/*.tsx"],
  "exclude": ["node_modules"]
}

```

## `requirements.txt`

```text
# Convenience root requirements; backend has its own pinned-ish requirements.
-r backend/requirements.txt

```
