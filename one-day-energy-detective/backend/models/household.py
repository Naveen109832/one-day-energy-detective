"""
Household Data Access Model (JSON backend).
Maintains household configuration, occupants, locality type, tariff, and region.
Ensures strong user isolation so one user cannot access another household.
"""

import datetime
from typing import Optional, Dict, Any
from backend.database import JsonDB


class HouseholdModel:

    @staticmethod
    def create(
        user_id: int,
        household_name: str,
        dwelling_type: str = "apartment",
        occupants: int = 3,
        locality_type: str = "urban",
        tariff_rate: float = 7.50,
        currency_symbol: str = "₹",
        grid_region: str = "india_cea",
        custom_emission_factor: Optional[float] = None
    ) -> int:
        now = datetime.datetime.utcnow().isoformat()
        with JsonDB("households") as db:
            record = {
                "user_id": user_id,
                "household_name": household_name.strip(),
                "dwelling_type": dwelling_type,
                "occupants": occupants,
                "locality_type": locality_type,
                "tariff_rate": tariff_rate,
                "currency_symbol": currency_symbol,
                "grid_region": grid_region,
                "custom_emission_factor": custom_emission_factor,
                "created_at": now,
                "updated_at": now
            }
            return db.append(record)

    @staticmethod
    def get_by_user_id(user_id: int) -> Optional[Dict[str, Any]]:
        with JsonDB("households") as db:
            for r in db.records:
                if r.get("user_id") == user_id:
                    return dict(r)
        return None

    @staticmethod
    def get_by_id(household_id: int) -> Optional[Dict[str, Any]]:
        with JsonDB("households") as db:
            for r in db.records:
                if r.get("id") == household_id:
                    return dict(r)
        return None

    @staticmethod
    def update(
        household_id: int,
        user_id: int,
        household_name: str,
        dwelling_type: str,
        occupants: int,
        locality_type: str,
        tariff_rate: float,
        currency_symbol: str,
        grid_region: str,
        custom_emission_factor: Optional[float]
    ) -> bool:
        with JsonDB("households") as db:
            for r in db.records:
                if r.get("id") == household_id and r.get("user_id") == user_id:
                    r["household_name"] = household_name.strip()
                    r["dwelling_type"] = dwelling_type
                    r["occupants"] = occupants
                    r["locality_type"] = locality_type
                    r["tariff_rate"] = tariff_rate
                    r["currency_symbol"] = currency_symbol
                    r["grid_region"] = grid_region
                    r["custom_emission_factor"] = custom_emission_factor
                    r["updated_at"] = datetime.datetime.utcnow().isoformat()
                    db.save()
                    return True
        return False
