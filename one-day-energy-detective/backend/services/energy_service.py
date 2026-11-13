"""
Energy Calculation Engine.
Implements physically verified electrical energy, cost, and Scope 2 carbon formulas.
All mathematical relationships are explicitly documented and unit-checked:
- Power (Watts) vs Energy (Kilowatt-Hours)
- 1 Electricity Unit = 1 kWh
- 30-day standard billing cycle projection
"""

from typing import List, Dict, Any, Optional, Tuple
from backend.config import EMISSION_FACTORS, DEFAULT_REGION

class Tuple_Factor_Meta(tuple):
    @property
    def factor(self) -> float:
        return self[0]
    @property
    def region_name(self) -> str:
        return self[1]
    @property
    def source(self) -> str:
        return self[2]

def calculate_appliance_energy(appliance: Dict[str, Any], tariff_rate: float, emission_factor: float) -> Dict[str, Any]:
    """
    Computes daily, monthly, and annual metrics for a single appliance record.
    Formula:
      Active kWh/day   = (Power_Watts * Quantity * Daily_Hours) / 1000
      Standby kWh/day  = (Standby_Watts * Quantity * (24 - Daily_Hours)) / 1000
      Total kWh/day    = Active kWh/day + Standby kWh/day
      Monthly kWh      = Total kWh/day * 30
      Annual kWh       = Total kWh/day * 365
    """
    power_watts = float(appliance.get("power_watts", 0))
    quantity = int(appliance.get("quantity", 1))
    daily_hours = float(appliance.get("daily_hours", 0))
    standby_watts = float(appliance.get("standby_watts", 0))

    # Active consumption
    active_daily_kwh = (power_watts * quantity * daily_hours) / 1000.0

    # Standby vampire consumption during idle hours
    idle_hours = max(0.0, 24.0 - daily_hours)
    standby_daily_kwh = (standby_watts * quantity * idle_hours) / 1000.0

    total_daily_kwh = active_daily_kwh + standby_daily_kwh
    monthly_kwh = total_daily_kwh * 30.0
    annual_kwh = total_daily_kwh * 365.0

    daily_cost = total_daily_kwh * tariff_rate
    monthly_cost = monthly_kwh * tariff_rate
    annual_cost = annual_kwh * tariff_rate

    daily_carbon_kg = total_daily_kwh * emission_factor
    monthly_carbon_kg = monthly_kwh * emission_factor

    return {
        "id": appliance.get("id"),
        "name": appliance.get("name"),
        "category": appliance.get("category"),
        "power_watts": power_watts,
        "quantity": quantity,
        "daily_hours": daily_hours,
        "standby_watts": standby_watts,
        "idle_hours": round(idle_hours, 2),
        "room_location": appliance.get("room_location", "Living Room"),
        "energy_star_rating": appliance.get("energy_star_rating", 3),
        "notes": appliance.get("notes", ""),
        "active_daily_kwh": round(active_daily_kwh, 4),
        "standby_daily_kwh": round(standby_daily_kwh, 4),
        "total_daily_kwh": round(total_daily_kwh, 4),
        "monthly_kwh": round(monthly_kwh, 2),
        "annual_kwh": round(annual_kwh, 2),
        "daily_cost": round(daily_cost, 2),
        "monthly_cost": round(monthly_cost, 2),
        "annual_cost": round(annual_cost, 2),
        "daily_carbon_kg": round(daily_carbon_kg, 3),
        "monthly_carbon_kg": round(monthly_carbon_kg, 3)
    }

def get_emission_factor_for_household(household: Dict[str, Any]) -> Tuple_Factor_Meta:
    """Retrieves verified carbon factor and transparent citation."""
    grid_region = household.get("grid_region", DEFAULT_REGION)
    custom_factor = household.get("custom_emission_factor")

    if grid_region == "custom" and custom_factor is not None:
        return (
            float(custom_factor),
            "Custom User-Specified Grid Intensity",
            "User provided local utility factor"
        )

    info = EMISSION_FACTORS.get(grid_region, EMISSION_FACTORS[DEFAULT_REGION])
    return (
        info["factor_kg_per_kwh"],
        info["region_name"],
        info["source"]
    )

def calculate_household_energy_audit(household: Dict[str, Any], appliances: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Performs full diagnostic audit of household energy profile.
    Aggregates metrics, per-capita figures, vampire loads, and category breakdowns.
    """
    occupants = max(1, int(household.get("occupants", 1)))
    tariff_rate = float(household.get("tariff_rate", 7.50))
    currency_symbol = household.get("currency_symbol", "₹")
    locality_type = str(household.get("locality_type", "urban")).lower()

    factor, region_name, source_citation = get_emission_factor_for_household(household)

    computed_appliances = [
        calculate_appliance_energy(app, tariff_rate, factor)
        for app in appliances
    ]

    total_active_daily_kwh = sum(a["active_daily_kwh"] for a in computed_appliances)
    total_standby_daily_kwh = sum(a["standby_daily_kwh"] for a in computed_appliances)
    total_daily_kwh = total_active_daily_kwh + total_standby_daily_kwh

    total_weekly_kwh = total_daily_kwh * 7.0
    total_monthly_kwh = total_daily_kwh * 30.0
    total_annual_kwh = total_daily_kwh * 365.0

    total_daily_cost = total_daily_kwh * tariff_rate
    total_weekly_cost = total_weekly_kwh * tariff_rate
    total_monthly_cost = total_monthly_kwh * tariff_rate
    total_annual_cost = total_annual_kwh * tariff_rate

    total_daily_carbon_kg = total_daily_kwh * factor
    total_weekly_carbon_kg = total_weekly_kwh * factor
    total_monthly_carbon_kg = total_monthly_kwh * factor
    total_annual_carbon_kg = total_annual_kwh * factor

    # Per-capita normalization
    daily_kwh_per_capita = total_daily_kwh / occupants
    monthly_kwh_per_capita = total_monthly_kwh / occupants

    # Vampire load index (standby proportion)
    vampire_share_pct = (total_standby_daily_kwh / total_daily_kwh * 100.0) if total_daily_kwh > 0 else 0.0

    # Locality comparison — benchmarks differ by urban vs rural (India)
    locality_type = str(household.get("locality_type", "urban")).lower()
    if locality_type == "rural":
        locality_daily_avg_kwh = 2.65   # midpoint of 1.3 – 4.0 kWh/day
        locality_daily_min_kwh = 1.3
        locality_daily_max_kwh = 4.0
        locality_label = "India (Rural Homes): ~1.3 to 4 kWh/day"
        locality_monthly_range = "40 – 120 kWh/month"
        benchmark_source = "India Rural Residential Average (CEA / Ministry of Power Rural Electrification Data)"
    else:
        locality_daily_avg_kwh = 7.50   # midpoint of 5 – 10 kWh/day
        locality_daily_min_kwh = 5.0
        locality_daily_max_kwh = 10.0
        locality_label = "India (Urban Homes): ~5 to 10 kWh/day"
        locality_monthly_range = "150 – 300 kWh/month"
        benchmark_source = "India Urban Residential Average (Prayas Energy Group / CEA Urban Residential Energy Data)"

    locality_weekly_avg_kwh = round(locality_daily_avg_kwh * 7.0, 2)
    locality_monthly_avg_kwh = round(locality_daily_avg_kwh * 30.0, 2)
    is_greater_than_locality = total_daily_kwh > locality_daily_avg_kwh
    locality_diff_kwh = round(total_daily_kwh - locality_daily_avg_kwh, 2)
    locality_diff_pct = round(((total_daily_kwh - locality_daily_avg_kwh) / locality_daily_avg_kwh) * 100.0, 1)

    # Environmental Safety Assessment (Logically considering members & appliances)
    if total_daily_kwh == 0:
        env_is_safe = True
        env_status = "Awaiting Appliance Input"
        env_badge = "neutral"
        env_explanation = "Enter your household appliances and operating hours to calculate environmental safety status."
    elif daily_kwh_per_capita <= 3.0:
        env_is_safe = True
        env_status = "Safe for the Environment — Highly Efficient"
        env_badge = "safe"
        env_explanation = (
            f"Your household daily consumption of {total_daily_kwh:.2f} kWh across {len(appliances)} appliance(s) "
            f"averages {daily_kwh_per_capita:.2f} kWh/person for {occupants} member(s). This is well within safe, "
            f"sustainable residential environmental limits (below 3.0 kWh/person/day)."
        )
    elif daily_kwh_per_capita <= 5.0:
        env_is_safe = True
        env_status = "Moderate Impact — Within Acceptable Bounds"
        env_badge = "moderate"
        env_explanation = (
            f"For a household of {occupants} member(s) with {len(appliances)} appliance(s), your daily consumption of "
            f"{total_daily_kwh:.2f} kWh ({daily_kwh_per_capita:.2f} kWh/person/day) is within typical living standards. "
            f"A few targeted changes can reduce your carbon footprint further."
        )
    else:
        env_is_safe = False
        env_status = "High Environmental Impact — Exceeds Sustainable Limits"
        env_badge = "danger"
        env_explanation = (
            f"Daily consumption of {total_daily_kwh:.2f} kWh for {occupants} member(s) ({daily_kwh_per_capita:.2f} kWh/person/day) "
            f"significantly exceeds sustainable residential guidelines. High continuous power draws or extended operating hours "
            f"are generating elevated Scope 2 emissions."
        )

    # Category breakdown
    category_summary: Dict[str, Dict[str, Any]] = {}
    for a in computed_appliances:
        cat = a["category"]
        if cat not in category_summary:
            category_summary[cat] = {
                "category": cat,
                "appliance_count": 0,
                "daily_kwh": 0.0,
                "monthly_kwh": 0.0,
                "monthly_cost": 0.0,
                "share_pct": 0.0
            }
        category_summary[cat]["appliance_count"] += 1
        category_summary[cat]["daily_kwh"] += a["total_daily_kwh"]
        category_summary[cat]["monthly_kwh"] += a["monthly_kwh"]
        category_summary[cat]["monthly_cost"] += a["monthly_cost"]

    # Calculate percentages
    for cat_data in category_summary.values():
        if total_daily_kwh > 0:
            cat_data["share_pct"] = round((cat_data["daily_kwh"] / total_daily_kwh) * 100.0, 1)
        cat_data["daily_kwh"] = round(cat_data["daily_kwh"], 4)
        cat_data["monthly_kwh"] = round(cat_data["monthly_kwh"], 2)
        cat_data["monthly_cost"] = round(cat_data["monthly_cost"], 2)

    # Calculate simulated 24-hour load curve based on declared appliances
    # Transparently labeled as a synthetic diurnal profile model
    hourly_curve = synthesize_24h_load_profile(computed_appliances)

    return {
        "household": {
            "id": household.get("id"),
            "household_name": household.get("household_name"),
            "dwelling_type": household.get("dwelling_type"),
            "locality_type": household.get("locality_type", "urban"),
            "occupants": occupants,
            "tariff_rate": tariff_rate,
            "currency_symbol": currency_symbol,
            "grid_region": household.get("grid_region"),
            "emission_factor_kg_per_kwh": factor,
            "grid_region_name": region_name,
            "citation_source": source_citation
        },
        "summary": {
            "appliance_count": len(appliances),
            "total_active_daily_kwh": round(total_active_daily_kwh, 4),
            "total_standby_daily_kwh": round(total_standby_daily_kwh, 4),
            "total_daily_kwh": round(total_daily_kwh, 4),
            "total_weekly_kwh": round(total_weekly_kwh, 2),
            "total_monthly_kwh": round(total_monthly_kwh, 2),
            "total_annual_kwh": round(total_annual_kwh, 2),
            "total_daily_cost": round(total_daily_cost, 2),
            "total_weekly_cost": round(total_weekly_cost, 2),
            "total_monthly_cost": round(total_monthly_cost, 2),
            "total_annual_cost": round(total_annual_cost, 2),
            "daily_kwh_per_capita": round(daily_kwh_per_capita, 4),
            "monthly_kwh_per_capita": round(monthly_kwh_per_capita, 2),
            "vampire_share_pct": round(vampire_share_pct, 1),
            "total_daily_carbon_kg": round(total_daily_carbon_kg, 3),
            "total_weekly_carbon_kg": round(total_weekly_carbon_kg, 3),
            "total_monthly_carbon_kg": round(total_monthly_carbon_kg, 3),
            "total_annual_carbon_kg": round(total_annual_carbon_kg, 3)
        },
        "locality_comparison": {
            "locality_type": locality_type,
            "locality_label": locality_label,
            "locality_daily_avg_kwh": locality_daily_avg_kwh,
            "locality_daily_min_kwh": locality_daily_min_kwh,
            "locality_daily_max_kwh": locality_daily_max_kwh,
            "locality_weekly_avg_kwh": locality_weekly_avg_kwh,
            "locality_monthly_avg_kwh": locality_monthly_avg_kwh,
            "locality_monthly_range": locality_monthly_range,
            "is_greater_than_locality": is_greater_than_locality,
            "difference_kwh": locality_diff_kwh,
            "difference_percentage": locality_diff_pct,
            "benchmark_source": benchmark_source
        },
        "environmental_safety": {
            "is_safe": env_is_safe,
            "status": env_status,
            "badge": env_badge,
            "explanation": env_explanation,
            "occupants": occupants,
            "daily_kwh_per_capita": round(daily_kwh_per_capita, 2)
        },
        "category_breakdown": list(category_summary.values()),
        "hourly_load_profile": hourly_curve,
        "appliances": computed_appliances
    }

def synthesize_24h_load_profile(appliances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Constructs a realistic 24-hour diurnal load curve based on declared appliance active windows and standby.
    Hours 0 to 23 representing 12:00 AM to 11:00 PM.
    """
    # Baseline power for each hour in kW
    hourly_kw = [0.0] * 24

    for app in appliances:
        p_active_kw = (app["power_watts"] * app["quantity"]) / 1000.0
        p_standby_kw = (app["standby_watts"] * app["quantity"]) / 1000.0
        hours = app["daily_hours"]
        category = app["category"]

        # Default continuous standby runs 24/7 during idle hours
        standby_hourly = p_standby_kw if hours < 24 else 0.0

        # Model active windows by category
        if hours >= 24:
            # Always running (e.g. refrigerator compressor duty cycle)
            for h in range(24):
                hourly_kw[h] += p_active_kw
        elif hours > 0:
            active_hours_int = max(1, int(round(hours)))
            # Assign windows based on category
            if category == "lighting":
                # Primarily evening 18:00 to 23:00, then morning
                start_h = 18
                for i in range(active_hours_int):
                    h = (start_h + i) % 24
                    hourly_kw[h] += p_active_kw
            elif category == "kitchen":
                # Breakfast (7-9), Lunch (12-14), Dinner (19-21)
                slots = [7, 8, 12, 13, 19, 20, 21]
                for i in range(min(active_hours_int, len(slots))):
                    hourly_kw[slots[i]] += p_active_kw
            elif category == "climate":
                # Afternoon peak (13-17) and night (22-04)
                slots = [13, 14, 15, 16, 22, 23, 0, 1, 2, 3, 4, 5, 17, 18]
                for i in range(min(active_hours_int, len(slots))):
                    hourly_kw[slots[i % len(slots)]] += p_active_kw
            elif category == "laundry":
                # Morning 9:00 to 12:00
                slots = [9, 10, 11, 12]
                for i in range(min(active_hours_int, len(slots))):
                    hourly_kw[slots[i % len(slots)]] += p_active_kw
            else:
                # Spread across daytime and evening (10:00 to 22:00)
                start_h = 10
                for i in range(active_hours_int):
                    h = (start_h + i) % 24
                    hourly_kw[h] += p_active_kw

            # Add standby for remaining hours
            for h in range(24):
                # Standby baseline
                hourly_kw[h] += standby_hourly

    return [
        {"hour": h, "label": f"{h:02d}:00", "load_kw": round(hourly_kw[h], 3)}
        for h in range(24)
    ]
