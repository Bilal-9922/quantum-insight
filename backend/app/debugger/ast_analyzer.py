import ast

def analyze_ast(code):
    try:
        tree = ast.parse(code)
        imports = [n.names[0].name for n in ast.walk(tree) if isinstance(n, ast.Import) and n.names]
        return {"valid": True, "imports": imports, "nodes": len(list(ast.walk(tree)))}
    except SyntaxError as e:
        return {"valid": False, "error": {"line": e.lineno, "message": e.msg}}
