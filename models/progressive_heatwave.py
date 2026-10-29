"""
AGNAYA V3.0 - 7-Stage Progressive Heatwave Lifecycle Simulator
Synthesizing research from GridStressDigitalTwin (7-stage time-stepping)
and ClimateSim (diurnal environmental and resilience dynamics)
"""

import numpy as np
from typing import Dict, List, Any
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.raipur_data import RAIPUR_SUBSTATIONS, RAIPUR_ZONES, RAIPUR_HOSPITALS, CSPDCL_PARAMS
from models.grid_power_flow import DCPowerFlowEngine
from models.grid_digital_twin import GridStressNetwork
from models.tapas_health import TapasHealthEngine


HEATWAVE_STAGES = [
    {
        "stage_id": 1,
        "name": "Stage 1: Morning Onset & Solar Inception",
        "time_label": "Day 1 — 08:30 AM",
        "ambient_temp_c": 39.5,
        "rel_humidity_pct": 46.0,
        "solar_w_m2": 620.0,
        "wind_speed_ms": 1.6,
        "base_load_mw": 325.0,
        "tripped_substation": None,
        "description": "Solar radiation starts warming concrete and tin rooftops. Residential AC baseline loading begins ramping across Civil Lines and Shankar Nagar.",
        "operational_directive": "CSPDCL State Load Dispatch Center (SLDC) puts spinning thermal reserves on hot standby. Municipal tankers pre-position at central depots.",
    },
    {
        "stage_id": 2,
        "name": "Stage 2: Solar AC Ramp & Pumping Surge",
        "time_label": "Day 1 — 12:00 PM",
        "ambient_temp_c": 43.2,
        "rel_humidity_pct": 34.0,
        "solar_w_m2": 920.0,
        "wind_speed_ms": 1.4,
        "base_load_mw": 395.0,
        "tripped_substation": None,
        "description": "Municipal water pumping stations operating at full capacity. Commercial refrigeration and cooling loads surge by +30%.",
        "operational_directive": "Activate Orange Heat Advisory. Prohibit non-essential heavy industrial smelting in Urla between 12:00 and 16:00.",
    },
    {
        "stage_id": 3,
        "name": "Stage 3: Peak Thermal Surge & Air-Cooling Crunch",
        "time_label": "Day 1 — 03:30 PM",
        "ambient_temp_c": 46.5,
        "rel_humidity_pct": 24.0,
        "solar_w_m2": 980.0,
        "wind_speed_ms": 1.1,
        "base_load_mw": 468.0,
        "tripped_substation": None,
        "description": "Ambient temperature reaches maximum summer peak. Raipur city demand exceeds normal summer capacity by +48 MW. Transformer top-oil hits 115°C.",
        "operational_directive": "ISSUE RED ALERT. Open all 12 municipal air-cooled refuge centers. Instruct outdoor construction laborers to suspend work.",
    },
    {
        "stage_id": 4,
        "name": "Stage 4: Critical Conductor Sag & Line Congestion",
        "time_label": "Day 1 — 05:30 PM",
        "ambient_temp_c": 45.8,
        "rel_humidity_pct": 26.0,
        "solar_w_m2": 450.0,
        "wind_speed_ms": 0.9,
        "base_load_mw": 455.0,
        "tripped_substation": None,
        "description": "High conductor temperatures cause physical thermal expansion on 132 kV lines. Ground clearance drops to cautionary limits over National Highway 53.",
        "operational_directive": "CSPTCL line transmission patrol monitors line sag on Raipur-Mowa corridor. Implement rotational peak shaving on industrial feeders.",
    },
    {
        "stage_id": 5,
        "name": "Stage 5: Nighttime Stifling Heat Entrapment",
        "time_label": "Day 1 — 11:30 PM",
        "ambient_temp_c": 35.2,
        "rel_humidity_pct": 44.0,
        "solar_w_m2": 0.0,
        "wind_speed_ms": 0.6,
        "base_load_mw": 410.0,
        "tripped_substation": None,
        "description": "Nighttime minimum fails to cool down. Transformers cannot dissipate stored core heat. Kutcha tin-roof shacks trap trapped daytime heat (+6°C).",
        "operational_directive": "Keep cooling shelters open overnight for unhoused and tin-roof slum residents. Night hydration patrols dispatched by ASHA/Mitanin workers.",
    },
    {
        "stage_id": 6,
        "name": "Stage 6: Cascading Transformer Burnout & Outage",
        "time_label": "Day 2 — 02:45 PM",
        "ambient_temp_c": 47.2,
        "rel_humidity_pct": 22.0,
        "solar_w_m2": 990.0,
        "wind_speed_ms": 1.0,
        "base_load_mw": 515.0,
        "tripped_substation": "S01",  # Raipur Main 220 kV tripped
        "description": "S01 Raipur Main (220 kV) transformer trips on over-temperature protection. Power redistributes across Mowa and Urla, cutting power to 4 municipal water pumps.",
        "operational_directive": "DEFCON 1 EMERGENCY. Disconnect non-critical industrial loads. Deploy mobile emergency diesel generators to Ambedkar Hospital and Telibandha Water Plant.",
    },
    {
        "stage_id": 7,
        "name": "Stage 7: AGNAYA Resilience & Lifeline Restoration",
        "time_label": "Day 3 — 10:00 AM",
        "ambient_temp_c": 44.0,
        "rel_humidity_pct": 32.0,
        "solar_w_m2": 820.0,
        "wind_speed_ms": 1.8,
        "base_load_mw": 420.0,
        "tripped_substation": None,
        "description": "AGNAYA autonomous dispatch plan executes: 5 cooling shelters, 20 water tankers, and 5 power resilience backup units restore city vital services.",
        "operational_directive": "Lifeline recovery verified. Excess hospitalizations drop by 68%. Transition to controlled rotational cooling and damage assessment.",
    },
]


class ProgressiveHeatwaveSimulator:
    """
    Executes a structured 7-stage heatwave scenario, integrating DC power flow,
    IEEE C57.91 transformer thermal aging, and TAPAS public health metrics.
    """
    def __init__(self):
        self.power_flow_engine = DCPowerFlowEngine()
        self.transformer_twin = GridStressNetwork()
        self.health_engine = TapasHealthEngine()
        self.stages = HEATWAVE_STAGES

    def get_stage_count(self) -> int:
        return len(self.stages)

    def evaluate_stage(self, stage_idx: int) -> Dict[str, Any]:
        """
        Evaluates physical state of grid, corridors, and wards for a specific heatwave stage.
        """
        idx = max(0, min(len(self.stages) - 1, stage_idx))
        s_data = self.stages[idx]

        t_amb = s_data["ambient_temp_c"]
        load_mw = s_data["base_load_mw"]
        tripped_sub = s_data["tripped_substation"]
        wind_ms = s_data["wind_speed_ms"]

        # 1. DC Power Flow & Corridor Thermal Evaluation
        pf_res = self.power_flow_engine.solve_power_flow(
            ambient_temp_c=t_amb,
            total_city_load_mw=load_mw,
            tripped_substation_id=tripped_sub,
            wind_speed_ms=wind_ms,
        )

        # 2. Transformer IEEE C57.91 Hotspot & Aging Rate
        tx_res = self.transformer_twin.compute_composite_grid_risk(
            ambient_temp_c=t_amb,
            city_demand_mw=load_mw,
            tripped_substation=tripped_sub,
        )

        # 3. TAPAS Ward Heat-Health Stress Index (HTSI)
        outage_hrs = 4.0 if tripped_sub else (1.5 if s_data["stage_id"] >= 5 else 0.0)
        health_res = self.health_engine.compute_ward_htsi(
            ambient_temp_c=t_amb,
            power_outage_hours=outage_hrs,
        )

        total_exposed_pop = sum(w["population"] for w in health_res if w["risk_band"] in ["SEVERE", "HIGH"])
        total_excess_deaths = sum(w["daily_excess_deaths"] for w in health_res)
        total_excess_admissions = sum(w["daily_emergency_admissions"] for w in health_res)
        max_indoor_temp = max(w["est_indoor_temp_c"] for w in health_res)

        return {
            "stage_info": s_data,
            "power_flow": pf_res,
            "transformers": tx_res,
            "wards_health": health_res,
            "metrics": {
                "ambient_temp_c": t_amb,
                "city_load_mw": load_mw,
                "grid_shortfall_mw": max(0.0, load_mw - CSPDCL_PARAMS["raipur_peak_demand_mw"]),
                "grid_stability_index": pf_res["grid_stability_index"],
                "congested_corridors_count": pf_res["congested_corridors_count"],
                "total_high_risk_citizens": int(total_exposed_pop),
                "total_daily_excess_deaths": round(total_excess_deaths, 1),
                "total_emergency_admissions": round(total_excess_admissions, 0),
                "max_indoor_temp_c": round(max_indoor_temp, 1),
            }
        }

    def get_all_stages(self) -> List[Dict[str, Any]]:

        """Returns structured summaries for all 7 chronological stages."""
        stage_colors = {
            1: "#00F0FF",
            2: "#38BDF8",
            3: "#F59E0B",
            4: "#F97316",
            5: "#E11D48",
            6: "#FF3366",
            7: "#10B981",
        }
        surges = [15.0, 85.0, 158.0, 145.0, 100.0, 205.0, 110.0]
        agings = [1.2, 2.4, 5.8, 4.9, 3.1, 14.5, 2.8]
        admissions = [12, 38, 115, 92, 64, 240, 42]
        sag_risks = ["LOW", "MODERATE", "HIGH", "CRITICAL", "MODERATE", "CRITICAL", "NORMAL"]

        all_stages = []
        for i, s in enumerate(self.stages):
            sid = s["stage_id"]
            all_stages.append({
                "stage_idx": sid,
                "stage_id": sid,
                "name": s["name"],
                "time_label": s["time_label"],
                "ambient_temp_c": s["ambient_temp_c"],
                "base_load_mw": s["base_load_mw"],
                "demand_surge_mw": surges[i],
                "transformer_aging_factor": agings[i],
                "hospital_heat_admissions": admissions[i],
                "sag_max_risk": sag_risks[i],
                "description": s["description"],
                "operational_directive": s["operational_directive"],
                "color": stage_colors.get(sid, "#00F0FF"),
            })
        return all_stages

    def get_stage_details(self, stage_idx: int) -> Dict[str, Any]:
        """Returns comprehensive operational profile for a selected stage (1-7)."""
        idx = max(1, min(7, stage_idx))
        all_s = self.get_all_stages()
        stg = next((s for s in all_s if s["stage_idx"] == idx), all_s[0])

        cascades = {
            1: "Morning temperature ramp elevates feeder ambient temperatures; minor thermal rise in substation top-oil.",
            2: "Simultaneous AC surge across commercial wards and high-lift water pump demand pushes 132 kV lines to 78% capacity.",
            3: "Extreme ambient air (46.5°C) impedes transformer cooling; IEEE C57.91 winding hot spots rise above 115°C across 3 substations.",
            4: "Thermal line elongation on 132 kV Mowa-Pandri span; catenary sag clearance decreases towards statutory NH-53 limits.",
            5: "Diurnal minimum stays at 35.2°C; informal settlements with tin roofs trap heat, increasing indoor temperatures up to 41.5°C.",
            6: "Over-temperature trip at S01 Raipur Main (220 kV) severs 4 municipal water pumps and plunges 3 residential wards into blackout.",
            7: "AGNAYA autonomous mobile generators and water tankers deploy; critical hospital power restored and cooling refuge centers staffed.",
        }

        lifelines = {
            1: ["Grid: Baseline 325 MW", "Water: Normal Pumping", "Health: Green Watch"],
            2: ["Grid: 395 MW (+22%)", "Water: Peak Filtration", "Health: Yellow Advisory"],
            3: ["Grid: 468 MW (+51%)", "Water: Storage Buffering", "Health: Red Alert Active"],
            4: ["Grid: 455 MW (Sag Risk)", "Water: 88% Flow", "Health: Red Alert"],
            5: ["Grid: 410 MW (Night Trap)", "Water: Low Pressure", "Health: Night Refuge Open"],
            6: ["Grid: S01 Tripped (Blackout)", "Water: 4 Pumps Down", "Health: Disaster Mode"],
            7: ["Grid: Emergency Tie-Ins", "Water: Tankers Dispatched", "Health: Recovery Mode"],
        }

        recommendations = {
            1: ["Alert CSPDCL SLDC to prime spinning reserve", "Inspect cooling oil pumps at Raipur Main 220 kV", "Broadcast preliminary heat advisory to public"],
            2: ["Enforce industrial peak-shaving in Urla & Siltara", "Pre-fill municipal overhead water reservoirs", "Distribute oral rehydration salts (ORS) to transit kiosks"],
            3: ["ISSUE MUNICIPAL RED ALERT", "Open all 12 air-cooled public cooling centers", "Mandate immediate cessation of outdoor labor from 12:00 to 16:00"],
            4: ["Deploy CSPTCL line thermal patrol along NH-53 corridors", "Reroute power via 132 kV Mandir Hasaud infeed", "Monitor catenary sag on ACSR Panther conductors"],
            5: ["Keep municipal cooling shelters open overnight", "ASHA & Mitanin workers conduct slum welfare checks", "Maintain emergency ventilation in elderly care facilities"],
            6: ["TRIGGER DEFCON 1 EMERGENCY RESPONSE", "Dispatch 5 mobile diesel generators to AIIMS & Ambedkar Hospital", "Reroute water tankers to severed Birgaon and Gudhiyari wards"],
            7: ["Transition to controlled rotational cooling", "Inspect tripped transformer for insulation damage", "Audit AGNAYA autonomous dispatch efficacy against CSERC targets"],
        }

        return {
            **stg,
            "cross_asset_cascade": cascades.get(idx, ""),
            "active_lifelines": lifelines.get(idx, []),
            "recommendations": recommendations.get(idx, []),
        }

    def generate_timeline_dataframe(self):
        """Returns a pandas DataFrame suitable for Plotly visualization across all 7 stages."""
        import pandas as pd
        all_s = self.get_all_stages()
        return pd.DataFrame([
            {
                "stage_idx": s["stage_idx"],
                "stage_name": f"Stage {s['stage_idx']}: {s['name'].split(': ')[1] if ': ' in s['name'] else s['name']}",
                "ambient_temp_c": s["ambient_temp_c"],
                "demand_surge_mw": s["demand_surge_mw"],
                "transformer_aging_factor": s["transformer_aging_factor"],
                "hospital_heat_admissions": s["hospital_heat_admissions"],
            }
            for s in all_s
        ])

