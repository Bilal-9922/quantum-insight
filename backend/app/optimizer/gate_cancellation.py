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
