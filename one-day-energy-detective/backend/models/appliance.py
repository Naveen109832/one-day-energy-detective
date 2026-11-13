"""
Appliance Data Access Model (JSON backend).
Full CRUD for household appliances with duplicate detection and user isolation.
"""

import datetime
from typing import Optional, Dict, Any, List
from backend.database import JsonDB


class ApplianceModel:

    @staticmethod
    def create(
        household_id: int,
        name: str,
        category: str,
        power_watts: float,
        quantity: int = 1,
        daily_hours: float = 1.0,
        standby_watts: float = 0.0,
        room_location: str = "Living Room",
        energy_star_rating: int = 3,
        notes: str = ""
    ) -> int:
        now = datetime.datetime.utcnow().isoformat()
        with JsonDB("appliances") as db:
            record = {
                "household_id": household_id,
                "name": name.strip(),
                "category": category,
                "power_watts": power_watts,
                "quantity": quantity,
                "daily_hours": daily_hours,
                "standby_watts": standby_watts,
                "room_location": room_location,
                "energy_star_rating": energy_star_rating,
                "notes": notes,
                "created_at": now,
                "updated_at": now
            }
            return db.append(record)

    @staticmethod
    def get_by_household(household_id: int) -> List[Dict[str, Any]]:
        with JsonDB("appliances") as db:
            return [dict(r) for r in db.records if r.get("household_id") == household_id]

    @staticmethod
    def get_by_id(appliance_id: int, household_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Fetch one appliance. When household_id is given, only returns it if it belongs to that household."""
        with JsonDB("appliances") as db:
            for r in db.records:
                if r.get("id") != appliance_id:
                    continue
                if household_id is not None and r.get("household_id") != household_id:
                    return None
                return dict(r)
        return None

    @staticmethod
    def update(
        appliance_id: int,
        household_id: int,
        name: str,
        category: str,
        power_watts: float,
        quantity: int,
        daily_hours: float,
        standby_watts: float,
        room_location: str,
        energy_star_rating: int,
        notes: str
    ) -> bool:
        with JsonDB("appliances") as db:
            for r in db.records:
                if r.get("id") == appliance_id and r.get("household_id") == household_id:
                    r["name"] = name.strip()
                    r["category"] = category
                    r["power_watts"] = power_watts
                    r["quantity"] = quantity
                    r["daily_hours"] = daily_hours
                    r["standby_watts"] = standby_watts
                    r["room_location"] = room_location
                    r["energy_star_rating"] = energy_star_rating
                    r["notes"] = notes
                    r["updated_at"] = datetime.datetime.utcnow().isoformat()
                    db.save()
                    return True
        return False

    @staticmethod
    def delete(appliance_id: int, household_id: int) -> bool:
        with JsonDB("appliances") as db:
            original_len = len(db.records)
            db.records = [
                r for r in db.records
                if not (r.get("id") == appliance_id and r.get("household_id") == household_id)
            ]
            if len(db.records) != original_len:
                db.save()
                return True
        return False

    @staticmethod
    def find_duplicate(household_id: int, name: str, exclude_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Returns an existing appliance record matching the name in this household (case-insensitive)."""
        with JsonDB("appliances") as db:
            for r in db.records:
                if r.get("household_id") != household_id:
                    continue
                if exclude_id is not None and r.get("id") == exclude_id:
                    continue
                if r.get("name", "").lower() == name.strip().lower():
                    return dict(r)
        return None
