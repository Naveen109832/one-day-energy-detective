"""
Application Configuration and Constants.
Provides environment-aware settings, cryptographic secrets, database paths,
and transparently cited regional carbon emission factors.
"""

import os
import secrets
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FRONTEND_DIR = BASE_DIR / "frontend"

# Server Settings
HOST = os.getenv("APP_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", os.getenv("APP_PORT", "8000")))

# Database Settings
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "energy_detective.db"))

# Security Settings
# If SECRET_KEY is not provided in env, we load or generate a persistent secret file in DATA_DIR
SECRET_FILE = DATA_DIR / ".secret_key"
if os.getenv("APP_SECRET_KEY"):
    SECRET_KEY = os.getenv("APP_SECRET_KEY")
elif SECRET_FILE.exists():
    SECRET_KEY = SECRET_FILE.read_text(encoding="utf-8").strip()
else:
    SECRET_KEY = secrets.token_hex(32)
    SECRET_FILE.write_text(SECRET_KEY, encoding="utf-8")

SESSION_DURATION_SECONDS = int(os.getenv("SESSION_DURATION_SECONDS", str(24 * 3600)))  # 24 hours
PASSWORD_SALT_BYTES = 16
PBKDF2_ITERATIONS = 100_000

# Transparent Regional Grid Carbon Emission Factors (kg CO2e per kWh)
# With strict citations to prevent invented statistics
EMISSION_FACTORS = {
    "india_cea": {
        "region_name": "India (National Grid Average)",
        "factor_kg_per_kwh": 0.716,
        "source": "Central Electricity Authority (CEA) CO2 Baseline Database for Indian Power Sector v20",
        "currency_symbol": "₹",
        "default_tariff": 7.50
    },
    "us_egrid": {
        "region_name": "United States (eGRID National Average)",
        "factor_kg_per_kwh": 0.386,
        "source": "US EPA eGRID2024 Summary Tables (Released 2024)",
        "currency_symbol": "$",
        "default_tariff": 0.17
    },
    "uk_desnz": {
        "region_name": "United Kingdom (Grid Average)",
        "factor_kg_per_kwh": 0.207,
        "source": "UK Department for Energy Security and Net Zero (DESNZ) 2024 Factors",
        "currency_symbol": "£",
        "default_tariff": 0.28
    },
    "eu_eea": {
        "region_name": "European Union (EU-27 Average)",
        "factor_kg_per_kwh": 0.230,
        "source": "European Environment Agency (EEA) Greenhouse Gas Emission Intensity 2024",
        "currency_symbol": "€",
        "default_tariff": 0.25
    },
    "custom": {
        "region_name": "Custom User-Specified Grid",
        "factor_kg_per_kwh": 0.500,
        "source": "User-defined localized utility factor",
        "currency_symbol": "$",
        "default_tariff": 0.15
    }
}

DEFAULT_REGION = "india_cea"
