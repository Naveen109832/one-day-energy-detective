"""
User Data Access Model (JSON backend).
Handles account creation, lookup, and session management.
Passwords are stored as PBKDF2-HMAC-SHA256 hashes — never plaintext.
"""

import datetime
from typing import Optional, Dict, Any, List
from backend.database import JsonDB


class UserModel:

    @staticmethod
    def create(email: str, password_hash: str, password_salt: str, full_name: str) -> int:
        with JsonDB("users") as db:
            # Duplicate email check (case-insensitive)
            if any(r["email"].lower() == email.lower() for r in db.records):
                raise ValueError("Email address is already registered")
            record = {
                "email": email.lower().strip(),
                "password_hash": password_hash,
                "password_salt": password_salt,
                "full_name": full_name.strip(),
                "created_at": datetime.datetime.utcnow().isoformat()
            }
            return db.append(record)

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        with JsonDB("users") as db:
            for r in db.records:
                if r["email"].lower() == email.lower().strip():
                    return dict(r)
        return None

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        with JsonDB("users") as db:
            for r in db.records:
                if r.get("id") == user_id:
                    return dict(r)
        return None

    # ── Session management ────────────────────────────────────────────────────

    @staticmethod
    def create_session(token: str, user_id: int, expires_at: str) -> None:
        with JsonDB("sessions") as db:
            db.append({
                "token": token,
                "user_id": user_id,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "expires_at": expires_at
            })

    @staticmethod
    def get_session(token: str) -> Optional[Dict[str, Any]]:
        with JsonDB("sessions") as db:
            for r in db.records:
                if r.get("token") == token:
                    return dict(r)
        return None

    @staticmethod
    def delete_session(token: str) -> None:
        with JsonDB("sessions") as db:
            original_len = len(db.records)
            db.records = [r for r in db.records if r.get("token") != token]
            if len(db.records) != original_len:
                db.save()

    @staticmethod
    def cleanup_expired_sessions() -> None:
        now = datetime.datetime.utcnow().isoformat()
        with JsonDB("sessions") as db:
            original_len = len(db.records)
            db.records = [r for r in db.records if r.get("expires_at", "") > now]
            if len(db.records) != original_len:
                db.save()
