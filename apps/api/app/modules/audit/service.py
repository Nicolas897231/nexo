import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.middleware.request_context import get_request_id
from app.modules.audit.models import AuditLog

SENSITIVE_STATE_KEYS = {"password", "password_hash", "access_token", "refresh_token", "reset_token"}


def _safe_state(state: dict[str, Any] | None) -> dict[str, Any] | None:
    if state is None:
        return None
    return {key: value for key, value in state.items() if key.lower() not in SENSITIVE_STATE_KEYS}


def write_audit_log(
    db: Session,
    *,
    event_type: str,
    user_id: uuid.UUID | None = None,
    actor_user_id: uuid.UUID | None = None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    before_state: dict[str, Any] | None = None,
    after_state: dict[str, Any] | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            request_id=uuid.UUID(get_request_id()),
            before_state=_safe_state(before_state),
            after_state=_safe_state(after_state),
        )
    )
