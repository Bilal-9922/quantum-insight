def diagnose(code, error=None):
    """
    Generate a circuit-specific diagnosis based on the
    reported error message and the submitted Qiskit code.
    """

    message = str(error or "").strip()
    text = message.lower()
    source = code or ""

    # ---------------------------------------------------------
    # Syntax errors
    # ---------------------------------------------------------

    if (
        "syntaxerror" in text
        or "invalid syntax" in text
        or "unexpected indent" in text
    ):
        return {
            "diagnosis": (
                "The submitted Python/Qiskit code contains a syntax "
                "error, so the circuit cannot be parsed correctly."
            ),
            "suggestions": [
                "Check parentheses, brackets, commas, and indentation.",
                "Inspect the line identified by the Python error message.",
                "Make sure every gate call uses valid Python syntax.",
            ],
        }

    # ---------------------------------------------------------
    # Qubit index errors
    # ---------------------------------------------------------

    if (
        "index out of range" in text
        or "out of range for size" in text
        or "invalid qubit index" in text
        or "qubit index" in text
        or "qarg" in text
        or "qargs" in text
    ):
        return {
            "diagnosis": (
                "A gate references a qubit index that is outside the "
                "available circuit range."
            ),
            "suggestions": [
                "Check the QuantumCircuit qubit count.",
                "Verify that every gate uses valid qubit indices.",
                "For a circuit with N qubits, valid indices are 0 through N-1.",
            ],
        }

    # ---------------------------------------------------------
    # Parameter errors
    # ---------------------------------------------------------

    if (
        "invalid parameter" in text
        or "parameter error" in text
        or "invalid angle" in text
        or "invalid phase" in text
        or "invalid value for parameter" in text
    ):
        return {
            "diagnosis": (
                "A gate appears to contain an invalid or unsupported "
                "parameter value."
            ),
            "suggestions": [
                "Check the parameter values passed to rotation and phase gates.",
                "Verify that numerical parameters have valid values.",
                "Check the order of gate parameters against the Qiskit API.",
            ],
        }

    # ---------------------------------------------------------
    # Gate errors
    # ---------------------------------------------------------

    if (
        "unknown gate" in text
        or "invalid gate" in text
        or "unsupported gate" in text
        or "gate not found" in text
    ):
        return {
            "diagnosis": (
                "The circuit contains a gate that Qiskit cannot recognize "
                "or does not support in the current context."
            ),
            "suggestions": [
                "Check the gate name for spelling mistakes.",
                "Verify that the required Qiskit gate is imported or available.",
                "Replace unsupported operations with a supported equivalent.",
            ],
        }

    # ---------------------------------------------------------
    # Import errors
    # ---------------------------------------------------------

    if (
        "modulenotfounderror" in text
        or "importerror" in text
        or "no module named" in text
    ):
        return {
            "diagnosis": (
                "The submitted code depends on a Python module or import "
                "that is not available in the execution environment."
            ),
            "suggestions": [
                "Check the module name and import statement.",
                "Verify that the required package is installed.",
                "Confirm that the imported Qiskit component exists in the installed version.",
            ],
        }

    # ---------------------------------------------------------
    # Circuit errors
    # ---------------------------------------------------------

    if (
        "circuiterror" in text
        or "invalid circuit" in text
        or "cannot add instruction" in text
    ):
        return {
            "diagnosis": (
                "Qiskit rejected an operation while constructing or "
                "modifying the circuit."
            ),
            "suggestions": [
                "Check the gate arguments and target qubits.",
                "Verify that the operation is compatible with the circuit.",
                "Inspect the reported Qiskit error for the rejected instruction.",
            ],
        }

    # ---------------------------------------------------------
    # Generic runtime error
    # ---------------------------------------------------------

    if message:
        return {
            "diagnosis": (
                f"The debugger received a runtime error: {message}. "
                "The exact failure should be investigated using the "
                "reported exception and the corresponding circuit operation."
            ),
            "suggestions": [
                "Inspect the operation associated with the reported error.",
                "Check gate arguments, qubit indices, and parameter values.",
                "Run the corrected circuit in a controlled Qiskit environment.",
            ],
        }

    # ---------------------------------------------------------
    # No error supplied
    # ---------------------------------------------------------

    return {
        "diagnosis": (
            "No runtime error was supplied. The submitted circuit can "
            "still be inspected for syntax and structural issues."
        ),
        "suggestions": [
            "Validate the circuit structure and gate arguments.",
            "Review qubit usage and circuit depth.",
            "Run the circuit through the analyzer and optimizer.",
        ],
    }
