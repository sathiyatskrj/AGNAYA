"""
AGNAYA - Raipur, Chhattisgarh Data Module
Parameters synthesized from CSERC Tariff Order FY2024-25, CSPTCL substation records, and IMD climatological normals.

Data Provenance Classification:
- VERIFIED: Directly sourced from CSERC Tariff Order FY2024-25 / IMD official records.
- DERIVED: Calculated from verified engineering or geographic data.
- ASSUMED: Engineering rule-of-thumb parameter pending utility field calibration.
- SYNTHETIC: Heuristic scenario data clearly marked as simulation-only.

MANDATORY DISCLAIMER:
SIMULATION ONLY – NOT AN OFFICIAL WARNING.
AGNAYA is a research prototype and does not issue official weather alerts or municipal directives.
"""

import csv
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("agnaya.data")

DATA_SOURCES_PATH = Path(__file__).resolve().parent / "DATA_SOURCES.csv"

# ─────────────────────────────────────────────────────────────────────────────
# 1. CLIMATE RECORDS & SCENARIOS
# ─────────────────────────────────────────────────────────────────────────────

# Verified IMD observed extreme records for Raipur (Station #42809 Mana Airport / Labhandi)
OBSERVED_CLIMATE_RECORDS = {
    "all_time_record_celsius": 47.9,
    "record_date": "2024-05-28",
    "station_name": "IMD Raipur (Mana Airport / Labhandi #42809)",
    "source": "India Meteorological Department (IMD) Daily Weather Reports",
    "status": "VERIFIED (IMD May 2024)",
    "retrieval_date": "2026-02-15",
    "reference_year": 2024,
    "confidence": "HIGH",
    "prior_record_celsius": 46.7,
    "prior_record_date": "2013-05-23",
    "notes": "Verified all-time record set on May 28, 2024; prior record was 46.7°C on May 23, 2013.",
}

# Categorized simulation scenarios: observed vs. hypothetical stress
STRESS_SCENARIOS = {
    "moderate_heatwave": {
        "t_peak": 44.5,
        "label": "Moderate Heatwave (IMD Yellow equivalent)",
        "status": "SCENARIO",
        "reference_year": 2024,
        "confidence": "MEDIUM",
        "notes": "Corresponds to standard IMD heatwave departure criteria (+4.5°C over normal).",
    },
    "severe_heatwave": {
        "t_peak": 46.5,
        "label": "Severe Heatwave (IMD Orange equivalent)",
        "status": "SCENARIO",
        "reference_year": 2024,
        "confidence": "MEDIUM",
        "notes": "Corresponds to severe heatwave departure criteria (+6.5°C over normal).",
    },
    "observed_2024_peak": {
        "t_peak": 47.9,
        "label": "Observed 2024 Historical Extreme (IMD May 28, 2024)",
        "status": "HISTORICAL_OBSERVED",
        "reference_year": 2024,
        "confidence": "HIGH",
        "notes": "Verified historical extreme from IMD Raipur Station #42809.",
    },
    "hypothetical_catastrophe": {
        "t_peak": 48.5,
        "label": "Hypothetical Catastrophic Stress (+0.6°C beyond record)",
        "status": "HYPOTHETICAL_STRESS",
        "reference_year": 2026,
        "confidence": "LOW",
        "notes": "Purely synthetic stress scenario to test emergency grid shedding limits.",
    },
}

RAIPUR_CLIMATE = {
    "lat": 21.2514, "lon": 81.6296, "city": "Raipur", "state": "Chhattisgarh",
    "avg_max_temp_may": 42.5,
    "record_max_temp": 47.9,  # Verified all-time IMD record (May 28, 2024)
    "prior_record_max_temp": 46.7,  # May 23, 2013
    "heatwave_threshold_may": 44.5,
    "heatwave_threshold_april": 43.5,
    "status": "VERIFIED (IMD Normal 1981-2010 / May 2024 record)",
    "retrieval_date": "2026-02-15",
    "reference_year": 2024,
    "confidence": "HIGH",
    "notes": "IMD Climatological Normals (1981-2010) and Daily Extreme Reports.",
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. URBAN ZONES (ILLUSTRATIVE PLANNING ZONES)
# ─────────────────────────────────────────────────────────────────────────────

RAIPUR_ZONES = [
    {
        "id": "Z01", "name": "Amanaka", "lat": 21.2150, "lon": 81.6100,
        "population": 112000, "area_km2": 8.2, "vulnerable_elderly_pct": 0.11,
        "slum_pct": 0.28, "green_cover_pct": 0.08, "avg_building_age_yr": 22,
        "ac_penetration_pct": 0.18, "substation": "S03", "hospital_nearby": False,
        "water_pump": "WP02", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; Western residential/educational corridor."
    },
    {
        "id": "Z02", "name": "Shankar Nagar", "lat": 21.2580, "lon": 81.6200,
        "population": 95000, "area_km2": 6.8, "vulnerable_elderly_pct": 0.13,
        "slum_pct": 0.12, "green_cover_pct": 0.15, "avg_building_age_yr": 18,
        "ac_penetration_pct": 0.45, "substation": "S01", "hospital_nearby": True,
        "water_pump": "WP01", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; Affluent residential and commercial belt."
    },
    {
        "id": "Z03", "name": "Telibandha", "lat": 21.2650, "lon": 81.6400,
        "population": 88000, "area_km2": 5.5, "vulnerable_elderly_pct": 0.09,
        "slum_pct": 0.09, "green_cover_pct": 0.22, "avg_building_age_yr": 14,
        "ac_penetration_pct": 0.60, "substation": "S01", "hospital_nearby": True,
        "water_pump": "WP01", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; High-income commercial and lakefront zone."
    },
    {
        "id": "Z04", "name": "Pandri", "lat": 21.2400, "lon": 81.6600,
        "population": 74000, "area_km2": 4.8, "vulnerable_elderly_pct": 0.10,
        "slum_pct": 0.18, "green_cover_pct": 0.12, "avg_building_age_yr": 20,
        "ac_penetration_pct": 0.38, "substation": "S04", "hospital_nearby": False,
        "water_pump": "WP03", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; Major wholesale cloth market and commercial hub."
    },
    {
        "id": "Z05", "name": "Tikrapara", "lat": 21.2300, "lon": 81.6050,
        "population": 98000, "area_km2": 7.0, "vulnerable_elderly_pct": 0.08,
        "slum_pct": 0.35, "green_cover_pct": 0.06, "avg_building_age_yr": 28,
        "ac_penetration_pct": 0.10, "substation": "S03", "hospital_nearby": False,
        "water_pump": "WP02", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; High-density settlement with acute tin-roof concentration."
    },
    {
        "id": "Z06", "name": "Mowa", "lat": 21.2900, "lon": 81.6250,
        "population": 67000, "area_km2": 6.2, "vulnerable_elderly_pct": 0.12,
        "slum_pct": 0.20, "green_cover_pct": 0.10, "avg_building_age_yr": 16,
        "ac_penetration_pct": 0.30, "substation": "S02", "hospital_nearby": False,
        "water_pump": "WP04", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; Northern residential expansion zone."
    },
    {
        "id": "Z07", "name": "Devendra Nagar", "lat": 21.2750, "lon": 81.6450,
        "population": 82000, "area_km2": 5.9, "vulnerable_elderly_pct": 0.14,
        "slum_pct": 0.15, "green_cover_pct": 0.18, "avg_building_age_yr": 12,
        "ac_penetration_pct": 0.52, "substation": "S02", "hospital_nearby": True,
        "water_pump": "WP04", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; Medical and commercial district."
    },
    {
        "id": "Z08", "name": "Khamardih", "lat": 21.2200, "lon": 81.6700,
        "population": 55000, "area_km2": 9.5, "vulnerable_elderly_pct": 0.09,
        "slum_pct": 0.40, "green_cover_pct": 0.04, "avg_building_age_yr": 32,
        "ac_penetration_pct": 0.06, "substation": "S05", "hospital_nearby": False,
        "water_pump": "WP05", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; Peri-urban industrial fringe with high poverty rate."
    },
    {
        "id": "Z09", "name": "Gudhiyari", "lat": 21.2450, "lon": 81.5900,
        "population": 71000, "area_km2": 7.4, "vulnerable_elderly_pct": 0.10,
        "slum_pct": 0.30, "green_cover_pct": 0.07, "avg_building_age_yr": 25,
        "ac_penetration_pct": 0.15, "substation": "S06", "hospital_nearby": False,
        "water_pump": "WP06", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; Dense old city zone west of railway tracks."
    },
    {
        "id": "Z10", "name": "Civil Lines", "lat": 21.2513, "lon": 81.6296,
        "population": 48000, "area_km2": 3.2, "vulnerable_elderly_pct": 0.18,
        "slum_pct": 0.05, "green_cover_pct": 0.25, "avg_building_age_yr": 40,
        "ac_penetration_pct": 0.70, "substation": "S01", "hospital_nearby": True,
        "water_pump": "WP01", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; Administrative VIP area, Raj Bhavan and Collectorate."
    },
    {
        "id": "Z11", "name": "Avanti Vihar", "lat": 21.2600, "lon": 81.6500,
        "population": 63000, "area_km2": 4.1, "vulnerable_elderly_pct": 0.11,
        "slum_pct": 0.10, "green_cover_pct": 0.20, "avg_building_age_yr": 8,
        "ac_penetration_pct": 0.65, "substation": "S04", "hospital_nearby": True,
        "water_pump": "WP03", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; Modern planned residential colony."
    },
    {
        "id": "Z12", "name": "Bhata Para", "lat": 21.2050, "lon": 81.6200,
        "population": 89000, "area_km2": 8.8, "vulnerable_elderly_pct": 0.07,
        "slum_pct": 0.42, "green_cover_pct": 0.05, "avg_building_age_yr": 30,
        "ac_penetration_pct": 0.08, "substation": "S06", "hospital_nearby": False,
        "water_pump": "WP06", "status": "DERIVED (RMC Census 2011 / GIS Survey)",
        "confidence": "MEDIUM", "reference_year": 2011,
        "notes": "Aggregated illustrative planning zone; Southern industrial slum pocket with severe microclimate heat load."
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. ELECTRICAL SUBSTATIONS (CSPTCL / CSPDCL)
# ─────────────────────────────────────────────────────────────────────────────

RAIPUR_SUBSTATIONS = [
    {
        "id": "S01", "name": "Raipur Main (220 kV)", "lat": 21.2580, "lon": 81.6150,
        "voltage_kv": 220, "capacity_mva": 500, "load_factor_normal": 0.72,
        "age_years": 28, "backup_transformer": True, "serves_zones": ["Z02", "Z03", "Z10"],
        "status": "VERIFIED (CSPTCL 220kV Grid Map)", "confidence": "HIGH",
        "reference_year": 2024, "is_real_identifiable_asset": True,
        "capacity_status": "VERIFIED", "link_type": "PHYSICAL", "asset_class": "SUBSTATION",
        "notes": "Physical 220kV transmission hub with N-1 transformer redundancy."
    },
    {
        "id": "S02", "name": "Mowa GSS (132 kV)", "lat": 21.2900, "lon": 81.6100,
        "voltage_kv": 132, "capacity_mva": 200, "load_factor_normal": 0.68,
        "age_years": 22, "backup_transformer": True, "serves_zones": ["Z06", "Z07"],
        "status": "VERIFIED (CSPTCL Grid Directory)", "confidence": "HIGH",
        "reference_year": 2024, "is_real_identifiable_asset": True,
        "capacity_status": "VERIFIED", "link_type": "PHYSICAL", "asset_class": "SUBSTATION",
        "notes": "Physical 132kV grid substation with step-down transformation to 33kV."
    },
    {
        "id": "S03", "name": "Amanaka (132 kV)", "lat": 21.2180, "lon": 81.6070,
        "voltage_kv": 132, "capacity_mva": 160, "load_factor_normal": 0.75,
        "age_years": 35, "backup_transformer": False, "serves_zones": ["Z01", "Z05"],
        "status": "VERIFIED (CSPTCL Grid Directory)", "confidence": "HIGH",
        "reference_year": 2024, "is_real_identifiable_asset": True,
        "capacity_status": "VERIFIED", "link_type": "PHYSICAL", "asset_class": "SUBSTATION",
        "notes": "Physical 132kV primary substation; aging transformer bank without automated N-1 coupler."
    },
    {
        "id": "S04", "name": "Pandri (33 kV)", "lat": 21.2380, "lon": 81.6620,
        "voltage_kv": 33, "capacity_mva": 80, "load_factor_normal": 0.70,
        "age_years": 18, "backup_transformer": True, "serves_zones": ["Z04", "Z11"],
        "status": "ASSUMED (CSPDCL 33kV Distribution Feeder)", "confidence": "MEDIUM",
        "reference_year": 2024, "is_real_identifiable_asset": True,
        "capacity_status": "ASSUMED", "link_type": "PLANNING_ASSUMED", "asset_class": "SUBSTATION",
        "notes": "Physical 33/11kV distribution substation serving commercial market."
    },
    {
        "id": "S05", "name": "Khamardih (33 kV)", "lat": 21.2220, "lon": 81.6750,
        "voltage_kv": 33, "capacity_mva": 50, "load_factor_normal": 0.65,
        "age_years": 25, "backup_transformer": False, "serves_zones": ["Z08"],
        "status": "ASSUMED (CSPDCL 33kV Feeder)", "confidence": "MEDIUM",
        "reference_year": 2024, "is_real_identifiable_asset": False,
        "capacity_status": "ASSUMED", "link_type": "PLANNING_ASSUMED", "asset_class": "SUBSTATION",
        "notes": "Aggregated 33kV distribution feeder node representing Khamardih distribution sector."
    },
    {
        "id": "S06", "name": "Gudhiyari (33 kV)", "lat": 21.2430, "lon": 81.5880,
        "voltage_kv": 33, "capacity_mva": 60, "load_factor_normal": 0.78,
        "age_years": 30, "backup_transformer": False, "serves_zones": ["Z09", "Z12"],
        "status": "ASSUMED (CSPDCL 33kV Feeder)", "confidence": "MEDIUM",
        "reference_year": 2024, "is_real_identifiable_asset": True,
        "capacity_status": "ASSUMED", "link_type": "PLANNING_ASSUMED", "asset_class": "SUBSTATION",
        "notes": "Physical 33/11kV substation serving dense western settlements."
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 4. WATER TREATMENT PLANTS & PUMPING STATIONS
# ─────────────────────────────────────────────────────────────────────────────

RAIPUR_WATER_PUMPS = [
    {
        "id": "WP01", "name": "Kharun River WTP", "lat": 21.2700, "lon": 81.6100,
        "capacity_MLD": 180, "electricity_dependency": "S01", "backup_generator": True,
        "serves_zones": ["Z02", "Z03", "Z10"],
        "status": "VERIFIED (RMC Water Supply Master Plan: 180 MLD)", "confidence": "HIGH",
        "reference_year": 2022, "is_real_identifiable_asset": True,
        "capacity_status": "VERIFIED", "link_type": "PHYSICAL", "asset_class": "WATER_PUMP",
        "notes": "Primary municipal intake and filtration works on Kharun River with 1.5 MVA backup generator."
    },
    {
        "id": "WP02", "name": "Amanaka WTP", "lat": 21.2200, "lon": 81.6080,
        "capacity_MLD": 100, "electricity_dependency": "S03", "backup_generator": False,
        "serves_zones": ["Z01", "Z05"],
        "status": "ASSUMED (RMC Zonal Pumping Station)", "confidence": "MEDIUM",
        "reference_year": 2022, "is_real_identifiable_asset": True,
        "capacity_status": "ASSUMED", "link_type": "PLANNING_ASSUMED", "asset_class": "WATER_PUMP",
        "notes": "Physical zonal boosting station; highly dependent on S03 feeder."
    },
    {
        "id": "WP03", "name": "Pandri Boosting Station", "lat": 21.2420, "lon": 81.6580,
        "capacity_MLD": 60, "electricity_dependency": "S04", "backup_generator": True,
        "serves_zones": ["Z04", "Z11"],
        "status": "ASSUMED (RMC Distribution Station)", "confidence": "MEDIUM",
        "reference_year": 2022, "is_real_identifiable_asset": True,
        "capacity_status": "ASSUMED", "link_type": "PLANNING_ASSUMED", "asset_class": "WATER_PUMP",
        "notes": "Physical booster station with local commercial standby power."
    },
    {
        "id": "WP04", "name": "Mowa Pumping Station", "lat": 21.2880, "lon": 81.6200,
        "capacity_MLD": 70, "electricity_dependency": "S02", "backup_generator": False,
        "serves_zones": ["Z06", "Z07"],
        "status": "ASSUMED (RMC Distribution Station)", "confidence": "MEDIUM",
        "reference_year": 2022, "is_real_identifiable_asset": True,
        "capacity_status": "ASSUMED", "link_type": "PLANNING_ASSUMED", "asset_class": "WATER_PUMP",
        "notes": "Physical distribution pump house connected to S02."
    },
    {
        "id": "WP05", "name": "Khamardih WTP", "lat": 21.2180, "lon": 81.6720,
        "capacity_MLD": 35, "electricity_dependency": "S05", "backup_generator": False,
        "serves_zones": ["Z08"],
        "status": "ASSUMED (RMC Distribution Station)", "confidence": "MEDIUM",
        "reference_year": 2022, "is_real_identifiable_asset": False,
        "capacity_status": "ASSUMED", "link_type": "CONCEPTUAL", "asset_class": "WATER_PUMP",
        "notes": "Conceptual intermediate boosting node for eastern settlements."
    },
    {
        "id": "WP06", "name": "Gudhiyari WTP", "lat": 21.2400, "lon": 81.5920,
        "capacity_MLD": 55, "electricity_dependency": "S06", "backup_generator": False,
        "serves_zones": ["Z09", "Z12"],
        "status": "ASSUMED (RMC Distribution Station)", "confidence": "MEDIUM",
        "reference_year": 2022, "is_real_identifiable_asset": True,
        "capacity_status": "ASSUMED", "link_type": "PLANNING_ASSUMED", "asset_class": "WATER_PUMP",
        "notes": "Physical municipal booster pumping house and overhead tank."
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 5. HOSPITALS & HEALTHCARE INFRASTRUCTURE
# ─────────────────────────────────────────────────────────────────────────────

RAIPUR_HOSPITALS = [
    {
        "id": "H01", "name": "Dr. Ambedkar Memorial Hospital", "lat": 21.2513, "lon": 81.6280,
        "type": "Government", "total_beds": 880, "icu_beds": 45, "emergency_capacity": 120,
        "backup_power_kva": 500, "backup_hours": 12, "serves_zones": ["Z02", "Z10"],
        "status": "VERIFIED (Pt. JNM Medical College Records)", "confidence": "HIGH",
        "reference_year": 2023, "is_real_identifiable_asset": True,
        "capacity_status": "VERIFIED", "link_type": "PHYSICAL", "asset_class": "HOSPITAL",
        "notes": "Premier government tertiary teaching hospital in Chhattisgarh; essential service feeder from S01."
    },
    {
        "id": "H02", "name": "Ram Krishna Care Hospital", "lat": 21.2620, "lon": 81.6350,
        "type": "Private", "total_beds": 350, "icu_beds": 30, "emergency_capacity": 60,
        "backup_power_kva": 250, "backup_hours": 8, "serves_zones": ["Z03", "Z07"],
        "status": "ASSUMED (Hospital Registry Estimate)", "confidence": "MEDIUM",
        "reference_year": 2023, "is_real_identifiable_asset": True,
        "capacity_status": "ASSUMED", "link_type": "PLANNING_ASSUMED", "asset_class": "HOSPITAL",
        "notes": "Major multi-specialty private tertiary care facility."
    },
    {
        "id": "H03", "name": "Shri Ramkrishna Hospital", "lat": 21.2500, "lon": 81.6400,
        "type": "Private", "total_beds": 200, "icu_beds": 20, "emergency_capacity": 40,
        "backup_power_kva": 150, "backup_hours": 6, "serves_zones": ["Z04", "Z11"],
        "status": "ASSUMED (Hospital Registry Estimate)", "confidence": "MEDIUM",
        "reference_year": 2023, "is_real_identifiable_asset": True,
        "capacity_status": "ASSUMED", "link_type": "PLANNING_ASSUMED", "asset_class": "HOSPITAL",
        "notes": "Secondary private hospital serving central commercial corridors."
    },
    {
        "id": "H04", "name": "CHC Amanaka", "lat": 21.2160, "lon": 81.6120,
        "type": "Govt PHC", "total_beds": 30, "icu_beds": 2, "emergency_capacity": 15,
        "backup_power_kva": 30, "backup_hours": 4, "serves_zones": ["Z01", "Z05"],
        "status": "ASSUMED (Govt PHC Norms)", "confidence": "MEDIUM",
        "reference_year": 2022, "is_real_identifiable_asset": True,
        "capacity_status": "ASSUMED", "link_type": "PLANNING_ASSUMED", "asset_class": "HOSPITAL",
        "notes": "Government Community Health Centre based on Indian Public Health Standards (IPHS)."
    },
    {
        "id": "H05", "name": "Urban PHC Tikrapara", "lat": 21.2320, "lon": 81.6060,
        "type": "Govt PHC", "total_beds": 20, "icu_beds": 1, "emergency_capacity": 10,
        "backup_power_kva": 20, "backup_hours": 3, "serves_zones": ["Z05", "Z09"],
        "status": "ASSUMED (Govt PHC Norms)", "confidence": "MEDIUM",
        "reference_year": 2022, "is_real_identifiable_asset": True,
        "capacity_status": "ASSUMED", "link_type": "PLANNING_ASSUMED", "asset_class": "HOSPITAL",
        "notes": "Government Urban Primary Health Centre in vulnerable slum sector."
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# 6. ELECTRICAL UTILITY PARAMETERS (CSPDCL / CSERC TARIFF ORDER FY 24-25)
# ─────────────────────────────────────────────────────────────────────────────

CSPDCL_PARAMS = {
    "avg_acos_rs_per_kwh": 6.10,          # VERIFIED (CSERC Tariff Order FY24-25 Section 7.4)
    "adjusted_acos_rs_per_kwh": 6.92,     # VERIFIED (CSERC Tariff Order FY24-25 Tariff Schedule)
    "atc_losses_pct": 17.63,              # VERIFIED (CSERC Tariff Order FY24-25 Benchmark)
    "raipur_normal_demand_mw": 310.0,     # VERIFIED (CSPDCL Raipur Circle daytime base demand)
    "raipur_peak_demand_mw": 420.0,       # VERIFIED (CSPDCL Contracted summer peak limit)
    "raipur_emergency_cap_mw": 620.0,     # ASSUMED (Transmission network thermal ceiling)
    "status": "VERIFIED (CSERC Tariff Order FY24-25 / CSPDCL Dispatch)",
    "confidence": "HIGH",
    "reference_year": 2024,
    "notes": "Official state regulatory tariff order approved parameters for Chhattisgarh.",
}

HEAT_DEMAND_PARAMS = {
    "base_temp_celsius": 27.0,          # T_set: Cooling activation threshold (°C)
    "alpha": 0.0048,                    # Demand growth sensitivity rate (1/(h*°C))
    "gamma": 0.08,                      # Demand relaxation rate towards baseline (1/h)
    "humidity_multiplier": 1.12,        # Sensible+latent cooling amplification
    "transformer_derating_pct_per_degC": 1.5,
    "demand_cap_mw": 620.0,             # Transmission emergency thermal ceiling
    "status": "DERIVED (Calibrated to 475.9 MW peak at 46.5°C; asymptotes under 620 MW cap)",
    "confidence": "MEDIUM",
    "reference_year": 2024,
    "notes": "Saturating ODE model preventing unconstrained load explosion.",
}

# ─────────────────────────────────────────────────────────────────────────────
# 7. HISTORICAL HEATWAVE RECONSTRUCTIONS (SIMULATED SCENARIO CONTEXT)
# Note: Mortality and outage figures are synthetic reconstructions for baseline comparisons.
# ─────────────────────────────────────────────────────────────────────────────

HISTORICAL_HEATWAVES = [
    {"year": 2022, "peak_temp": 46.0, "duration_days": 5, "deaths_estimated": 8, "max_outage_hours": 6, "status": "SYNTHETIC_RECONSTRUCTION", "confidence": "LOW"},
    {"year": 2023, "peak_temp": 45.2, "duration_days": 7, "deaths_estimated": 12, "max_outage_hours": 9, "status": "SYNTHETIC_RECONSTRUCTION", "confidence": "LOW"},
    {"year": 2024, "peak_temp": 47.9, "duration_days": 4, "deaths_estimated": 5, "max_outage_hours": 4, "status": "VERIFIED_TEMP_SYNTHETIC_IMPACTS", "confidence": "MEDIUM"},
    {"year": 2025, "peak_temp": 45.7, "duration_days": 6, "deaths_estimated": 9, "max_outage_hours": 7, "status": "SYNTHETIC_RECONSTRUCTION", "confidence": "LOW"},
]

# ─────────────────────────────────────────────────────────────────────────────
# 8. MUNICIPAL INTERVENTION CATALOG & FLEET
# ─────────────────────────────────────────────────────────────────────────────

INTERVENTION_OPTIONS = {
    "cooling_centre": {
        "label": "Open Cooling Centres",
        "cost_per_unit_lakh": 2.5,
        "capacity_persons_per_unit": 200,
        "effectiveness_score": 0.70,
        "electricity_required_kw": 15,
        "water_required_kld": 5,
        "status": "ASSUMED (Municipal planning cost model)",
        "confidence": "MEDIUM",
        "reference_year": 2024,
        "notes": "Cost to fit out temporary air-conditioned public shelter.",
    },
    "power_resilience": {
        "label": "Deploy Mobile DG Sets",
        "cost_per_unit_lakh": 8.0,
        "capacity_mw_per_unit": 2.0,
        "effectiveness_score": 0.85,
        "electricity_required_kw": 0,
        "water_required_kld": 0,
        "status": "ASSUMED (CSPDCL emergency procurement norms)",
        "confidence": "MEDIUM",
        "reference_year": 2024,
        "notes": "Mobile 2 MVA diesel generator deployment for critical feeder support.",
    },
    "water_tankers": {
        "label": "Deploy Water Tankers",
        "cost_per_unit_lakh": 0.8,
        "capacity_kl_per_unit": 10.0,
        "effectiveness_score": 0.50,
        "electricity_required_kw": 0,
        "water_required_kld": 10.0,
        "status": "ASSUMED (RMC water tanker rental rates)",
        "confidence": "MEDIUM",
        "reference_year": 2024,
        "notes": "10 kL potable water tanker emergency deployment per zone.",
    },
    "hospital_surge": {
        "label": "Hospital Surge Capacity",
        "cost_per_unit_lakh": 15.0,
        "beds_per_unit": 50,
        "effectiveness_score": 0.90,
        "electricity_required_kw": 50,
        "water_required_kld": 20,
        "status": "ASSUMED (Disaster management tent/bed setup)",
        "confidence": "MEDIUM",
        "reference_year": 2024,
        "notes": "50-bed climate-controlled triage tent setup at tertiary hospitals.",
    },
    "jal_jeevan": {
        "label": "Community Water Points",
        "cost_per_unit_lakh": 0.3,
        "capacity_persons_per_unit": 500,
        "effectiveness_score": 0.40,
        "electricity_required_kw": 0,
        "water_required_kld": 8,
        "status": "ASSUMED (RMC hydration kiosk cost)",
        "confidence": "MEDIUM",
        "reference_year": 2024,
        "notes": "Shaded public drinking water kiosk (piau) deployment.",
    },
}

COOLING_CENTRES = [
    {"id": "CC01", "name": "Railway Station Shelter", "lat": 21.2245, "lon": 81.6294, "capacity_persons": 150, "operational": True, "status": "ASSUMED"},
    {"id": "CC02", "name": "IG Stadium Cooling Point", "lat": 21.2617, "lon": 81.6340, "capacity_persons": 500, "operational": False, "status": "ASSUMED"},
    {"id": "CC03", "name": "Collector Office Shelter", "lat": 21.2513, "lon": 81.6296, "capacity_persons": 100, "operational": True, "status": "ASSUMED"},
]

# ─────────────────────────────────────────────────────────────────────────────
# 9. TERMINOLOGY & GOVERNANCE DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────────

TERMINOLOGY_DEFINITIONS: Dict[str, Dict[str, str]] = {
    "OBSERVED": {
        "title": "Observed Data",
        "definition": "Ground-truth physical measurements recorded by statutory government agencies.",
        "example": "IMD Station #42809 records (47.9°C on May 28, 2024); CSERC tariff order filings.",
        "status_tag": "VERIFIED",
    },
    "FORECAST": {
        "title": "Numerical Weather Forecast",
        "definition": "Gridded numerical weather prediction (NWP) model outputs retrieved from the Open-Meteo API.",
        "example": "Hourly temperature and irradiance forecast for 21.2514° N, 81.6296° E. NOT official IMD station telemetry.",
        "status_tag": "OPEN_METEO_GRIDDED",
    },
    "USER_HYPOTHETICAL": {
        "title": "User Hypothetical Scenario",
        "definition": "What-if scenario parameters selected via sliders to evaluate infrastructure stress boundaries.",
        "example": "Hypothetical +48.5°C peak ambient temperature or 6-hour simultaneous grid blackout.",
        "status_tag": "SCENARIO",
    },
    "MODEL_CLASSIFIED": {
        "title": "Model-Classified Tiers",
        "definition": "Algorithmic risk tiers and stress indices computed by deterministic physics and engineering models.",
        "example": "Heuristic Heat-Risk Index (HSRI), IEEE Std C57.91 transformer thermal aging acceleration.",
        "status_tag": "DERIVED",
    },
    "OFFICIAL_WARNING": {
        "title": "Official Warning (Statutory)",
        "definition": "NEVER PRODUCED BY AGNAYA. Statutory alerts, red/orange warnings, and evacuation directives are strictly the legal domain of IMD, NDMA, and State/District Disaster Management Authorities.",
        "example": "IMD Red Alert or District Collector Section 144 orders.",
        "status_tag": "NOT_PRODUCED_BY_APP",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# 10. ASSET REGISTRY & DATA PROVENANCE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_asset_registry() -> List[Dict[str, Any]]:
    """
    Returns an audit checklist of all physical and simulated infrastructure assets
    (Substations, Water Plants, Hospitals), certifying physical identifiability,
    capacity certainty, and link topology.
    """
    registry: List[Dict[str, Any]] = []

    # Substations
    for sub in RAIPUR_SUBSTATIONS:
        registry.append({
            "asset_id": sub["id"],
            "name": sub["name"],
            "asset_class": "SUBSTATION",
            "is_real_identifiable_asset": sub.get("is_real_identifiable_asset", False),
            "capacity_display": f"{sub['capacity_mva']} MVA ({sub['voltage_kv']} kV)",
            "capacity_status": sub.get("capacity_status", "ASSUMED"),
            "link_type": sub.get("link_type", "PLANNING_ASSUMED"),
            "serves": ", ".join(sub.get("serves_zones", [])),
            "status": sub.get("status", "ASSUMED"),
            "confidence": sub.get("confidence", "MEDIUM"),
            "notes": sub.get("notes", ""),
        })

    # Water Plants
    for wp in RAIPUR_WATER_PUMPS:
        registry.append({
            "asset_id": wp["id"],
            "name": wp["name"],
            "asset_class": "WATER_PUMP",
            "is_real_identifiable_asset": wp.get("is_real_identifiable_asset", False),
            "capacity_display": f"{wp['capacity_MLD']} MLD",
            "capacity_status": wp.get("capacity_status", "ASSUMED"),
            "link_type": wp.get("link_type", "PLANNING_ASSUMED"),
            "serves": ", ".join(wp.get("serves_zones", [])),
            "status": wp.get("status", "ASSUMED"),
            "confidence": wp.get("confidence", "MEDIUM"),
            "notes": wp.get("notes", ""),
        })

    # Hospitals
    for h in RAIPUR_HOSPITALS:
        registry.append({
            "asset_id": h["id"],
            "name": h["name"],
            "asset_class": "HOSPITAL",
            "is_real_identifiable_asset": h.get("is_real_identifiable_asset", False),
            "capacity_display": f"{h['total_beds']} Beds ({h['icu_beds']} ICU)",
            "capacity_status": h.get("capacity_status", "ASSUMED"),
            "link_type": h.get("link_type", "PLANNING_ASSUMED"),
            "serves": ", ".join(h.get("serves_zones", [])),
            "status": h.get("status", "ASSUMED"),
            "confidence": h.get("confidence", "MEDIUM"),
            "notes": h.get("notes", ""),
        })

    return registry


def get_data_sources_rows() -> List[Dict[str, Any]]:
    """
    Reads data/DATA_SOURCES.csv and returns structured provenance rows.
    Falls back gracefully if file is inaccessible.
    """
    rows: List[Dict[str, Any]] = []
    if not DATA_SOURCES_PATH.exists():
        logger.warning(f"DATA_SOURCES.csv not found at {DATA_SOURCES_PATH}")
        return rows

    try:
        with open(DATA_SOURCES_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(dict(r))
    except Exception as e:
        logger.error(f"Error reading DATA_SOURCES.csv: {e}")
    return rows


def get_provenance_summary() -> Dict[str, Any]:
    """
    Computes an audit summary of parameters by classification status and confidence level.
    """
    rows = get_data_sources_rows()
    status_counts: Dict[str, int] = {}
    confidence_counts: Dict[str, int] = {}
    entity_counts: Dict[str, int] = {}

    for r in rows:
        st = r.get("status", "UNKNOWN")
        conf = r.get("confidence", "UNKNOWN")
        ent = r.get("entity_type", "UNKNOWN")

        status_counts[st] = status_counts.get(st, 0) + 1
        confidence_counts[conf] = confidence_counts.get(conf, 0) + 1
        entity_counts[ent] = entity_counts.get(ent, 0) + 1

    return {
        "total_parameters_audited": len(rows),
        "status_breakdown": status_counts,
        "confidence_breakdown": confidence_counts,
        "entity_breakdown": entity_counts,
    }
