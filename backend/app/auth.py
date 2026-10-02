import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Header, HTTPException

from app.core.supabase import supabase


JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET environment variable is not configured."
    )

JWT_ALGORITHM = "HS256"

TOKEN_DAYS = 7

RESET_TOKEN_MINUTES = 30

EMAIL_VERIFICATION_MINUTES = 10

EMAIL_VERIFICATION_MAX_ATTEMPTS = 5


def init_auth_db():
    """
    Authentication tables are managed in Supabase.

    The tables are created through the Supabase SQL Editor,
    so there is no local SQLite database involved.
    """
    return True


def _hash_password(
    password: str,
    salt: str | None = None,
):
    salt = salt or secrets.token_hex(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        120_000,
    )

    return digest.hex(), salt


def _user(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "created_at": row["created_at"],
    }


def register_user(
    name: str,
    email: str,
    password: str,
):
    email = email.strip().lower()

    password_hash, salt = _hash_password(password)

    created_at = datetime.now(timezone.utc).isoformat()

    try:
        response = (
            supabase
            .table("users")
            .insert(
                {
                    "name": name.strip(),
                    "email": email,
                    "password_hash": password_hash,
                    "salt": salt,
                    "created_at": created_at,
                }
            )
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to create account.",
        )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Unable to create account.",
        )

    return _user(response.data[0])


# ============================================================
# EMAIL VERIFICATION
# ============================================================

def create_email_verification(
    name: str,
    email: str,
    password: str,
):
    """
    Create a temporary email-verification record.

    The actual users table is NOT modified here.

    A six-digit verification code is generated and only
    its SHA-256 hash is stored in Supabase.
    """

    name = name.strip()
    email = email.strip().lower()

    if len(name) < 2:
        raise HTTPException(
            status_code=422,
            detail="Name must contain at least 2 characters.",
        )

    if len(name) > 80:
        raise HTTPException(
            status_code=422,
            detail="Name must not exceed 80 characters.",
        )

    if len(password) < 8:
        raise HTTPException(
            status_code=422,
            detail="Password must contain at least 8 characters.",
        )

    if len(password) > 128:
        raise HTTPException(
            status_code=422,
            detail="Password must not exceed 128 characters.",
        )

    # Check whether an account already exists.
    existing_user = (
        supabase
        .table("users")
        .select("id")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    if existing_user.data:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    # Generate a cryptographically secure six-digit code.
    verification_code = f"{secrets.randbelow(1_000_000):06d}"

    verification_code_hash = hashlib.sha256(
        verification_code.encode("utf-8")
    ).hexdigest()

    # Hash the password now so the plaintext password is
    # never stored in the temporary verification table.
    password_hash, salt = _hash_password(password)

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=EMAIL_VERIFICATION_MINUTES
    )

    # Invalidate previous verification requests for this
    # email by removing them.
    try:
        (
            supabase
            .table("email_verifications")
            .delete()
            .eq("email", email)
            .execute()
        )
    except Exception:
        pass

    try:
        response = (
            supabase
            .table("email_verifications")
            .insert(
                {
                    "name": name,
                    "email": email,
                    "password_hash": password_hash,
                    "salt": salt,
                    "verification_code_hash": verification_code_hash,
                    "expires_at": expires_at.isoformat(),
                    "attempts": 0,
                    "created_at": now.isoformat(),
                }
            )
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to start email verification.",
        )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Unable to start email verification.",
        )

    return {
        "email": email,
        "name": name,
        "verification_code": verification_code,
    }


def verify_email_code(
    email: str,
    verification_code: str,
):
    """
    Verify the six-digit email verification code.

    Only after successful verification is the actual
    users account created.
    """

    email = email.strip().lower()
    verification_code = verification_code.strip()

    if not verification_code.isdigit() or len(verification_code) != 6:
        raise HTTPException(
            status_code=400,
            detail="Enter the 6-digit verification code.",
        )

    response = (
        supabase
        .table("email_verifications")
        .select("*")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=400,
            detail=(
                "No active email verification request was found. "
                "Please request a new verification code."
            ),
        )

    verification = response.data[0]

    # Check attempt limit.
    attempts = verification.get("attempts", 0)

    if attempts >= EMAIL_VERIFICATION_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail=(
                "Too many incorrect verification attempts. "
                "Please request a new verification code."
            ),
        )

    # Check expiration.
    expires_at = datetime.fromisoformat(
        verification["expires_at"].replace(
            "Z",
            "+00:00",
        )
    )

    if datetime.now(timezone.utc) >= expires_at:
        (
            supabase
            .table("email_verifications")
            .delete()
            .eq("id", verification["id"])
            .execute()
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "This verification code has expired. "
                "Please request a new code."
            ),
        )

    # Hash the supplied code and compare it with the stored hash.
    supplied_hash = hashlib.sha256(
        verification_code.encode("utf-8")
    ).hexdigest()

    if not hmac.compare_digest(
        supplied_hash,
        verification["verification_code_hash"],
    ):
        new_attempts = attempts + 1

        try:
            (
                supabase
                .table("email_verifications")
                .update(
                    {
                        "attempts": new_attempts,
                    }
                )
                .eq("id", verification["id"])
                .execute()
            )
        except Exception:
            pass

        remaining = max(
            0,
            EMAIL_VERIFICATION_MAX_ATTEMPTS - new_attempts,
        )

        if remaining == 0:
            raise HTTPException(
                status_code=429,
                detail=(
                    "Too many incorrect verification attempts. "
                    "Please request a new verification code."
                ),
            )

        raise HTTPException(
            status_code=400,
            detail=(
                "Incorrect verification code. "
                f"{remaining} attempt(s) remaining."
            ),
        )

    # Before creating the account, check once more that
    # another account has not appeared for this email.
    existing_user = (
        supabase
        .table("users")
        .select("id")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    if existing_user.data:
        (
            supabase
            .table("email_verifications")
            .delete()
            .eq("id", verification["id"])
            .execute()
        )

        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    # Create the real account only after successful verification.
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        user_response = (
            supabase
            .table("users")
            .insert(
                {
                    "name": verification["name"],
                    "email": verification["email"],
                    "password_hash": verification["password_hash"],
                    "salt": verification["salt"],
                    "created_at": created_at,
                }
            )
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to create your account.",
        )

    if not user_response.data:
        raise HTTPException(
            status_code=500,
            detail="Unable to create your account.",
        )

    # Verification is complete, so remove the temporary record.
    try:
        (
            supabase
            .table("email_verifications")
            .delete()
            .eq("id", verification["id"])
            .execute()
        )
    except Exception:
        pass

    return _user(user_response.data[0])


def authenticate(
    email: str,
    password: str,
):
    email = email.strip().lower()

    response = (
        supabase
        .table("users")
        .select("*")
        .eq("email", email)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    row = response.data[0]

    # Google-created accounts do not have a local password.
    if not row.get("password_hash") or not row.get("salt"):
        raise HTTPException(
            status_code=401,
            detail=(
                "This account uses Google Sign-In. "
                "Please continue with Google."
            ),
        )

    candidate, _ = _hash_password(
        password,
        row["salt"],
    )

    if not hmac.compare_digest(
        candidate,
        row["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    return _user(row)


def update_user_name(
    user_id: int,
    new_name: str,
):
    new_name = new_name.strip()

    if len(new_name) < 2:
        raise HTTPException(
            status_code=422,
            detail="Name must contain at least 2 characters.",
        )

    if len(new_name) > 80:
        raise HTTPException(
            status_code=422,
            detail="Name must not exceed 80 characters.",
        )

    try:
        response = (
            supabase
            .table("users")
            .update(
                {
                    "name": new_name,
                }
            )
            .eq("id", user_id)
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to update your name.",
        )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Unable to update your name.",
        )

    return _user(response.data[0])


def change_password(
    user_id: int,
    current_password: str,
    new_password: str,
):
    if len(new_password) < 8:
        raise HTTPException(
            status_code=422,
            detail="New password must contain at least 8 characters.",
        )

    if len(new_password) > 128:
        raise HTTPException(
            status_code=422,
            detail="New password must not exceed 128 characters.",
        )

    if current_password == new_password:
        raise HTTPException(
            status_code=400,
            detail="New password must be different from your current password.",
        )

    try:
        response = (
            supabase
            .table("users")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to verify your account.",
        )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="User account not found.",
        )

    row = response.data[0]

    # Google-created accounts do not have a local password.
    if not row.get("password_hash") or not row.get("salt"):
        raise HTTPException(
            status_code=400,
            detail=(
                "This account uses Google Sign-In and does not "
                "have a password to change."
            ),
        )

    current_hash, _ = _hash_password(
        current_password,
        row["salt"],
    )

    if not hmac.compare_digest(
        current_hash,
        row["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect.",
        )

    new_hash, new_salt = _hash_password(
        new_password
    )

    try:
        update_response = (
            supabase
            .table("users")
            .update(
                {
                    "password_hash": new_hash,
                    "salt": new_salt,
                }
            )
            .eq("id", user_id)
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to change password.",
        )

    if not update_response.data:
        raise HTTPException(
            status_code=500,
            detail="Unable to change password.",
        )

    # Invalidate any outstanding password-reset links
    # after a successful password change.
    try:
        (
            supabase
            .table("password_resets")
            .update({"used": True})
            .eq("user_id", user_id)
            .eq("used", False)
            .execute()
        )
    except Exception:
        pass

    return True


def create_token(user):
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user["id"]),
        "email": user["email"],
        "exp": now + timedelta(days=TOKEN_DAYS),
    }

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def create_password_reset_token(user_id: int):
    raw_token = secrets.token_urlsafe(32)

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=RESET_TOKEN_MINUTES
    )

    # Disable previous unused reset tokens.
    (
        supabase
        .table("password_resets")
        .update({"used": True})
        .eq("user_id", user_id)
        .eq("used", False)
        .execute()
    )

    response = (
        supabase
        .table("password_resets")
        .insert(
            {
                "user_id": user_id,
                "token_hash": token_hash,
                "expires_at": expires_at.isoformat(),
                "used": False,
                "created_at": now.isoformat(),
            }
        )
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Unable to create password reset token.",
        )

    return raw_token


def reset_password(
    token: str,
    new_password: str,
):
    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    response = (
        supabase
        .table("password_resets")
        .select("*")
        .eq("token_hash", token_hash)
        .eq("used", False)
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired password reset link.",
        )

    row = response.data[0]

    expires_at = datetime.fromisoformat(
        row["expires_at"].replace("Z", "+00:00")
    )

    if datetime.now(timezone.utc) >= expires_at:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired password reset link.",
        )

    password_hash, salt = _hash_password(
        new_password
    )

    user_response = (
        supabase
        .table("users")
        .update(
            {
                "password_hash": password_hash,
                "salt": salt,
            }
        )
        .eq("id", row["user_id"])
        .execute()
    )

    if not user_response.data:
        raise HTTPException(
            status_code=500,
            detail="Unable to reset password.",
        )

    (
        supabase
        .table("password_resets")
        .update({"used": True})
        .eq("id", row["id"])
        .execute()
    )

    return True


def current_user(
    authorization: str | None = Header(default=None),
):
    if (
        not authorization
        or not authorization.lower().startswith("bearer ")
    ):
        raise HTTPException(
            status_code=401,
            detail="Authentication required.",
        )

    token = authorization.split(
        " ",
        1,
    )[1].strip()

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token.",
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token.",
        )

    response = (
        supabase
        .table("users")
        .select("*")
        .eq("id", int(user_id))
        .limit(1)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=401,
            detail="User account not found.",
        )

    return _user(response.data[0])


def delete_user_account(
    user_id: int,
    password: str,
):
    """
    Permanently delete a user's account.

    The current password must be verified before deletion.
    Google-created accounts cannot use this password-based
    deletion flow because they do not have a local password.
    """

    try:
        response = (
            supabase
            .table("users")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to verify your account.",
        )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="User account not found.",
        )

    row = response.data[0]

    # Google-created accounts do not have a local password.
    if not row.get("password_hash") or not row.get("salt"):
        raise HTTPException(
            status_code=400,
            detail=(
                "This account uses Google Sign-In and does not "
                "have a password. Account deletion through "
                "password verification is not available."
            ),
        )

    # Verify the current password.
    current_hash, _ = _hash_password(
        password,
        row["salt"],
    )

    if not hmac.compare_digest(
        current_hash,
        row["password_hash"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password.",
        )

    # Delete password-reset records first because they
    # reference the users table.
    try:
        (
            supabase
            .table("password_resets")
            .delete()
            .eq("user_id", user_id)
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to remove account recovery data.",
        )

    # Delete the user account.
    try:
        delete_response = (
            supabase
            .table("users")
            .delete()
            .eq("id", user_id)
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete your account.",
        )

    if not delete_response.data:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete your account.",
        )

    return True

def admin_user(
    authorization: str | None = Header(default=None),
):
    user = current_user(authorization)

    admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()

    if not admin_email:
        raise HTTPException(
            status_code=500,
            detail="Admin account is not configured.",
        )

    if user["email"].strip().lower() != admin_email:
        raise HTTPException(
            status_code=403,
            detail="Administrator access required.",
        )

    return user
