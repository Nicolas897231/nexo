from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.errors import AppError
from app.core.responses import ok
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from app.modules.auth.service import AuthService

router = APIRouter()


def _client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.client.host if request.client else None


def _set_session_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    settings = get_settings()
    cookie_options = {
        "httponly": True,
        "secure": settings.session_cookie_secure,
        "samesite": settings.session_cookie_samesite,
        "domain": settings.session_cookie_domain,
        "path": "/",
    }
    response.set_cookie(
        "access_token",
        access_token,
        max_age=settings.access_token_expire_minutes * 60,
        **cookie_options,
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        **cookie_options,
    )


def _clear_session_cookies(response: Response) -> None:
    settings = get_settings()
    for name in ("access_token", "refresh_token"):
        response.delete_cookie(
            name,
            path="/",
            domain=settings.session_cookie_domain,
            secure=settings.session_cookie_secure,
            samesite=settings.session_cookie_samesite,
        )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService(db).register(payload)
    return ok(
        {
            "user_id": str(user.id),
            "status": "created",
            "next_step": "onboarding",
        }
    )


@router.post("/login")
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    user, access_token, refresh_token = AuthService(db).login(
        payload,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    settings = get_settings()
    _set_session_cookies(response, access_token, refresh_token)
    return ok(
        {
            "access_status": "authenticated",
            "user": {"id": str(user.id), "email": user.email},
            "tokens": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.access_token_expire_minutes * 60,
            },
        }
    )


@router.post("/refresh")
def refresh(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
    refresh_cookie: str | None = Cookie(default=None, alias="refresh_token"),
    db: Session = Depends(get_db),
):
    raw_refresh_token = payload.refresh_token if payload else refresh_cookie
    if raw_refresh_token is None:
        raise AppError("AUTH_INVALID_TOKEN", "Token invalido.", 401)
    _, access_token, refresh_token = AuthService(db).refresh(
        raw_refresh_token,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
    )
    settings = get_settings()
    _set_session_cookies(response, access_token, refresh_token)
    return ok(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }
    )


@router.post("/logout")
def logout(
    response: Response,
    payload: LogoutRequest | None = None,
    refresh_cookie: str | None = Cookie(default=None, alias="refresh_token"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    AuthService(db).logout(payload.refresh_token if payload else refresh_cookie)
    _clear_session_cookies(response)
    return ok({"status": "logged_out"})


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    AuthService(db).request_password_reset(str(payload.email))
    return ok({"status": "accepted"})


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    AuthService(db).reset_password(payload)
    return ok({"status": "password_updated"})


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    AuthService(db).change_password(current_user, payload)
    return ok({"status": "password_updated"})


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return ok(
        {
            "id": str(current_user.id),
            "email": current_user.email,
            "status": current_user.status,
        }
    )
