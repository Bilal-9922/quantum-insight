import os
import re
from html import escape

import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth import (
    admin_user,
    authenticate,
    change_password,
    create_email_verification,
    create_password_reset_token,
    create_token,
    current_user,
    delete_user_account,
    init_auth_db,
    reset_password,
    update_user_name,
    verify_email_code,
)

from app.core.supabase import supabase


router = APIRouter(tags=["authentication"])

init_auth_db()


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str
    password: str = Field(min_length=8, max_length=128)


class VerifyEmailRequest(BaseModel):
    email: str
    code: str = Field(min_length=6, max_length=6)


class LoginRequest(BaseModel):
    email: str
    password: str


class GoogleLoginRequest(BaseModel):
    access_token: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class ChangeNameRequest(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=80,
    )


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


def send_verification_email(
    name: str,
    email: str,
    verification_code: str,
):
    brevo_api_key = os.getenv("BREVO_API_KEY")

    if not brevo_api_key:
        raise HTTPException(
            status_code=500,
            detail="Email service is not configured.",
        )

    safe_name = escape(name)
    safe_code = escape(verification_code)

    email_payload = {
        "sender": {
            "name": "QuantumInsight",
            "email": "bilalshaikh1339@gmail.com",
        },
        "to": [
            {
                "email": email,
                "name": name,
            }
        ],
        "subject": "Verify your QuantumInsight account",
        "htmlContent": f"""
        <div style="
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 40px auto;
            padding: 30px;
            background: #ffffff;
            color: #1e293b;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        ">

            <h2 style="
                margin-top: 0;
                color: #0f172a;
            ">
                Verify your QuantumInsight account
            </h2>

            <p>
                Hello {safe_name},
            </p>

            <p>
                Thank you for creating a QuantumInsight account.
                Please verify your email address using the
                verification code below.
            </p>

            <div style="
                margin: 30px 0;
                padding: 20px;
                background: #f1f5f9;
                border-radius: 10px;
                text-align: center;
            ">
                <div style="
                    font-size: 14px;
                    color: #64748b;
                    margin-bottom: 10px;
                ">
                    Your verification code
                </div>

                <div style="
                    font-size: 32px;
                    font-weight: 700;
                    letter-spacing: 8px;
                    color: #2563eb;
                ">
                    {safe_code}
                </div>
            </div>

            <p>
                This verification code expires in
                <strong>10 minutes</strong>.
            </p>

            <p>
                If you did not create a QuantumInsight account,
                you can safely ignore this email.
            </p>

            <p style="
                margin-top: 30px;
                color: #64748b;
            ">
                — QuantumInsight
            </p>

        </div>
        """,
    }

    try:
        email_response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "accept": "application/json",
                "api-key": brevo_api_key,
                "content-type": "application/json",
            },
            json=email_payload,
            timeout=15,
        )

        if email_response.status_code >= 400:
            raise RuntimeError(
                f"Brevo API error: {email_response.text}"
            )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to send verification email.",
        )


@router.post("/auth/register")
def register(req: RegisterRequest):
    email = req.email.strip().lower()

    if not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email,
    ):
        raise HTTPException(
            status_code=422,
            detail="Enter a valid email address.",
        )

    verification = create_email_verification(
        req.name,
        email,
        req.password,
    )

    send_verification_email(
        verification["name"],
        verification["email"],
        verification["verification_code"],
    )

    return {
        "success": True,
        "verification_required": True,
        "email": verification["email"],
        "message": (
            "A verification code has been sent to your email address."
        ),
    }


@router.post("/auth/verify-email")
def verify_email(req: VerifyEmailRequest):
    email = req.email.strip().lower()

    if not re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        email,
    ):
        raise HTTPException(
            status_code=422,
            detail="Enter a valid email address.",
        )

    if not re.fullmatch(r"\d{6}", req.code):
        raise HTTPException(
            status_code=422,
            detail="Verification code must contain 6 digits.",
        )

    user = verify_email_code(
        email,
        req.code,
    )

    return {
        "success": True,
        "user": user,
        "token": create_token(user),
        "message": (
            "Email verified successfully. "
            "Your QuantumInsight account has been created."
        ),
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
        "message": (
            "Your QuantumInsight account has been permanently deleted."
        ),
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

    # Create a secure, single-use password reset token.
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

    # Brevo API key from Render environment variables.
    brevo_api_key = os.getenv("BREVO_API_KEY")

    if not brevo_api_key:
        raise HTTPException(
            status_code=500,
            detail="Email service is not configured.",
        )

    email_payload = {
        "sender": {
            "name": "QuantumInsight",
            "email": "bilalshaikh1339@gmail.com",
        },
        "to": [
            {
                "email": user["email"],
                "name": user["name"],
            }
        ],
        "subject": "Reset your QuantumInsight password",
        "htmlContent": f"""
        <div style="
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 40px auto;
            padding: 30px;
            background: #ffffff;
            color: #1e293b;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
        ">

            <h2 style="
                margin-top: 0;
                color: #0f172a;
            ">
                Reset your QuantumInsight password
            </h2>

            <p>
                Hello {escape(user["name"])},
            </p>

            <p>
                We received a request to reset your
                QuantumInsight password.
            </p>

            <p>
                Click the button below to create a new password:
            </p>

            <p style="margin: 30px 0;">
                <a
                    href="{reset_url}"
                    style="
                        display: inline-block;
                        padding: 12px 22px;
                        background: #2563eb;
                        color: #ffffff;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: 600;
                    "
                >
                    Reset Password
                </a>
            </p>

            <p>
                This password-reset link expires in
                <strong>30 minutes</strong> and can only
                be used once.
            </p>

            <p>
                If you did not request this password reset,
                you can safely ignore this email.
            </p>

            <p style="
                margin-top: 30px;
                color: #64748b;
            ">
                — QuantumInsight
            </p>

        </div>
        """,
    }

    try:
        email_response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "accept": "application/json",
                "api-key": brevo_api_key,
                "content-type": "application/json",
            },
            json=email_payload,
            timeout=15,
        )

        if email_response.status_code >= 400:
            raise RuntimeError(
                f"Brevo API error: {email_response.text}"
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

@router.get("/admin/users")
def admin_users(
    user=Depends(admin_user),
):
    response = (
        supabase
        .table("users")
        .select("id, name, email, created_at")
        .order("created_at", desc=True)
        .execute()
    )

    return {
        "success": True,
        "users": response.data or [],
    }   
