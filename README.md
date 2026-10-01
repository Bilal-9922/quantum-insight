# ⚛️ QuantumInsight

# LIVE :- https://quantum-insight.bilalshaikh1339.workers.dev/

### An AI-Powered Quantum Circuit Intelligence, Optimization & Health Analysis Framework

---

## 📌 Overview

**QuantumInsight** is a web-based quantum circuit intelligence platform designed to analyze, evaluate, debug, optimize, and understand **Qiskit quantum circuits**.

The platform converts quantum circuit code into engineering-oriented metrics and quality indicators, helping developers understand their circuits from multiple perspectives:

* Circuit complexity
* Gate usage
* Circuit depth
* Two-qubit operations
* Noise exposure
* Optimization potential
* Maintainability
* Scalability
* Hardware compatibility
* Anomaly detection
* Quantum debugging
* Optimization recommendations

Instead of manually inspecting every aspect of a quantum circuit, QuantumInsight provides a centralized workflow for analyzing quantum programs through a web interface.

> **Analyze → Measure → Understand → Optimize**

---

# 🎯 Problem Statement

Quantum programs are fundamentally different from conventional software.

A quantum circuit can be syntactically valid while still having characteristics that make it difficult to execute efficiently on quantum hardware.

For example, a circuit may contain:

* Excessive circuit depth
* Too many two-qubit gates
* Poor gate efficiency
* High noise exposure
* Unnecessary operations
* Hardware compatibility issues
* Scaling problems
* Difficult-to-maintain circuit structures

Traditional quantum development tools provide circuit construction and execution capabilities, but developers may still need to manually interpret these engineering characteristics.

QuantumInsight addresses this problem by transforming quantum circuit code into measurable quality indicators and actionable engineering recommendations.

---

# 🚀 Key Features

## 1. Quantum Circuit Analyzer

QuantumInsight provides a dedicated circuit analyzer where users can paste **Qiskit Python code** and analyze the structure of the circuit.

The analyzer extracts important metrics including:

* Number of qubits
* Total number of gates
* Circuit depth
* Number of two-qubit gates

The analyzer also provides structural and quality information about the submitted circuit.

### Example Circuit

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)

qc.h(0)
qc.cx(0, 1)

qc.measure_all()
```

QuantumInsight uses a static-safe analysis approach and does not directly execute arbitrary submitted source code.

---

# 🩺 Quantum Health Index (QHI)

The **Quantum Health Index (QHI)** is one of the main metrics of QuantumInsight.

QHI provides a normalized circuit-health score between:

```text
0 – 100
```

The score combines multiple characteristics of a quantum circuit into an overall engineering-oriented health indicator.

## QHI Components

The framework considers factors such as:

* Depth efficiency
* Gate efficiency
* Qubit utilization
* Two-qubit gate efficiency
* Noise exposure
* Optimization potential

## QHI Categories

| QHI Score | Category             |
| --------: | -------------------- |
|      ≥ 70 | 🟢 Healthy           |
| 50 – 69.9 | 🟡 Moderate          |
| 40 – 49.9 | 🟠 Needs Improvement |
|      < 40 | 🔴 Critical          |

QHI is intended as an engineering indicator and should not be interpreted as a guarantee of execution performance on a particular quantum processor.

---

# 🧩 Quantum Maintainability Index (QMI)

QuantumInsight also introduces the **Quantum Maintainability Index (QMI)**.

While QHI focuses on overall circuit health, QMI focuses on the software-engineering quality and maintainability of a quantum circuit.

## QMI Components

QMI evaluates:

* Readability
* Gate Efficiency
* Modularity
* Scalability
* Gate Diversity
* Circuit Complexity

The final QMI score is normalized to:

```text
0 – 100
```

## QHI vs QMI

| Metric  | Purpose                                                       |
| ------- | ------------------------------------------------------------- |
| **QHI** | Measures overall quantum circuit health                       |
| **QMI** | Measures quantum circuit maintainability and software quality |

This allows QuantumInsight to evaluate a circuit from both a quantum-engineering perspective and a software-engineering perspective.

---

# 🤖 AI-Assisted Recommendations

After analyzing a circuit, QuantumInsight generates recommendations based on the detected circuit characteristics.

Recommendations can address areas such as:

* Reducing unnecessary two-qubit operations
* Reducing circuit depth
* Improving gate efficiency
* Managing noise exposure
* Investigating anomalies
* Optimizing circuit structure
* Improving hardware compatibility

The recommendations are presented alongside the underlying analysis so that users can understand the characteristics that led to them.

---

# 🐞 AI Quantum Debugger

QuantumInsight includes a dedicated **AI Quantum Debugger**.

Users can provide:

1. Quantum code
2. An error message

The debugger analyzes the reported problem and provides:

* Error type
* Diagnosis
* Suggested debugging direction
* Verification status

For example:

```text
Type: QUBIT_INDEX_ERROR
```

The debugger is designed to help developers understand quantum programming errors and identify possible corrections.

---

# ⚡ Quantum Circuit Optimizer

QuantumInsight provides a quantum circuit optimization workflow.

The optimizer focuses on characteristics such as:

* Gate count
* Circuit depth
* Two-qubit operations
* Redundant operations
* Circuit structure

The objective is to identify opportunities for improving a circuit while preserving its intended computational structure.

---

# 🖥️ Hardware Recommendations

QuantumInsight provides hardware-oriented analysis of quantum circuits.

The hardware assessment considers characteristics such as:

* Circuit qubit requirements
* Requested backend
* Connectivity requirements
* Gate fidelity
* Noise sensitivity
* Quantum hardware provider
* Execution target

For Qiskit programs targeting IBM Quantum infrastructure, the system can identify IBM Quantum-related execution patterns and provide corresponding hardware guidance.

The system distinguishes between:

```text
Static hardware assessment
```

and:

```text
Actual quantum hardware execution
```

QuantumInsight does not claim live hardware availability unless live backend information is explicitly queried.

---

# 🔍 Anomaly Detection

QuantumInsight includes an anomaly-analysis component for identifying unusual circuit characteristics.

The system evaluates circuit features against an analysis baseline and produces an anomaly signal/score.

This can help identify circuits that differ significantly from expected structural characteristics.

The anomaly result is presented alongside other circuit-quality information rather than being treated as an independent guarantee of a problem.

---

# 📊 Dashboard & Analytics

The QuantumInsight dashboard provides an overview of analyzed circuits.

It includes information such as:

* Total analyses
* Average QHI
* Average QMI
* Average anomaly score
* Recent analyses
* QHI trends
* QMI trends
* Analysis history

The dashboard allows users to understand circuit-quality trends across multiple analyses.

---

# 📚 Analysis History

QuantumInsight stores analysis results for authenticated users.

Historical analyses can be used to:

* Review previous circuits
* Track circuit quality
* Compare circuit versions
* Review recommendations
* Track QHI
* Track QMI
* Review anomaly information
* Monitor changes after optimization

---

# 🔄 Circuit Analysis Comparison

QuantumInsight supports comparison between analyzed circuits.

Users can compare different circuit versions and observe changes in:

* Qubits
* Gates
* Circuit depth
* Two-qubit gates
* QHI
* QMI
* Anomaly measurements

This is useful when evaluating the effect of circuit optimization or structural changes.

---

# 👁️ Circuit Visualizer

QuantumInsight includes a circuit visualization interface for helping users understand the structure of an analyzed quantum circuit.

The visualizer works alongside the circuit analysis information so that users can inspect:

* Quantum registers
* Gates
* Circuit structure
* Operations
* Circuit relationships

This provides both numerical and visual representations of the circuit.

---

# 📄 Analysis Report Export

QuantumInsight provides report-export functionality for preserving analysis results.

Reports can include important information from the circuit-analysis workflow, allowing results to be used for:

* Documentation
* Project reports
* Research
* Presentations
* Engineering records

---

# 📥 History CSV Export

Historical analysis information can also be exported in CSV format.

This makes the collected analysis data useful for:

* Spreadsheet analysis
* Research
* Documentation
* External data processing
* Performance comparison

---

# 🔐 Authentication & User Accounts

QuantumInsight includes a complete user authentication system.

Supported functionality includes:

* User registration
* Email/password login
* JWT authentication
* Google Sign-In
* Logout
* Profile management
* Password change
* Password reset
* Authenticated analysis history

Each user's historical analysis data is associated with their authenticated account.

---

# 🔒 Security

Security is an important part of the QuantumInsight architecture.

## Static-Safe Code Analysis

QuantumInsight does not directly execute arbitrary user-submitted Python source code during normal circuit analysis.

The analyzer uses a static-safe parsing and analysis approach.

The application communicates this explicitly through the analyzer interface:

> **No submitted code is executed directly.**

This reduces the security risks associated with executing arbitrary Python code on the backend.

## Authentication

Protected API endpoints use bearer-token authentication.

## CORS

The production backend uses an explicitly configured frontend origin rather than unrestricted production cross-origin access.

## Secrets

Sensitive credentials and API keys are stored through environment variables.

Real credentials should never be committed to GitHub.

---

# 🏗️ System Architecture

QuantumInsight uses a separated frontend/backend architecture.

```text
                         ┌───────────────────────┐
                         │      User Browser     │
                         │                       │
                         │   Next.js Frontend    │
                         └───────────┬───────────┘
                                     │
                                     │ HTTPS / REST API
                                     ▼
                         ┌───────────────────────┐
                         │    FastAPI Backend    │
                         │                       │
                         │  Circuit Analysis     │
                         │  QHI                  │
                         │  QMI                  │
                         │  Debugger             │
                         │  Optimizer            │
                         │  Hardware Analysis    │
                         │  Recommendations      │
                         │  Authentication       │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       Supabase        │
                         │                       │
                         │ Users                 │
                         │ Analysis History      │
                         │ Password Reset Data   │
                         └───────────────────────┘
```

---

# 🧰 Technology Stack

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* Recharts
* Cloudflare Workers

## Backend

* Python
* FastAPI
* Pydantic
* Uvicorn
* NumPy
* JWT authentication

## Quantum Computing

* Qiskit
* IBM Quantum / Qiskit Runtime compatible workflows

## Database

* Supabase
* PostgreSQL

## Authentication

* Custom JWT authentication
* Supabase Authentication integration
* Google Sign-In

## Deployment

* Cloudflare Workers — Frontend
* Render — Backend
* Supabase — Database
* UptimeRobot — Backend monitoring

---

# 📁 Project Structure

```text
quantum-insight/
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── analyzer/
│   │   │   ├── dashboard/
│   │   │   ├── debugger/
│   │   │   ├── history/
│   │   │   ├── optimizer/
│   │   │   ├── settings/
│   │   │   └── ...
│   │   │
│   │   ├── components/
│   │   │   ├── AIRecommendation.tsx
│   │   │   ├── AppShell.tsx
│   │   │   ├── CircuitEditor.tsx
│   │   │   ├── CircuitViewer.tsx
│   │   │   ├── HealthChart.tsx
│   │   │   ├── HealthScore.tsx
│   │   │   ├── HardwareRecommendations.tsx
│   │   │   ├── QMI.tsx
│   │   │   └── ...
│   │   │
│   │   ├── lib/
│   │   ├── services/
│   │   └── types/
│   │
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes_analysis.py
│   │   │   ├── routes_auth.py
│   │   │   ├── routes_debugger.py
│   │   │   ├── routes_history.py
│   │   │   ├── routes_optimizer.py
│   │   │   ├── routes_reports.py
│   │   │   └── routes_health.py
│   │   │
│   │   ├── auth.py
│   │   ├── core/
│   │   ├── hardware/
│   │   ├── qmi/
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── README.md
└── ...
```

---

# 🔬 Analysis Workflow

A typical QuantumInsight analysis follows this workflow:

```text
                  Qiskit Source Code
                          │
                          ▼
                 Static-Safe Parsing
                          │
                          ▼
                  Circuit Extraction
                          │
                          ▼
              ┌──────────────────────┐
              │   Circuit Metrics    │
              │                      │
              │   Qubits             │
              │   Gates              │
              │   Depth              │
              │   2Q Gates            │
              └──────────┬───────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
            QHI                    QMI
              │                     │
              ▼                     ▼
       Circuit Health        Maintainability
              │                     │
              └──────────┬──────────┘
                         ▼
                 Anomaly Analysis
                         │
                         ▼
                Hardware Assessment
                         │
                         ▼
               AI Recommendations
                         │
                         ▼
                  Final Analysis
```

---

# 📐 QHI Calculation Concept

The Quantum Health Index combines several normalized circuit-health factors.

Conceptually:

```text
QHI
│
├── Depth Efficiency
├── Gate Efficiency
├── Qubit Utilization
├── Two-Qubit Efficiency
├── Noise Exposure
└── Optimization Potential
```

Each component contributes to the overall health assessment.

The resulting score is normalized to a range of:

```text
0 – 100
```

---

# 📐 QMI Calculation Concept

The Quantum Maintainability Index combines six maintainability-oriented components:

```text
QMI
│
├── Readability       20%
├── Gate Efficiency   20%
├── Modularity        20%
├── Scalability       15%
├── Gate Diversity    15%
└── Complexity        10%
```

The resulting score is normalized to:

```text
0 – 100
```

QMI is designed to provide a reproducible engineering measure of circuit maintainability rather than a subjective rating.

---

# 🧪 Example Analysis

Consider the following Qiskit circuit:

```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2)

qc.h(0)
qc.cx(0, 1)

qc.measure_all()
```

QuantumInsight can extract characteristics such as:

```text
Qubits       → 2
Gates        → 3
Depth        → 3
2Q Gates     → 2
```

The circuit is then evaluated through the QHI and QMI analysis pipelines.

The final result may include:

```text
Circuit Metrics
        ↓
QHI
        ↓
QMI
        ↓
Anomaly Signal
        ↓
Hardware Assessment
        ↓
AI Recommendations
```

Exact scores depend on the circuit and the analysis implementation.

---

# 🌐 Live Application

## QuantumInsight

### LIVE

**https://quantum-insight.bilalshaikh1339.workers.dev/**

The live application provides access to:

* Dashboard
* Circuit Analyzer
* Circuit Visualizer
* Quantum Health Index
* Quantum Maintainability Index
* AI Recommendations
* AI Quantum Debugger
* Circuit Optimizer
* Analysis History
* Circuit Comparison
* Hardware Recommendations
* Report Export
* CSV History Export
* Settings and Account Management

---

# ⚙️ Local Development

## 1. Clone the Repository

```bash
git clone https://github.com/Bilal-9922/quantum-insight.git

cd quantum-insight
```

---

# 🐍 Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a Python virtual environment.

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 🖥️ Frontend Setup

Open another terminal.

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Create:

```text
.env.local
```

Add:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:3000
```

---

# 🔑 Environment Variables

Do not commit real credentials to GitHub.

A basic frontend development configuration may contain:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

The backend requires its configured environment variables for:

* Application configuration
* CORS
* Database access
* Authentication
* JWT signing
* Password reset functionality
* External service integrations where applicable

Example structure:

```env
APP_NAME=QuantumInsight

CORS_ORIGINS=http://localhost:3000

SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

JWT_SECRET=your_secret
```

Use the appropriate environment-variable configuration for production deployments.

**Never commit real API keys, passwords, JWT secrets, database credentials, or OAuth secrets to the repository.**

---

# 🚀 Production Deployment

QuantumInsight uses a separated production architecture.

```text
                         GitHub Repository
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
                 ▼                             ▼
          Cloudflare Workers                Render
                 │                             │
                 ▼                             ▼
          Next.js Frontend             FastAPI Backend
                                               │
                                               ▼
                                           Supabase
```

## Frontend

The frontend is deployed through **Cloudflare Workers**.

Live frontend:

```text
https://quantum-insight.bilalshaikh1339.workers.dev/
```

## Backend

The FastAPI backend is deployed through **Render**.

## Database

Application data is stored using **Supabase/PostgreSQL**.

## Monitoring

Backend availability is monitored using **UptimeRobot**.

The production health endpoint is:

```text
https://quantuminsight-backend.onrender.com/api/healthcheck
```

The endpoint supports health monitoring requests and is used to verify backend availability.

---

# ❤️ Backend Health Monitoring

QuantumInsight uses a dedicated health-check endpoint:

```text
/api/healthcheck
```

A successful health check returns:

```json
{
  "status": "healthy"
}
```

The backend also supports HTTP `HEAD` requests for uptime monitoring.

This allows the production API to be monitored without requiring a paid HTTP `GET` monitoring method.

---

# 📊 Engineering Metrics

QuantumInsight works with several categories of measurements.

## Circuit Metrics

```text
Qubits
Gates
Depth
Two-Qubit Gates
```

## Quality Metrics

```text
QHI
QMI
Anomaly Score
```

## Hardware Characteristics

```text
Connectivity
Gate Fidelity
Noise Sensitivity
Backend Requirements
Execution Target
```

---

# 🧠 Design Philosophy

QuantumInsight is designed around three main principles.

## 1. Explainability

A score should be supported by meaningful engineering information.

The platform therefore exposes the metrics and components behind its circuit assessments.

## 2. Static Analysis First

The platform emphasizes safe analysis of submitted quantum source code instead of directly executing arbitrary user code.

## 3. Engineering-Oriented Quantum Development

The objective is not simply to execute a quantum circuit.

The objective is to help developers understand:

```text
How complex is the circuit?
        ↓
How healthy is it?
        ↓
How maintainable is it?
        ↓
What problems can be identified?
        ↓
What can be improved?
        ↓
What hardware characteristics matter?
```

---

# 🎓 Project Objectives

The major objectives of QuantumInsight are:

1. Analyze Qiskit quantum circuits automatically.
2. Extract meaningful circuit-level engineering metrics.
3. Develop a normalized Quantum Health Index.
4. Develop a Quantum Maintainability Index.
5. Detect unusual circuit characteristics.
6. Generate AI-assisted optimization recommendations.
7. Assist developers with quantum programming errors.
8. Provide hardware-oriented circuit assessment.
9. Maintain historical analysis records.
10. Compare different circuit versions.
11. Provide circuit visualization.
12. Provide a complete web-based quantum development interface.

---

# 🔮 Future Improvements

Potential future improvements include:

* More advanced circuit optimization
* Expanded quantum hardware profiles
* Additional quantum SDK support
* Deeper circuit dependency analysis
* More advanced anomaly detection
* More detailed noise modeling
* Real-time quantum backend availability
* Advanced circuit visualization
* Benchmarking across different circuit types
* Additional export formats
* Research-oriented analytics
* Automated optimization comparison
* Expanded quantum software engineering metrics

---

# ⚠️ Limitations

QuantumInsight is an engineering analysis and decision-support platform.

The calculated QHI and QMI values should not be interpreted as guaranteed predictions of quantum hardware execution fidelity.

Actual quantum execution can depend on factors including:

* Hardware topology
* Hardware calibration
* Noise characteristics
* Transpilation
* Backend configuration
* Runtime conditions
* Measurement behavior
* Circuit compilation
* Hardware availability

Hardware recommendations should therefore be treated as **static-analysis guidance**, not a guarantee of hardware availability or execution success.

Similarly, AI-generated recommendations should be reviewed by the developer before being applied to production quantum programs.

---

# 🧪 Example Use Cases

QuantumInsight can be useful for:

### Quantum Software Development

Analyze a quantum circuit before execution.

### Circuit Optimization

Compare an original circuit against an optimized version.

### Quantum Programming Education

Help students understand how circuit structure affects quality metrics.

### Research

Use QHI, QMI, and circuit metrics as engineering indicators when studying quantum software.

### Quantum Debugging

Analyze common quantum programming errors and understand possible causes.

### Hardware Selection

Evaluate circuit requirements before considering a target quantum backend.

### Software Engineering

Apply maintainability concepts to quantum circuit development.

---

# 🛠️ Development Workflow

A typical development workflow using QuantumInsight is:

```text
Write Qiskit Circuit
        │
        ▼
Open QuantumInsight
        │
        ▼
Paste Circuit
        │
        ▼
Analyze Circuit
        │
        ▼
Review Metrics
        │
        ├──────────────► QHI
        │
        ├──────────────► QMI
        │
        ├──────────────► Anomaly
        │
        ├──────────────► Hardware
        │
        └──────────────► Recommendations
                         │
                         ▼
                   Improve Circuit
                         │
                         ▼
                  Analyze Again
```

This creates an iterative workflow:

> **Analyze → Improve → Re-analyze**

---

# 👨‍💻 Author

## Mohammad Bilal Shaikh

**QuantumInsight** was designed and developed by **Mohammad Bilal Shaikh**.

### Project Title

**QuantumInsight: An AI-Powered Quantum Circuit Intelligence, Optimization & Health Analysis Framework**

### GitHub Repository

https://github.com/Bilal-9922/quantum-insight

### Live Application

https://quantum-insight.bilalshaikh1339.workers.dev/

---

# ⭐ Support the Project

If you find QuantumInsight useful or interesting:

* ⭐ Star the repository
* 🍴 Fork the project
* 🐛 Report issues
* 💡 Suggest improvements
* 🔬 Explore the quantum software engineering approach

---

# 📜 License

This project is distributed under the license included in this repository.

See the `LICENSE` file for the complete terms.

---

# ⚛️ QuantumInsight

> **Analyze quantum circuits. Understand their health. Improve their quality.**

**Designed & Developed by Mohammad Bilal Shaikh**
