import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel

from .. import auth
from ..db import db, now_iso

router = APIRouter(prefix="/api/auth", tags=["auth"])
_DUMMY_HASH = auth.hash_password("dummy-password")      # keeps login timing similar for unknown emails


class Credentials(BaseModel):
    email: str
    password: str


def _clean_email(email: str) -> str:
    e = email.strip().lower()
    if len(e) > 254 or " " in e or "@" not in e or e.startswith("@") or e.endswith("@"):
        raise HTTPException(422, "Please enter a valid email address.")
    return e


@router.post("/register")
def register(body: Credentials, conn=Depends(db)):
    email = _clean_email(body.email)
    if not 8 <= len(body.password) <= 128:
        raise HTTPException(422, "The password must be 8 to 128 characters long.")
    try:
        cur = conn.execute("INSERT INTO users (email, password_hash, created_at) VALUES (?,?,?)",
                           (email, auth.hash_password(body.password), now_iso()))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(409, "An account with this email already exists.")
    return {"access_token": auth.create_session(conn, cur.lastrowid), "token_type": "bearer", "email": email}


@router.post("/login")
def login(body: Credentials, conn=Depends(db)):
    row = conn.execute("SELECT id, email, password_hash FROM users WHERE email = ?",
                       (body.email.strip().lower(),)).fetchone()
    ok = auth.verify_password(body.password, row["password_hash"] if row else _DUMMY_HASH)
    if not row or not ok:
        raise HTTPException(401, "Incorrect email or password.")
    return {"access_token": auth.create_session(conn, row["id"]), "token_type": "bearer", "email": row["email"]}


@router.post("/logout")
def logout(creds: HTTPAuthorizationCredentials | None = Depends(auth.bearer), conn=Depends(db)):
    if creds:
        auth.delete_session(conn, creds.credentials)
    return {"status": "logged out"}


@router.get("/me")
def me(user=Depends(auth.require_user)):
    return {"id": user["id"], "email": user["email"]}