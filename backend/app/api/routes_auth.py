import os
import re

import resend
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.auth import (
    authenticate,
    create_password_reset_token,
    create_token,
    current_user,
    init_auth_db,
    register_user,
    reset_password,
)

router = APIRouter(tags=["authentication"])
init_auth_db()

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)

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

@router.post("/auth/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    email = req.email.strip().lower()

    import sqlite3
    from app.auth import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    user = conn.execute(
        "SELECT * FROM users WHERE email=?",
        (email,),
    ).fetchone()
    conn.close()

    # Always return the same response so attackers cannot
    # discover whether an email is registered.
    if not user:
        return {
            "success": True,
            "message": "If an account exists for this email, a reset link has been sent.",
        }

    token = create_password_reset_token(user["id"])

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000",
    ).rstrip("/")

    reset_url = f"{frontend_url}/reset-password?token={token}"

    resend.api_key = os.getenv("RESEND_API_KEY")

    if not resend.api_key:
        raise HTTPException(
            status_code=500,
            detail="Email service is not configured.",
        )

       try:
        resend.Emails.send(
            {
                "from": "QuantumInsight <onboarding@resend.dev>",
                "to": [user["email"]],
                "subject": "Reset your QuantumInsight password",
                "html": f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
                    <h2>Reset your QuantumInsight password</h2>

                    <p>Hello {user["name"]},</p>

                    <p>
                        We received a request to reset your QuantumInsight password.
                    </p>

                    <p>
                        <a
                            href="{reset_url}"
                            style="
                                display:inline-block;
                                padding:12px 20px;
                                background:#2563eb;
                                color:white;
                                text-decoration:none;
                                border-radius:8px;
                            "
                        >
                            Reset Password
                        </a>
                    </p>

                    <p>
                        This link expires in 30 minutes and can only be used once.
                    </p>

                    <p>
                        If you did not request this, you can safely ignore this email.
                    </p>

                    <p>— QuantumInsight</p>
                </div>
                """ ,
            }
        )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send password reset email: {str(e)}",
            )
        return {
            "success": True,
            "message": "If an account exists for this email, a reset link has been sent.",
        }

@router.post("/auth/reset-password")
def reset_password_endpoint(req: ResetPasswordRequest):
    reset_password(req.token, req.password)

    return {
        "success": True,
        "message": "Password reset successfully. You can now sign in.",
    }
