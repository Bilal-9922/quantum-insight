def parse_error(error):
    if not error:
        return None
    text = str(error)
    if "index" in text.lower() and "qubit" in text.lower():
        kind = "QUBIT_INDEX_ERROR"
    elif "syntax" in text.lower():
        kind = "SYNTAX_ERROR"
    else:
        kind = "GENERAL_ERROR"
    return {"type": kind, "message": text}
