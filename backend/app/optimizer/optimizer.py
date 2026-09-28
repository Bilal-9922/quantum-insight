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
