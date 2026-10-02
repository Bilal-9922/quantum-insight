import re


def _find_circuit_size(code: str) -> int | None:
    match = re.search(
        r"\bQuantumCircuit\s*\(\s*(\d+)",
        code,
        flags=re.IGNORECASE,
    )

    if match:
        return int(match.group(1))

    return None


def _find_circuit_names(code: str) -> list[str]:
    return re.findall(
        r"\b([A-Za-z_]\w*)\s*=\s*QuantumCircuit\s*\(",
        code,
    )


def _fix_qubit_index(
    code: str,
    invalid_index: int,
    circuit_size: int,
):
    """
    Find the actual Qiskit operation containing the invalid
    qubit index and replace only that argument.
    """

    if circuit_size <= 0:
        return None

    # Use the first valid qubit.
    replacement_index = 0

    gate_pattern = re.compile(
        r"\b([A-Za-z_]\w*)\."
        r"(h|x|y|z|s|sdg|t|tdg|sx|sxdg|id|reset|"
        r"cx|cy|cz|ch|swap|iswap|ecr|ccx|cswap|"
        r"rx|ry|rz|p|phase|u|u1|u2|u3)"
        r"\s*\(([^)]*)\)",
        flags=re.IGNORECASE,
    )

    for match in gate_pattern.finditer(code):

        args = match.group(3)

        number_matches = list(
            re.finditer(
                r"(?<![A-Za-z0-9_])(-?\d+)(?![A-Za-z0-9_])",
                args,
            )
        )

        for number_match in number_matches:

            value = int(number_match.group(1))

            if value != invalid_index:
                continue

            args_start = match.start(3)

            replacement_start = (
                args_start + number_match.start(1)
            )

            replacement_end = (
                args_start + number_match.end(1)
            )

            return (
                code[:replacement_start]
                + str(replacement_index)
                + code[replacement_end:]
            )

    return None


def _fix_missing_gate_argument(code: str):
    """
    Fix:

        qc.cx(0)

    into:

        qc.cx(0, 1)
    """

    pattern = re.compile(
        r"\b([A-Za-z_]\w*)\."
        r"(cx|cy|cz|ch|swap|iswap|ecr)"
        r"\s*\(\s*(\d+)\s*\)",
        flags=re.IGNORECASE,
    )

    match = pattern.search(code)

    if not match:
        return None

    circuit_name = match.group(1)
    gate_name = match.group(2)
    first_qubit = match.group(3)

    replacement = (
        f"{circuit_name}.{gate_name}"
        f"({first_qubit}, 1)"
    )

    return (
        code[:match.start()]
        + replacement
        + code[match.end():]
    )


def _fix_extra_gate_argument(code: str):
    """
    Fix:

        qc.cx(0, 1, 2)

    into:

        qc.cx(0, 1)
    """

    pattern = re.compile(
        r"\b([A-Za-z_]\w*)\."
        r"(cx|cy|cz|ch|swap|iswap|ecr)"
        r"\s*\(\s*"
        r"(\d+)\s*,\s*(\d+)\s*,\s*(\d+)"
        r"\s*\)",
        flags=re.IGNORECASE,
    )

    match = pattern.search(code)

    if not match:
        return None

    circuit_name = match.group(1)
    gate_name = match.group(2)
    first = match.group(3)
    second = match.group(4)

    replacement = (
        f"{circuit_name}.{gate_name}"
        f"({first}, {second})"
    )

    return (
        code[:match.start()]
        + replacement
        + code[match.end():]
    )


def _fix_undefined_variable(
    code: str,
    variable_name: str,
):
    """
    Fix an undefined variable used as a qubit argument.

    Example:

        qc.x(qubit)

    becomes:

        qc.x(0)
    """

    circuit_size = _find_circuit_size(code)

    if circuit_size is None:
        return None

    replacement_index = 0

    # Look specifically for the undefined variable inside
    # a Qiskit gate's argument list.
    pattern = re.compile(
        rf"(\b[A-Za-z_]\w*\."
        rf"(?:h|x|y|z|s|sdg|t|tdg|sx|sxdg|id|reset|"
        rf"cx|cy|cz|ch|swap|iswap|ecr|ccx|cswap|"
        rf"rx|ry|rz|p|phase|u|u1|u2|u3)"
        rf"\s*\([^)]*)"
        rf"\b{re.escape(variable_name)}\b"
        rf"([^)]*\))",
        flags=re.IGNORECASE,
    )

    match = pattern.search(code)

    if not match:
        return None

    return (
        code[:match.start()]
        + match.group(1)
        + str(replacement_index)
        + match.group(2)
        + code[match.end():]
    )


def _fix_syntax_error(code: str):
    """
    Repair the common Qiskit case:

        qc.cx(0, 1

    into:

        qc.cx(0, 1)
    """

    lines = code.splitlines()

    for index, line in enumerate(lines):

        if not line.strip():
            continue

        open_count = line.count("(")
        close_count = line.count(")")

        if open_count > close_count:

            # Only repair a line that looks like a function call.
            if re.search(
                r"\b[A-Za-z_]\w*\."
                r"[A-Za-z_]\w*\s*\(",
                line,
            ):
                lines[index] = line + (
                    ")" * (open_count - close_count)
                )

                return "\n".join(lines)

    # Fallback for simple unmatched parentheses.
    open_count = code.count("(")
    close_count = code.count(")")

    if open_count > close_count:
        return code + (
            ")" * (open_count - close_count)
        )

    return None


def generate_patch(
    code: str,
    error_message: str | None,
):
    """
    Generate an automatic suggested fix for common real
    Qiskit errors.

    The generated code is returned through:

        suggested_fix["code"]

    and:

        fixed_code

    The caller should verify fixed_code before treating it
    as verified.
    """

    original_code = code or ""
    message = (error_message or "").strip().lower()

    fixed_code = original_code
    changed = False

    note = "No automatic fix could be generated."

    suggested_fix = None

    # =========================================================
    # 1. SYNTAX ERROR
    # =========================================================

    if (
        "syntaxerror" in message
        or "invalid syntax" in message
        or "was never closed" in message
        or "parenthesis" in message
        or "unterminated" in message
    ):

        candidate = _fix_syntax_error(
            original_code
        )

        if candidate and candidate != original_code:

            fixed_code = candidate
            changed = True

            note = (
                "A missing closing parenthesis was detected "
                "and repaired in the Qiskit code."
            )

            suggested_fix = {
                "code": fixed_code,
                "type": "SYNTAX_ERROR",
                "warning": (
                    "The missing parenthesis was repaired. "
                    "Review the corrected Qiskit code before execution."
                ),
            }

    # =========================================================
    # 2. QUBIT INDEX ERROR
    # =========================================================

    elif (
        "qubit index" in message
        or "out of range" in message
        or "qubit does not exist" in message
    ):

        # Supports BOTH:

        # Index 3 out of range for size 2

        # and:

        # Qubit index 3 is out of range for a circuit
        # with 2 qubit(s).

        match = re.search(
            r"index\s+(-?\d+).*?"
            r"(?:size|with)\s+(\d+)",
            message,
        )

        if match:

            invalid_index = int(
                match.group(1)
            )

            circuit_size = int(
                match.group(2)
            )

            candidate = _fix_qubit_index(
                original_code,
                invalid_index,
                circuit_size,
            )

            if candidate and candidate != original_code:

                fixed_code = candidate
                changed = True

                note = (
                    f"Qubit index {invalid_index} is invalid "
                    f"for a {circuit_size}-qubit circuit. "
                    "It was replaced with qubit 0."
                )

                suggested_fix = {
                    "code": fixed_code,
                    "type": "QUBIT_INDEX_ERROR",
                    "invalid_qubit": invalid_index,
                    "suggested_qubit": 0,
                    "warning": (
                        "The invalid qubit index was replaced "
                        "with a valid index. Verify that qubit 0 "
                        "matches your intended circuit logic."
                    ),
                }

    # =========================================================
    # 3. CLASSICAL BIT INDEX ERROR
    # =========================================================

    elif (
        "classical bit index" in message
        or (
            "classical bit" in message
            and "out of range" in message
        )
    ):

        match = re.search(
            r"classical bit index\s+(-?\d+).*?"
            r"(?:with|has)\s+(\d+)\s+classical bit",
            message,
        )

        if match:

            invalid_index = int(
                match.group(1)
            )

            classical_size = int(
                match.group(2)
            )

            if classical_size > 0:

                replacement_index = (
                    classical_size - 1
                )

                pattern = re.compile(
                    rf"(\bmeasure\s*\(\s*"
                    rf"[^,()]+\s*,\s*)"
                    rf"{invalid_index}"
                    rf"(\s*\))",
                    flags=re.IGNORECASE,
                )

                candidate = pattern.sub(
                    rf"\g<1>{replacement_index}\g<2>",
                    original_code,
                    count=1,
                )

                if candidate != original_code:

                    fixed_code = candidate
                    changed = True

                    note = (
                        f"Classical bit index "
                        f"{invalid_index} is invalid. "
                        f"It was changed to "
                        f"{replacement_index}."
                    )

                    suggested_fix = {
                        "code": fixed_code,
                        "type": "CLASSICAL_BIT_INDEX_ERROR",
                        "invalid_bit": invalid_index,
                        "suggested_bit": replacement_index,
                        "warning": (
                            "The measurement was mapped to a "
                            "valid classical bit. Verify the "
                            "intended measurement mapping."
                        ),
                    }

    # =========================================================
    # 4. GATE ARGUMENT ERROR
    # =========================================================

    elif (
        "gate argument" in message
        or "expects" in message
        and "argument" in message
        or "argument(s)" in message
        or "only 1 was provided" in message
        or "too many" in message
    ):

        # -----------------------------------------------------
        # Missing argument
        # -----------------------------------------------------

        candidate = _fix_missing_gate_argument(
            original_code
        )

        if candidate and candidate != original_code:

            fixed_code = candidate
            changed = True

            note = (
                "The two-qubit gate was missing its "
                "second qubit argument. Qubit 1 was added."
            )

            suggested_fix = {
                "code": fixed_code,
                "type": "GATE_ARGUMENT_ERROR",
                "warning": (
                    "A valid second qubit was added. "
                    "Verify that it is the intended target."
                ),
            }

        else:

            # -------------------------------------------------
            # Too many arguments
            # -------------------------------------------------

            candidate = _fix_extra_gate_argument(
                original_code
            )

            if candidate and candidate != original_code:

                fixed_code = candidate
                changed = True

                note = (
                    "The two-qubit gate contained an extra "
                    "qubit argument. The extra argument was removed."
                )

                suggested_fix = {
                    "code": fixed_code,
                    "type": "GATE_ARGUMENT_ERROR",
                    "warning": (
                        "The extra argument was removed. "
                        "Verify the intended circuit operation."
                    ),
                }

    # =========================================================
    # 5. NAME ERROR
    # =========================================================

    elif (
        "nameerror" in message
        or "is not defined" in message
    ):

        name_match = re.search(
            r"name\s+['\"]([a-zA-Z_]\w*)['\"]"
            r"\s+is not defined",
            message,
        )

        if name_match:

            undefined_name = (
                name_match.group(1)
            )

            candidate = _fix_undefined_variable(
                original_code,
                undefined_name,
            )

            if candidate and candidate != original_code:

                fixed_code = candidate
                changed = True

                note = (
                    f"The undefined qubit variable "
                    f"'{undefined_name}' was replaced "
                    "with valid qubit index 0."
                )

                suggested_fix = {
                    "code": fixed_code,
                    "type": "NAME_ERROR",
                    "undefined_name": undefined_name,
                    "suggested_value": 0,
                    "warning": (
                        "The undefined variable was replaced "
                        "with qubit 0. Verify that this is "
                        "the intended qubit."
                    ),
                }

            else:

                # Handle an undefined circuit object.
                circuit_names = _find_circuit_names(
                    original_code
                )

                if len(circuit_names) == 1:

                    correct_name = (
                        circuit_names[0]
                    )

                    receiver_pattern = re.compile(
                        rf"(?<![A-Za-z0-9_])"
                        rf"{re.escape(undefined_name)}"
                        rf"(?=\s*\.)"
                    )

                    candidate = receiver_pattern.sub(
                        correct_name,
                        original_code,
                    )

                    if candidate != original_code:

                        fixed_code = candidate
                        changed = True

                        note = (
                            f"The undefined circuit variable "
                            f"'{undefined_name}' was replaced "
                            f"with '{correct_name}'."
                        )

                        suggested_fix = {
                            "code": fixed_code,
                            "type": "NAME_ERROR",
                            "undefined_name": undefined_name,
                            "suggested_name": correct_name,
                            "warning": (
                                "The circuit variable was replaced "
                                "with the detected QuantumCircuit."
                            ),
                        }

    # =========================================================
    # 6. NO AUTOMATIC FIX
    # =========================================================

    if not suggested_fix:

        suggested_fix = {
            "code": "",
            "type": "NO_AUTOMATIC_FIX",
            "warning": (
                "QuantumInsight could not safely generate "
                "an automatic fix for this Qiskit error."
            ),
        }

    return {
        "fixed_code": fixed_code,
        "changed": changed,
        "note": note,
        "suggested_fix": suggested_fix,
    }
