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

    is_syntax_error = (
        "syntaxerror" in text
        or "invalid syntax" in text
        or "was never closed" in text
        or "unexpected eof" in text
        or "unexpected end of input" in text
        or "eof while parsing" in text
    )

    if is_syntax_error:
        syntax_patch = _handle_syntax_error(original_code)

        if syntax_patch is not None:
            return syntax_patch

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
    Safely repair an unclosed delimiter.

    Tokenization is allowed to stop with EOF because incomplete
    Python such as:

        qc.h(0

    can produce a TokenError before all tokens are returned.

    We still inspect the tokens collected before that error.
    """

    stack = []

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
                # Incomplete code can end with an EOF tokenization
                # error. The tokens collected before this point are
                # still useful for detecting an unmatched delimiter.
                break

            value = token.string

            if value in {"(", "[", "{"}:
                stack.append(value)

            elif value in {")", "]", "}"}:
                if not stack:
                    return None

                expected_opening = {
                    ")": "(",
                    "]": "[",
                    "}": "{",
                }[value]

                if stack[-1] != expected_opening:
                    return None

                stack.pop()

    except (IndentationError, SyntaxError):
        return None

    # Nothing is structurally unclosed.
    if not stack:
        return None

    closing_delimiters = {
        "(": ")",
        "[": "]",
        "{": "}",
    }

    missing = "".join(
        closing_delimiters[item]
        for item in reversed(stack)
    )

    fixed_code = code.rstrip() + missing

    # Make sure the generated code is actually valid Python.
    try:
        ast.parse(fixed_code)
    except SyntaxError:
        return None

    return {
        "fixed_code": fixed_code,
        "changed": True,
        "note": (
            "The debugger detected an unclosed Python delimiter "
            "and safely added the required closing delimiter(s)."
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
