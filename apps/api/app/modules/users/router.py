from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.responses import ok
from app.core.security import get_current_user
from app.modules.audit.models import AuditLog
from app.modules.auth.models import User, UserPreference, UserProfile
from app.modules.users.schemas import ProfileUpdate, SettingsUpdate

router = APIRouter()


@router.get("/users/me")
def get_profile(current_user: User = Depends(get_current_user)):
    profile = current_user.profile
    return ok(
        {
            "id": str(current_user.id),
            "email": current_user.email,
            "status": current_user.status,
            "profile": {
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "country_code": profile.country_code,
                "city": profile.city,
                "currency_code": profile.currency_code,
                "payday": profile.payday,
                "paydays": profile.paydays,
                "income_frequency": profile.income_frequency,
            },
        }
    )


@router.patch("/users/me")
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = current_user.profile or UserProfile(user_id=current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    db.add(profile)
    db.commit()
    return get_profile(current_user)


@router.get("/settings/me")
def get_settings_me(current_user: User = Depends(get_current_user)):
    preferences = current_user.preferences
    return ok(
        {
            "theme_mode": preferences.theme_mode,
            "accent_color": preferences.accent_color,
            "dashboard_layout": preferences.dashboard_layout,
            "notification_settings": preferences.notification_settings,
        }
    )


@router.patch("/settings/me")
def update_settings_me(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    preferences = current_user.preferences or UserPreference(user_id=current_user.id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(preferences, field, value)
    db.add(preferences)
    db.commit()
    return get_settings_me(current_user)


@router.get("/users/me/preferences")
def get_preferences(current_user: User = Depends(get_current_user)):
    return get_settings_me(current_user)


@router.patch("/users/me/preferences")
def update_preferences(
    payload: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_settings_me(payload, db, current_user)


@router.get("/users/me/security-settings")
def get_security_settings(current_user: User = Depends(get_current_user)):
    return ok(
        {
            "email_verified": current_user.email_verified_at is not None,
            "last_login_at": current_user.last_login_at.isoformat()
            if current_user.last_login_at
            else None,
            "active_session_policy": "refresh_token_rotation",
            "password_policy": {
                "min_length": 12,
                "max_length": 128,
                "hashed_with": "argon2",
            },
        }
    )


@router.get("/users/me/activity")
def get_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = db.scalars(
        select(AuditLog)
        .where((AuditLog.user_id == current_user.id) | (AuditLog.actor_user_id == current_user.id))
        .order_by(AuditLog.created_at.desc())
        .limit(50)
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
        ]
    )
