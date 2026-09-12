import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import HTTPException, status

from app.config import get_settings

_ALGORITHM = "HS256"
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters")
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
    encode = lambda value: base64.urlsafe_b64encode(value).decode().rstrip("=")
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${encode(salt)}${encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, n, r, p, salt_text, digest_text = encoded.split("$")
        if scheme != "scrypt":
            return False
        decode = lambda value: base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        expected = decode(digest_text)
        actual = hashlib.scrypt(password.encode(), salt=decode(salt_text), n=int(n), r=int(r), p=int(p))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_token(subject: str, roles: list[str], token_type: str, lifetime: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "roles": roles,
        "type": token_type,
        "iat": now,
        "exp": now + lifetime,
    }
    return jwt.encode(payload, get_settings().jwt_secret, algorithm=_ALGORITHM)


def create_access_token(subject: str, roles: list[str]) -> str:
    return create_token(subject, roles, "access", timedelta(minutes=get_settings().jwt_access_minutes))


def create_refresh_token(subject: str, roles: list[str]) -> str:
    return create_token(subject, roles, "refresh", timedelta(days=get_settings().jwt_refresh_days))


def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "INVALID_TOKEN", "message": "Token is invalid or expired"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, get_settings().jwt_secret, algorithms=[_ALGORITHM])
        if payload.get("type") != expected_type or not payload.get("sub"):
            raise credentials_error
        return payload
    except jwt.PyJWTError as error:
        raise credentials_error from error
