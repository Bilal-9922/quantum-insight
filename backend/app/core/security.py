def sanitize_code_input(code: str, max_chars: int = 50000) -> str:
    if not isinstance(code, str):
        raise ValueError("Code must be a string.")
    if len(code) > max_chars:
        raise ValueError(f"Code exceeds the {max_chars} character limit.")
    return code
