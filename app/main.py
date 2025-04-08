import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import models, schemas, security
from app import cache, crud
from database import get_db
from app.config import settings

app = FastAPI()


@app.post("/secret", response_model=schemas.ResponseSecret)
async def create_secret(
        secret: schemas.SecretCreate,
        request: Request,
        db: Session = Depends(get_db)
):
    secret_key = uuid.uuid4()
    ttl = max(secret.ttl_seconds or 0, settings.MIN_TTL)

    encrypted_secret = security.encrypt_secret(secret.secret)
    passphrase_hash = security.hash_passphrase(secret.passphrase) if secret.passphrase else None

    expires_at = datetime.utcnow() + timedelta(seconds=ttl)

    db_secret = models.Secret(
        id=secret_key,
        encrypted_secret=encrypted_secret,
        passphrase_hash=passphrase_hash,
        ttl=ttl,
        expires_at=expires_at
    )

    db.add(db_secret)
    db.commit()

    cache[secret_key] = db_secret

    crud.create_log(
        db=db,
        secret_id=secret_key,
        action="create",
        request=request
    )

    return {"secret_key": str(secret_key)}


@app.get("/secret/{secret_key}", response_model=schemas.SecretReadResponse)
async def read_secret(
        secret_key: str,
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        secret_id = uuid.UUID(secret_key)
    except ValueError:
        raise HTTPException(status_code=404, detail="Secret not found")

    secret = cache.get(secret_id)
    if secret and secret.is_active:
        decrypted_secret = security.decrypt_secret(secret.encrypted_secret)
        secret.is_active = False
        db.commit()
        del cache[secret_id]
    else:
        secret = crud.get_secret(db, secret_id)
        if not secret or not secret.is_active or datetime.utcnow() > secret.expires_at:
            raise HTTPException(status_code=404, detail="Secret not found or expired")

        decrypted_secret = security.decrypt_secret(secret.encrypted_secret)
        secret.is_active = False
        db.commit()

    # Log access
    crud.create_log(
        db=db,
        secret_id=secret_id,
        action="read",
        request=request
    )

    return {"secret": decrypted_secret}


@app.delete("/secret/{secret_key}", response_model=schemas.SecretDeleteResponse)
async def delete_secret_endpoint(
        secret_key: str,
        passphrase: str = None,
        request: Request,
        db: Session = Depends(get_db)
):
    try:
        secret_id = uuid.UUID(secret_key)
    except ValueError:
        raise HTTPException(status_code=404, detail="Secret not found")

    secret = crud.get_secret(db, secret_id)
    if not secret:
        raise HTTPException(status_code=404, detail="Secret not found")

    if secret.passphrase_hash and not security.verify_passphrase(passphrase, secret.passphrase_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid passphrase"
        )

    secret.is_active = False
    db.commit()
    cache.pop(secret_id, None)

    crud.create_log(
        db=db,
        secret_id=secret_id,
        action="delete",
        request=request
    )

    return {"status": "secret_deleted"}