"""
Password hashing and verification using bcrypt.

Never store plain-text passwords. The hashing is intentionally
slow (bcrypt cost factor 12) to resist brute-force attacks.
"""
from passlib.context import CryptContext

# bcrypt with cost factor 12 — adjust higher for production
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password for storage."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)
