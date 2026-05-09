import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.errors import AppError
from app.core.responses import ok
from app.core.security import get_current_user
from app.modules.alerts.models import Alert
from app.modules.audit.service import write_audit_log
from app.modules.auth.models import User

router = APIRouter()


def _alert_payload(alert: Alert) -> dict:
    return {
        "id": str(alert.id),
        "goal_id": str(alert.goal_id) if alert.goal_id else None,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "message": alert.message,
        "payload": alert.payload,
        "status": alert.status,
        "created_at": alert.created_at.isoformat(),
    }


@router.get("")
def list_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alerts = db.scalars(
        select(Alert)
        .where(Alert.user_id == current_user.id, Alert.status == "active")
        .order_by(Alert.created_at.desc())
        .limit(100)
    )
    return ok([_alert_payload(alert) for alert in alerts])


@router.patch("/{alert_id}/read")
def mark_alert_read(
    alert_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = db.scalar(select(Alert).where(Alert.id == alert_id, Alert.user_id == current_user.id))
    if alert is None:
        raise AppError("RESOURCE_NOT_FOUND", "Recurso no encontrado.", 404)
    alert.status = "resolved"
    alert.resolved_at = datetime.now(UTC)
    write_audit_log(
        db,
        event_type="alert.read",
        user_id=current_user.id,
        actor_user_id=current_user.id,
        entity_type="alert",
        entity_id=alert.id,
    )
    db.commit()
    return ok({"status": "read"})
