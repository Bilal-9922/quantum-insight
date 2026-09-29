import hashlib
import hmac
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from fastapi import Header, HTTPException

DB_PATH = Path(os.getenv("AUTH_DB_PATH", "./quantuminsight.db"))
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-secret-in-production")
JWT_ALGORITHM = "HS256"
TOKEN_DAYS = 7
RESET_TOKEN_MINUTES = 30


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db():
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL UNIQUE,
            expires_at TEXT NOT NULL,
            used INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()


def _hash_password(password: str, salt: str | None = None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 120_000)
    return digest.hex(), salt


def _user(row):
    return {"id": row["id"], "name": row["name"], "email": row["email"], "created_at": row["created_at"]}


def register_user(name: str, email: str, password: str):
    email = email.strip().lower()
    password_hash, salt = _hash_password(password)
    created_at = datetime.now(timezone.utc).isoformat()
    conn = _connect()
    try:
        cur = conn.execute(
            "INSERT INTO users(name,email,password_hash,salt,created_at) VALUES(?,?,?,?,?)",
            (name.strip(), email, password_hash, salt, created_at),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id=?", (cur.lastrowid,)).fetchone()
        return _user(row)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    finally:
        conn.close()


def authenticate(email: str, password: str):
    conn = _connect()
    row = conn.execute("SELECT * FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    candidate, _ = _hash_password(password, row["salt"])
    if not hmac.compare_digest(candidate, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return _user(row)


def create_token(user):
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user["id"]), "email": user["email"], "exp": now + timedelta(days=TOKEN_DAYS)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_password_reset_token(user_id: int):
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=RESET_TOKEN_MINUTES)

    conn = _connect()
    conn.execute(
        "UPDATE password_resets SET used=1 WHERE user_id=? AND used=0",
        (user_id,),
    )
    conn.execute(
        """
        INSERT INTO password_resets
        (user_id, token_hash, expires_at, used, created_at)
        VALUES (?, ?, ?, 0, ?)
        """,
        (
            user_id,
            token_hash,
            expires_at.isoformat(),
            now.isoformat(),
        ),
    )
    conn.commit()
    conn.close()

    return raw_token


def reset_password(token: str, new_password: str):
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    conn = _connect()
    row = conn.execute(
        """
        SELECT *
        FROM password_resets
        WHERE token_hash=?
          AND used=0
        """,
        (token_hash,),
    ).fetchone()

    if not row:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired password reset link.",
        )

    expires_at = datetime.fromisoformat(row["expires_at"])

    if datetime.now(timezone.utc) >= expires_at:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired password reset link.",
        )

    password_hash, salt = _hash_password(new_password)

    conn.execute(
        """
        UPDATE users
        SET password_hash=?, salt=?
        WHERE id=?
        """,
        (password_hash, salt, row["user_id"]),
    )

    conn.execute(
        """
        UPDATE password_resets
        SET used=1
        WHERE id=?
        """,
        (row["id"],),
    )

    conn.commit()
    conn.close()

    return True


def current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Authentication required.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    conn = _connect()
    row = conn.execute("SELECT * FROM users WHERE id=?", (payload.get("sub"),)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="User account not found.")
    return _user(row)
