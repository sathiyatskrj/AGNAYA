"""
AGNAYA - Raipur, Chhattisgarh Data Module
Parameters synthesized from CSERC Tariff Order FY2024-25, CSPTCL substation records, and IMD climatological normals.

Data Provenance Classification:
- VERIFIED: Directly sourced from CSERC Tariff Order FY2024-25 / IMD official records.
- DERIVED: Calculated from verified engineering or geographic data.
- ASSUMED: Engineering rule-of-thumb parameter pending utility field calibration.
- SYNTHETIC: Heuristic scenario data clearly marked as simulation-only.
"""
import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# 1. CLIMATE RECORDS & SCENARIOS
# ─────────────────────────────────────────────────────────────────────────────

# Verified IMD observed extreme records for Raipur (Station #42809)
OBSERVED_CLIMATE_RECORDS = {
    "all_time_record_celsius": 47.9,
    "record_date": "2024-05-28",
    "station_name": "IMD Raipur (Mana Airport / Labhandi #42809)",
    "source": "India Meteorological Department (IMD) Daily Weather Reports",
    "status": "VERIFIED (IMD May 2024)",
    "prior_record_celsius": 46.7,
    "prior_record_date": "2013-05-23",
}

# Categorized simulation scenarios: observed vs. hypothetical stress
STRESS_SCENARIOS = {
    "moderate_heatwave": {
        "t_peak": 44.5,
        "label": "Moderate Heatwave (IMD Yellow equivalent)",
        "status": "SCENARIO"
    },
    "severe_heatwave": {
        "t_peak": 46.5,
        "label": "Severe Heatwave (IMD Orange equivalent)",
        "status": "SCENARIO"
    },
    "observed_2024_peak": {
        "t_peak": 47.9,
        "label": "Observed 2024 Historical Extreme (IMD May 28, 2024)",
        "status": "HISTORICAL_OBSERVED"
    },
    "hypothetical_catastrophe": {
        "t_peak": 48.5,
        "label": "Hypothetical Catastrophic Stress (+0.6°C beyond record)",
        "status": "HYPOTHETICAL_STRESS"
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
}

# ─────────────────────────────────────────────────────────────────────────────
# 2. URBAN ZONES (ILLUSTRATIVE PLANNING ZONES)
# ─────────────────────────────────────────────────────────────────────────────

RAIPUR_ZONES = [
    {"id":"Z01","name":"Amanaka","lat":21.2150,"lon":81.6100,"population":112000,"area_km2":8.2,"vulnerable_elderly_pct":0.11,"slum_pct":0.28,"green_cover_pct":0.08,"avg_building_age_yr":22,"ac_penetration_pct":0.18,"substation":"S03","hospital_nearby":False,"water_pump":"WP02","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
    {"id":"Z02","name":"Shankar Nagar","lat":21.2580,"lon":81.6200,"population":95000,"area_km2":6.8,"vulnerable_elderly_pct":0.13,"slum_pct":0.12,"green_cover_pct":0.15,"avg_building_age_yr":18,"ac_penetration_pct":0.45,"substation":"S01","hospital_nearby":True,"water_pump":"WP01","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
    {"id":"Z03","name":"Telibandha","lat":21.2650,"lon":81.6400,"population":88000,"area_km2":5.5,"vulnerable_elderly_pct":0.09,"slum_pct":0.09,"green_cover_pct":0.22,"avg_building_age_yr":14,"ac_penetration_pct":0.60,"substation":"S01","hospital_nearby":True,"water_pump":"WP01","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
    {"id":"Z04","name":"Pandri","lat":21.2400,"lon":81.6600,"population":74000,"area_km2":4.8,"vulnerable_elderly_pct":0.10,"slum_pct":0.18,"green_cover_pct":0.12,"avg_building_age_yr":20,"ac_penetration_pct":0.38,"substation":"S04","hospital_nearby":False,"water_pump":"WP03","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
    {"id":"Z05","name":"Tikrapara","lat":21.2300,"lon":81.6050,"population":98000,"area_km2":7.0,"vulnerable_elderly_pct":0.08,"slum_pct":0.35,"green_cover_pct":0.06,"avg_building_age_yr":28,"ac_penetration_pct":0.10,"substation":"S03","hospital_nearby":False,"water_pump":"WP02","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
    {"id":"Z06","name":"Mowa","lat":21.2900,"lon":81.6250,"population":67000,"area_km2":6.2,"vulnerable_elderly_pct":0.12,"slum_pct":0.20,"green_cover_pct":0.10,"avg_building_age_yr":16,"ac_penetration_pct":0.30,"substation":"S02","hospital_nearby":False,"water_pump":"WP04","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
    {"id":"Z07","name":"Devendra Nagar","lat":21.2750,"lon":81.6450,"population":82000,"area_km2":5.9,"vulnerable_elderly_pct":0.14,"slum_pct":0.15,"green_cover_pct":0.18,"avg_building_age_yr":12,"ac_penetration_pct":0.52,"substation":"S02","hospital_nearby":True,"water_pump":"WP04","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
    {"id":"Z08","name":"Khamardih","lat":21.2200,"lon":81.6700,"population":55000,"area_km2":9.5,"vulnerable_elderly_pct":0.09,"slum_pct":0.40,"green_cover_pct":0.04,"avg_building_age_yr":32,"ac_penetration_pct":0.06,"substation":"S05","hospital_nearby":False,"water_pump":"WP05","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
    {"id":"Z09","name":"Gudhiyari","lat":21.2450,"lon":81.5900,"population":71000,"area_km2":7.4,"vulnerable_elderly_pct":0.10,"slum_pct":0.30,"green_cover_pct":0.07,"avg_building_age_yr":25,"ac_penetration_pct":0.15,"substation":"S06","hospital_nearby":False,"water_pump":"WP06","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
    {"id":"Z10","name":"Civil Lines","lat":21.2513,"lon":81.6296,"population":48000,"area_km2":3.2,"vulnerable_elderly_pct":0.18,"slum_pct":0.05,"green_cover_pct":0.25,"avg_building_age_yr":40,"ac_penetration_pct":0.70,"substation":"S01","hospital_nearby":True,"water_pump":"WP01","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
    {"id":"Z11","name":"Avanti Vihar","lat":21.2600,"lon":81.6500,"population":63000,"area_km2":4.1,"vulnerable_elderly_pct":0.11,"slum_pct":0.10,"green_cover_pct":0.20,"avg_building_age_yr":8,"ac_penetration_pct":0.65,"substation":"S04","hospital_nearby":True,"water_pump":"WP03","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
    {"id":"Z12","name":"Bhata Para","lat":21.2050,"lon":81.6200,"population":89000,"area_km2":8.8,"vulnerable_elderly_pct":0.07,"slum_pct":0.42,"green_cover_pct":0.05,"avg_building_age_yr":30,"ac_penetration_pct":0.08,"substation":"S06","hospital_nearby":False,"water_pump":"WP06","status":"DERIVED (RMC Census 2011 / GIS Survey)"},
]

# ─────────────────────────────────────────────────────────────────────────────
# 3. ELECTRICAL SUBSTATIONS (CSPTCL / CSPDCL)
# ─────────────────────────────────────────────────────────────────────────────

RAIPUR_SUBSTATIONS = [
    {"id":"S01","name":"Raipur Main (220 kV)","lat":21.2580,"lon":81.6150,"voltage_kv":220,"capacity_mva":500,"load_factor_normal":0.72,"age_years":28,"backup_transformer":True,"serves_zones":["Z02","Z03","Z10"],"status":"VERIFIED (CSPTCL 220kV Grid Map)"},
    {"id":"S02","name":"Mowa GSS (132 kV)","lat":21.2900,"lon":81.6100,"voltage_kv":132,"capacity_mva":200,"load_factor_normal":0.68,"age_years":22,"backup_transformer":True,"serves_zones":["Z06","Z07"],"status":"VERIFIED (CSPTCL Grid Directory)"},
    {"id":"S03","name":"Amanaka (132 kV)","lat":21.2180,"lon":81.6070,"voltage_kv":132,"capacity_mva":160,"load_factor_normal":0.75,"age_years":35,"backup_transformer":False,"serves_zones":["Z01","Z05"],"status":"VERIFIED (CSPTCL Grid Directory)"},
    {"id":"S04","name":"Pandri (33 kV)","lat":21.2380,"lon":81.6620,"voltage_kv":33,"capacity_mva":80,"load_factor_normal":0.70,"age_years":18,"backup_transformer":True,"serves_zones":["Z04","Z11"],"status":"ASSUMED (CSPDCL 33kV Distribution Feeder)"},
    {"id":"S05","name":"Khamardih (33 kV)","lat":21.2220,"lon":81.6750,"voltage_kv":33,"capacity_mva":50,"load_factor_normal":0.65,"age_years":25,"backup_transformer":False,"serves_zones":["Z08"],"status":"ASSUMED (CSPDCL 33kV Feeder)"},
    {"id":"S06","name":"Gudhiyari (33 kV)","lat":21.2430,"lon":81.5880,"voltage_kv":33,"capacity_mva":60,"load_factor_normal":0.78,"age_years":30,"backup_transformer":False,"serves_zones":["Z09","Z12"],"status":"ASSUMED (CSPDCL 33kV Feeder)"},
]

# ─────────────────────────────────────────────────────────────────────────────
# 4. WATER TREATMENT PLANTS & PUMPING STATIONS
# ─────────────────────────────────────────────────────────────────────────────

RAIPUR_WATER_PUMPS = [
    {"id":"WP01","name":"Kharun River WTP","lat":21.2700,"lon":81.6100,"capacity_MLD":180,"electricity_dependency":"S01","backup_generator":True,"serves_zones":["Z02","Z03","Z10"],"status":"VERIFIED (RMC Water Supply Master Plan: 180 MLD)"},
    {"id":"WP02","name":"Amanaka WTP","lat":21.2200,"lon":81.6080,"capacity_MLD":100,"electricity_dependency":"S03","backup_generator":False,"serves_zones":["Z01","Z05"],"status":"ASSUMED (RMC Zonal Pumping Station)"},
    {"id":"WP03","name":"Pandri Boosting Station","lat":21.2420,"lon":81.6580,"capacity_MLD":60,"electricity_dependency":"S04","backup_generator":True,"serves_zones":["Z04","Z11"],"status":"ASSUMED (RMC Distribution Station)"},
    {"id":"WP04","name":"Mowa Pumping Station","lat":21.2880,"lon":81.6200,"capacity_MLD":70,"electricity_dependency":"S02","backup_generator":False,"serves_zones":["Z06","Z07"],"status":"ASSUMED (RMC Distribution Station)"},
    {"id":"WP05","name":"Khamardih WTP","lat":21.2180,"lon":81.6720,"capacity_MLD":35,"electricity_dependency":"S05","backup_generator":False,"serves_zones":["Z08"],"status":"ASSUMED (RMC Distribution Station)"},
    {"id":"WP06","name":"Gudhiyari WTP","lat":21.2400,"lon":81.5920,"capacity_MLD":55,"electricity_dependency":"S06","backup_generator":False,"serves_zones":["Z09","Z12"],"status":"ASSUMED (RMC Distribution Station)"},
]

# ─────────────────────────────────────────────────────────────────────────────
# 5. HOSPITALS & HEALTHCARE INFRASTRUCTURE
# ─────────────────────────────────────────────────────────────────────────────

RAIPUR_HOSPITALS = [
    {"id":"H01","name":"Dr. Ambedkar Memorial Hospital","lat":21.2513,"lon":81.6280,"type":"Government","total_beds":880,"icu_beds":45,"emergency_capacity":120,"backup_power_kva":500,"backup_hours":12,"serves_zones":["Z02","Z10"],"status":"VERIFIED (Pt. JNM Medical College Records)"},
    {"id":"H02","name":"Ram Krishna Care Hospital","lat":21.2620,"lon":81.6350,"type":"Private","total_beds":350,"icu_beds":30,"emergency_capacity":60,"backup_power_kva":250,"backup_hours":8,"serves_zones":["Z03","Z07"],"status":"ASSUMED (Hospital Registry Estimate)"},
    {"id":"H03","name":"Shri Ramkrishna Hospital","lat":21.2500,"lon":81.6400,"type":"Private","total_beds":200,"icu_beds":20,"emergency_capacity":40,"backup_power_kva":150,"backup_hours":6,"serves_zones":["Z04","Z11"],"status":"ASSUMED (Hospital Registry Estimate)"},
    {"id":"H04","name":"CHC Amanaka","lat":21.2160,"lon":81.6120,"type":"Govt PHC","total_beds":30,"icu_beds":2,"emergency_capacity":15,"backup_power_kva":30,"backup_hours":4,"serves_zones":["Z01","Z05"],"status":"ASSUMED (Govt PHC Norms)"},
    {"id":"H05","name":"Urban PHC Tikrapara","lat":21.2320,"lon":81.6060,"type":"Govt PHC","total_beds":20,"icu_beds":1,"emergency_capacity":10,"backup_power_kva":20,"backup_hours":3,"serves_zones":["Z05","Z09"],"status":"ASSUMED (Govt PHC Norms)"},
]

# ─────────────────────────────────────────────────────────────────────────────
# 6. ELECTRICAL UTILITY PARAMETERS (CSPDCL / CSERC TARIFF ORDER FY 24-25)
# ─────────────────────────────────────────────────────────────────────────────

CSPDCL_PARAMS = {
    "avg_acos_rs_per_kwh": 6.10,          # VERIFIED (CSERC Tariff Order FY24-25)
    "adjusted_acos_rs_per_kwh": 6.92,     # VERIFIED (CSERC Tariff Order FY24-25)
    "atc_losses_pct": 17.63,              # VERIFIED (CSERC Tariff Order FY24-25 Aggregate Technical & Commercial Losses)
    "raipur_normal_demand_mw": 310,       # VERIFIED (CSPDCL Baseline daytime demand)
    "raipur_peak_demand_mw": 420,         # VERIFIED (CSPDCL Contracted summer peak threshold)
    "raipur_emergency_cap_mw": 620,       # ASSUMED (Transmission network thermal emergency ceiling)
}

HEAT_DEMAND_PARAMS = {
    "base_temp_celsius": 27.0,          # T_set: Cooling activation threshold (°C)
    "alpha": 0.0048,                    # Demand growth sensitivity rate (1/(h*°C))
    "gamma": 0.08,                      # Demand relaxation rate towards baseline (1/h)
    "humidity_multiplier": 1.12,        # Sensible+latent cooling amplification
    "transformer_derating_pct_per_degC": 1.5,
    "demand_cap_mw": 620.0,             # Transmission emergency thermal ceiling
    "status": "DERIVED (Calibrated to 468 MW peak at 46.5°C; asymptotes under 620 MW cap)"
}

# ─────────────────────────────────────────────────────────────────────────────
# 7. HISTORICAL HEATWAVE RECONSTRUCTIONS (SIMULATED SCENARIO CONTEXT)
# Note: Mortality figures are illustrative estimates pending civil registry calibration.
# ─────────────────────────────────────────────────────────────────────────────

HISTORICAL_HEATWAVES = [
    {"year":2022,"peak_temp":46.0,"duration_days":5,"deaths_estimated":8,"max_outage_hours":6,"status":"SYNTHETIC_RECONSTRUCTION"},
    {"year":2023,"peak_temp":45.2,"duration_days":7,"deaths_estimated":12,"max_outage_hours":9,"status":"SYNTHETIC_RECONSTRUCTION"},
    {"year":2024,"peak_temp":47.9,"duration_days":4,"deaths_estimated":5,"max_outage_hours":4,"status":"VERIFIED_TEMP_ESTIMATED_IMPACTS"},
    {"year":2025,"peak_temp":45.7,"duration_days":6,"deaths_estimated":9,"max_outage_hours":7,"status":"SYNTHETIC_RECONSTRUCTION"},
]

# ─────────────────────────────────────────────────────────────────────────────
# 8. MUNICIPAL INTERVENTION CATALOG & FLEET
# ─────────────────────────────────────────────────────────────────────────────

INTERVENTION_OPTIONS = {
    "cooling_centre":   {"label":"Open Cooling Centres","cost_per_unit_lakh":2.5,"capacity_persons_per_unit":200,"effectiveness_score":0.70,"electricity_required_kw":15,"water_required_kld":5,"status":"ASSUMED (Municipal planning cost model)"},
    "power_resilience": {"label":"Deploy Mobile DG Sets","cost_per_unit_lakh":8.0,"capacity_mw_per_unit":2,"effectiveness_score":0.85,"electricity_required_kw":0,"water_required_kld":0,"status":"ASSUMED (CSPDCL emergency procurement norms)"},
    "water_tankers":    {"label":"Deploy Water Tankers","cost_per_unit_lakh":0.8,"capacity_kl_per_unit":10,"effectiveness_score":0.50,"electricity_required_kw":0,"water_required_kld":10,"status":"ASSUMED (RMC water tanker rental rates)"},
    "hospital_surge":   {"label":"Hospital Surge Capacity","cost_per_unit_lakh":15.0,"beds_per_unit":50,"effectiveness_score":0.90,"electricity_required_kw":50,"water_required_kld":20,"status":"ASSUMED (Disaster management tent/bed setup)"},
    "jal_jeevan":       {"label":"Community Water Points","cost_per_unit_lakh":0.3,"capacity_persons_per_unit":500,"effectiveness_score":0.40,"electricity_required_kw":0,"water_required_kld":8,"status":"ASSUMED (RMC hydration kiosk cost)"},
}

COOLING_CENTRES = [
    {"id":"CC01","name":"Railway Station Shelter","lat":21.2245,"lon":81.6294,"capacity_persons":150,"operational":True,"status":"ASSUMED"},
    {"id":"CC02","name":"IG Stadium Cooling Point","lat":21.2617,"lon":81.6340,"capacity_persons":500,"operational":False,"status":"ASSUMED"},
    {"id":"CC03","name":"Collector Office Shelter","lat":21.2513,"lon":81.6296,"capacity_persons":100,"operational":True,"status":"ASSUMED"},
]
