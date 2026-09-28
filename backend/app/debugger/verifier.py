from app.circuit.validator import validate_python

def verify(code):
    syntax = validate_python(code)
    return {"verified": syntax["valid"], "syntax": syntax}
