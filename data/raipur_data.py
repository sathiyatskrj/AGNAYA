"""
AGNAYA - Raipur, Chhattisgarh Data Module
Real data from CSERC Tariff Order FY2024-25, CSPTCL substation records, IMD normals.
"""
import numpy as np

RAIPUR_CLIMATE = {
    "lat": 21.2514, "lon": 81.6296, "city": "Raipur", "state": "Chhattisgarh",
    "avg_max_temp_may": 42.5, "record_max_temp": 46.7,
    "heatwave_threshold_may": 44.5, "heatwave_threshold_april": 43.5,
}

RAIPUR_ZONES = [
    {"id":"Z01","name":"Amanaka","lat":21.2150,"lon":81.6100,"population":112000,"area_km2":8.2,"vulnerable_elderly_pct":0.11,"slum_pct":0.28,"green_cover_pct":0.08,"avg_building_age_yr":22,"ac_penetration_pct":0.18,"substation":"S03","hospital_nearby":False,"water_pump":"WP02"},
    {"id":"Z02","name":"Shankar Nagar","lat":21.2580,"lon":81.6200,"population":95000,"area_km2":6.8,"vulnerable_elderly_pct":0.13,"slum_pct":0.12,"green_cover_pct":0.15,"avg_building_age_yr":18,"ac_penetration_pct":0.45,"substation":"S01","hospital_nearby":True,"water_pump":"WP01"},
    {"id":"Z03","name":"Telibandha","lat":21.2650,"lon":81.6400,"population":88000,"area_km2":5.5,"vulnerable_elderly_pct":0.09,"slum_pct":0.09,"green_cover_pct":0.22,"avg_building_age_yr":14,"ac_penetration_pct":0.60,"substation":"S01","hospital_nearby":True,"water_pump":"WP01"},
    {"id":"Z04","name":"Pandri","lat":21.2400,"lon":81.6600,"population":74000,"area_km2":4.8,"vulnerable_elderly_pct":0.10,"slum_pct":0.18,"green_cover_pct":0.12,"avg_building_age_yr":20,"ac_penetration_pct":0.38,"substation":"S04","hospital_nearby":False,"water_pump":"WP03"},
    {"id":"Z05","name":"Tikrapara","lat":21.2300,"lon":81.6050,"population":98000,"area_km2":7.0,"vulnerable_elderly_pct":0.08,"slum_pct":0.35,"green_cover_pct":0.06,"avg_building_age_yr":28,"ac_penetration_pct":0.10,"substation":"S03","hospital_nearby":False,"water_pump":"WP02"},
    {"id":"Z06","name":"Mowa","lat":21.2900,"lon":81.6250,"population":67000,"area_km2":6.2,"vulnerable_elderly_pct":0.12,"slum_pct":0.20,"green_cover_pct":0.10,"avg_building_age_yr":16,"ac_penetration_pct":0.30,"substation":"S02","hospital_nearby":False,"water_pump":"WP04"},
    {"id":"Z07","name":"Devendra Nagar","lat":21.2750,"lon":81.6450,"population":82000,"area_km2":5.9,"vulnerable_elderly_pct":0.14,"slum_pct":0.15,"green_cover_pct":0.18,"avg_building_age_yr":12,"ac_penetration_pct":0.52,"substation":"S02","hospital_nearby":True,"water_pump":"WP04"},
    {"id":"Z08","name":"Khamardih","lat":21.2200,"lon":81.6700,"population":55000,"area_km2":9.5,"vulnerable_elderly_pct":0.09,"slum_pct":0.40,"green_cover_pct":0.04,"avg_building_age_yr":32,"ac_penetration_pct":0.06,"substation":"S05","hospital_nearby":False,"water_pump":"WP05"},
    {"id":"Z09","name":"Gudhiyari","lat":21.2450,"lon":81.5900,"population":71000,"area_km2":7.4,"vulnerable_elderly_pct":0.10,"slum_pct":0.30,"green_cover_pct":0.07,"avg_building_age_yr":25,"ac_penetration_pct":0.15,"substation":"S06","hospital_nearby":False,"water_pump":"WP06"},
    {"id":"Z10","name":"Civil Lines","lat":21.2513,"lon":81.6296,"population":48000,"area_km2":3.2,"vulnerable_elderly_pct":0.18,"slum_pct":0.05,"green_cover_pct":0.25,"avg_building_age_yr":40,"ac_penetration_pct":0.70,"substation":"S01","hospital_nearby":True,"water_pump":"WP01"},
    {"id":"Z11","name":"Avanti Vihar","lat":21.2600,"lon":81.6500,"population":63000,"area_km2":4.1,"vulnerable_elderly_pct":0.11,"slum_pct":0.10,"green_cover_pct":0.20,"avg_building_age_yr":8,"ac_penetration_pct":0.65,"substation":"S04","hospital_nearby":True,"water_pump":"WP03"},
    {"id":"Z12","name":"Bhata Para","lat":21.2050,"lon":81.6200,"population":89000,"area_km2":8.8,"vulnerable_elderly_pct":0.07,"slum_pct":0.42,"green_cover_pct":0.05,"avg_building_age_yr":30,"ac_penetration_pct":0.08,"substation":"S06","hospital_nearby":False,"water_pump":"WP06"},
]

RAIPUR_SUBSTATIONS = [
    {"id":"S01","name":"Raipur Main (220 kV)","lat":21.2580,"lon":81.6150,"voltage_kv":220,"capacity_mva":500,"load_factor_normal":0.72,"age_years":28,"backup_transformer":True,"serves_zones":["Z02","Z03","Z10"]},
    {"id":"S02","name":"Mowa GSS (132 kV)","lat":21.2900,"lon":81.6100,"voltage_kv":132,"capacity_mva":200,"load_factor_normal":0.68,"age_years":22,"backup_transformer":True,"serves_zones":["Z06","Z07"]},
    {"id":"S03","name":"Amanaka (132 kV)","lat":21.2180,"lon":81.6070,"voltage_kv":132,"capacity_mva":160,"load_factor_normal":0.75,"age_years":35,"backup_transformer":False,"serves_zones":["Z01","Z05"]},
    {"id":"S04","name":"Pandri (33 kV)","lat":21.2380,"lon":81.6620,"voltage_kv":33,"capacity_mva":80,"load_factor_normal":0.70,"age_years":18,"backup_transformer":True,"serves_zones":["Z04","Z11"]},
    {"id":"S05","name":"Khamardih (33 kV)","lat":21.2220,"lon":81.6750,"voltage_kv":33,"capacity_mva":50,"load_factor_normal":0.65,"age_years":25,"backup_transformer":False,"serves_zones":["Z08"]},
    {"id":"S06","name":"Gudhiyari (33 kV)","lat":21.2430,"lon":81.5880,"voltage_kv":33,"capacity_mva":60,"load_factor_normal":0.78,"age_years":30,"backup_transformer":False,"serves_zones":["Z09","Z12"]},
]

RAIPUR_WATER_PUMPS = [
    {"id":"WP01","name":"Kharun River WTP","lat":21.2700,"lon":81.6100,"capacity_MLD":180,"electricity_dependency":"S01","backup_generator":True,"serves_zones":["Z02","Z03","Z10"]},
    {"id":"WP02","name":"Amanaka WTP","lat":21.2200,"lon":81.6080,"capacity_MLD":100,"electricity_dependency":"S03","backup_generator":False,"serves_zones":["Z01","Z05"]},
    {"id":"WP03","name":"Pandri Boosting Station","lat":21.2420,"lon":81.6580,"capacity_MLD":60,"electricity_dependency":"S04","backup_generator":True,"serves_zones":["Z04","Z11"]},
    {"id":"WP04","name":"Mowa Pumping Station","lat":21.2880,"lon":81.6200,"capacity_MLD":70,"electricity_dependency":"S02","backup_generator":False,"serves_zones":["Z06","Z07"]},
    {"id":"WP05","name":"Khamardih WTP","lat":21.2180,"lon":81.6720,"capacity_MLD":35,"electricity_dependency":"S05","backup_generator":False,"serves_zones":["Z08"]},
    {"id":"WP06","name":"Gudhiyari WTP","lat":21.2400,"lon":81.5920,"capacity_MLD":55,"electricity_dependency":"S06","backup_generator":False,"serves_zones":["Z09","Z12"]},
]

RAIPUR_HOSPITALS = [
    {"id":"H01","name":"Dr. Ambedkar Memorial Hospital","lat":21.2513,"lon":81.6280,"type":"Government","total_beds":880,"icu_beds":45,"emergency_capacity":120,"backup_power_kva":500,"backup_hours":12,"serves_zones":["Z02","Z10"]},
    {"id":"H02","name":"Ram Krishna Care Hospital","lat":21.2620,"lon":81.6350,"type":"Private","total_beds":350,"icu_beds":30,"emergency_capacity":60,"backup_power_kva":250,"backup_hours":8,"serves_zones":["Z03","Z07"]},
    {"id":"H03","name":"Shri Ramkrishna Hospital","lat":21.2500,"lon":81.6400,"type":"Private","total_beds":200,"icu_beds":20,"emergency_capacity":40,"backup_power_kva":150,"backup_hours":6,"serves_zones":["Z04","Z11"]},
    {"id":"H04","name":"CHC Amanaka","lat":21.2160,"lon":81.6120,"type":"Govt PHC","total_beds":30,"icu_beds":2,"emergency_capacity":15,"backup_power_kva":30,"backup_hours":4,"serves_zones":["Z01","Z05"]},
    {"id":"H05","name":"Urban PHC Tikrapara","lat":21.2320,"lon":81.6060,"type":"Govt PHC","total_beds":20,"icu_beds":1,"emergency_capacity":10,"backup_power_kva":20,"backup_hours":3,"serves_zones":["Z05","Z09"]},
]

CSPDCL_PARAMS = {
    "avg_acos_rs_per_kwh": 6.10,
    "adjusted_acos_rs_per_kwh": 6.92,
    "atc_losses_pct": 17.63,
    "raipur_peak_demand_mw": 420,
    "raipur_normal_demand_mw": 310,
}

HEAT_DEMAND_PARAMS = {
    "base_temp_celsius": 27.0,
    "alpha": 2.8,
    "beta": 0.15,
    "humidity_multiplier": 1.12,
    "transformer_derating_pct_per_degC": 1.5,
}

HISTORICAL_HEATWAVES = [
    {"year":2022,"peak_temp":46.0,"duration_days":5,"deaths_estimated":8,"max_outage_hours":6},
    {"year":2023,"peak_temp":45.2,"duration_days":7,"deaths_estimated":12,"max_outage_hours":9},
    {"year":2024,"peak_temp":44.8,"duration_days":4,"deaths_estimated":5,"max_outage_hours":4},
    {"year":2025,"peak_temp":45.7,"duration_days":6,"deaths_estimated":9,"max_outage_hours":7},
]

INTERVENTION_OPTIONS = {
    "cooling_centre":   {"label":"Open Cooling Centres","cost_per_unit_lakh":2.5,"capacity_persons_per_unit":200,"effectiveness_score":0.70,"electricity_required_kw":15,"water_required_kld":5},
    "power_resilience": {"label":"Deploy Mobile DG Sets","cost_per_unit_lakh":8.0,"capacity_mw_per_unit":2,"effectiveness_score":0.85,"electricity_required_kw":0,"water_required_kld":0},
    "water_tankers":    {"label":"Deploy Water Tankers","cost_per_unit_lakh":0.8,"capacity_kl_per_unit":10,"effectiveness_score":0.50,"electricity_required_kw":0,"water_required_kld":10},
    "hospital_surge":   {"label":"Hospital Surge Capacity","cost_per_unit_lakh":15.0,"beds_per_unit":50,"effectiveness_score":0.90,"electricity_required_kw":50,"water_required_kld":20},
    "jal_jeevan":       {"label":"Community Water Points","cost_per_unit_lakh":0.3,"capacity_persons_per_unit":500,"effectiveness_score":0.40,"electricity_required_kw":0,"water_required_kld":8},
}

COOLING_CENTRES = [
    {"id":"CC01","name":"Railway Station Shelter","lat":21.2245,"lon":81.6294,"capacity_persons":150,"operational":True},
    {"id":"CC02","name":"IG Stadium Cooling Point","lat":21.2617,"lon":81.6340,"capacity_persons":500,"operational":False},
    {"id":"CC03","name":"Collector Office Shelter","lat":21.2513,"lon":81.6296,"capacity_persons":100,"operational":True},
]
