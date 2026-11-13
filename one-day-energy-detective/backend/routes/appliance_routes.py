"""
Appliance Inventory API Endpoints.
Handles full CRUD operations, duplicate detection, and preset reference library.
Enforces multi-tenant data isolation on all read and write queries.
"""

from http import HTTPStatus
from backend.routes.base_handler import parse_json, send_json, send_error, get_auth_context
from backend.schemas.validators import validate_appliance, ValidationError
from backend.models.household import HouseholdModel
from backend.models.appliance import ApplianceModel

# Verified Common Appliance Presets (Realistic Watts and Typical Operating Hours)
STANDARD_PRESETS = [
    {
        "name": "Inverter Split Air Conditioner (1.5 Ton)",
        "category": "climate",
        "power_watts": 1400.0,
        "daily_hours": 6.0,
        "standby_watts": 3.0,
        "room_location": "Master Bedroom",
        "energy_star_rating": 4,
        "notes": "Variable speed inverter compressor"
    },
    {
        "name": "Standard Split Air Conditioner (1.5 Ton, 3-Star)",
        "category": "climate",
        "power_watts": 1650.0,
        "daily_hours": 8.0,
        "standby_watts": 4.0,
        "room_location": "Living Room",
        "energy_star_rating": 3,
        "notes": "Fixed speed compressor"
    },
    {
        "name": "Frost-Free Refrigerator (260L, 3-Star)",
        "category": "kitchen",
        "power_watts": 180.0,
        "daily_hours": 24.0,
        "standby_watts": 0.0,
        "room_location": "Kitchen",
        "energy_star_rating": 3,
        "notes": "Continuous duty cooling cycle"
    },
    {
        "name": "Storage Water Geyser (15L)",
        "category": "other",
        "power_watts": 2000.0,
        "daily_hours": 1.5,
        "standby_watts": 2.0,
        "room_location": "Bathroom",
        "energy_star_rating": 4,
        "notes": "Thermostatically controlled heating element"
    },
    {
        "name": "Ceiling Fan (Induction Motor)",
        "category": "climate",
        "power_watts": 75.0,
        "daily_hours": 12.0,
        "standby_watts": 0.0,
        "room_location": "Bedroom",
        "energy_star_rating": 2,
        "notes": "Conventional single-phase motor"
    },
    {
        "name": "BLDC High-Efficiency Ceiling Fan",
        "category": "climate",
        "power_watts": 32.0,
        "daily_hours": 12.0,
        "standby_watts": 1.0,
        "room_location": "Living Room",
        "energy_star_rating": 5,
        "notes": "Brushless DC energy-saving motor"
    },
    {
        "name": "LED Smart TV (55-Inch 4K)",
        "category": "entertainment",
        "power_watts": 95.0,
        "daily_hours": 4.0,
        "standby_watts": 1.5,
        "room_location": "Living Room",
        "energy_star_rating": 4,
        "notes": "Standby sleep mode with quick wake"
    },
    {
        "name": "Desktop Gaming PC & Dual Monitors",
        "category": "electronics",
        "power_watts": 350.0,
        "daily_hours": 5.0,
        "standby_watts": 8.0,
        "room_location": "Study",
        "energy_star_rating": 3,
        "notes": "High continuous draw under load; high phantom standby"
    },
    {
        "name": "Laptop Workstation",
        "category": "electronics",
        "power_watts": 65.0,
        "daily_hours": 8.0,
        "standby_watts": 2.0,
        "room_location": "Home Office",
        "energy_star_rating": 5,
        "notes": "High efficiency adapter"
    },
    {
        "name": "Incandescent Lamp (60W)",
        "category": "lighting",
        "power_watts": 60.0,
        "daily_hours": 5.0,
        "standby_watts": 0.0,
        "room_location": "Balcony / Hall",
        "energy_star_rating": 1,
        "notes": "Traditional filament incandescent lighting"
    },
    {
        "name": "LED Bulb (9W)",
        "category": "lighting",
        "power_watts": 9.0,
        "daily_hours": 5.0,
        "standby_watts": 0.0,
        "room_location": "Kitchen",
        "energy_star_rating": 5,
        "notes": "850 lumens equivalent to 60W incandescent"
    },
    {
        "name": "Microwave Oven (20L)",
        "category": "kitchen",
        "power_watts": 1200.0,
        "daily_hours": 0.3,
        "standby_watts": 3.0,
        "room_location": "Kitchen",
        "energy_star_rating": 3,
        "notes": "High instantaneous power with digital display clock"
    },
    {
        "name": "Front Load Washing Machine (7kg)",
        "category": "laundry",
        "power_watts": 500.0,
        "daily_hours": 0.7,
        "standby_watts": 2.0,
        "room_location": "Utility Area",
        "energy_star_rating": 5,
        "notes": "Inverter direct drive motor"
    },
    {
        "name": "WiFi Router & Fiber Modem",
        "category": "electronics",
        "power_watts": 12.0,
        "daily_hours": 24.0,
        "standby_watts": 0.0,
        "room_location": "Living Room",
        "energy_star_rating": 4,
        "notes": "24/7 continuous operation"
    }
]

def handle_get_presets(handler) -> None:
    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "presets": STANDARD_PRESETS
    })

def handle_get_appliances(handler) -> None:
    context = get_auth_context(handler)
    household = HouseholdModel.get_by_user_id(context["user_id"])
    if not household:
        send_error(handler, HTTPStatus.NOT_FOUND, "Household profile not found")
        return

    appliances = ApplianceModel.get_by_household(household["id"])
    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "count": len(appliances),
        "appliances": appliances
    })

def handle_create_appliance(handler) -> None:
    context = get_auth_context(handler)
    household = HouseholdModel.get_by_user_id(context["user_id"])
    if not household:
        send_error(handler, HTTPStatus.NOT_FOUND, "Household profile not found")
        return

    body = parse_json(handler)
    try:
        clean_data = validate_appliance(body)
    except ValidationError as err:
        send_error(handler, HTTPStatus.BAD_REQUEST, err.message, {"field": err.field})
        return

    # Check for duplicate appliance name within this household
    allow_duplicate = bool(body.get("allow_duplicate", False))
    duplicate = ApplianceModel.find_duplicate(household["id"], clean_data["name"])
    if duplicate and not allow_duplicate:
        send_error(
            handler,
            HTTPStatus.CONFLICT,
            f"An appliance named '{clean_data['name']}' already exists in your inventory. Choose a distinct name or check 'Allow duplicate'.",
            {"duplicate_id": duplicate["id"], "field": "name"}
        )
        return

    appliance_id = ApplianceModel.create(
        household_id=household["id"],
        name=clean_data["name"],
        category=clean_data["category"],
        power_watts=clean_data["power_watts"],
        quantity=clean_data["quantity"],
        daily_hours=clean_data["daily_hours"],
        standby_watts=clean_data["standby_watts"],
        room_location=clean_data["room_location"],
        energy_star_rating=clean_data["energy_star_rating"],
        notes=clean_data["notes"]
    )

    created = ApplianceModel.get_by_id(appliance_id, household["id"])
    send_json(handler, HTTPStatus.CREATED, {
        "success": True,
        "message": f"'{clean_data['name']}' added to detective inventory",
        "appliance": created
    })

def handle_update_appliance(handler, id: int = None, appliance_id: int = None) -> None:
    target_id = id if id is not None else appliance_id
    context = get_auth_context(handler)
    household = HouseholdModel.get_by_user_id(context["user_id"])
    if not household:
        send_error(handler, HTTPStatus.NOT_FOUND, "Household profile not found")
        return

    existing = ApplianceModel.get_by_id(target_id, household["id"])
    if not existing:
        send_error(handler, HTTPStatus.NOT_FOUND, f"Appliance with ID {target_id} not found in your household")
        return

    body = parse_json(handler)
    try:
        clean_data = validate_appliance(body)
    except ValidationError as err:
        send_error(handler, HTTPStatus.BAD_REQUEST, err.message, {"field": err.field})
        return

    # Check duplicate name with other appliances
    allow_duplicate = bool(body.get("allow_duplicate", False))
    duplicate = ApplianceModel.find_duplicate(household["id"], clean_data["name"], exclude_id=target_id)
    if duplicate and not allow_duplicate:
        send_error(
            handler,
            HTTPStatus.CONFLICT,
            f"Another appliance named '{clean_data['name']}' already exists in your inventory.",
            {"duplicate_id": duplicate["id"], "field": "name"}
        )
        return

    updated = ApplianceModel.update(
        appliance_id=target_id,
        household_id=household["id"],
        name=clean_data["name"],
        category=clean_data["category"],
        power_watts=clean_data["power_watts"],
        quantity=clean_data["quantity"],
        daily_hours=clean_data["daily_hours"],
        standby_watts=clean_data["standby_watts"],
        room_location=clean_data["room_location"],
        energy_star_rating=clean_data["energy_star_rating"],
        notes=clean_data["notes"]
    )

    if not updated:
        send_error(handler, HTTPStatus.INTERNAL_SERVER_ERROR, "Failed to update appliance")
        return

    refreshed = ApplianceModel.get_by_id(target_id, household["id"])
    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "message": f"'{clean_data['name']}' updated successfully",
        "appliance": refreshed
    })

def handle_delete_appliance(handler, id: int = None, appliance_id: int = None) -> None:
    target_id = id if id is not None else appliance_id
    context = get_auth_context(handler)
    household = HouseholdModel.get_by_user_id(context["user_id"])
    if not household:
        send_error(handler, HTTPStatus.NOT_FOUND, "Household profile not found")
        return

    existing = ApplianceModel.get_by_id(target_id, household["id"])
    if not existing:
        send_error(handler, HTTPStatus.NOT_FOUND, f"Appliance with ID {target_id} not found in your household")
        return

    ApplianceModel.delete(target_id, household["id"])
    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "message": f"Appliance '{existing['name']}' removed from detective inventory"
    })
