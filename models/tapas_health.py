"""
AGNAYA - Heuristic Heat-Risk Index (HSRI) & Heat Action Plan (HAP) Engine
Synthesizing urban heat risk frameworks (Nature Scientific Reports 2026, Kacker et al.; NDMA HAP Guidelines).
Customized for Raipur Municipal Corporation (RMC) illustrative planning zones.

DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
Not clinically calibrated or endorsed by IMD, NDMA, RMC, or Health Department.
"""

import numpy as np
from typing import Dict, List, Any
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.raipur_data import RAIPUR_ZONES, RAIPUR_CLIMATE
from models.cascade_model import calculate_indoor_temp, classify_risk_band


# ═══════════════════════════════════════════════════════════════════════════════
# 1. HEAT ACTION PLAN (HAP) ACTION LIBRARY (NDMA Protocol Alignment)
# ═══════════════════════════════════════════════════════════════════════════════

HAP_MEASURES = {
    "admin": {
        "LOW": [
            "Maintain regular municipal drinking water supply schedule.",
            "Display weather forecast and heat precautions on digital billboards across Pandri and Jaistambh Chowk.",
            "Ensure primary health centers have standard stocks of ORS packets."
        ],
        "MODERATE": [
            "Issue yellow heat advisory; activate municipal cooling-centre helpline (1800-RAIPUR).",
            "Deploy municipal water tankers to high-vulnerability informal settlements (Birgaon, Urla, Gudhiyari).",
            "Alert Dr. B.R. Ambedkar Memorial & AIIMS Raipur to prepare dedicated heatstroke beds.",
            "Brief ward health workers (Mitanins / ASHA workers) on door-to-door hydration checks."
        ],
        "HIGH": [
            "Open public air-cooled refuge centers with 24/7 operating hours.",
            "Prioritize mobile water tankers and shaded waiting sheds at major transit hubs (Raipur Junction, Pandri Bus Stand).",
            "Mandate rest breaks and provide shaded rest areas for outdoor construction laborers; shift heavy work away from 12:00-16:00.",
            "Pre-position intravenous fluids, ice packs, and oral rehydration salts at all 12 ward health centers.",
            "Alert CSPDCL / CSPTCL load dispatch to prioritize power lines feeding water pumping stations and hospitals."
        ],
        "SEVERE": [
            "Activate Raipur City Emergency Heat Response Cell under Municipal Commissioner.",
            "Deploy mobile emergency diesel generators (DG sets) to maintain water pumping plants in Telibandha and Gudhiyari.",
            "Suspend outdoor construction work, stone crushing, and physical school sessions between 11:00 and 17:00.",
            "Initiate active welfare checks on high-risk citizens (elderly living alone, chronically ill, unhoused persons).",
            "Escalate to State Disaster Management Authority (SDMA) for inter-agency relief mobilization."
        ]
    },
    "public": {
        "LOW": [
            "Drink at least 2.5 to 3 liters of water throughout the day.",
            "Wear lightweight, light-colored cotton clothing."
        ],
        "MODERATE": [
            "Increase intake of water, chaas (buttermilk), and homemade ORS even when not thirsty.",
            "Avoid direct exposure to the sun between 12:00 PM and 3:30 PM.",
            "Cover your head with a cloth, hat, or umbrella when stepping outdoors.",
            "Do not leave children or pets unattended in parked vehicles."
        ],
        "HIGH": [
            "Drink cool fluids at regular intervals; strictly avoid alcohol, soda, and heavily sweetened beverages.",
            "Stay in shaded or cooled rooms. Apply damp cloths to skin to aid evaporative cooling.",
            "Check frequently on elderly neighbors and young children.",
            "Watch for early warning signs of heat exhaustion: heavy sweating, dizziness, weakness, nausea, and headache."
        ],
        "SEVERE": [
            "Immediately move to the nearest municipal cooling centre, shaded public hall, or air-conditioned space.",
            "Seek emergency medical treatment immediately if someone exhibits confusion, hot dry skin without sweating, rapid pulse, or fainting (Heat Stroke).",
            "Call 108 / 112 emergency services immediately for acute heat emergencies."
        ]
    }
}

# Aliases for NDMA color codes
for section in ["admin", "public"]:
    HAP_MEASURES[section]["RED"] = HAP_MEASURES[section]["SEVERE"]
    HAP_MEASURES[section]["ORANGE"] = HAP_MEASURES[section]["HIGH"]
    HAP_MEASURES[section]["YELLOW"] = HAP_MEASURES[section]["MODERATE"]
    HAP_MEASURES[section]["GREEN"] = HAP_MEASURES[section]["LOW"]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. HEURISTIC HEAT-RISK INDEX (HSRI)
# ═══════════════════════════════════════════════════════════════════════════════

class TapasHealthEngine:
    """
    Computes zone-level Heuristic Heat-Risk Index (HSRI):
        HSRI = f(Hazard, Exposure, Vulnerability, Adaptive_Capacity)
    Synthesized from the urban heat stress risk framework (Kacker et al., Nature Sci Rep 2026).

    Status: SIMULATION HEURISTIC - NOT CLINICALLY VALIDATED.
    """
    def __init__(self):
        self.normal_tmax = RAIPUR_CLIMATE.get("avg_max_temp_may", 42.5)

    def compute_ward_hsri(
        self,
        ambient_temp_c: float,
        power_outage_hours: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Calculates HSRI, contributing stress drivers, and relative risk tiers for all zones.
        """
        # 1. Hazard (H): Departure above seasonal climatological baseline
        temp_departure = max(0.0, ambient_temp_c - self.normal_tmax)
        anomaly_factor = min(1.0, temp_departure / 5.0)  # max at +5°C departure
        heat_surge = min(1.0, max(0.0, (ambient_temp_c - 38.0) / 10.0))
        H = min(1.0, 0.60 * anomaly_factor + 0.40 * heat_surge)

        results = []
        for z in RAIPUR_ZONES:
            pop = z["population"]

            # 2. Exposure (E): Population density & informal settlement share
            density_score = min(1.0, pop / 90000.0)
            slum_share = z["slum_pct"]
            E = min(1.0, 0.50 * density_score + 0.50 * slum_share)

            # 3. Vulnerability (V): Elderly demographics & uninsulated CGI tin roofs
            elderly_score = min(1.0, z["vulnerable_elderly_pct"] / 0.18)
            kutcha_roof_factor = slum_share
            V = min(1.0, 0.35 * elderly_score + 0.65 * kutcha_roof_factor)

            # 4. Adaptive Capacity (AC): AC access, canopy cover, power continuity
            ac_pen = z["ac_penetration_pct"]
            green_cover = z["green_cover_pct"]
            power_factor = max(0.15, 1.0 - (power_outage_hours / 12.0))
            AC = max(0.15, min(0.95, 0.50 * ac_pen * power_factor + 0.35 * green_cover + 0.15 * 0.5))

            # 5. Composite HSRI Score [0, 100]
            hsri_score = round(min(96.0, max(15.0, 100.0 * (0.35 * H + 0.25 * E + 0.25 * V + 0.15 * (1.0 - AC)))), 1)

            # Standardized Risk Classification
            if hsri_score >= 68.0:
                band = "SEVERE"
                relative_tier = "CRITICAL / RED"
            elif hsri_score >= 58.0:
                band = "HIGH"
                relative_tier = "HIGH / ORANGE"
            elif hsri_score >= 45.0:
                band = "MODERATE"
                relative_tier = "ELEVATED / YELLOW"
            else:
                band = "LOW"
                relative_tier = "GUARDED / GREEN"

            # 6. Standardized Microclimatic Indoor Temperature
            indoor_temp_estimate = calculate_indoor_temp(
                ambient_temp_c=ambient_temp_c,
                slum_pct=slum_share,
                green_cover_pct=green_cover,
                outage_hours=power_outage_hours
            )

            # 7. Identify Top Contributing Stress Factors
            drivers = []
            if slum_share >= 0.25:
                drivers.append("High CGI tin-roof heat entrapment")
            if z["vulnerable_elderly_pct"] >= 0.11:
                drivers.append("Elderly population vulnerability")
            if ac_pen <= 0.20:
                drivers.append("Low mechanical cooling penetration")
            if green_cover <= 0.08:
                drivers.append("Low urban vegetative shade")
            if power_outage_hours > 0:
                drivers.append(f"Active grid outage ({power_outage_hours:.1f}h)")
            if not drivers:
                drivers.append("Ambient atmospheric heat accumulation")

            results.append({
                "zone_id": z["id"],
                "zone_name": z["name"],
                "population": pop,
                "slum_pct": round(slum_share * 100.0, 1),
                "ac_pct": round(ac_pen * 100.0, 1),
                "green_cover_pct": round(green_cover * 100.0, 1),
                "elderly_pct": round(z["vulnerable_elderly_pct"] * 100.0, 1),
                "hazard_H": round(H, 3),
                "exposure_E": round(E, 3),
                "vulnerability_V": round(V, 3),
                "adaptive_capacity_AC": round(AC, 3),
                "hsri_score": round(hsri_score, 1),
                "htsi_score": round(hsri_score, 1),  # Backward compatibility alias
                "risk_band": band,
                "relative_risk_tier": relative_tier,
                "top_drivers": drivers,
                "daily_excess_deaths": 0.0,  # Suppressed from primary UI: uncalibrated heuristic
                "daily_emergency_admissions": 0.0,  # Suppressed from primary UI: uncalibrated heuristic
                "tin_roof_penalty_c": round(4.0 * slum_share, 1),
                "est_indoor_temp_c": round(indoor_temp_estimate, 1),
                "admin_actions": HAP_MEASURES["admin"][band],
                "public_advisories": HAP_MEASURES["public"][band],
                "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING / NOT CLINICALLY VALIDATED"
            })

        return results

    # Backward compatibility alias
    compute_ward_htsi = compute_ward_hsri
