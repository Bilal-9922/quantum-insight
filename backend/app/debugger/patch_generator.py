def generate_patch(code, error=None):
    return {
        "fixed_code": code,
        "changed": False,
        "note": "MVP patch generator does not rewrite code automatically without a verified, isolated execution environment."
    }
