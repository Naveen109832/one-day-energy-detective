"""
HTTP Request/Response Utilities and Authentication Guards.
Provides unified JSON responses, error formatting, CORS headers, and auth parsing.
"""

import json
from http import HTTPStatus
from typing import Dict, Any, Optional, Tuple
from backend.services.auth_service import authenticate_session

class APIError(Exception):
    def __init__(self, message: str, status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

def parse_json(handler) -> Dict[str, Any]:
    """Parses JSON request body with robust error handling."""
    content_length = int(handler.headers.get("Content-Length", 0))
    if content_length == 0:
        return {}
    
    try:
        raw_body = handler.rfile.read(content_length).decode("utf-8")
        if not raw_body.strip():
            return {}
        return json.loads(raw_body)
    except json.JSONDecodeError as err:
        raise APIError(f"Malformed JSON request payload: {err.msg}", HTTPStatus.BAD_REQUEST)
    except Exception as err:
        raise APIError(f"Failed to read request body: {str(err)}", HTTPStatus.BAD_REQUEST)

def get_auth_context(handler) -> Dict[str, Any]:
    """Extracts and validates Bearer token from Authorization header."""
    auth_header = handler.headers.get("Authorization", "")
    if not auth_header:
        raise APIError("Authorization header is missing", HTTPStatus.UNAUTHORIZED)

    parts = auth_header.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise APIError("Invalid authorization format. Expected 'Bearer <token>'", HTTPStatus.UNAUTHORIZED)

    token = parts[1]
    context = authenticate_session(token)
    if not context:
        raise APIError("Invalid or expired session token. Please log in again.", HTTPStatus.UNAUTHORIZED)

    return context

def send_json(handler, status_code: int, data: Any) -> None:
    """Sends JSON response with strict security headers."""
    payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("X-Frame-Options", "DENY")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    handler.end_headers()
    handler.wfile.write(payload)

def send_error(handler, status_code: int, message: str, details: Optional[Any] = None) -> None:
    """Sends structured error response."""
    error_body = {
        "success": False,
        "error": message,
        "status_code": status_code
    }
    if details:
        error_body["details"] = details
    send_json(handler, status_code, error_body)
