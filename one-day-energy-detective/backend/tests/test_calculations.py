"""
Test Suite: Electricity Energy, Cost, and Carbon Footprint Calculations.
Verifies formulas for power (W), energy (kWh), monthly estimates, and grid emission factors.
"""

import unittest
from backend.services.energy_service import (
    calculate_appliance_energy,
    calculate_household_energy_audit
)
from backend.services.detective_service import analyze_detective_findings, simulate_energy_scenario

class TestEnergyCalculations(unittest.TestCase):
    def setUp(self):
        self.sample_tariff = 8.0  # ₹8.00 per kWh
        self.sample_emission_factor = 0.716  # CEA India Grid Baseline (kg CO2e/kWh)

    def test_appliance_active_energy_formula(self):
        """
        Verify: E_active = (Power_W * Quantity * Hours) / 1000
        Example: 1500W AC running 6 hours = (1500 * 1 * 6) / 1000 = 9.0 kWh/day
        """
        appliance = {
            "id": 1,
            "name": "Air Conditioner",
            "category": "climate",
            "power_watts": 1500.0,
            "quantity": 1,
            "daily_hours": 6.0,
            "standby_watts": 0.0
        }
        res = calculate_appliance_energy(appliance, self.sample_tariff, self.sample_emission_factor)
        self.assertAlmostEqual(res["active_daily_kwh"], 9.0, places=3)
        self.assertAlmostEqual(res["standby_daily_kwh"], 0.0, places=3)
        self.assertAlmostEqual(res["total_daily_kwh"], 9.0, places=3)
        # 30-day monthly estimate: 9 * 30 = 270 kWh
        self.assertAlmostEqual(res["monthly_kwh"], 270.0, places=2)
        # 365-day annual estimate: 9 * 365 = 3285 kWh
        self.assertAlmostEqual(res["annual_kwh"], 3285.0, places=2)
        # Monthly cost: 270 kWh * 8 = ₹2160
        self.assertAlmostEqual(res["monthly_cost"], 2160.0, places=2)
        # Monthly carbon: 270 * 0.716 = 193.32 kg CO2e
        self.assertAlmostEqual(res["monthly_carbon_kg"], 193.32, places=2)

    def test_appliance_vampire_standby_energy_formula(self):
        """
        Verify: E_standby = (Standby_W * Quantity * (24 - Hours)) / 1000
        Example: Gaming PC with 10W standby, active 4 hours -> idle 20 hours:
          Active: (300 * 1 * 4) / 1000 = 1.2 kWh/day
          Standby: (10 * 1 * 20) / 1000 = 0.2 kWh/day
          Total: 1.4 kWh/day
        """
        appliance = {
            "id": 2,
            "name": "Desktop PC",
            "category": "electronics",
            "power_watts": 300.0,
            "quantity": 1,
            "daily_hours": 4.0,
            "standby_watts": 10.0
        }
        res = calculate_appliance_energy(appliance, self.sample_tariff, self.sample_emission_factor)
        self.assertAlmostEqual(res["active_daily_kwh"], 1.2, places=3)
        self.assertAlmostEqual(res["standby_daily_kwh"], 0.2, places=3)
        self.assertAlmostEqual(res["total_daily_kwh"], 1.4, places=3)
        self.assertAlmostEqual(res["idle_hours"], 20.0, places=2)
        self.assertAlmostEqual(res["monthly_kwh"], 42.0, places=2)

    def test_multiple_quantity_scaling(self):
        """
        Verify quantity multiplier:
        4 LED bulbs of 9W running 5 hours = (9 * 4 * 5) / 1000 = 0.18 kWh/day
        """
        appliance = {
            "id": 3,
            "name": "LED Bulb",
            "category": "lighting",
            "power_watts": 9.0,
            "quantity": 4,
            "daily_hours": 5.0,
            "standby_watts": 0.0
        }
        res = calculate_appliance_energy(appliance, self.sample_tariff, self.sample_emission_factor)
        self.assertAlmostEqual(res["active_daily_kwh"], 0.18, places=3)
        self.assertAlmostEqual(res["total_daily_kwh"], 0.18, places=3)
        self.assertAlmostEqual(res["monthly_kwh"], 5.4, places=2)

    def test_household_per_capita_and_vampire_index(self):
        """
        Verify per-capita normalization by household size (occupants).
        """
        household = {
            "id": 1,
            "household_name": "Test Residence",
            "occupants": 4,
            "tariff_rate": 8.0,
            "currency_symbol": "₹",
            "grid_region": "india_cea"
        }
        appliances = [
            {"id": 1, "name": "AC", "category": "climate", "power_watts": 1500, "quantity": 1, "daily_hours": 6, "standby_watts": 5},
            {"id": 2, "name": "Fridge", "category": "kitchen", "power_watts": 150, "quantity": 1, "daily_hours": 24, "standby_watts": 0},
            {"id": 3, "name": "TV", "category": "entertainment", "power_watts": 100, "quantity": 1, "daily_hours": 4, "standby_watts": 10}
        ]
        audit = calculate_household_energy_audit(household, appliances)
        summary = audit["summary"]

        # AC: (1500*6)/1000 = 9.0 active, standby: (5*18)/1000 = 0.09 -> total 9.09 kWh
        # Fridge: (150*24)/1000 = 3.6 active, standby 0 -> total 3.6 kWh
        # TV: (100*4)/1000 = 0.4 active, standby: (10*20)/1000 = 0.2 -> total 0.6 kWh
        # Grand Total Daily = 9.09 + 3.6 + 0.6 = 13.29 kWh/day
        self.assertAlmostEqual(summary["total_daily_kwh"], 13.29, places=2)
        # Monthly = 13.29 * 30 = 398.7 kWh
        self.assertAlmostEqual(summary["total_monthly_kwh"], 398.7, places=1)
        # Per-capita daily = 13.29 / 4 = 3.3225 kWh/person/day
        self.assertAlmostEqual(summary["daily_kwh_per_capita"], 3.3225, places=2)
        # Total standby = 0.09 + 0.20 = 0.29 kWh/day
        self.assertAlmostEqual(summary["total_standby_daily_kwh"], 0.29, places=2)
        # Vampire share pct = (0.29 / 13.29) * 100 = 2.18%
        self.assertAlmostEqual(summary["vampire_share_pct"], 2.2, places=1)

    def test_simulation_savings_delta(self):
        """
        Verify that What-If simulation computes exact mathematical reduction.
        """
        household = {
            "id": 1,
            "household_name": "Test Residence",
            "occupants": 3,
            "tariff_rate": 8.0,
            "currency_symbol": "₹",
            "grid_region": "india_cea"
        }
        # Baseline with an old 60W bulb running 6h
        appliances = [
            {"id": 1, "name": "Old Bulb", "category": "lighting", "power_watts": 60, "quantity": 1, "daily_hours": 6, "standby_watts": 0}
        ]
        base_audit = calculate_household_energy_audit(household, appliances)
        # Base: (60 * 6) / 1000 = 0.36 kWh/day -> 10.8 kWh/month -> ₹86.40/month

        # Simulate replacement with 9W LED
        mods = [{"id": 1, "power_watts": 9.0}]
        sim = simulate_energy_scenario(base_audit, mods)

        # Sim: (9 * 6) / 1000 = 0.054 kWh/day -> 1.62 kWh/month -> ₹12.96/month
        # Saved monthly kWh = 10.8 - 1.62 = 9.18 kWh
        # Saved monthly cost = ₹86.40 - ₹12.96 = ₹73.44
        savings = sim["estimated_savings"]
        self.assertAlmostEqual(savings["saved_monthly_kwh"], 9.18, places=2)
        self.assertAlmostEqual(savings["saved_monthly_cost"], 73.44, places=2)
        self.assertAlmostEqual(savings["reduction_percentage"], 85.0, places=1)

if __name__ == "__main__":
    unittest.main()
