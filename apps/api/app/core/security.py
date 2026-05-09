from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from fastapi import Cookie, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db, set_db_current_user
from app.core.errors import AppError
from app.modules.auth.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def _jwt_secret() -> str:
    secret = get_settings().jwt_secret
    if secret is None:
        raise AppError("CONFIG_MISSING_SECRET", "JWT_SECRET no está configurado.", 500)
    return secret.get_secret_value()


def create_access_token(user: User, session_id: UUID) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user.id),
        "session_id": str(session_id),
        "token_version": user.token_version,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[get_settings().jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise AppError("AUTH_TOKEN_EXPIRED", "Tu sesión expiró.", 401) from exc
    except jwt.InvalidTokenError as exc:
        raise AppError("AUTH_INVALID_TOKEN", "Token inválido.", 401) from exc
    if payload.get("type") != "access":
        raise AppError("AUTH_INVALID_TOKEN", "Token inválido.", 401)
    return payload


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = token or access_token
    if token is None:
        raise AppError("AUTH_REQUIRED", "Autenticacion requerida.", 401)
    payload = decode_access_token(token)
    user = db.get(User, UUID(payload["sub"]))
    if user is None or user.status != "active":
        raise AppError("AUTH_INVALID_TOKEN", "Token inválido.", 401)
    if user.token_version != payload.get("token_version"):
        raise AppError("AUTH_TOKEN_EXPIRED", "Tu sesión expiró.", 401)
    set_db_current_user(db, str(user.id))
    return user
