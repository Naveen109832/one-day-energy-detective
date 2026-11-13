"""
Central API Route Dispatcher.
Routes incoming HTTP requests to corresponding domain handlers.
Provides robust URL pattern matching, CORS preflight handling, and exception recovery.
"""

import re
from http import HTTPStatus
from typing import Callable, Dict, Any, List, Tuple

from backend.routes.base_handler import send_json, send_error, APIError
from backend.routes.auth_routes import handle_register, handle_login, handle_me, handle_logout
from backend.routes.household_routes import handle_get_household, handle_update_household
from backend.routes.appliance_routes import (
    handle_get_presets,
    handle_get_appliances,
    handle_create_appliance,
    handle_update_appliance,
    handle_delete_appliance
)
from backend.routes.audit_routes import (
    handle_get_summary,
    handle_get_detective_case,
    handle_simulate
)

# Route registry: list of (method, regex_pattern, handler_func, param_names)
ROUTES: List[Tuple[str, re.Pattern, Callable, List[str]]] = [
    # Auth
    ("POST", re.compile(r"^/api/auth/register$"), handle_register, []),
    ("POST", re.compile(r"^/api/auth/login$"), handle_login, []),
    ("GET", re.compile(r"^/api/auth/me$"), handle_me, []),
    ("POST", re.compile(r"^/api/auth/logout$"), handle_logout, []),

    # Household
    ("GET", re.compile(r"^/api/household$"), handle_get_household, []),
    ("PUT", re.compile(r"^/api/household$"), handle_update_household, []),

    # Appliances
    ("GET", re.compile(r"^/api/appliances/presets$"), handle_get_presets, []),
    ("GET", re.compile(r"^/api/appliances$"), handle_get_appliances, []),
    ("POST", re.compile(r"^/api/appliances$"), handle_create_appliance, []),
    ("PUT", re.compile(r"^/api/appliances/(?P<id>\d+)$"), handle_update_appliance, ["id"]),
    ("DELETE", re.compile(r"^/api/appliances/(?P<id>\d+)$"), handle_delete_appliance, ["id"]),

    # Audit & Detective
    ("GET", re.compile(r"^/api/audit/summary$"), handle_get_summary, []),
    ("GET", re.compile(r"^/api/audit/detective-case$"), handle_get_detective_case, []),
    ("POST", re.compile(r"^/api/audit/simulate$"), handle_simulate, []),
]

def dispatch_api_request(handler, method: str, path: str) -> bool:
    """
    Dispatches request to matching route handler.
    Returns True if route was handled, False if path is not an API route.
    """
    if not path.startswith("/api/"):
        return False

    # Handle CORS preflight
    if method == "OPTIONS":
        handler.send_response(HTTPStatus.NO_CONTENT)
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        handler.send_header("Access-Control-Max-Age", "86400")
        handler.end_headers()
        return True

    clean_path = path.split("?")[0].rstrip("/")
    if clean_path == "/api":
        send_json(handler, HTTPStatus.OK, {
            "name": "One-Day Energy Detective API",
            "version": "1.0.0",
            "status": "healthy"
        })
        return True

    for route_method, pattern, route_handler, param_names in ROUTES:
        if route_method == method:
            match = pattern.match(clean_path)
            if match:
                try:
                    kwargs = {}
                    for param_name in param_names:
                        val = match.group(param_name)
                        if param_name == "id":
                            val = int(val)
                        kwargs[param_name] = val
                    
                    if kwargs:
                        route_handler(handler, **kwargs)
                    else:
                        route_handler(handler)
                except APIError as api_err:
                    send_error(handler, api_err.status_code, api_err.message, api_err.details)
                except Exception as ex:
                    send_error(handler, HTTPStatus.INTERNAL_SERVER_ERROR, f"Internal Server Error: {str(ex)}")
                return True

    # If API endpoint matched no route
    send_error(handler, HTTPStatus.NOT_FOUND, f"API route '{method} {clean_path}' not found")
    return True
