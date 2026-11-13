"""
Test Suite: Strict Input Validation and Error Enforcement.
Verifies that invalid numbers, out-of-range hours, malformed emails, and invalid categories are rejected.
"""

import unittest
from backend.schemas.validators import (
    validate_registration,
    validate_login,
    validate_household,
    validate_appliance,
    ValidationError
)

class TestValidationRules(unittest.TestCase):
    def test_appliance_power_validation(self):
        # Rated power cannot be 0 or negative
        with self.assertRaises(ValidationError) as ctx:
            validate_appliance({
                "name": "Zero Watt Machine",
                "category": "kitchen",
                "power_watts": 0,
                "quantity": 1,
                "daily_hours": 2
            })
        self.assertEqual(ctx.exception.field, "power_watts")

        with self.assertRaises(ValidationError) as ctx:
            validate_appliance({
                "name": "Negative Power",
                "category": "kitchen",
                "power_watts": -50,
                "quantity": 1,
                "daily_hours": 2
            })
        self.assertEqual(ctx.exception.field, "power_watts")

        # Exceeding maximum realistic limit (50,000 W)
        with self.assertRaises(ValidationError) as ctx:
            validate_appliance({
                "name": "Huge Industrial Substation",
                "category": "kitchen",
                "power_watts": 100_000,
                "quantity": 1,
                "daily_hours": 2
            })
        self.assertEqual(ctx.exception.field, "power_watts")

    def test_appliance_daily_hours_range(self):
        # A day has only 24 hours
        with self.assertRaises(ValidationError) as ctx:
            validate_appliance({
                "name": "Perpetual Motion Lamp",
                "category": "lighting",
                "power_watts": 10,
                "quantity": 1,
                "daily_hours": 25.5
            })
        self.assertEqual(ctx.exception.field, "daily_hours")

        # Negative hours
        with self.assertRaises(ValidationError) as ctx:
            validate_appliance({
                "name": "Negative Time Machine",
                "category": "lighting",
                "power_watts": 10,
                "quantity": 1,
                "daily_hours": -1.0
            })
        self.assertEqual(ctx.exception.field, "daily_hours")

    def test_appliance_category_validation(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_appliance({
                "name": "Quantum Warp Core",
                "category": "warp_drive",
                "power_watts": 500,
                "quantity": 1,
                "daily_hours": 2
            })
        self.assertEqual(ctx.exception.field, "category")

    def test_registration_validation(self):
        # Malformed email
        with self.assertRaises(ValidationError) as ctx:
            validate_registration({
                "email": "not-an-email",
                "password": "validpassword123",
                "full_name": "Detective Holmes"
            })
        self.assertEqual(ctx.exception.field, "email")

        # Short password
        with self.assertRaises(ValidationError) as ctx:
            validate_registration({
                "email": "holmes@audit.com",
                "password": "123",
                "full_name": "Detective Holmes"
            })
        self.assertEqual(ctx.exception.field, "password")

    def test_household_occupants_and_tariff(self):
        with self.assertRaises(ValidationError) as ctx:
            validate_household({
                "household_name": "Baker Street Flat",
                "occupants": 0,
                "tariff_rate": 7.5
            })
        self.assertEqual(ctx.exception.field, "occupants")

        with self.assertRaises(ValidationError) as ctx:
            validate_household({
                "household_name": "Baker Street Flat",
                "occupants": 3,
                "tariff_rate": -4.0
            })
        self.assertEqual(ctx.exception.field, "tariff_rate")

if __name__ == "__main__":
    unittest.main()
