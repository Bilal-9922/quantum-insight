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
