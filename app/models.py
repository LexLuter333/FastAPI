from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from database import Base


class Secret(Base):
    __tablename__ = "secrets"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    encrypted_secret = Column(String, nullable=False)
    passphrase_hash = Column(String)
    ttl = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)


class SecretLog(Base):
    __tablename__ = "secret_logs"

    id = Column(Integer, primary_key=True, index=True)
    secret_id = Column(UUID(as_uuid=True), ForeignKey("secrets.id"))
    action = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45))
    user_agent = Column(String)
