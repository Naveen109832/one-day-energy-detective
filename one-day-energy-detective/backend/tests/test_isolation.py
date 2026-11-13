"""
Test Suite: Multi-Tenant Data Isolation and Access Scoping.
Ensures that a user can never access, mutate, or delete another household's data.
"""

import unittest
from backend.database import init_db
from backend.models.user import UserModel
from backend.models.household import HouseholdModel
from backend.models.appliance import ApplianceModel
from backend.services.auth_service import hash_password

class TestDataIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

        # Create User A
        salt_a, hash_a = hash_password("pass_user_a")
        user_a = UserModel.get_by_email("tenant_a@audit.com")
        if not user_a:
            cls.user_a_id = UserModel.create("tenant_a@audit.com", hash_a, salt_a, "Tenant Alpha")
            cls.household_a_id = HouseholdModel.create(cls.user_a_id, "Household Alpha", "apartment", 2, 7.0, "₹")
        else:
            cls.user_a_id = user_a["id"]
            cls.household_a_id = HouseholdModel.get_by_user_id(cls.user_a_id)["id"]

        # Create User B
        salt_b, hash_b = hash_password("pass_user_b")
        user_b = UserModel.get_by_email("tenant_b@audit.com")
        if not user_b:
            cls.user_b_id = UserModel.create("tenant_b@audit.com", hash_b, salt_b, "Tenant Beta")
            cls.household_b_id = HouseholdModel.create(cls.user_b_id, "Household Beta", "villa", 5, 8.5, "₹")
        else:
            cls.user_b_id = user_b["id"]
            cls.household_b_id = HouseholdModel.get_by_user_id(cls.user_b_id)["id"]

    def test_appliance_cross_tenant_isolation(self):
        # 1. User A creates an appliance in Household A
        app_a_id = ApplianceModel.create(
            household_id=self.household_a_id,
            name="Alpha Inverter AC",
            category="climate",
            power_watts=1200.0,
            quantity=1,
            daily_hours=5.0
        )

        # 2. User B creates an appliance in Household B
        app_b_id = ApplianceModel.create(
            household_id=self.household_b_id,
            name="Beta Geyser",
            category="other",
            power_watts=2000.0,
            quantity=1,
            daily_hours=2.0
        )

        # 3. User A queries appliances for Household A - should NOT see User B's appliance
        apps_a = ApplianceModel.get_by_household(self.household_a_id)
        apps_a_ids = [a["id"] for a in apps_a]
        self.assertIn(app_a_id, apps_a_ids)
        self.assertNotIn(app_b_id, apps_a_ids)

        # 4. Attempting to get User B's appliance under Household A context returns None
        stolen_lookup = ApplianceModel.get_by_id(app_b_id, self.household_a_id)
        self.assertIsNone(stolen_lookup)

        # 5. Attempting to update User B's appliance under Household A context fails
        tamper_success = ApplianceModel.update(
            appliance_id=app_b_id,
            household_id=self.household_a_id,
            name="Hacked Name",
            category="climate",
            power_watts=10.0,
            quantity=1,
            daily_hours=1.0,
            standby_watts=0.0,
            room_location="Bedroom",
            energy_star_rating=5,
            notes=""
        )
        self.assertFalse(tamper_success)

        # Verify User B's appliance remained untouched
        original_b = ApplianceModel.get_by_id(app_b_id, self.household_b_id)
        self.assertEqual(original_b["name"], "Beta Geyser")

        # 6. Attempting to delete User B's appliance under Household A context fails
        delete_tamper = ApplianceModel.delete(app_b_id, self.household_a_id)
        self.assertFalse(delete_tamper)
        still_exists_b = ApplianceModel.get_by_id(app_b_id, self.household_b_id)
        self.assertIsNotNone(still_exists_b)

if __name__ == "__main__":
    unittest.main()
