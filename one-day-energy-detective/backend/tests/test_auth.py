"""
Test Suite: Authentication, Cryptographic Hashing, and Session Tokens.
"""

import os
import unittest
from backend.database import init_db
from backend.services.auth_service import (
    hash_password,
    verify_password,
    create_user_session,
    authenticate_session,
    revoke_session
)
from backend.models.user import UserModel
from backend.models.household import HouseholdModel

class TestAuthSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_password_hashing_uniqueness_and_verification(self):
        password = "DetectiveSecretPass!123"
        salt1, hash1 = hash_password(password)
        salt2, hash2 = hash_password(password)

        # Unique salts generated each time
        self.assertNotEqual(salt1, salt2)
        self.assertNotEqual(hash1, hash2)

        # Verification succeeds with correct password
        self.assertTrue(verify_password(password, salt1, hash1))
        self.assertTrue(verify_password(password, salt2, hash2))

        # Verification fails with incorrect password
        self.assertFalse(verify_password("WrongPassword999", salt1, hash1))
        self.assertFalse(verify_password("", salt1, hash1))

    def test_user_session_lifecycle(self):
        email = "detective.test@energyaudit.org"
        salt, pwd_hash = hash_password("validpassword123")
        
        # Cleanup if leftover
        existing = UserModel.get_by_email(email)
        if existing:
            user_id = existing["id"]
        else:
            user_id = UserModel.create(email, pwd_hash, salt, "Audit Officer")
            HouseholdModel.create(user_id, "Detective HQ", "apartment", 3, 7.50, "₹", "india_cea")

        # Create session
        session = create_user_session(user_id)
        token = session["token"]
        self.assertTrue(len(token) > 20)

        # Authenticate session
        ctx = authenticate_session(token)
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["user_id"], user_id)
        self.assertEqual(ctx["email"], email)
        self.assertIsNotNone(ctx["household"])

        # Revoke session
        revoke_session(token)
        revoked_ctx = authenticate_session(token)
        self.assertIsNone(revoked_ctx)

if __name__ == "__main__":
    unittest.main()
