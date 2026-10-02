import re


def _find_quantum_circuit_size(code: str) -> int | None:
    """
    Extract the first QuantumCircuit qubit count.

    Example:
        qc = QuantumCircuit(2)
        -> 2
    """

    match = re.search(
        r"\bQuantumCircuit\s*\(\s*(\d+)",
        code,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return int(match.group(1))


def _find_circuit_names(code: str) -> list[str]:
    """
    Find variables assigned from QuantumCircuit().
    """

    return re.findall(
        r"\b([A-Za-z_]\w*)\s*=\s*QuantumCircuit\s*\(",
        code,
    )


def _find_invalid_qubit_fix(
    code: str,
    invalid_index: int,
    circuit_size: int,
) -> tuple[str, int] | None:
    """
    Find the Qiskit gate containing the invalid qubit and
    replace only that argument.

    We intentionally do NOT replace arbitrary numbers in the
    source code.
    """

    if circuit_size <= 0:
        return None

    replacement_index = 0

    gate_pattern = re.compile(
        r"(?P<prefix>\b[A-Za-z_]\w*\."
        r"(?:h|x|y|z|s|sdg|t|tdg|rx|ry|rz|p|u|u1|u2|u3|"
        r"cx|cy|cz|ch|swap|ccx|ccz|cswap|crx|cry|crz)"
        r"\s*\()"
        r"(?P<args>[^)]*)"
        r"(?P<close>\))",
        flags=re.IGNORECASE,
    )

    for match in gate_pattern.finditer(code):
        args = match.group("args")

        numbers = list(
            re.finditer(
                r"(?<![A-Za-z0-9_])(\d+)(?![A-Za-z0-9_])",
                args,
            )
        )

        for number_match in numbers:
            value = int(number_match.group(1))

            if value == invalid_index:
                start = match.start("args") + number_match.start(1)
                end = match.start("args") + number_match.end(1)

                fixed_code = (
                    code[:start]
                    + str(replacement_index)
                    + code[end:]
                )

                return fixed_code, replacement_index

    return None


def _fix_missing_two_qubit_argument(code: str) -> tuple[str, str] | None:
    """
    Fix common two-qubit gate calls such as:

        qc.cx(0)

    into:

        qc.cx(0, 1)

    Only fixes a gate that visibly contains exactly one
    numeric qubit argument.
    """

    pattern = re.compile(
        r"\b([A-Za-z_]\w*)\."
        r"(cx|cy|cz|ch|swap)"
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

    fixed_code = (
        code[:match.start()]
        + replacement
        + code[match.end():]
    )

    return fixed_code, gate_name


def _fix_too_many_two_qubit_arguments(code: str) -> tuple[str, str] | None:
    """
    Fix:

        qc.cx(0, 1, 2)

    into:

        qc.cx(0, 1)

    This is specifically for two-qubit gates.
    """

    pattern = re.compile(
        r"\b([A-Za-z_]\w*)\."
        r"(cx|cy|cz|ch|swap)"
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

    fixed_code = (
        code[:match.start()]
        + replacement
        + code[match.end():]
    )

    return fixed_code, gate_name


def _fix_syntax_error(code: str) -> str | None:
    """
    Fix the common case:

        qc.cx(0, 1

    where one closing parenthesis is missing.

    We repair the specific incomplete Qiskit call rather than
    blindly appending ')' to the entire source.
    """

    lines = code.splitlines()

    for index, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            continue

        if (
            re.search(
                r"\b[A-Za-z_]\w*\."
                r"[A-Za-z_]\w*\s*\([^)]*$",
                stripped,
            )
            and stripped.count("(") > stripped.count(")")
        ):
            lines[index] = line + ")"
            return "\n".join(lines)

    # Fallback for a simple unmatched parenthesis.
    open_count = code.count("(")
    close_count = code.count(")")

    if open_count > close_count:
        return code + (")" * (open_count - close_count))

    return None


def generate_patch(code: str, error_message: str | None):
    """
    Generate a conservative automatic fix for common real
    Qiskit programming errors.

    Every suggested fix is intended to be passed through the
    verifier before being presented as verified.
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
        candidate = _fix_syntax_error(original_code)

        if candidate and candidate != original_code:
            fixed_code = candidate
            changed = True

            note = (
                "A missing closing parenthesis was detected "
                "in the Qiskit code and repaired."
            )

            suggested_fix = {
                "code": fixed_code,
                "type": "SYNTAX_ERROR",
                "warning": (
                    "The syntax was automatically repaired. "
                    "Review the corrected Qiskit code before execution."
                ),
            }

    # =========================================================
    # 2. QUBIT INDEX ERROR
    # =========================================================

    elif (
        "index out of range" in message
        or "out of range for size" in message
        or "qubit index" in message
        or "invalid qubit index" in message
        or "qubit does not exist" in message
    ):
        match = re.search(
            r"index\s+(\d+)\s+out\s+of\s+range\s+for\s+size\s+(\d+)",
            message,
        )

        if match:
            invalid_index = int(match.group(1))
            circuit_size = int(match.group(2))

            fix = _find_invalid_qubit_fix(
                original_code,
                invalid_index,
                circuit_size,
            )

            if fix:
                fixed_code, suggested_index = fix
                changed = fixed_code != original_code

                if changed:
                    note = (
                        f"Qubit index {invalid_index} is invalid for "
                        f"a {circuit_size}-qubit circuit. "
                        f"The invalid gate argument was changed to "
                        f"qubit {suggested_index}."
                    )

                    suggested_fix = {
                        "code": fixed_code,
                        "type": "QUBIT_INDEX_ERROR",
                        "invalid_qubit": invalid_index,
                        "suggested_qubit": suggested_index,
                        "warning": (
                            "The replacement uses a valid qubit index. "
                            "Verify that it matches the intended circuit logic."
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
            r"classical bit index\s+(\d+)"
            r"\s+is out of range.*?"
            r"(\d+)\s+classical bit",
            message,
        )

        if match:
            invalid_index = int(match.group(1))
            classical_size = int(match.group(2))

            if classical_size > 0:
                suggested_index = classical_size - 1

                measure_pattern = re.compile(
                    rf"(\bmeasure\s*\(\s*"
                    rf"[^,()]+\s*,\s*)"
                    rf"{invalid_index}"
                    rf"(\s*\))",
                    flags=re.IGNORECASE,
                )

                candidate = measure_pattern.sub(
                    rf"\g<1>{suggested_index}\g<2>",
                    original_code,
                    count=1,
                )

                if candidate != original_code:
                    fixed_code = candidate
                    changed = True

                    note = (
                        f"Classical bit index {invalid_index} is "
                        f"outside the circuit's {classical_size} "
                        f"classical bits. It was changed to "
                        f"{suggested_index}."
                    )

                    suggested_fix = {
                        "code": fixed_code,
                        "type": "CLASSICAL_BIT_INDEX_ERROR",
                        "invalid_bit": invalid_index,
                        "suggested_bit": suggested_index,
                        "warning": (
                            "The measurement was mapped to a valid "
                            "classical bit. Verify the intended mapping."
                        ),
                    }

    # =========================================================
    # 4. GATE ARGUMENT ERROR
    # =========================================================

    elif (
        "requires 2 qubit arguments" in message
        or "requires 2 qubits" in message
        or "only 1 was provided" in message
        or "one argument" in message
        or "too many arguments" in message
        or "too many qubits" in message
        or "argument" in message
        and "provided" in message
    ):
        # -----------------------------------------------------
        # Missing second qubit
        # -----------------------------------------------------

        fix = _fix_missing_two_qubit_argument(original_code)

        if fix:
            fixed_code, gate_name = fix
            changed = True

            note = (
                f"The {gate_name} gate requires two qubit "
                "arguments. A valid second qubit was added."
            )

            suggested_fix = {
                "code": fixed_code,
                "type": "GATE_ARGUMENT_ERROR",
                "gate": gate_name,
                "warning": (
                    "Qubit 1 was selected as the second argument. "
                    "Verify that this is the intended target qubit."
                ),
            }

        else:
            # -------------------------------------------------
            # Too many qubits
            # -------------------------------------------------

            fix = _fix_too_many_two_qubit_arguments(
                original_code
            )

            if fix:
                fixed_code, gate_name = fix
                changed = True

                note = (
                    f"The {gate_name} gate accepts two qubit "
                    "arguments. The extra argument was removed."
                )

                suggested_fix = {
                    "code": fixed_code,
                    "type": "GATE_ARGUMENT_ERROR",
                    "gate": gate_name,
                    "warning": (
                        "The extra qubit argument was removed. "
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
        circuit_definitions = _find_circuit_names(
            original_code
        )

        name_match = re.search(
            r"name ['\"]([a-zA-Z_]\w*)['\"] is not defined",
            message,
        )

        if name_match and len(circuit_definitions) == 1:
            undefined_name = name_match.group(1)
            correct_name = circuit_definitions[0]

            # Only replace the undefined name when it appears
            # as a circuit/gate receiver or obvious variable.
            candidate = re.sub(
                rf"(?<![A-Za-z0-9_])"
                rf"{re.escape(undefined_name)}"
                rf"(?=\s*\.)",
                correct_name,
                original_code,
            )

            if candidate != original_code:
                fixed_code = candidate
                changed = True

                note = (
                    f"The undefined variable '{undefined_name}' "
                    f"was replaced with the detected "
                    f"QuantumCircuit variable '{correct_name}'."
                )

                suggested_fix = {
                    "code": fixed_code,
                    "type": "NAME_ERROR",
                    "undefined_name": undefined_name,
                    "suggested_name": correct_name,
                    "warning": (
                        "The replacement uses the detected "
                        "QuantumCircuit variable."
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
