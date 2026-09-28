def diagnose(code, error=None):
    if error:
        msg = str(error)
        return {
            "diagnosis": f"Review the reported error: {msg}",
            "suggestions": [
                "Check the referenced qubit index and circuit size.",
                "Validate gate arguments and parameter values.",
                "Run the corrected code through a sandbox before trusting it."
            ]
        }
    return {
        "diagnosis": "No runtime error was supplied. Static syntax and circuit validation can still be performed.",
        "suggestions": ["Analyze the circuit metrics and run the optimizer."]
    }
