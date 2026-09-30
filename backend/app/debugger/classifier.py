def classify(message):
    m = (message or "").lower().strip()

    # ---------------------------------------------------------
    # Syntax errors
    # ---------------------------------------------------------

    syntax_patterns = [
        "syntaxerror",
        "invalid syntax",
        "unexpected indent",
        "unexpected token",
        "unterminated",
        "parenthesis",
        "bracket",
        "invalid decimal literal",
    ]

    if any(pattern in m for pattern in syntax_patterns):
        return "SYNTAX_ERROR"

    # ---------------------------------------------------------
    # Qubit index / circuit size errors
    # ---------------------------------------------------------

    qubit_index_patterns = [
        "index out of range",
        "out of range for size",
        "qubit index",
        "qubit indices",
        "invalid qubit index",
        "indexerror",
        "qarg",
        "qargs",
        "too many qubits",
        "number of qubits",
        "qubit does not exist",
    ]

    if any(pattern in m for pattern in qubit_index_patterns):
        return "QUBIT_INDEX_ERROR"

    # ---------------------------------------------------------
    # Parameter errors
    # ---------------------------------------------------------

    parameter_patterns = [
        "invalid parameter",
        "parameter error",
        "invalid parameter value",
        "invalid value for parameter",
        "parameter is invalid",
        "invalid rotation",
        "invalid angle",
        "invalid phase",
    ]

    if any(pattern in m for pattern in parameter_patterns):
        return "PARAMETER_ERROR"

    # ---------------------------------------------------------
    # Gate errors
    # ---------------------------------------------------------

    gate_patterns = [
        "gate error",
        "invalid gate",
        "unknown gate",
        "unsupported gate",
        "gate not found",
        "operation not supported",
    ]

    if any(pattern in m for pattern in gate_patterns):
        return "GATE_ERROR"

    # ---------------------------------------------------------
    # Circuit errors
    # ---------------------------------------------------------

    circuit_patterns = [
        "circuiterror",
        "invalid circuit",
        "circuit is invalid",
        "circuit construction",
        "cannot add instruction",
    ]

    if any(pattern in m for pattern in circuit_patterns):
        return "CIRCUIT_ERROR"

    # ---------------------------------------------------------
    # Import / module errors
    # ---------------------------------------------------------

    import_patterns = [
        "modulenotfounderror",
        "importerror",
        "no module named",
        "cannot import name",
    ]

    if any(pattern in m for pattern in import_patterns):
        return "IMPORT_ERROR"

    # ---------------------------------------------------------
    # General fallback
    # ---------------------------------------------------------

    return "GENERAL_ERROR"
