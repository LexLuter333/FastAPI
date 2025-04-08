from pydantic import BaseModel
from datetime import datetime


class SecretCreate(BaseModel):
    secret: str
    passphrase: str
    ttl: int


class ResponseSecret(BaseModel):
    secret: str


class SecretReadResponse(BaseModel):
    secret: str


class SecretDeleteResponse(BaseModel):
    status: str


class LogEntry(BaseModel):
    action: str
    timestamp: datetime
    ip_address: str
    user_agent: str
