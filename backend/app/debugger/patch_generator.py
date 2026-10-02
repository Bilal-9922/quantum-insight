import re


def generate_patch(code: str, error_message: str | None):
    """
    Generate a safe suggested fix for common Qiskit errors.

    The function always returns:
    - fixed_code
    - changed
    - note
    - suggested_fix

    The frontend uses suggested_fix.code for the
    "Apply Suggested Fix" button.
    """

    original_code = code or ""
    message = (error_message or "").strip().lower()

    fixed_code = original_code
    changed = False
    note = "No automatic fix could be generated."

    suggested_fix = None

    # ---------------------------------------------------------
    # 1. SYNTAX ERROR
    # ---------------------------------------------------------
    if (
        "syntaxerror" in message
        or "invalid syntax" in message
        or "was never closed" in message
        or "parenthesis" in message
        or "unterminated" in message
    ):
        # Common missing closing parenthesis:
        # qc.h(0
        #
        # Only attempt this when the parentheses are actually
        # unbalanced.

        open_count = original_code.count("(")
        close_count = original_code.count(")")

        if open_count > close_count:
            fixed_code = original_code + (")" * (open_count - close_count))
            changed = fixed_code != original_code

            if changed:
                note = "A missing closing parenthesis was detected and added."

                suggested_fix = {
                    "code": fixed_code,
                    "type": "SYNTAX_ERROR",
                    "warning": "Review the corrected syntax before running the circuit.",
                }

    # ---------------------------------------------------------
    # 2. QUBIT INDEX ERROR
    # ---------------------------------------------------------
    elif (
        "index out of range" in message
        or "out of range for size" in message
        or "qubit index" in message
        or "invalid qubit index" in message
        or "qubit does not exist" in message
    ):
        # Try to detect:
        # Index 2 out of range for size 2
        #
        # Then replace the invalid index with the largest
        # valid index.

        match = re.search(
            r"index\s+(\d+)\s+out\s+of\s+range\s+for\s+size\s+(\d+)",
            message,
        )

        if match:
            invalid_index = int(match.group(1))
            size = int(match.group(2))
            suggested_index = size - 1

            pattern = rf"(?<!\d){invalid_index}(?!\d)"

            candidate = re.sub(
                pattern,
                str(suggested_index),
                original_code,
                count=1,
            )

            if candidate != original_code:
                fixed_code = candidate
                changed = True

                note = (
                    f"Qubit index {invalid_index} is outside the circuit size "
                    f"and was changed to {suggested_index}."
                )

                suggested_fix = {
                    "code": fixed_code,
                    "type": "QUBIT_INDEX_ERROR",
                    "invalid_qubit": invalid_index,
                    "suggested_qubit": suggested_index,
                    "warning": (
                        "The replacement is automatic. "
                        "Verify that the selected qubit matches your intended circuit."
                    ),
                }

    # ---------------------------------------------------------
    # 3. CLASSICAL BIT INDEX ERROR
    # ---------------------------------------------------------
    elif (
        "classical bit index" in message
        or "classical bit" in message
        and "out of range" in message
    ):
        match = re.search(
            r"classical bit index\s+(\d+)\s+is out of range.*?(\d+)\s+classical bit",
            message,
        )

        if match:
            invalid_index = int(match.group(1))
            classical_size = int(match.group(2))

            suggested_index = classical_size - 1

            # Look specifically for measure(qubit, classical_bit)
            pattern = rf"(measure\s*\(\s*\d+\s*,\s*){invalid_index}(\s*\))"

            candidate = re.sub(
                pattern,
                rf"\g<1>{suggested_index}\g<2>",
                original_code,
                count=1,
                flags=re.IGNORECASE,
            )

            if candidate != original_code:
                fixed_code = candidate
                changed = True

                note = (
                    f"Classical bit index {invalid_index} was changed "
                    f"to {suggested_index}."
                )

                suggested_fix = {
                    "code": fixed_code,
                    "type": "CLASSICAL_BIT_INDEX_ERROR",
                    "invalid_bit": invalid_index,
                    "suggested_bit": suggested_index,
                    "warning": (
                        "Verify that the corrected classical bit matches "
                        "the intended measurement mapping."
                    ),
                }

    # ---------------------------------------------------------
    # 4. MISSING GATE ARGUMENT
    # ---------------------------------------------------------
    elif (
        "requires 2 qubit arguments" in message
        or "only 1 was provided" in message
        or "gate requires" in message
    ):
        # Example:
        #
        # qc.cx(0)
        #
        # We cannot safely guess the intended target qubit.
        # Therefore provide a conservative suggested fix
        # using qubit 1 when the circuit has at least two qubits.

        match = re.search(
            r"([a-zA-Z_]\w*)\.(cx|cz|swap)\s*\(\s*(\d+)\s*\)",
            original_code,
        )

        if match:
            circuit_name = match.group(1)
            gate_name = match.group(2)
            first_qubit = match.group(3)

            if gate_name == "cx":
                replacement = (
                    f"{circuit_name}.{gate_name}"
                    f"({first_qubit}, 1)"
                )
            elif gate_name == "cz":
                replacement = (
                    f"{circuit_name}.{gate_name}"
                    f"({first_qubit}, 1)"
                )
            else:
                replacement = (
                    f"{circuit_name}.{gate_name}"
                    f"({first_qubit}, 1)"
                )

            candidate = original_code.replace(
                match.group(0),
                replacement,
                1,
            )

            if candidate != original_code:
                fixed_code = candidate
                changed = True

                note = (
                    f"The {gate_name} gate requires two qubit arguments. "
                    "A second qubit was added."
                )

                suggested_fix = {
                    "code": fixed_code,
                    "type": "GATE_ARGUMENT_ERROR",
                    "gate": gate_name,
                    "warning": (
                        "The second qubit was automatically selected as 1. "
                        "Verify that this is the intended target qubit."
                    ),
                }

    # ---------------------------------------------------------
    # 5. UNDEFINED CIRCUIT VARIABLE
    # ---------------------------------------------------------
    elif (
        "nameerror" in message
        or "is not defined" in message
    ):
        # Example:
        #
        # circuit = QuantumCircuit(2)
        # qc.h(0)
        #
        # If only one QuantumCircuit variable exists, use it.

        circuit_definitions = re.findall(
            r"([a-zA-Z_]\w*)\s*=\s*QuantumCircuit\s*\(",
            original_code,
        )

        name_match = re.search(
            r"name ['\"]([a-zA-Z_]\w*)['\"] is not defined",
            message,
        )

        if name_match and circuit_definitions:
            undefined_name = name_match.group(1)

            # Only auto-fix when there is exactly one obvious
            # QuantumCircuit variable.
            if len(circuit_definitions) == 1:
                correct_name = circuit_definitions[0]

                candidate = re.sub(
                    rf"\b{re.escape(undefined_name)}\b",
                    correct_name,
                    original_code,
                )

                if candidate != original_code:
                    fixed_code = candidate
                    changed = True

                    note = (
                        f"The undefined circuit variable '{undefined_name}' "
                        f"was replaced with '{correct_name}'."
                    )

                    suggested_fix = {
                        "code": fixed_code,
                        "type": "NAME_ERROR",
                        "undefined_name": undefined_name,
                        "suggested_name": correct_name,
                        "warning": (
                            "Verify that the replacement variable is "
                            "the intended QuantumCircuit."
                        ),
                    }

    # ---------------------------------------------------------
    # 6. NO AUTOMATIC FIX
    # ---------------------------------------------------------
    if not suggested_fix:
        suggested_fix = {
            "code": "",
            "type": "NO_AUTOMATIC_FIX",
            "warning": "QuantumInsight could not safely generate an automatic fix.",
        }

    return {
        "fixed_code": fixed_code,
        "changed": changed,
        "note": note,
        "suggested_fix": suggested_fix,
    }
