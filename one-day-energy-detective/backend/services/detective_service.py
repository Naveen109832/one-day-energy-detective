"""
Detective Diagnostic & Recommendation Engine.
Analyzes user appliances to uncover top energy culprits, quantify vampire loads,
and generate dynamic, mathematically-grounded efficiency recommendations.
Strictly generates recommendations tailored to actual user inventory.
"""

from typing import List, Dict, Any, Optional

def analyze_detective_findings(audit_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates audit results to identify primary suspects, vampire drains,
    and calculates an objective audit efficiency rating.
    """
    appliances = audit_data.get("appliances", [])
    summary = audit_data.get("summary", {})
    household = audit_data.get("household", {})
    
    total_daily_kwh = summary.get("total_daily_kwh", 0.0)
    occupants = household.get("occupants", 1)
    daily_kwh_per_capita = summary.get("daily_kwh_per_capita", 0.0)
    vampire_share_pct = summary.get("vampire_share_pct", 0.0)
    tariff_rate = household.get("tariff_rate", 7.50)
    currency_symbol = household.get("currency_symbol", "₹")

    # 1. Rank Suspects (Top Energy Consumers)
    sorted_appliances = sorted(appliances, key=lambda a: a["total_daily_kwh"], reverse=True)
    culprits = []
    for app in sorted_appliances[:5]:
        share = round((app["total_daily_kwh"] / total_daily_kwh * 100.0), 1) if total_daily_kwh > 0 else 0.0
        culprits.append({
            "id": app["id"],
            "name": app["name"],
            "category": app["category"],
            "room_location": app["room_location"],
            "daily_kwh": app["total_daily_kwh"],
            "monthly_kwh": app["monthly_kwh"],
            "monthly_cost": app["monthly_cost"],
            "share_of_household_pct": share,
            "power_watts": app["power_watts"],
            "daily_hours": app["daily_hours"],
            "is_dominant": share >= 25.0
        })

    # 2. Identify Vampire Drains (High Standby Loads)
    vampire_drains = []
    for app in appliances:
        standby_w = app.get("standby_watts", 0.0)
        standby_kwh = app.get("standby_daily_kwh", 0.0)
        idle_hours = app.get("idle_hours", 0.0)
        if standby_w >= 3.0 and standby_kwh > 0:
            annual_standby_cost = standby_kwh * 365.0 * tariff_rate
            vampire_drains.append({
                "id": app["id"],
                "name": app["name"],
                "standby_watts": standby_w,
                "idle_hours": idle_hours,
                "daily_standby_kwh": standby_kwh,
                "monthly_standby_kwh": round(standby_kwh * 30.0, 2),
                "annual_standby_cost": round(annual_standby_cost, 2),
                "severity": "high" if standby_w >= 10.0 else "medium"
            })
    vampire_drains.sort(key=lambda v: v["daily_standby_kwh"], reverse=True)

    # 3. Objective Detective Efficiency Rating
    # Evaluates per-capita daily kWh benchmark and vampire loss ratio:
    # Benchmark basis: Typical urban electrified dwelling ~3 to 5 kWh/person/day
    if total_daily_kwh == 0:
        rating = "Pending Audit"
        rating_color = "gray"
        verdict = "No appliances logged yet. Add your household appliances to initiate the energy investigation."
    elif daily_kwh_per_capita <= 3.0 and vampire_share_pct <= 8.0:
        rating = "Grade A — Detective Commendation"
        rating_color = "emerald"
        verdict = f"High electrical efficiency observed at {daily_kwh_per_capita:.2f} kWh/person/day. Standby losses are well-contained."
    elif daily_kwh_per_capita <= 5.5 and vampire_share_pct <= 15.0:
        rating = "Grade B — Balanced Operation"
        rating_color = "teal"
        verdict = f"Standard consumption profile ({daily_kwh_per_capita:.2f} kWh/person/day). Targeted tuning can unlock notable savings."
    elif daily_kwh_per_capita <= 8.5:
        rating = "Grade C — Elevated Drain Detected"
        rating_color = "amber"
        verdict = f"Above-average consumption ({daily_kwh_per_capita:.2f} kWh/person/day). Prominent culprits identified requiring operational adjustments."
    else:
        rating = "Grade D — Critical Energy Leakage"
        rating_color = "rose"
        verdict = f"Heavy energy draw ({daily_kwh_per_capita:.2f} kWh/person/day). Substantial continuous or unoptimized thermal loads detected."

    # 4. Generate Dynamically Tailored Recommendations
    recommendations = generate_tailored_recommendations(appliances, tariff_rate, currency_symbol)

    return {
        "efficiency_grade": rating,
        "rating_color": rating_color,
        "detective_verdict": verdict,
        "top_culprits": culprits,
        "vampire_drains": vampire_drains,
        "recommendations": recommendations,
        "benchmark_context": {
            "household_occupants": occupants,
            "daily_kwh_per_capita": daily_kwh_per_capita,
            "benchmark_urban_range_kwh": "3.0 - 5.5 kWh/person/day",
            "citation": "Referenced against Central Electricity Authority & BEE Urban Residential Appliance Benchmarks"
        }
    }

def generate_tailored_recommendations(
    appliances: List[Dict[str, Any]],
    tariff_rate: float,
    currency_symbol: str
) -> List[Dict[str, Any]]:
    """
    Generates action items strictly derived from the user's active appliance inventory.
    Calculates estimated, non-guaranteed monthly financial and kWh savings.
    """
    recs = []

    for app in appliances:
        name_lower = app["name"].lower()
        category = app["category"]
        power_w = app["power_watts"]
        qty = app["quantity"]
        hours = app["daily_hours"]
        standby_w = app["standby_watts"]

        # 1. Air Conditioning / Climate Setpoint Optimization
        if category == "climate" or any(k in name_lower for k in ["ac", "air conditioner", "hvac", "split"]):
            if power_w >= 800 and hours >= 2:
                # Modulating setpoint by +2°C reduces compressor thermal load by ~14%
                # Ref: BEE India Energy Conservation Guidelines & ASHRAE 55
                daily_kwh_base = (power_w * qty * hours) / 1000.0
                est_saved_daily_kwh = daily_kwh_base * 0.14
                est_saved_monthly_kwh = est_saved_daily_kwh * 30.0
                est_saved_monthly_cost = est_saved_monthly_kwh * tariff_rate

                recs.append({
                    "appliance_id": app["id"],
                    "appliance_name": app["name"],
                    "category": "Climate Optimization",
                    "action_title": f"Adjust {app['name']} Setpoint to 24°C - 25°C",
                    "impact_tier": "High Impact",
                    "difficulty": "Immediate / Zero Cost",
                    "description": (
                        f"Your {app['name']} runs {hours}h/day at {power_w}W. "
                        "Raising thermostat setpoint from 20-22°C to the recommended 24°C reduces "
                        "compressor duty cycle by an estimated 12% to 15% without sacrificing comfort."
                    ),
                    "estimated_monthly_kwh_savings": round(est_saved_monthly_kwh, 2),
                    "estimated_monthly_cost_savings": round(est_saved_monthly_cost, 2),
                    "currency_symbol": currency_symbol,
                    "disclaimer": "Estimated savings based on typical compressor duty reduction; actual savings depend on room insulation and ambient temperature."
                })

        # 2. Lighting Efficiency Upgrades
        if category == "lighting" or any(k in name_lower for k in ["bulb", "lamp", "tubelight", "halogen", "incandescent"]):
            if power_w > 15:  # Standard incandescent/CFL/fluorescent draws 40W - 100W
                # Upgrade to 9W high-lumen LED
                target_w = 9.0
                saved_w = (power_w - target_w) * qty
                est_saved_daily_kwh = (saved_w * hours) / 1000.0
                est_saved_monthly_kwh = est_saved_daily_kwh * 30.0
                est_saved_monthly_cost = est_saved_monthly_kwh * tariff_rate

                recs.append({
                    "appliance_id": app["id"],
                    "appliance_name": app["name"],
                    "category": "Use LED Lighting",
                    "action_title": f"Use LED Lighting: Upgrade {qty}x {app['name']} ({power_w}W) to 9W LED",
                    "impact_tier": "Medium Impact",
                    "difficulty": "Low Cost Upgrade",
                    "description": (
                        f"Replacing {qty}x {power_w}W bulb(s) with modern 9W LED alternatives "
                        f"maintains equivalent lumen output while eliminating {saved_w:.0f} Watts of continuous draw."
                    ),
                    "estimated_monthly_kwh_savings": round(est_saved_monthly_kwh, 2),
                    "estimated_monthly_cost_savings": round(est_saved_monthly_cost, 2),
                    "currency_symbol": currency_symbol,
                    "disclaimer": "Estimated savings based on rated wattage differential and declared daily operating duration."
                })

            if hours >= 4.0:
                # Switch off unused lights habit
                saved_light_kwh = (power_w * qty * 1.5) / 1000.0
                recs.append({
                    "appliance_id": app["id"],
                    "appliance_name": app["name"],
                    "category": "Switch Off Unused Lights",
                    "action_title": f"Switch Off Unused Lights: Save on {app['name']}",
                    "impact_tier": "High Impact",
                    "difficulty": "Zero Cost / Habit",
                    "description": (
                        f"Your lighting in {app.get('room_location', 'home')} runs for {hours} hours daily. "
                        "Developing the habit of switching off lights when leaving rooms saves up to 1.5 hours of wasted illumination daily."
                    ),
                    "estimated_monthly_kwh_savings": round(saved_light_kwh * 30.0, 2),
                    "estimated_monthly_cost_savings": round(saved_light_kwh * 30.0 * tariff_rate, 2),
                    "currency_symbol": currency_symbol,
                    "disclaimer": "Savings estimated by turning off lights for 1.5 unused hours daily."
                })

        # 3. Water Heating / Geyser Management
        if any(k in name_lower for k in ["geyser", "water heater", "boiler", "immersion"]):
            if power_w >= 1000 and hours >= 1:
                # Reducing thermostat to 50°C + turning off 30m before end of use saves ~15%
                daily_kwh_base = (power_w * qty * hours) / 1000.0
                est_saved_daily_kwh = daily_kwh_base * 0.15
                est_saved_monthly_kwh = est_saved_daily_kwh * 30.0
                est_saved_monthly_cost = est_saved_monthly_kwh * tariff_rate

                recs.append({
                    "appliance_id": app["id"],
                    "appliance_name": app["name"],
                    "category": "Water Heating Efficiency",
                    "action_title": f"Optimize Heating Schedule for {app['name']}",
                    "impact_tier": "High Impact",
                    "difficulty": "Behavioral / Low Cost",
                    "description": (
                        f"{app['name']} draws {power_w}W. Setting a timer or switching off the geyser "
                        "once the tank is heated prevents standing thermal losses and avoids keeping "
                        "high-draw resistive elements engaged continuously."
                    ),
                    "estimated_monthly_kwh_savings": round(est_saved_monthly_kwh, 2),
                    "estimated_monthly_cost_savings": round(est_saved_monthly_cost, 2),
                    "currency_symbol": currency_symbol,
                    "disclaimer": "Estimated savings based on reduced thermal standing losses and cycle runtime."
                })

        # 4. Standby Vampire Load Elimination
        if standby_w >= 5.0 and hours < 24:
            idle_h = 24.0 - hours
            est_saved_daily_kwh = (standby_w * qty * idle_h) / 1000.0
            est_saved_monthly_kwh = est_saved_daily_kwh * 30.0
            est_saved_monthly_cost = est_saved_monthly_kwh * tariff_rate

            recs.append({
                "appliance_id": app["id"],
                "appliance_name": app["name"],
                "category": "Avoid Unnecessary Standby Operation",
                "action_title": f"Avoid Unnecessary Standby: Unplug {app['name']} ({standby_w}W)",
                "impact_tier": "Medium Impact",
                "difficulty": "Immediate / Smart Strip",
                "description": (
                    f"{app['name']} continues drawing {standby_w}W during its {idle_h:.1f} idle hours every day. "
                    "Avoid unnecessary standby operation by switching off the wall socket or using a smart power strip to eliminate phantom load."
                ),
                "estimated_monthly_kwh_savings": round(est_saved_monthly_kwh, 2),
                "estimated_monthly_cost_savings": round(est_saved_monthly_cost, 2),
                "currency_symbol": currency_symbol,
                "disclaimer": "Estimated savings calculated directly from declared standby wattage during idle hours."
            })

        # 5. Maintain Appliances Properly (Fridge / AC)
        if category == "kitchen" and any(k in name_lower for k in ["fridge", "refrigerator"]):
            if power_w >= 180:
                est_saved_monthly_kwh = round((power_w * 24 / 1000.0) * 0.10 * 30, 2)
                est_saved_monthly_cost = round(est_saved_monthly_kwh * tariff_rate, 2)
                recs.append({
                    "appliance_id": app["id"],
                    "appliance_name": app["name"],
                    "category": "Maintain Appliances Properly",
                    "action_title": f"Maintain Properly: Clean Coils & Door Seal on {app['name']}",
                    "impact_tier": "Medium Impact",
                    "difficulty": "Maintenance",
                    "description": (
                        f"Refrigeration compressor efficiency degrades when rear coils gather dust or door gaskets leak cold air. "
                        "Routine vacuuming and seal inspection restores optimal heat transfer and prevents excessive compressor cycling."
                    ),
                    "estimated_monthly_kwh_savings": est_saved_monthly_kwh,
                    "estimated_monthly_cost_savings": est_saved_monthly_cost,
                    "currency_symbol": currency_symbol,
                    "disclaimer": "Estimated savings assume baseline 10% compressor duty reduction through standard maintenance."
                })

    # Keep only essential advice: ignore trivial savings, one tip per type
    # (the strongest), highest savings first, at most 3 in total.
    recs = [r for r in recs if r["estimated_monthly_kwh_savings"] >= 1.0]
    recs.sort(key=lambda r: r["estimated_monthly_cost_savings"], reverse=True)
    essential, seen = [], set()
    for r in recs:
        if r["category"] in seen:
            continue
        seen.add(r["category"])
        essential.append(r)
    return essential[:3]

def simulate_energy_scenario(
    base_audit: Dict[str, Any],
    modifications: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Simulates the impact of efficiency modifications against the baseline audit.
    Modifications format:
      [{"id": 1, "power_watts": 9, "daily_hours": 4, "standby_watts": 0}]
    """
    household = base_audit["household"]
    tariff_rate = household["tariff_rate"]
    factor = household["emission_factor_kg_per_kwh"]

    # Clone appliances list
    mod_map = {m["id"]: m for m in modifications if "id" in m}
    simulated_appliances = []

    for app in base_audit["appliances"]:
        app_copy = dict(app)
        if app["id"] in mod_map:
            mods = mod_map[app["id"]]
            if "power_watts" in mods:
                app_copy["power_watts"] = float(mods["power_watts"])
            if "daily_hours" in mods:
                app_copy["daily_hours"] = float(mods["daily_hours"])
            if "standby_watts" in mods:
                app_copy["standby_watts"] = float(mods["standby_watts"])
            if "quantity" in mods:
                app_copy["quantity"] = int(mods["quantity"])
        simulated_appliances.append(app_copy)

    # Re-run calculations with modified parameters
    from backend.services.energy_service import calculate_household_energy_audit
    sim_audit = calculate_household_energy_audit(household, simulated_appliances)

    base_summary = base_audit["summary"]
    sim_summary = sim_audit["summary"]

    delta_daily_kwh = round(base_summary["total_daily_kwh"] - sim_summary["total_daily_kwh"], 4)
    delta_monthly_kwh = round(base_summary["total_monthly_kwh"] - sim_summary["total_monthly_kwh"], 2)
    delta_monthly_cost = round(base_summary["total_monthly_cost"] - sim_summary["total_monthly_cost"], 2)
    delta_annual_cost = round(base_summary["total_annual_cost"] - sim_summary["total_annual_cost"], 2)
    delta_monthly_carbon = round(base_summary["total_monthly_carbon_kg"] - sim_summary["total_monthly_carbon_kg"], 3)
    reduction_pct = round((delta_daily_kwh / base_summary["total_daily_kwh"] * 100.0), 1) if base_summary["total_daily_kwh"] > 0 else 0.0

    return {
        "baseline": {
            "total_daily_kwh": base_summary["total_daily_kwh"],
            "total_monthly_kwh": base_summary["total_monthly_kwh"],
            "total_monthly_cost": base_summary["total_monthly_cost"],
            "total_monthly_carbon_kg": base_summary["total_monthly_carbon_kg"]
        },
        "simulated": {
            "total_daily_kwh": sim_summary["total_daily_kwh"],
            "total_monthly_kwh": sim_summary["total_monthly_kwh"],
            "total_monthly_cost": sim_summary["total_monthly_cost"],
            "total_monthly_carbon_kg": sim_summary["total_monthly_carbon_kg"]
        },
        "estimated_savings": {
            "saved_daily_kwh": delta_daily_kwh,
            "saved_monthly_kwh": delta_monthly_kwh,
            "saved_monthly_cost": delta_monthly_cost,
            "saved_annual_cost": delta_annual_cost,
            "saved_monthly_carbon_kg": delta_monthly_carbon,
            "reduction_percentage": reduction_pct,
            "currency_symbol": household.get("currency_symbol", "₹")
        }
    }
