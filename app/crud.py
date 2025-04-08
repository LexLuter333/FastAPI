from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from fastapi import Request
import models
import schemas
import uuid
import datetime


def create_secret(
        db: Session, secret_data: schemas.SecretCreate,
        secret_id: uuid.UUID,
        encrypted_secret: str,
        passphrase_hash: str,
        expires_at: datetime
):
    db_secret = models.Secret(
        id=secret_id,
        encrypted_secret=encrypted_secret,
        passphrase_hash=passphrase_hash,
        ttl=secret_data.ttl_seconds,
        expires_at=expires_at
    )
    db.add(db_secret)
    db.commit()
    db.refresh(db_secret)
    return db_secret


def get_secret(
        db: Session,
        secret_id: uuid.UUID
):
    try:
        return db.query(models.Secret).filter(models.Secret.id == secret_id, models.Secret.is_active is True).one()
    except NoResultFound:
        return None


def delete_secret(
        db: Session,
        secret_id: uuid.UUID
):
    secret = db.query(models.Secret).filter(models.Secret.id == secret_id).first()
    if secret:
        secret.is_active = False
        db.commit()
    return secret


def create_log(
        db: Session,
        secret_id: uuid.UUID,
        action: str,
        request: Request
):
    log_entry = models.SecretLog(
        secret_id=secret_id,
        action=action,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
