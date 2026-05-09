import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import set_db_current_user
from app.core.errors import AppError
from app.core.security import create_access_token
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import (
    PasswordResetToken,
    RefreshToken,
    User,
    UserPreference,
    UserProfile,
)
from app.modules.auth.passwords import hash_password, verify_password
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuthRepository(db)

    def register(self, payload: RegisterRequest) -> User:
        email = payload.email.lower()
        if self.repo.get_user_by_email(email):
            raise AppError("AUTH_EMAIL_UNAVAILABLE", "No fue posible crear la cuenta.", 409)
        first_name, last_name = self._split_name(payload.full_name)
        user = User(email=email, password_hash=hash_password(payload.password), status="active")
        self.db.add(user)
        self.db.flush()
        set_db_current_user(self.db, str(user.id))
        self.db.add(UserProfile(user_id=user.id, first_name=first_name, last_name=last_name))
        self.db.add(UserPreference(user_id=user.id))
        write_audit_log(
            self.db,
            event_type="user.registered",
            user_id=user.id,
            actor_user_id=user.id,
            entity_type="user",
            entity_id=user.id,
            after_state={"email": email, "status": user.status},
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(
        self, payload: LoginRequest, ip_address: str | None, user_agent: str | None
    ) -> tuple[User, str, str]:
        email = payload.email.lower()
        user = self.repo.get_user_by_email(email)
        if user is None or not verify_password(payload.password, user.password_hash):
            self.repo.record_login_attempt(email, ip_address, False, "invalid_credentials")
            write_audit_log(
                self.db,
                event_type="auth.login.failed",
                after_state={"reason": "invalid_credentials"},
            )
            self.db.commit()
            raise AppError("AUTH_INVALID_CREDENTIALS", "Credenciales inválidas.", 401)
        if user.status != "active":
            self.repo.record_login_attempt(email, ip_address, False, "inactive_user")
            write_audit_log(
                self.db, event_type="auth.login.failed", after_state={"reason": "inactive_user"}
            )
            self.db.commit()
            raise AppError("AUTH_INVALID_CREDENTIALS", "Credenciales inválidas.", 401)

        set_db_current_user(self.db, str(user.id))
        user.last_login_at = datetime.now(UTC)
        self.repo.record_login_attempt(email, ip_address, True, "ok")
        access_token, refresh_token = self._issue_tokens(user, ip_address, user_agent)
        write_audit_log(
            self.db,
            event_type="auth.login.success",
            user_id=user.id,
            actor_user_id=user.id,
            entity_type="session",
        )
        self.db.commit()
        return user, access_token, refresh_token

    def refresh(
        self, refresh_token: str, ip_address: str | None, user_agent: str | None
    ) -> tuple[User, str, str]:
        token_hash = hash_token(refresh_token)
        token = self.repo.get_refresh_token(token_hash)
        now = datetime.now(UTC)
        if token is None:
            raise AppError("AUTH_INVALID_TOKEN", "Token inválido.", 401)
        if token.revoked_at is not None:
            self.repo.revoke_family(token.family_id)
            set_db_current_user(self.db, str(token.user_id))
            write_audit_log(
                self.db,
                event_type="security.refresh_reuse_detected",
                user_id=token.user_id,
                actor_user_id=token.user_id,
                entity_type="session",
                entity_id=token.id,
            )
            self.db.commit()
            raise AppError("AUTH_INVALID_TOKEN", "Token inválido.", 401)
        if token.expires_at <= now:
            self.repo.revoke_token(token)
            self.db.commit()
            raise AppError("AUTH_TOKEN_EXPIRED", "Tu sesión expiró.", 401)

        user = self.db.get(User, token.user_id)
        if user is None or user.status != "active":
            raise AppError("AUTH_INVALID_TOKEN", "Token inválido.", 401)
        set_db_current_user(self.db, str(user.id))
        self.repo.revoke_token(token)
        access_token, new_refresh = self._issue_tokens(
            user,
            ip_address,
            user_agent,
            family_id=token.family_id,
        )
        self.db.commit()
        return user, access_token, new_refresh

    def logout(self, refresh_token: str | None) -> None:
        if not refresh_token:
            return
        token = self.repo.get_refresh_token(hash_token(refresh_token))
        if token and token.revoked_at is None:
            set_db_current_user(self.db, str(token.user_id))
            self.repo.revoke_token(token)
            write_audit_log(
                self.db,
                event_type="auth.logout",
                user_id=token.user_id,
                actor_user_id=token.user_id,
                entity_type="session",
                entity_id=token.id,
            )
            self.db.commit()

    def request_password_reset(self, email: str) -> None:
        normalized_email = email.lower()
        user = self.repo.get_user_by_email(normalized_email)
        if user is not None and user.status == "active":
            raw_token = secrets.token_urlsafe(48)
            self.db.add(
                PasswordResetToken(
                    user_id=user.id,
                    token_hash=hash_token(raw_token),
                    expires_at=datetime.now(UTC) + timedelta(minutes=30),
                )
            )
            set_db_current_user(self.db, str(user.id))
            write_audit_log(
                self.db,
                event_type="auth.password_reset.requested",
                user_id=user.id,
                actor_user_id=user.id,
                entity_type="password_reset",
                after_state={"email": normalized_email},
            )
        else:
            write_audit_log(
                self.db,
                event_type="auth.password_reset.requested_unknown",
                after_state={"email": normalized_email},
            )
        self.db.commit()

    def reset_password(self, payload: ResetPasswordRequest) -> None:
        token = self.repo.get_password_reset_token(hash_token(payload.reset_token))
        now = datetime.now(UTC)
        if token is None or token.used_at is not None or token.expires_at <= now:
            raise AppError("AUTH_INVALID_TOKEN", "Token invÃ¡lido.", 401)
        user = self.db.get(User, token.user_id)
        if user is None or user.status != "active":
            raise AppError("AUTH_INVALID_TOKEN", "Token invÃ¡lido.", 401)
        set_db_current_user(self.db, str(user.id))
        user.password_hash = hash_password(payload.new_password)
        user.token_version += 1
        token.used_at = now
        self.repo.revoke_user_tokens(user.id)
        write_audit_log(
            self.db,
            event_type="auth.password_reset.completed",
            user_id=user.id,
            actor_user_id=user.id,
            entity_type="user",
            entity_id=user.id,
        )
        self.db.commit()

    def change_password(self, user: User, payload: ChangePasswordRequest) -> None:
        if not verify_password(payload.current_password, user.password_hash):
            raise AppError("AUTH_INVALID_CREDENTIALS", "Credenciales invÃ¡lidas.", 401)
        set_db_current_user(self.db, str(user.id))
        user.password_hash = hash_password(payload.new_password)
        user.token_version += 1
        self.repo.revoke_user_tokens(user.id)
        write_audit_log(
            self.db,
            event_type="auth.password.changed",
            user_id=user.id,
            actor_user_id=user.id,
            entity_type="user",
            entity_id=user.id,
        )
        self.db.commit()

    def _issue_tokens(
        self,
        user: User,
        ip_address: str | None,
        user_agent: str | None,
        family_id: uuid.UUID | None = None,
    ) -> tuple[str, str]:
        settings = get_settings()
        session_id = uuid.uuid4()
        access_token = create_access_token(user, session_id)
        raw_refresh = secrets.token_urlsafe(48)
        refresh = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(raw_refresh),
            family_id=family_id or uuid.uuid4(),
            device_id=str(session_id),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
        )
        self.db.add(refresh)
        return access_token, raw_refresh

    @staticmethod
    def _split_name(full_name: str) -> tuple[str, str | None]:
        parts = " ".join(full_name.strip().split()).split(" ", 1)
        return parts[0], parts[1] if len(parts) > 1 else None
