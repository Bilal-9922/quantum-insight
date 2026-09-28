# Architecture

QuantumInsight has four logical intelligence layers:

1. Quantum engine: parser, Qiskit/Aer, metrics, transpilation.
2. ML engine: Isolation Forest and Random Forest.
3. AI engine: debugger, explanations and recommendations.
4. Health engine: custom Quantum Health Index.

The web dashboard consumes FastAPI endpoints and renders the structured results.
