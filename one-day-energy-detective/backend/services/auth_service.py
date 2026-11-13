"""
Authentication Service.
Handles cryptographic password hashing with PBKDF2-HMAC-SHA256,
salt generation, and bearer session token lifecycle.
"""

import os
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional, Dict, Any

from backend.config import PASSWORD_SALT_BYTES, PBKDF2_ITERATIONS, SESSION_DURATION_SECONDS
from backend.models.user import UserModel
from backend.models.household import HouseholdModel

def hash_password(password: str) -> Tuple[str, str]:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a unique random salt."""
    salt = secrets.token_bytes(PASSWORD_SALT_BYTES)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS
    )
    return salt.hex(), derived.hex()

def verify_password(password: str, salt_hex: str, hash_hex: str) -> bool:
    """Verifies a plaintext password against the stored salt and derived hash in constant time."""
    try:
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS
        )
        return hmac.compare_digest(actual_hash, expected_hash)
    except Exception:
        return False

def create_user_session(user_id: int) -> Dict[str, Any]:
    """Generates a secure cryptographically random session token with expiry."""
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=SESSION_DURATION_SECONDS)).strftime("%Y-%m-%d %H:%M:%S")
    UserModel.create_session(token, user_id, expires_at)
    return {
        "token": token,
        "expires_at": expires_at
    }

def authenticate_session(token: str) -> Optional[Dict[str, Any]]:
    """Validates session token and returns current user and household details."""
    if not token:
        return None
    session = UserModel.get_session(token)
    if not session:
        return None
    
    # Reject expired sessions
    try:
        expires = datetime.strptime(session["expires_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            UserModel.delete_session(token)
            return None
    except (KeyError, ValueError, TypeError):
        pass

    user_id = session["user_id"]
    user = UserModel.get_by_id(user_id)
    if not user:
        return None
    household = HouseholdModel.get_by_user_id(user_id)
    return {
        "user_id": user_id,
        "email": user["email"],
        "full_name": user["full_name"],
        "token": session["token"],
        "household": household
    }

def revoke_session(token: str) -> None:
    """Terminates an active session token."""
    UserModel.delete_session(token)
