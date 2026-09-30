import re


def generate_patch(code, error=None):
    """
    Generate a safe deterministic patch for simple
    Qiskit qubit-index errors.

    The generator only changes code when the offending
    qubit index can be identified with high confidence.
    """

    original_code = code or ""
    message = str(error or "").strip()
    text = message.lower()

    # Only attempt an automatic patch for a detected
    # qubit-index error.
    is_qubit_error = (
        "index out of range" in text
        or "out of range for size" in text
        or "invalid qubit index" in text
        or "qubit index" in text
    )

    if not is_qubit_error:
        return {
            "fixed_code": original_code,
            "changed": False,
            "note": (
                "No safe automatic patch was generated. "
                "The debugger only rewrites code when the "
                "required correction can be identified reliably."
            ),
        }

    # Extract the invalid qubit index and circuit size
    # from our runner's error message.
    match = re.search(
        r"Qubit index\s+(-?\d+)\s+is out of range\s+"
        r"for a circuit with\s+(\d+)\s+qubit",
        message,
        re.IGNORECASE,
    )

    if not match:
        return {
            "fixed_code": original_code,
            "changed": False,
            "note": (
                "A qubit-index error was detected, but the "
                "invalid index could not be identified safely."
            ),
        }

    invalid_index = int(match.group(1))
    qubit_count = int(match.group(2))

    # We only handle the common case where a gate directly
    # contains the invalid integer index.
    pattern = re.compile(
        rf"(?P<prefix>\b(?:qc|circuit)\."
        rf"[A-Za-z_][A-Za-z0-9_]*\("
        rf"[^()\n]*?)"
        rf"\b{re.escape(str(invalid_index))}\b"
        rf"(?P<suffix>[^()\n]*\))"
    )

    replacement = f"0"

    fixed_code, replacements = pattern.subn(
        rf"\g<prefix>{replacement}\g<suffix>",
        original_code,
        count=1,
    )

    if replacements == 0:
        return {
            "fixed_code": original_code,
            "changed": False,
            "note": (
                f"Qubit index {invalid_index} is invalid for a "
                f"{qubit_count}-qubit circuit, but the debugger "
                "could not safely identify the exact gate argument "
                "to modify."
            ),
        }

    return {
        "fixed_code": fixed_code,
        "changed": True,
        "note": (
            f"Replaced invalid qubit index {invalid_index} with "
            "qubit 0. The circuit should be re-verified before use."
        ),
    }
