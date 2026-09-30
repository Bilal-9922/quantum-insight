import ast
import re


def generate_patch(code, error=None):
    """
    Generate safe deterministic patches for simple Qiskit errors.
    """

    original_code = code or ""
    message = str(error or "").strip()
    text = message.lower()

    # ---------------------------------------------------------
    # Syntax error auto-fix
    # ---------------------------------------------------------

    syntax_patch = _handle_syntax_error(original_code, message)

    if syntax_patch is not None:
        return syntax_patch

    # ---------------------------------------------------------
    # Qubit index errors
    # ---------------------------------------------------------

    is_qubit_error = (
        "index out of range" in text
        or "out of range for size" in text
        or "invalid qubit index" in text
        or "qubit index" in text
    )

    if is_qubit_error:
        return _handle_qubit_error(
            original_code,
            message,
        )

    # ---------------------------------------------------------
    # No safe automatic patch
    # ---------------------------------------------------------

    return {
        "fixed_code": original_code,
        "changed": False,
        "note": (
            "No safe automatic patch was generated. "
            "The debugger only rewrites code when the "
            "correction can be determined reliably."
        ),
    }


def _handle_syntax_error(code, error_message):
    """
    Safely fix a simple missing closing parenthesis.

    Example:

        qc.h(0

    becomes:

        qc.h(0)
    """

    if not code.strip():
        return None

    # First confirm that the submitted code is actually invalid.
    try:
        ast.parse(code)
        return None
    except SyntaxError as exc:
        parser_message = str(exc.msg or "").lower()

    # Python normally reports this exact condition as:
    #
    #     '(' was never closed
    #
    # Also accept common EOF wording.
    combined_message = (
        parser_message + " " + error_message.lower()
    )

    is_unclosed_parenthesis = (
        "was never closed" in combined_message
        or "eof while parsing" in combined_message
        or "unexpected eof" in combined_message
    )

    if not is_unclosed_parenthesis:
        return None

    # Count parentheses while ignoring the most common
    # quoted strings and comments.
    balance = _parenthesis_balance(code)

    # We only fix exactly one missing ")".
    if balance != 1:
        return None

    # Do not modify a line where the missing parenthesis would
    # be placed inside a comment.
    lines = code.splitlines()

    if not lines:
        return None

    last_code_line = lines[-1]

    if "#" in last_code_line:
        return None

    # Add the missing closing parenthesis.
    fixed_code = code.rstrip() + ")"

    # Verify the generated code.
    try:
        ast.parse(fixed_code)
    except SyntaxError:
        return None

    return {
        "fixed_code": fixed_code,
        "changed": True,
        "note": (
            "The debugger detected an unclosed parenthesis "
            "and automatically added the missing ')'."
        ),
    }


def _parenthesis_balance(code):
    """
    Count unmatched parentheses while ignoring strings
    and comments.

    Returns:
        1  -> exactly one '(' is unclosed
        0  -> balanced
        -1 -> more closing ')' than opening '('
    """

    balance = 0
    i = 0
    length = len(code)

    while i < length:
        char = code[i]

        # -----------------------------------------------------
        # Comment
        # -----------------------------------------------------

        if char == "#":
            newline = code.find("\n", i)

            if newline == -1:
                break

            i = newline + 1
            continue

        # -----------------------------------------------------
        # Single-quoted string
        # -----------------------------------------------------

        if char == "'":
            i += 1

            while i < length:
                if code[i] == "\\":
                    i += 2
                    continue

                if code[i] == "'":
                    i += 1
                    break

                i += 1

            continue

        # -----------------------------------------------------
        # Double-quoted string
        # -----------------------------------------------------

        if char == '"':
            i += 1

            while i < length:
                if code[i] == "\\":
                    i += 2
                    continue

                if code[i] == '"':
                    i += 1
                    break

                i += 1

            continue

        # -----------------------------------------------------
        # Parentheses
        # -----------------------------------------------------

        if char == "(":
            balance += 1

        elif char == ")":
            balance -= 1

            if balance < 0:
                return balance

        i += 1

    return balance


def _handle_qubit_error(code, message):
    """
    Handle qubit-index errors conservatively.
    """

    details = _extract_qubit_error(message)

    if details is None:
        return {
            "fixed_code": code,
            "changed": False,
            "note": (
                "A qubit-index error was detected, but the "
                "invalid index and circuit size could not be "
                "identified safely."
            ),
        }

    invalid_index, qubit_count = details

    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "fixed_code": code,
            "changed": False,
            "note": (
                "The submitted code contains a syntax error, "
                "so no automatic patch was generated."
            ),
        }

    offending_gate = _find_offending_gate(
        tree,
        invalid_index,
        qubit_count,
    )

    if offending_gate is None:
        return {
            "fixed_code": code,
            "changed": False,
            "note": (
                f"Qubit index {invalid_index} is invalid for a "
                f"{qubit_count}-qubit circuit, but the debugger "
                "could not safely identify the affected gate."
            ),
        }

    gate_name, line_number = offending_gate

    return {
        "fixed_code": code,
        "changed": False,
        "note": (
            f"Qubit index {invalid_index} is invalid for a "
            f"{qubit_count}-qubit circuit. The affected gate "
            f"'{gate_name}' is on line {line_number}. "
            "No automatic replacement was made because choosing "
            "another qubit could change the circuit's intended "
            "quantum operation."
        ),
    }


def _extract_qubit_error(message):
    """
    Extract invalid qubit index and circuit size.
    """

    match = re.search(
        r"Qubit index\s+(-?\d+)\s+is out of range\s+"
        r"for a circuit with\s+(\d+)\s+qubit",
        message,
        re.IGNORECASE,
    )

    if not match:
        return None

    invalid_index = int(match.group(1))
    qubit_count = int(match.group(2))

    return invalid_index, qubit_count


def _find_offending_gate(tree, invalid_index, qubit_count):
    """
    Locate the gate containing the invalid integer qubit index.
    """

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Attribute):
            continue

        gate_name = node.func.attr

        for arg in node.args:

            if isinstance(arg, ast.Constant):

                if isinstance(arg.value, int):

                    if (
                        arg.value == invalid_index
                        and (
                            invalid_index < 0
                            or invalid_index >= qubit_count
                        )
                    ):
                        return (
                            gate_name,
                            getattr(node, "lineno", None),
                        )

    return None
