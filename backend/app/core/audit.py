import json

from sqlalchemy.orm import Session

from app.models import AuditEvent, User


def record(db: Session, actor: User, action: str, target_type: str, target_id: int,
           tenant_id: int | None = None, **detail) -> None:
    """Add an audit row to the current transaction. Never pass secrets in detail."""
    db.add(AuditEvent(
        actor_user_id=actor.id, action=action, target_type=target_type, target_id=target_id,
        tenant_id=tenant_id, detail=json.dumps(detail, ensure_ascii=False),
    ))
