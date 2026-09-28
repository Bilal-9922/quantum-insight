from fastapi import APIRouter
from pydantic import BaseModel
from app.debugger.ast_analyzer import analyze_ast
from app.debugger.classifier import classify
from app.debugger.ai_debugger import diagnose
from app.debugger.patch_generator import generate_patch
from app.debugger.verifier import verify

router = APIRouter(tags=["debugger"])

class DebugRequest(BaseModel):
    code: str
    error: str | None = None
    language: str = "python"

@router.post("/debug")
def debug(req: DebugRequest):
    ast_result = analyze_ast(req.code)
    error_type = classify(req.error)
    diagnosis = diagnose(req.code, req.error)
    patch = generate_patch(req.code, req.error)
    verification = verify(patch["fixed_code"])
    return {
        "success": True,
        "ast": ast_result,
        "error": {"type": error_type, "message": req.error},
        **diagnosis,
        **patch,
        **verification,
    }
