def classify(message):
    m = (message or "").lower()
    if "syntax" in m or "invalid syntax" in m:
        return "SYNTAX_ERROR"
    if "index" in m or "qubit" in m:
        return "QUBIT_INDEX_ERROR"
    if "parameter" in m:
        return "PARAMETER_ERROR"
    return "GENERAL_ERROR"
