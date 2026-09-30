import ast
import re


# -------------------------------------------------------------
# Safe Qiskit gate aliases
# -------------------------------------------------------------

GATE_ALIASES = {
    "hadamard": "h",
    "paulix": "x",
    "pauliy": "y",
    "pauliz": "z",
    "cnot": "cx",
    "controllednot": "cx",
    "controlled_x": "cx",
    "controlled_z": "cz",
    "phasegate": "p",
    "identity": "id",
}


# -------------------------------------------------------------
# Gates that commonly accept numeric parameters
# -------------------------------------------------------------

PARAMETERIZED_GATES = {
    "rx",
    "ry",
    "rz",
    "p",
    "u",
    "u1",
    "u2",
    "u3",
    "r",
    "cu",
    "crx",
    "cry",
    "crz",
}


def generate_patch(code, error=None):
    """
    Generate safe deterministic patches for simple Qiskit errors.
    """

    original_code = code or ""
    message = str(error or "").strip()
    text = message.lower()

    # ---------------------------------------------------------
    # Indentation error
    # ---------------------------------------------------------

    indentation_patch = _handle_indentation_error(
        original_code,
        message,
    )

    if indentation_patch is not None:
        return indentation_patch

    # ---------------------------------------------------------
    # Syntax error
    # ---------------------------------------------------------

    syntax_patch = _handle_syntax_error(
        original_code,
        message,
    )

    if syntax_patch is not None:
        return syntax_patch

    # ---------------------------------------------------------
    # Parameter error
    # ---------------------------------------------------------

    parameter_patch = _handle_parameter_error(
        original_code,
        message,
    )

    if parameter_patch is not None:
        return parameter_patch

    # ---------------------------------------------------------
    # Wrong gate-name error
    # ---------------------------------------------------------

    gate_patch = _handle_gate_name_error(
        original_code,
        message,
    )

    if gate_patch is not None:
        return gate_patch

    # ---------------------------------------------------------
    # Qubit index error
    # ---------------------------------------------------------

    is_qubit_error = (
        "index out of range" in text
        or "out of range for size" in text
        or "invalid qubit index" in text
        or "qubit index" in text
        or "qarg" in text
        or "qargs" in text
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


# =============================================================
# PARAMETER ERROR
# =============================================================

def _handle_parameter_error(code, error_message):
    """
    Handle simple invalid parameters in parameterized Qiskit gates.

    This intentionally only suggests a correction when an obviously
    non-numeric literal is being passed to a gate that expects a
    numeric parameter.

    Example:

        qc.ry("invalid", 0)

    Suggested:

        qc.ry(0.0, 0)

    The suggestion is not automatically applied because replacing a
    parameter changes the mathematical behavior of the circuit.
    """

    if not code.strip():
        return None

    message = str(error_message or "").lower()

    parameter_error = (
        "invalid parameter" in message
        or "parameter error" in message
        or "invalid parameter value" in message
        or "invalid value for parameter" in message
        or "parameter is invalid" in message
        or "invalid rotation" in message
        or "invalid angle" in message
        or "invalid phase" in message
        or "parameter must be" in message
        or "cannot bind" in message
        or "expected a numeric" in message
        or "numeric parameter" in message
    )

    if not parameter_error:
        return None

    try:
        tree = ast.parse(code)

    except SyntaxError:
        return None

    candidate = _find_invalid_parameter(tree)

    if candidate is None:
        return {
            "fixed_code": code,
            "changed": False,
            "note": (
                "A parameter error was detected, but the debugger "
                "could not identify a safe literal parameter to "
                "replace automatically."
            ),
        }

    (
        gate_name,
        line_number,
        parameter_index,
        parameter_value,
    ) = candidate

    lines = code.splitlines()

    index = line_number - 1

    if index < 0 or index >= len(lines):
        return None

    line = lines[index]

    replacement = "0.0"

    new_line = _replace_parameter_on_line(
        line,
        parameter_value,
        replacement,
        parameter_index,
    )

    if new_line is None:
        return {
            "fixed_code": code,
            "changed": False,
            "note": (
                f"The parameter error affects gate '{gate_name}' "
                f"on line {line_number}, but the debugger could "
                "not safely construct a replacement."
            ),
        }

    lines[index] = new_line

    fixed_code = "\n".join(lines)

    if code.endswith("\n"):
        fixed_code += "\n"

    try:
        ast.parse(fixed_code)

    except SyntaxError:
        return {
            "fixed_code": code,
            "changed": False,
            "note": (
                "A possible parameter correction was identified, "
                "but the resulting code did not pass Python syntax "
                "validation."
            ),
        }

    return {
        "fixed_code": code,
        "changed": False,
        "note": (
            f"The debugger detected a non-numeric parameter "
            f"'{parameter_value}' in gate '{gate_name}' "
            f"on line {line_number}. A possible correction is "
            f"to replace it with the numeric value 0.0."
        ),
        "suggested_fix": {
            "gate": gate_name,
            "line": line_number,
            "parameter_index": parameter_index,
            "invalid_parameter": parameter_value,
            "suggested_parameter": 0.0,
            "code": fixed_code,
            "warning": (
                "Replacing a gate parameter changes the circuit's "
                "mathematical operation. Review the value before "
                "applying this suggestion."
            ),
        },
    }


def _find_invalid_parameter(tree):
    """
    Find a clearly invalid string literal used as the parameter
    of a parameterized Qiskit gate.

    Returns:

        (
            gate_name,
            line_number,
            parameter_index,
            parameter_value
        )

    or None.
    """

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Attribute):
            continue

        if not isinstance(node.func.value, ast.Name):
            continue

        object_name = node.func.value.id.lower()

        if object_name not in {
            "qc",
            "circuit",
            "quantum_circuit",
        }:
            continue

        gate_name = node.func.attr.lower()

        if gate_name not in PARAMETERIZED_GATES:
            continue

        for index, argument in enumerate(node.args):

            if not isinstance(
                argument,
                ast.Constant,
            ):
                continue

            value = argument.value

            if not isinstance(value, str):
                continue

            stripped = value.strip()

            if not stripped:
                continue

            # A numeric string is not considered an invalid
            # parameter because it can be converted safely.
            try:
                float(stripped)
                continue
            except ValueError:
                pass

            return (
                gate_name,
                getattr(
                    node,
                    "lineno",
                    None,
                ),
                index,
                value,
            )

    return None


def _replace_parameter_on_line(
    line,
    invalid_value,
    replacement,
    parameter_index,
):
    """
    Replace the specific quoted parameter on the affected line.

    Only the matching quoted literal is replaced.
    """

    escaped_value = re.escape(
        str(invalid_value)
    )

    patterns = [
        re.compile(
            r"(['\"])"
            + escaped_value
            + r"\1"
        ),
    ]

    for pattern in patterns:

        matches = list(
            pattern.finditer(line)
        )

        if not matches:
            continue

        if parameter_index < len(matches):
            match = matches[parameter_index]

            return (
                line[:match.start()]
                + replacement
                + line[match.end():]
            )

        return None

    return None


# =============================================================
# GATE NAME ERROR
# =============================================================

def _handle_gate_name_error(code, error_message):
    """
    Safely repair an unambiguous Qiskit gate-name mistake.

    Example:

        qc.hadamard(0)

    becomes:

        qc.h(0)
    """

    if not code.strip():
        return None

    message = str(error_message or "").lower()

    gate_error = (
        "unknown or unsupported gate" in message
        or "unknown gate" in message
        or "invalid gate" in message
        or "unsupported gate" in message
        or "gate not found" in message
    )

    if not gate_error:
        return None

    try:
        tree = ast.parse(code)

    except SyntaxError:
        return None

    replacements = []

    for node in ast.walk(tree):

        if not isinstance(node, ast.Call):
            continue

        if not isinstance(node.func, ast.Attribute):
            continue

        if not isinstance(node.func.value, ast.Name):
            continue

        object_name = node.func.value.id.lower()

        if object_name not in {
            "qc",
            "circuit",
            "quantum_circuit",
        }:
            continue

        current_name = node.func.attr.lower()

        replacement = GATE_ALIASES.get(
            current_name
        )

        if replacement is None:
            continue

        replacements.append(
            (
                node.func.lineno,
                current_name,
                replacement,
            )
        )

    if not replacements:
        return {
            "fixed_code": code,
            "changed": False,
            "note": (
                "An unsupported gate was detected, but no "
                "safe and unambiguous gate replacement was found."
            ),
        }

    lines = code.splitlines()

    for (
        line_number,
        current_name,
        replacement,
    ) in sorted(
        replacements,
        reverse=True,
    ):

        index = line_number - 1

        if index < 0 or index >= len(lines):
            return None

        line = lines[index]

        pattern = re.compile(
            r"(\.\s*)"
            + re.escape(current_name)
            + r"(\s*\()",
            re.IGNORECASE,
        )

        new_line, count = pattern.subn(
            r"\1" + replacement + r"\2",
            line,
            count=1,
        )

        if count != 1:
            return None

        lines[index] = new_line

    fixed_code = "\n".join(lines)

    if code.endswith("\n"):
        fixed_code += "\n"

    try:
        ast.parse(fixed_code)

    except SyntaxError:
        return None

    first_change = replacements[0]

    return {
        "fixed_code": fixed_code,
        "changed": True,
        "note": (
            f"The debugger detected the unsupported gate "
            f"'{first_change[1]}' and replaced it with the "
            f"supported Qiskit gate '{first_change[2]}'."
        ),
        "suggested_fix": {
            "gate": first_change[1],
            "replacement": first_change[2],
            "line": first_change[0],
            "code": fixed_code,
            "warning": (
                "Review the replacement before using the "
                "corrected circuit."
            ),
        },
    }


# =============================================================
# INDENTATION ERROR
# =============================================================

def _handle_indentation_error(code, error_message):
    """
    Safely fix a simple missing indentation after a block statement.
    """

    message = str(error_message or "").lower()

    indentation_patterns = (
        "expected an indented block",
        "unexpected indent",
        "unindent does not match",
    )

    if not any(
        pattern in message
        for pattern in indentation_patterns
    ):
        return None

    lines = code.splitlines()

    if not lines:
        return None

    error_line = None

    try:
        ast.parse(code)

    except SyntaxError as exc:
        error_line = exc.lineno

    if error_line is not None:

        target_index = error_line - 1

        if (
            0 <= target_index < len(lines)
            and lines[target_index].strip()
        ):

            if target_index > 0:

                previous_line = lines[target_index - 1]
                target_line = lines[target_index]

                previous_stripped = previous_line.strip()
                target_stripped = target_line.strip()

                previous_indent = (
                    len(previous_line)
                    - len(previous_line.lstrip())
                )

                target_indent = (
                    len(target_line)
                    - len(target_line.lstrip())
                )

                if (
                    previous_stripped.endswith(":")
                    and target_indent <= previous_indent
                    and not target_stripped.startswith("#")
                    and not target_stripped.startswith(
                        (
                            "else:",
                            "elif ",
                            "except",
                            "finally:",
                        )
                    )
                ):

                    lines[target_index] = (
                        " " * (previous_indent + 4)
                        + target_stripped
                    )

                    fixed_code = "\n".join(lines)

                    if code.endswith("\n"):
                        fixed_code += "\n"

                    try:
                        ast.parse(fixed_code)

                    except SyntaxError:
                        return None

                    return {
                        "fixed_code": fixed_code,
                        "changed": True,
                        "note": (
                            f"The debugger detected a missing "
                            f"indentation on line {error_line} "
                            "and automatically indented the "
                            "statement by four spaces."
                        ),
                        "suggested_fix": {
                            "line": error_line,
                            "code": fixed_code,
                            "warning": (
                                "Review the indentation because "
                                "Python block structure determines "
                                "program execution."
                            ),
                        },
                    }

    for index in range(len(lines) - 1):

        current = lines[index]
        following = lines[index + 1]

        if not current.strip():
            continue

        if not following.strip():
            continue

        current_stripped = current.strip()
        following_stripped = following.strip()

        if not current_stripped.endswith(":"):
            continue

        if following_stripped.startswith("#"):
            continue

        current_indent = (
            len(current)
            - len(current.lstrip())
        )

        following_indent = (
            len(following)
            - len(following.lstrip())
        )

        if following_indent > current_indent:
            continue

        if following_stripped.startswith(
            (
                "else:",
                "elif ",
                "except",
                "finally:",
            )
        ):
            continue

        lines[index + 1] = (
            " " * (current_indent + 4)
            + following_stripped
        )

        fixed_code = "\n".join(lines)

        if code.endswith("\n"):
            fixed_code += "\n"

        try:
            ast.parse(fixed_code)

        except SyntaxError:
            return None

        return {
            "fixed_code": fixed_code,
            "changed": True,
            "note": (
                f"The debugger detected a missing indentation "
                f"after the block statement on line {index + 1} "
                "and automatically indented the following "
                "statement by four spaces."
            ),
            "suggested_fix": {
                "line": index + 2,
                "code": fixed_code,
                "warning": (
                    "Review the indentation before running "
                    "the corrected circuit."
                ),
            },
        }

    return None


# =============================================================
# SYNTAX ERROR
# =============================================================

def _handle_syntax_error(code, error_message):
    """
    Safely fix one missing closing delimiter.
    """

    if not code.strip():
        return None

    try:
        ast.parse(code)
        return None

    except SyntaxError as exc:
        error_line = exc.lineno
        parser_message = str(exc.msg or "").lower()

    combined_message = (
        parser_message
        + " "
        + str(error_message or "").lower()
    )

    if (
        "was never closed" not in combined_message
        and "eof while parsing" not in combined_message
        and "unexpected eof" not in combined_message
        and "unexpected end of file" not in combined_message
    ):
        return None

    if not error_line:
        return None

    lines = code.splitlines()

    if error_line < 1 or error_line > len(lines):
        return None

    delimiter_stack = _find_delimiter_stack(code)

    if delimiter_stack is None:
        return None

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

    target_index = error_line - 1
    target_line = lines[target_index]

    stripped = target_line.lstrip()

    if stripped.startswith("#"):
        return None

    comment_position = _find_comment_position(
        target_line
    )

    if comment_position is not None:

        code_part = (
            target_line[:comment_position]
            .rstrip()
        )

        comment_part = target_line[
            comment_position:
        ]

        if not code_part:
            return None

        lines[target_index] = (
            code_part
            + closing
            + " "
            + comment_part.lstrip()
        )

    else:
        lines[target_index] = (
            target_line
            + closing
        )

    fixed_code = "\n".join(lines)

    if code.endswith("\n"):
        fixed_code += "\n"

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
        "suggested_fix": {
            "line": error_line,
            "delimiter": closing,
            "code": fixed_code,
            "warning": (
                f"The debugger inferred that the closing "
                f"'{closing}' was missing. Review the "
                "corrected line before running the circuit."
            ),
        },
    }


# =============================================================
# DELIMITER ANALYSIS
# =============================================================

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

        if char == "#":

            newline = code.find(
                "\n",
                i,
            )

            if newline == -1:
                break

            i = newline + 1
            continue

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

        if char in "([{":
            stack.append(char)

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


# =============================================================
# COMMENT ANALYSIS
# =============================================================

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

        if (
            char == "#"
            and not in_single
            and not in_double
        ):
            return index

    return None


# =============================================================
# QUBIT INDEX ERROR
# =============================================================

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

    (
        gate_name,
        line_number,
        qubit_arguments,
    ) = offending_gate

    valid_qubits = list(range(qubit_count))

    used_valid_qubits = [
        q
        for q in qubit_arguments
        if 0 <= q < qubit_count
    ]

    available_qubits = [
        q
        for q in valid_qubits
        if q not in used_valid_qubits
    ]

    suggested_qubit = None

    if available_qubits:
        suggested_qubit = available_qubits[0]

    if suggested_qubit is not None:

        suggested_code = _build_qubit_suggestion(
            code,
            line_number,
            invalid_index,
            suggested_qubit,
        )

        return {
            "fixed_code": code,
            "changed": False,
            "note": (
                f"Qubit index {invalid_index} is invalid for a "
                f"{qubit_count}-qubit circuit. The affected gate "
                f"'{gate_name}' is on line {line_number}. "
                f"A possible correction is to replace qubit "
                f"{invalid_index} with qubit {suggested_qubit}. "
                "This is only a suggestion because changing the "
                "target qubit may change the intended quantum operation."
            ),
            "suggested_fix": {
                "gate": gate_name,
                "line": line_number,
                "invalid_qubit": invalid_index,
                "suggested_qubit": suggested_qubit,
                "code": suggested_code,
                "warning": (
                    "Review this suggestion before applying it. "
                    "The replacement may change the circuit's semantics."
                ),
            },
        }

    return {
        "fixed_code": code,
        "changed": False,
        "note": (
            f"Qubit index {invalid_index} is invalid for a "
            f"{qubit_count}-qubit circuit. The affected gate "
            f"'{gate_name}' is on line {line_number}. "
            "No safe replacement qubit was identified."
        ),
    }


def _extract_qubit_error(message):
    """
    Extract invalid qubit index and circuit size.
    """

    patterns = [
        re.compile(
            r"Qubit index\s+(-?\d+)\s+is out of range\s+"
            r"for a circuit with\s+(\d+)\s+qubit",
            re.IGNORECASE,
        ),
        re.compile(
            r"Index\s+(-?\d+)\s+out of range\s+for size\s+(\d+)",
            re.IGNORECASE,
        ),
    ]

    for pattern in patterns:

        match = pattern.search(message)

        if match:

            invalid_index = int(
                match.group(1)
            )

            qubit_count = int(
                match.group(2)
            )

            return (
                invalid_index,
                qubit_count,
            )

    return None


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

        integer_arguments = []

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

            integer_arguments.append(
                arg.value
            )

        if invalid_index in integer_arguments:

            return (
                gate_name,
                getattr(
                    node,
                    "lineno",
                    None,
                ),
                integer_arguments,
            )

    return None


def _build_qubit_suggestion(
    code,
    line_number,
    invalid_index,
    suggested_qubit,
):
    """
    Build a suggested version of the affected source line.
    """

    if not line_number:
        return code

    lines = code.splitlines()

    index = line_number - 1

    if index < 0 or index >= len(lines):
        return code

    line = lines[index]

    pattern = re.compile(
        r"(?<![\w])"
        + re.escape(str(invalid_index))
        + r"(?![\w])"
    )

    new_line, count = pattern.subn(
        str(suggested_qubit),
        line,
        count=1,
    )

    if count != 1:
        return code

    lines[index] = new_line

    suggested_code = "\n".join(lines)

    if code.endswith("\n"):
        suggested_code += "\n"

    return suggested_code
