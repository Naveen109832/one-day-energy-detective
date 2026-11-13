"""
Energy Audit and Detective Case API Endpoints.
Calculates authentic household electricity statistics, culprit rankings,
and simulation scenarios using real user data.
"""

from http import HTTPStatus
from backend.routes.base_handler import parse_json, send_json, send_error, get_auth_context
from backend.models.household import HouseholdModel
from backend.models.appliance import ApplianceModel
from backend.services.energy_service import calculate_household_energy_audit
from backend.services.detective_service import analyze_detective_findings, simulate_energy_scenario

def handle_get_summary(handler) -> None:
    context = get_auth_context(handler)
    household = HouseholdModel.get_by_user_id(context["user_id"])
    if not household:
        send_error(handler, HTTPStatus.NOT_FOUND, "Household profile not found")
        return

    appliances = ApplianceModel.get_by_household(household["id"])
    audit_data = calculate_household_energy_audit(household, appliances)
    
    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "audit": audit_data
    })

def handle_get_detective_case(handler) -> None:
    context = get_auth_context(handler)
    household = HouseholdModel.get_by_user_id(context["user_id"])
    if not household:
        send_error(handler, HTTPStatus.NOT_FOUND, "Household profile not found")
        return

    appliances = ApplianceModel.get_by_household(household["id"])
    audit_data = calculate_household_energy_audit(household, appliances)
    detective_case = analyze_detective_findings(audit_data)

    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "detective_case": detective_case
    })

def handle_simulate(handler) -> None:
    context = get_auth_context(handler)
    household = HouseholdModel.get_by_user_id(context["user_id"])
    if not household:
        send_error(handler, HTTPStatus.NOT_FOUND, "Household profile not found")
        return

    body = parse_json(handler)
    modifications = body.get("modifications", [])
    if not isinstance(modifications, list):
        send_error(handler, HTTPStatus.BAD_REQUEST, "Field 'modifications' must be a list of modifications")
        return

    appliances = ApplianceModel.get_by_household(household["id"])
    base_audit = calculate_household_energy_audit(household, appliances)
    
    simulation_result = simulate_energy_scenario(base_audit, modifications)
    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "simulation": simulation_result
    })
