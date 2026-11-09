"""Password hashing and login sessions (standard library only)."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .db import db, iso, now_iso

SESSION_DAYS = 7
bearer = HTTPBearer(auto_error=False)      # gives the Authorize button in /docs


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    h = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return salt.hex() + "$" + h.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, h_hex = stored.split("$")
        h = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=2**14, r=8, p=1)
        return hmac.compare_digest(h, bytes.fromhex(h_hex))
    except Exception:
        return False


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(conn, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires = iso(datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS))
    conn.execute("INSERT INTO sessions (token_hash, user_id, created_at, expires_at) VALUES (?,?,?,?)",
                 (_token_hash(token), user_id, now_iso(), expires))
    conn.commit()
    return token


def delete_session(conn, token: str) -> None:
    conn.execute("DELETE FROM sessions WHERE token_hash = ?", (_token_hash(token),))
    conn.commit()


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer), conn=Depends(db)):
    """Returns the logged-in user row, or None if there is no valid token."""
    if creds is None:
        return None
    return conn.execute(
        "SELECT u.id, u.email FROM sessions s JOIN users u ON u.id = s.user_id "
        "WHERE s.token_hash = ? AND s.expires_at > ?",
        (_token_hash(creds.credentials), now_iso())).fetchone()


def require_user(user=Depends(current_user)):
    if user is None:
        raise HTTPException(401, "Please log in.")
    return user