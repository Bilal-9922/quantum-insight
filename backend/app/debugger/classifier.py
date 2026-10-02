def classify(message):
    m = (message or "").lower().strip()

    # ---------------------------------------------------------
    # No error
    # ---------------------------------------------------------

    if not m:
        return "NO_ERROR"

    # ---------------------------------------------------------
    # Syntax errors
    # ---------------------------------------------------------

    syntax_patterns = [
        "syntaxerror",
        "syntax error",
        "invalid syntax",
        "unexpected indent",
        "unexpected token",
        "unterminated",
        "parenthesis",
        "parentheses",
        "bracket",
        "invalid decimal literal",
        "was never closed",
        "expected an indented block",
    ]

    if any(pattern in m for pattern in syntax_patterns):
        return "SYNTAX_ERROR"

    # ---------------------------------------------------------
    # Undefined names / variables
    # ---------------------------------------------------------

    name_patterns = [
        "nameerror",
        "name error",
        "is not defined",
        "undefined variable",
        "undefined name",
        "unknown variable",
    ]

    if any(pattern in m for pattern in name_patterns):
        return "NAME_ERROR"

    # ---------------------------------------------------------
    # Classical-bit index errors
    # ---------------------------------------------------------

    classical_patterns = [
        "classical bit index",
        "classical bit",
        "clbit",
        "classical-bit",
        "classical bit index",
        "out of range for a circuit with",
    ]

    if any(pattern in m for pattern in classical_patterns):
        return "CLASSICAL_BIT_INDEX_ERROR"

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
        "qubit index is out of range",
    ]

    if any(pattern in m for pattern in qubit_index_patterns):
        return "QUBIT_INDEX_ERROR"

    # ---------------------------------------------------------
    # Gate argument errors
    # ---------------------------------------------------------
    #
    # Covers both QuantumInsight messages and actual Qiskit
    # messages such as:
    #
    # "The cx gate requires 2 qubit arguments,
    #  but only 1 was provided."
    #
    # "Gate 'cx' expects 2 argument(s), but 1 were provided."
    # ---------------------------------------------------------

    gate_argument_patterns = [
        "expects",
        "expected arguments",
        "argument(s)",
        "wrong number of arguments",
        "incorrect number of arguments",
        "missing required argument",
        "too few arguments",
        "too many arguments",
        "amount of qubit arguments",
        "requires 1 qubit argument",
        "requires 2 qubit arguments",
        "requires 3 qubit arguments",
        "requires 4 qubit arguments",
        "requires 1 argument",
        "requires 2 arguments",
        "requires 3 arguments",
        "requires 4 arguments",
        "qubit arguments",
        "only 1 was provided",
        "only 2 were provided",
        "only 3 were provided",
        "only 4 were provided",
    ]

    if any(pattern in m for pattern in gate_argument_patterns):
        return "GATE_ARGUMENT_ERROR"

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

    return "NO_ERROR"
