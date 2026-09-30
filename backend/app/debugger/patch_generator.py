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

    syntax_patch = _handle_syntax_error(
        original_code,
        message,
    )

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
    Safely fix one missing closing delimiter.

    Supported:
        (
        [
        {

    The correction is inserted on the line reported by Python.
    """

    if not code.strip():
        return None

    # ---------------------------------------------------------
    # Get the actual Python syntax error.
    # ---------------------------------------------------------

    try:
        ast.parse(code)
        return None

    except SyntaxError as exc:
        error_line = exc.lineno
        parser_message = str(exc.msg or "").lower()

    combined_message = (
        parser_message
        + " "
        + error_message.lower()
    )

    # Only handle an unclosed delimiter.
    if (
        "was never closed" not in combined_message
        and "eof while parsing" not in combined_message
        and "unexpected eof" not in combined_message
    ):
        return None

    if not error_line:
        return None

    lines = code.splitlines()

    if error_line < 1 or error_line > len(lines):
        return None

    # ---------------------------------------------------------
    # Find unmatched delimiters.
    # ---------------------------------------------------------

    delimiter_stack = _find_delimiter_stack(code)

    if delimiter_stack is None:
        return None

    # Only make a correction when exactly one delimiter is open.
    if len(delimiter_stack) != 1:
        return None

    opening = delimiter_stack[0]

    closing = {
        "(": ")",
        "[": "]",
        "{": "}",
    }.get(opening)

    if closing is None:
        return None

    # ---------------------------------------------------------
    # Insert the missing delimiter on the reported line.
    # ---------------------------------------------------------

    target_index = error_line - 1
    target_line = lines[target_index]

    stripped = target_line.lstrip()

    # Never modify a comment line.
    if stripped.startswith("#"):
        return None

    # Avoid inserting into a trailing comment.
    comment_position = _find_comment_position(target_line)

    if comment_position is not None:
        code_part = target_line[:comment_position].rstrip()
        comment_part = target_line[comment_position:]

        if not code_part:
            return None

        lines[target_index] = (
            code_part
            + closing
            + " "
            + comment_part.lstrip()
        )

    else:
        lines[target_index] = target_line + closing

    fixed_code = "\n".join(lines)

    if code.endswith("\n"):
        fixed_code += "\n"

    # ---------------------------------------------------------
    # Verify the generated code.
    # ---------------------------------------------------------

    try:
        ast.parse(fixed_code)

    except SyntaxError:
        return None

    return {
        "fixed_code": fixed_code,
        "changed": True,
        "note": (
            f"The debugger detected an unclosed "
            f"'{opening}' on line {error_line} "
            f"and automatically added the missing "
            f"'{closing}'."
        ),
    }


def _find_delimiter_stack(code):
    """
    Find unmatched (, [, and { delimiters.

    Strings and comments are ignored.
    """

    stack = []

    i = 0
    length = len(code)

    while i < length:

        char = code[i]

        # -----------------------------------------------------
        # Comment
        # -----------------------------------------------------

        if char == "#":

            newline = code.find(
                "\n",
                i,
            )

            if newline == -1:
                break

            i = newline + 1
            continue

        # -----------------------------------------------------
        # Single quoted string
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
        # Double quoted string
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
        # Opening delimiters
        # -----------------------------------------------------

        if char in "([{":
            stack.append(char)

        # -----------------------------------------------------
        # Closing delimiters
        # -----------------------------------------------------

        elif char in ")]}":

            expected = {
                ")": "(",
                "]": "[",
                "}": "{",
            }[char]

            if not stack:
                return None

            if stack[-1] != expected:
                return None

            stack.pop()

        i += 1

    return stack


def _find_comment_position(line):
    """
    Find a real # comment while ignoring # inside strings.
    """

    in_single = False
    in_double = False
    escaped = False

    for index, char in enumerate(line):

        if escaped:
            escaped = False
            continue

        if char == "\\":
            escaped = True
            continue

        if char == "'" and not in_double:
            in_single = not in_single
            continue

        if char == '"' and not in_single:
            in_double = not in_double
            continue

        if char == "#" and not in_single and not in_double:
            return index

    return None


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

    return (
        invalid_index,
        qubit_count,
    )


def _find_offending_gate(
    tree,
    invalid_index,
    qubit_count,
):
    """
    Locate the gate containing the invalid integer qubit index.
    """

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        if not isinstance(
            node.func,
            ast.Attribute,
        ):
            continue

        gate_name = node.func.attr

        for arg in node.args:

            if not isinstance(
                arg,
                ast.Constant,
            ):
                continue

            if not isinstance(
                arg.value,
                int,
            ):
                continue

            if (
                arg.value == invalid_index
                and (
                    invalid_index < 0
                    or invalid_index >= qubit_count
                )
            ):
                return (
                    gate_name,
                    getattr(
                        node,
                        "lineno",
                        None,
                    ),
                )

    return None
