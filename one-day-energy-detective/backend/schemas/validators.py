"""
Strict Input Validation Layer.
Rejects invalid inputs, malformed types, and out-of-range power/hour configurations.
"""

import re
from typing import Dict, Any, List, Optional
from backend.config import EMISSION_FACTORS

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
VALID_CATEGORIES = {"climate", "kitchen", "lighting", "entertainment", "laundry", "electronics", "other"}
VALID_DWELLINGS = {"apartment", "independent_house", "villa", "dorm", "townhouse"}
VALID_LOCALITY_TYPES = {"urban", "rural"}

class ValidationError(Exception):
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.field = field

def validate_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object")

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    full_name = str(data.get("full_name", "")).strip()
    household_name = str(data.get("household_name", "My Home")).strip()
    
    if not email or not EMAIL_REGEX.match(email):
        raise ValidationError("Valid email address is required", "email")
    if len(password) < 6:
        raise ValidationError("Password must be at least 6 characters long", "password")
    if len(full_name) < 2 or len(full_name) > 100:
        raise ValidationError("Full name must be between 2 and 100 characters", "full_name")
    if not household_name or len(household_name) > 100:
        raise ValidationError("Household name must be between 1 and 100 characters", "household_name")

    occupants = data.get("occupants", 3)
    try:
        occupants = int(occupants)
        if occupants < 1 or occupants > 50:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError("Household occupants must be an integer between 1 and 50", "occupants")

    tariff_rate = data.get("tariff_rate", 7.50)
    try:
        tariff_rate = float(tariff_rate)
        if tariff_rate <= 0 or tariff_rate > 1000:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError("Tariff rate must be a positive number up to 1000", "tariff_rate")

    currency_symbol = str(data.get("currency_symbol", "₹")).strip() or "₹"
    grid_region = str(data.get("grid_region", "india_cea")).strip()
    if grid_region not in EMISSION_FACTORS:
        grid_region = "india_cea"

    locality_type = str(data.get("locality_type", "urban")).strip().lower()
    if locality_type not in VALID_LOCALITY_TYPES:
        locality_type = "urban"

    return {
        "email": email,
        "password": password,
        "full_name": full_name,
        "household_name": household_name,
        "occupants": occupants,
        "locality_type": locality_type,
        "tariff_rate": round(tariff_rate, 4),
        "currency_symbol": currency_symbol[:5],
        "grid_region": grid_region
    }

def validate_login(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object")
    
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    
    if not email:
        raise ValidationError("Email is required", "email")
    if not password:
        raise ValidationError("Password is required", "password")
        
    return {"email": email, "password": password}

def validate_household(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object")

    household_name = str(data.get("household_name", "")).strip()
    if not household_name or len(household_name) > 100:
        raise ValidationError("Household name must be between 1 and 100 characters", "household_name")

    dwelling_type = str(data.get("dwelling_type", "apartment")).strip().lower()
    if dwelling_type not in VALID_DWELLINGS:
        dwelling_type = "apartment"

    try:
        occupants = int(data.get("occupants", 1))
        if occupants < 1 or occupants > 50:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError("Occupants must be an integer between 1 and 50", "occupants")

    try:
        tariff_rate = float(data.get("tariff_rate", 7.5))
        if tariff_rate <= 0 or tariff_rate > 1000:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError("Tariff rate must be a positive number greater than 0", "tariff_rate")

    currency_symbol = str(data.get("currency_symbol", "₹")).strip() or "₹"

    grid_region = str(data.get("grid_region", "india_cea")).strip()
    if grid_region not in EMISSION_FACTORS:
        raise ValidationError(f"Grid region must be one of: {', '.join(EMISSION_FACTORS.keys())}", "grid_region")

    locality_type = str(data.get("locality_type", "urban")).strip().lower()
    if locality_type not in VALID_LOCALITY_TYPES:
        locality_type = "urban"

    custom_emission_factor = data.get("custom_emission_factor")
    if custom_emission_factor is not None and custom_emission_factor != "":
        try:
            custom_emission_factor = float(custom_emission_factor)
            if custom_emission_factor <= 0 or custom_emission_factor > 10.0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValidationError("Custom emission factor must be a positive number (0.01 - 10.0 kg/kWh)", "custom_emission_factor")
    else:
        custom_emission_factor = None

    return {
        "household_name": household_name,
        "dwelling_type": dwelling_type,
        "occupants": occupants,
        "locality_type": locality_type,
        "tariff_rate": round(tariff_rate, 4),
        "currency_symbol": currency_symbol[:5],
        "grid_region": grid_region,
        "custom_emission_factor": custom_emission_factor
    }

def validate_appliance(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object")

    name = str(data.get("name", "")).strip()
    if not name or len(name) > 100:
        raise ValidationError("Appliance name must be between 1 and 100 characters", "name")

    category = str(data.get("category", "")).strip().lower()
    if category not in VALID_CATEGORIES:
        raise ValidationError(
            f"Invalid category '{category}'. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}",
            "category"
        )

    # Power in Watts (strictly positive)
    try:
        power_watts = float(data.get("power_watts", 0))
        if power_watts <= 0 or power_watts > 50_000:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError("Rated power must be a positive number up to 50,000 Watts", "power_watts")

    # Quantity (integer >= 1)
    try:
        quantity = int(data.get("quantity", 1))
        if quantity < 1 or quantity > 100:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError("Quantity must be an integer between 1 and 100", "quantity")

    # Daily Hours (0 <= hours <= 24)
    try:
        daily_hours = float(data.get("daily_hours", 0))
        if daily_hours < 0 or daily_hours > 24:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError("Daily operating hours must be between 0 and 24 hours", "daily_hours")

    # Standby Watts (>= 0)
    try:
        standby_watts = float(data.get("standby_watts", 0))
        if standby_watts < 0 or standby_watts > 2000:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValidationError("Standby power must be non-negative up to 2000 Watts", "standby_watts")

    room_location = str(data.get("room_location", "Living Room")).strip() or "Living Room"
    if len(room_location) > 50:
        room_location = room_location[:50]

    try:
        energy_star_rating = int(data.get("energy_star_rating", 3))
        if energy_star_rating < 1 or energy_star_rating > 5:
            energy_star_rating = 3
    except (TypeError, ValueError):
        energy_star_rating = 3

    notes = str(data.get("notes", "")).strip()
    if len(notes) > 500:
        notes = notes[:500]

    return {
        "name": name,
        "category": category,
        "power_watts": round(power_watts, 2),
        "quantity": quantity,
        "daily_hours": round(daily_hours, 2),
        "standby_watts": round(standby_watts, 2),
        "room_location": room_location,
        "energy_star_rating": energy_star_rating,
        "notes": notes
    }
