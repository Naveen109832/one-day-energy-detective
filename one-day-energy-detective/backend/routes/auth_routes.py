"""
Authentication API Endpoints.
Handles registration, login, profile retrieval, and session revocation.
Never leaks password hashes or salts in API responses.
"""

from http import HTTPStatus
from backend.routes.base_handler import parse_json, send_json, send_error, get_auth_context, APIError
from backend.schemas.validators import validate_registration, validate_login, ValidationError
from backend.models.user import UserModel
from backend.models.household import HouseholdModel
from backend.services.auth_service import hash_password, verify_password, create_user_session, revoke_session

def handle_register(handler) -> None:
    body = parse_json(handler)
    try:
        clean_data = validate_registration(body)
    except ValidationError as err:
        send_error(handler, HTTPStatus.BAD_REQUEST, err.message, {"field": err.field})
        return

    # Check email conflict
    existing = UserModel.get_by_email(clean_data["email"])
    if existing:
        send_error(handler, HTTPStatus.CONFLICT, "An account with this email address already exists.", {"field": "email"})
        return

    # Hash password securely
    salt_hex, hash_hex = hash_password(clean_data["password"])

    # Create user
    user_id = UserModel.create(
        email=clean_data["email"],
        password_hash=hash_hex,
        password_salt=salt_hex,
        full_name=clean_data["full_name"]
    )

    # Create household
    household_id = HouseholdModel.create(
        user_id=user_id,
        household_name=clean_data["household_name"],
        dwelling_type="apartment",
        occupants=clean_data["occupants"],
        locality_type=clean_data.get("locality_type", "urban"),
        tariff_rate=clean_data["tariff_rate"],
        currency_symbol=clean_data["currency_symbol"],
        grid_region=clean_data["grid_region"]
    )

    household = HouseholdModel.get_by_id(household_id)
    session = create_user_session(user_id)

    send_json(handler, HTTPStatus.CREATED, {
        "success": True,
        "message": "User registered successfully",
        "token": session["token"],
        "expires_at": session["expires_at"],
        "user": {
            "id": user_id,
            "email": clean_data["email"],
            "full_name": clean_data["full_name"]
        },
        "household": household
    })

def handle_login(handler) -> None:
    body = parse_json(handler)
    try:
        clean_data = validate_login(body)
    except ValidationError as err:
        send_error(handler, HTTPStatus.BAD_REQUEST, err.message, {"field": err.field})
        return

    user = UserModel.get_by_email(clean_data["email"])
    if not user:
        send_error(handler, HTTPStatus.UNAUTHORIZED, "Invalid email or password.")
        return

    # Constant-time password verification
    if not verify_password(clean_data["password"], user["password_salt"], user["password_hash"]):
        send_error(handler, HTTPStatus.UNAUTHORIZED, "Invalid email or password.")
        return

    session = create_user_session(user["id"])
    household = HouseholdModel.get_by_user_id(user["id"])

    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "message": "Logged in successfully",
        "token": session["token"],
        "expires_at": session["expires_at"],
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "created_at": user["created_at"]
        },
        "household": household
    })

def handle_me(handler) -> None:
    context = get_auth_context(handler)
    household = HouseholdModel.get_by_user_id(context["user_id"])
    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "user": {
            "id": context["user_id"],
            "email": context["email"],
            "full_name": context["full_name"]
        },
        "household": household
    })

def handle_logout(handler) -> None:
    try:
        context = get_auth_context(handler)
        revoke_session(context["token"])
    except APIError:
        pass  # Idempotent logout
    send_json(handler, HTTPStatus.OK, {
        "success": True,
        "message": "Logged out successfully"
    })
