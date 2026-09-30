import ast
import tokenize
from io import StringIO


def generate_patch(code, error=None):
    """
    Generate safe deterministic patches for simple Qiskit errors.

    The generator only changes code when the correction can be
    determined without changing the intended quantum operation.
    """

    original_code = code or ""
    message = str(error or "").strip()
    text = message.lower()

    # ---------------------------------------------------------
    # Syntax errors
    # ---------------------------------------------------------

    syntax_patch = _handle_syntax_error(original_code)

    if syntax_patch is not None:
        return syntax_patch

    is_syntax_error = (
        "syntaxerror" in text
        or "invalid syntax" in text
        or "was never closed" in text
        or "unexpected eof" in text
        or "unexpected end of input" in text
        or "eof while parsing" in text
    )

    if is_syntax_error:
        return {
            "fixed_code": original_code,
            "changed": False,
            "note": (
                "A syntax error was detected, but the debugger could "
                "not determine a safe structural correction."
            ),
        }

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


def _handle_syntax_error(code):
    """
    Detect an unmatched opening delimiter and safely close it.

    Example:

        qc.h(0

    becomes:

        qc.h(0)
    """

    if not code.strip():
        return None

    stack = []

    opening = {
        "(": ")",
        "[": "]",
        "{": "}",
    }

    closing = {
        ")": "(",
        "]": "[",
        "}": "{",
    }

    try:
        token_stream = tokenize.generate_tokens(
            StringIO(code).readline
        )

        while True:
            try:
                token = next(token_stream)

            except StopIteration:
                break

            except tokenize.TokenError:
                # Incomplete Python commonly ends with a TokenError.
                # The tokens collected before the error are still
                # sufficient to detect an unmatched delimiter.
                break

            value = token.string

            if value in opening:
                stack.append(value)

            elif value in closing:

                if not stack:
                    return None

                expected = closing[value]

                if stack[-1] != expected:
                    return None

                stack.pop()

    except (IndentationError, SyntaxError):
        return None

    # Nothing is unclosed.
    if not stack:
        return None

    # Only automatically fix a single unmatched parenthesis.
    #
    # This keeps the automatic fixer conservative and prevents
    # it from making large structural changes to user code.
    if len(stack) != 1:
        return None

    if stack[0] != "(":
        return None

    # Do not modify code when the final non-empty line is only
    # a comment. Appending ")" after a comment would be unsafe.
    non_empty_lines = [
        line
        for line in code.splitlines()
        if line.strip()
    ]

    if not non_empty_lines:
        return None

    last_line = non_empty_lines[-1]

    if "#" in last_line:
        return None

    fixed_code = code.rstrip() + ")"

    # Verify the generated Python syntax.
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


def _handle_qubit_error(code, message):
    """
    Handle qubit-index errors conservatively.

    We do NOT replace an invalid qubit with another arbitrary
    qubit because doing so can change the circuit's meaning.
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
    Extract invalid qubit index and circuit size from the
    debugger's validation message.
    """

    import re

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
