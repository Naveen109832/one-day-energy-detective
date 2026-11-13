"""
Household Management API Endpoints.
Ensures a user can only view and update their own household configuration.
"""

from http import HTTPStatus
from backend.routes.base_handler import parse_json, send_json, send_error, get_auth_context
from backend.schemas.validators import validate_household, ValidationError
from backend.models.household import HouseholdModel
from backend.config import EMISSION_FACTORS

def handle_get_household(handler) -> None:
    context = get_auth_context(handler)
    household = HouseholdModel.get_by_user_id(context["user_id"])
    if not household:
        send_error(handler, HTTPStatus.NOT_FOUND, "Household profile not found")
        return

    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "household": household,
        "available_regions": EMISSION_FACTORS
    })

def handle_update_household(handler) -> None:
    context = get_auth_context(handler)
    household = HouseholdModel.get_by_user_id(context["user_id"])
    if not household:
        send_error(handler, HTTPStatus.NOT_FOUND, "Household profile not found")
        return

    body = parse_json(handler)
    try:
        clean_data = validate_household(body)
    except ValidationError as err:
        send_error(handler, HTTPStatus.BAD_REQUEST, err.message, {"field": err.field})
        return

    updated = HouseholdModel.update(
        household_id=household["id"],
        user_id=context["user_id"],
        household_name=clean_data["household_name"],
        dwelling_type=clean_data["dwelling_type"],
        occupants=clean_data["occupants"],
        locality_type=clean_data.get("locality_type", "urban"),
        tariff_rate=clean_data["tariff_rate"],
        currency_symbol=clean_data["currency_symbol"],
        grid_region=clean_data["grid_region"],
        custom_emission_factor=clean_data["custom_emission_factor"]
    )

    if not updated:
        send_error(handler, HTTPStatus.INTERNAL_SERVER_ERROR, "Failed to update household settings")
        return

    fresh = HouseholdModel.get_by_id(household["id"])
    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "message": "Household settings updated successfully",
        "household": fresh
    })
