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
    raise RuntimeError("JWT_SECRET environment variable is not configured.")

JWT_ALGORITHM = "HS256"
TOKEN_DAYS = 7
RESET_TOKEN_MINUTES = 30


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

    # Disable previous unused reset tokens
    supabase \
        .table("password_resets") \
        .update({"used": True}) \
        .eq("user_id", user_id) \
        .eq("used", False) \
        .execute()

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
