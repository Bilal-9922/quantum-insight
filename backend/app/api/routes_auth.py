import re
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from app.auth import authenticate, create_token, current_user, init_auth_db, register_user

router = APIRouter(tags=["authentication"])
init_auth_db()

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/auth/register")
def register(req: RegisterRequest):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", req.email.strip()):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    user = register_user(req.name, req.email, req.password)
    return {"user": user, "token": create_token(user)}

@router.post("/auth/login")
def login(req: LoginRequest):
    user = authenticate(req.email, req.password)
    return {"user": user, "token": create_token(user)}

@router.get("/auth/me")
def me(user=Depends(current_user)):
    return {"user": user}
