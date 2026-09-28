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
