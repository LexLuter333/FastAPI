from cryptography.fernet import Fernet
from argon2 import PasswordHasher, exceptions
from app.config import settings


ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)


def encrypt_secret(secret: str) -> str:
    fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return fernet.encrypt(secret.encode()).decode()


def decrypt_secret(encrypted_secret: str) -> str:
    fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return fernet.decrypt(encrypted_secret.encode()).decode()


def hash_passphrase(passphrase: str) -> str:
    return ph.hash(passphrase)


def verify_passphrase(passphrase: str, hashed_passphrase: str) -> bool:
    try:
        return ph.verify(hashed_passphrase, passphrase)
    except exceptions.VerifyMismatchError:
        return False
    except exceptions.VerificationError:
        return False
    except exceptions.InvalidHash:
        return False
