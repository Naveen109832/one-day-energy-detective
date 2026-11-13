"""
Test Suite: End-to-End REST API Routing and Request Handling.
Verifies all HTTP endpoints, status codes, payload handling, and auth barriers.
"""

import time
import json
import unittest
from io import BytesIO
from http import HTTPStatus
from unittest.mock import MagicMock

from backend.routes import dispatch_api_request
from backend.database import init_db

class DummyHandler:
    """Mock handler simulating SimpleHTTPRequestHandler for direct route testing."""
    def __init__(self, method: str, path: str, body: dict = None, headers: dict = None):
        self.command = method
        self.path = path
        self.headers = headers or {}
        self.status_code = None
        self.response_headers = {}
        
        body_bytes = json.dumps(body).encode("utf-8") if body is not None else b""
        self.headers["Content-Length"] = str(len(body_bytes))
        self.rfile = BytesIO(body_bytes)
        self.wfile = BytesIO()

    def send_response(self, code, message=None):
        self.status_code = code

    def send_header(self, keyword, value):
        self.response_headers[keyword] = value

    def end_headers(self):
        pass

    def get_json_response(self):
        self.wfile.seek(0)
        content = self.wfile.read().decode("utf-8")
        return json.loads(content) if content else {}

class TestAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_end_to_end_api_flow(self):
        test_id = int(time.time() * 1000)
        # 1. Register a new user
        reg_payload = {
            "email": f"detective_{test_id}@energy.org",
            "password": "strongPassword#42",
            "full_name": "Detective Miller",
            "household_name": "Miller Residence",
            "occupants": 3,
            "tariff_rate": 7.50,
            "currency_symbol": "₹",
            "grid_region": "india_cea"
        }
        h_reg = DummyHandler("POST", "/api/auth/register", reg_payload)
        dispatched = dispatch_api_request(h_reg, "POST", "/api/auth/register")
        self.assertTrue(dispatched)
        self.assertEqual(h_reg.status_code, HTTPStatus.CREATED)

        # 2. Log in
        login_payload = {
            "email": f"detective_{test_id}@energy.org",
            "password": "strongPassword#42"
        }
        h_login = DummyHandler("POST", "/api/auth/login", login_payload)
        dispatch_api_request(h_login, "POST", "/api/auth/login")
        self.assertEqual(h_login.status_code, HTTPStatus.OK)
        login_res = h_login.get_json_response()
        self.assertTrue(login_res["success"])
        token = login_res["token"]
        self.assertTrue(bool(token))

        auth_headers = {"Authorization": f"Bearer {token}"}

        # 3. Get presets
        h_presets = DummyHandler("GET", "/api/appliances/presets", headers=auth_headers)
        dispatch_api_request(h_presets, "GET", "/api/appliances/presets")
        self.assertEqual(h_presets.status_code, HTTPStatus.OK)
        presets_res = h_presets.get_json_response()
        self.assertGreater(len(presets_res["presets"]), 5)

        # 4. Add Appliance: Air Conditioner
        ac_payload = {
            "name": f"Master Inverter AC {test_id}",
            "category": "climate",
            "power_watts": 1500.0,
            "quantity": 1,
            "daily_hours": 6.0,
            "standby_watts": 4.0,
            "room_location": "Bedroom",
            "energy_star_rating": 4,
            "notes": "Verified inverter"
        }
        h_add = DummyHandler("POST", "/api/appliances", ac_payload, auth_headers)
        dispatch_api_request(h_add, "POST", "/api/appliances")
        self.assertEqual(h_add.status_code, HTTPStatus.CREATED)
        app_res = h_add.get_json_response()
        app_id = app_res["appliance"]["id"]

        # 5. Duplicate Appliance detection
        h_dup = DummyHandler("POST", "/api/appliances", ac_payload, auth_headers)
        dispatch_api_request(h_dup, "POST", "/api/appliances")
        self.assertEqual(h_dup.status_code, HTTPStatus.CONFLICT)

        # 6. Fetch Summary
        h_sum = DummyHandler("GET", "/api/audit/summary", headers=auth_headers)
        dispatch_api_request(h_sum, "GET", "/api/audit/summary")
        self.assertEqual(h_sum.status_code, HTTPStatus.OK)
        audit_res = h_sum.get_json_response()
        self.assertGreater(audit_res["audit"]["summary"]["total_daily_kwh"], 0)

        # 7. Fetch Detective Findings & Recommendations
        h_case = DummyHandler("GET", "/api/audit/detective-case", headers=auth_headers)
        dispatch_api_request(h_case, "GET", "/api/audit/detective-case")
        self.assertEqual(h_case.status_code, HTTPStatus.OK)
        case_res = h_case.get_json_response()
        self.assertIn("detective_case", case_res)
        recs = case_res["detective_case"]["recommendations"]
        self.assertTrue(any("AC" in r["action_title"] or "Climate" in r["category"] for r in recs))

        # 8. Simulate optimization
        sim_payload = {
            "modifications": [
                {"id": app_id, "daily_hours": 4.0}
            ]
        }
        h_sim = DummyHandler("POST", "/api/audit/simulate", sim_payload, auth_headers)
        dispatch_api_request(h_sim, "POST", "/api/audit/simulate")
        self.assertEqual(h_sim.status_code, HTTPStatus.OK)
        sim_res = h_sim.get_json_response()
        savings = sim_res["simulation"]["estimated_savings"]
        self.assertGreater(savings["saved_monthly_cost"], 0)

        # 9. Clean up: Delete Appliance
        h_del = DummyHandler("DELETE", f"/api/appliances/{app_id}", headers=auth_headers)
        dispatch_api_request(h_del, "DELETE", f"/api/appliances/{app_id}")
        self.assertEqual(h_del.status_code, HTTPStatus.OK)

    def test_unauthorized_barrier(self):
        # Accessing protected endpoint without Bearer token must return 401
        h_unauth = DummyHandler("GET", "/api/household")
        dispatch_api_request(h_unauth, "GET", "/api/household")
        self.assertEqual(h_unauth.status_code, HTTPStatus.UNAUTHORIZED)

if __name__ == "__main__":
    unittest.main()
