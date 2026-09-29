import ast

def validate_python(code: str):
    try:
        ast.parse(code)
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {
            "valid": False,
            "error": {"type": "SyntaxError", "line": e.lineno, "message": e.msg}
        }
