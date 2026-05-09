from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.modules.audit.models import AuditLog
from app.modules.auth.models import User

router = APIRouter()


@router.get("/activity")
def list_my_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    rows = db.scalars(
        select(AuditLog)
        .where((AuditLog.user_id == current_user.id) | (AuditLog.actor_user_id == current_user.id))
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return ok(
        [
            {
                "id": str(row.id),
                "event_type": row.event_type,
                "entity_type": row.entity_type,
                "entity_id": str(row.entity_id) if row.entity_id else None,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ],
        pagination={"limit": limit, "offset": offset},
    )
