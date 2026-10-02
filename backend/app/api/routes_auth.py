import os
import re

import resend
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import (
    authenticate,
    change_password,
    create_password_reset_token,
    create_token,
    current_user,
    delete_user_account,
    init_auth_db,
    register_user,
    reset_password,
    update_user_name,
)
from app.core.supabase import supabase


router = APIRouter(tags=["authentication"])

init_auth_db()


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleLoginRequest(BaseModel):
    access_token: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)


class ChangeNameRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(
        min_length=1,
        max_length=128,
    )
    new_password: str = Field(
        min_length=8,
        max_length=128,
    )

class DeleteAccountRequest(BaseModel):
    password: str = Field(
        min_length=1,
        max_length=128,
    )


@router.post("/auth/register")
def register(req: RegisterRequest):
    if not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        req.email.strip(),
    ):
        raise HTTPException(
            status_code=422,
            detail="Enter a valid email address.",
        )

    user = register_user(
        req.name,
        req.email,
        req.password,
    )

    return {
        "user": user,
        "token": create_token(user),
    }


@router.post("/auth/login")
def login(req: LoginRequest):
    user = authenticate(
        req.email,
        req.password,
    )

    return {
        "user": user,
        "token": create_token(user),
    }


@router.get("/auth/me")
def me(user=Depends(current_user)):
    return {
        "user": user,
    }


@router.post("/auth/google")
def google_login(req: GoogleLoginRequest):
    try:
        google_response = supabase.auth.get_user(
            req.access_token
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google authentication.",
        )

    if not google_response or not google_response.user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google authentication.",
        )

    google_user = google_response.user

    email = (
        google_user.email or ""
    ).strip().lower()

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Google account does not have an email address.",
        )

    metadata = google_user.user_metadata or {}

    name = (
        metadata.get("full_name")
        or metadata.get("name")
        or email.split("@")[0]
    ).strip()

    response = (
        supabase
        .table("users")
        .select("*")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    if response.data:
        user = response.data[0]
    else:
        response = (
            supabase
            .table("users")
            .insert(
                {
                    "name": name,
                    "email": email,
                    "password_hash": "",
                    "salt": "",
                }
            )
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Unable to create Google account.",
            )

        user = response.data[0]

    user = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "created_at": user["created_at"],
    }

    return {
        "user": user,
        "token": create_token(user),
    }


@router.put("/auth/profile/name")
def change_name(
    req: ChangeNameRequest,
    user=Depends(current_user),
):
    updated_user = update_user_name(
        user["id"],
        req.name,
    )

    return {
        "success": True,
        "message": "Name updated successfully.",
        "user": updated_user,
    }


@router.put("/auth/profile/password")
def change_user_password(
    req: ChangePasswordRequest,
    user=Depends(current_user),
):
    change_password(
        user["id"],
        req.current_password,
        req.new_password,
    )

    return {
        "success": True,
        "message": "Password changed successfully.",
    }

@router.delete("/auth/account")
def delete_account(
    req: DeleteAccountRequest,
    user=Depends(current_user),
):
    delete_user_account(
        user["id"],
        req.password,
    )

    return {
        "success": True,
        "message": "Your QuantumInsight account has been permanently deleted.",
    }


@router.post("/auth/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    email = req.email.strip().lower()

    response = (
        supabase
        .table("users")
        .select("id, name, email")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    # Always return the same response so attackers cannot
    # discover whether an email is registered.
    if not response.data:
        return {
            "success": True,
            "message": (
                "If an account exists for this email, "
                "a reset link has been sent."
            ),
        }

    user = response.data[0]

    token = create_password_reset_token(
        user["id"]
    )

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000",
    ).rstrip("/")

    reset_url = (
        f"{frontend_url}/reset-password?token={token}"
    )

    resend.api_key = os.getenv(
        "RESEND_API_KEY"
    )

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
                        We received a request to reset your
                        QuantumInsight password.
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
                        This link expires in 30 minutes and can
                        only be used once.
                    </p>

                    <p>
                        If you did not request this, you can
                        safely ignore this email.
                    </p>

                    <p>— QuantumInsight</p>
                </div>
                """,
            }
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to send password reset email.",
        )

    return {
        "success": True,
        "message": (
            "If an account exists for this email, "
            "a reset link has been sent."
        ),
    }


@router.post("/auth/reset-password")
def reset_password_endpoint(
    req: ResetPasswordRequest,
):
    reset_password(
        req.token,
        req.password,
    )

    return {
        "success": True,
        "message": (
            "Password reset successfully. "
            "You can now sign in."
        ),
    }
