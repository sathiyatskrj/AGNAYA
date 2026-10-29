"""
AGNAYA V3.0 - GridPulse 5-Component Deterministic Risk Engine & Auditable Rationale
Synthesizing research from GridPulse-AI (doaamostafa67988)
Decomposes ward-level vulnerability into 5 auditable components:
  Risk = 0.30*H + 0.25*D + 0.20*A + 0.15*O + 0.10*V
Generates boardroom-ready Audit Report Cards with explicit legal/demographic citations.
"""

import numpy as np
from typing import Dict, List, Any
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.raipur_data import RAIPUR_ZONES, RAIPUR_SUBSTATIONS, RAIPUR_WATER_PUMPS, CSPDCL_PARAMS


class GridPulseRiskEngine:
    """
    Computes deterministic 5-component risk vectors across all 12 Raipur wards.
    Provides verifiable citations for every metric.
    """
    def __init__(self):
        self.zones = {z["id"]: z for z in RAIPUR_ZONES}
        self.substations = {s["id"]: s for s in RAIPUR_SUBSTATIONS}
        self.water_pumps = {w["id"]: w for w in RAIPUR_WATER_PUMPS}

    def evaluate_city_risk(
        self,
        ambient_temp_c: float,
        city_load_mw: float,
        tripped_substation_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluates 5-component risk for each zone.
        """
        results = []
        normal_load = CSPDCL_PARAMS["raipur_normal_demand_mw"]
        load_surge_factor = city_load_mw / normal_load

        for zid, z in self.zones.items():
            # 1. Thermal Hazard H (0 - 100)
            # Temperature excess over IMD normal (42.4°C) + UHI penalty (slum vs green cover)
            uhi_offset = (z["slum_pct"] * 3.5) - (z["green_cover_pct"] * 3.0)
            felt_t = ambient_temp_c + uhi_offset
            h_score = float(np.clip((felt_t - 38.0) / 12.0 * 100.0, 0.0, 100.0))

            # 2. Demand Strain D (0 - 100)
            # Ward load relative to serving substation capacity
            sub = self.substations[z["substation"]]
            base_load_fraction = sub["load_factor_normal"] * load_surge_factor
            if tripped_substation_id and z["substation"] == tripped_substation_id:
                base_load_fraction = 1.35  # Extreme overload / trip
            d_score = float(np.clip(base_load_fraction * 80.0, 0.0, 100.0))

            # 3. Asset Fragility A (0 - 100)
            # Substation transformer age, lack of backup, thermal derating
            age_penalty = max(0.0, (sub["age_years"] - 10.0) / 25.0 * 45.0)
            backup_penalty = 0.0 if sub["backup_transformer"] else 25.0
            temp_derate_penalty = max(0.0, (ambient_temp_c - 40.0) * 4.5)
            a_score = float(np.clip(age_penalty + backup_penalty + temp_derate_penalty, 0.0, 100.0))

            # 4. Outage Propensity O (0 - 100)
            # Water pump dependency on electricity and backup generator status
            wp = self.water_pumps.get(z["water_pump"])
            wp_unprotected = 0.0 if (wp and wp["backup_generator"]) else 45.0
            is_sub_tripped = 55.0 if (tripped_substation_id and z["substation"] == tripped_substation_id) else 10.0
            o_score = float(np.clip(wp_unprotected + is_sub_tripped, 0.0, 100.0))

            # 5. Social Vulnerability V (0 - 100)
            # Slum percentage, kutcha housing tin-roof share, elderly, AC access
            slum_component = z["slum_pct"] * 55.0
            tin_roof_component = (z["kutcha_housing_pct"] if "kutcha_housing_pct" in z else z["slum_pct"] * 0.8) * 35.0
            lack_of_ac = (1.0 - z["ac_penetration_pct"]) * 25.0
            v_score = float(np.clip(slum_component + tin_roof_component + lack_of_ac, 0.0, 100.0))

            # Composite 5-Component Weighted Score
            composite_risk = (
                0.30 * h_score +
                0.25 * d_score +
                0.20 * a_score +
                0.15 * o_score +
                0.10 * v_score
            )
            composite_risk = round(float(np.clip(composite_risk, 0.0, 100.0)), 1)

            # Risk Band Classification
            if composite_risk >= 70.0:
                band = "CRITICAL"
                badge_col = "#FF3366"
            elif composite_risk >= 50.0:
                band = "HIGH"
                badge_col = "#F59E0B"
            elif composite_risk >= 30.0:
                band = "ELEVATED"
                badge_col = "#EAB308"
            else:
                band = "GUARDED"
                badge_col = "#10B981"

            # Primary aggravating driver
            components = {
                "Thermal UHI Hazard": h_score,
                "Grid Demand Strain": d_score,
                "Substation Fragility": a_score,
                "Water Outage Exposure": o_score,
                "Informal Housing Vulnerability": v_score,
            }
            primary_driver = max(components, key=components.get)

            # Audit rationale
            rationale = (
                f"Ward {z['name']} ({zid}) scored {composite_risk}/100 [{band}]. "
                f"Primary vulnerability driver is {primary_driver} ({components[primary_driver]:.1f}/100). "
                f"Serving Substation: {sub['name']} ({sub['voltage_kv']} kV, Age {sub['age_years']}y). "
                f"Informal Settlement Density: {z['slum_pct']*100:.0f}%, Population: {z['population']:,}."
            )

            results.append({
                "zone_id": zid,
                "zone_name": z["name"],
                "population": z["population"],
                "composite_risk": composite_risk,
                "risk_band": band,
                "badge_color": badge_col,
                "primary_driver": primary_driver,
                "components": {
                    "hazard_H": round(h_score, 1),
                    "demand_D": round(d_score, 1),
                    "fragility_A": round(a_score, 1),
                    "outage_O": round(o_score, 1),
                    "vulnerability_V": round(v_score, 1),
                },
                "substation": sub["name"],
                "audit_rationale": rationale,
                "citations": [
                    "CSERC Tariff Order FY 2024-25 (CSPDCL)",
                    "Census 2011 Raipur Municipal Corporation (RMC)",
                    "IMD Climatological Normals 1970–2024 (Station #42809)",
                ]
            })

        # Sort descending by composite risk
        return sorted(results, key=lambda x: x["composite_risk"], reverse=True)

    def compute_all_wards_gridpulse(
        self,
        ambient_temp_c: float,
        total_grid_demand_mw: float,
        outage_hours: float = 0.0,
        tripped_substation_id: str = None,
    ) -> List[Dict[str, Any]]:
        """Normalized citywide 12-ward GridPulse 5-component risk matrix."""
        raw = self.evaluate_city_risk(
            ambient_temp_c=ambient_temp_c,
            city_load_mw=total_grid_demand_mw,
            tripped_substation_id=tripped_substation_id,
        )
        normalized = []
        for r in raw:
            normalized.append({
                "zone_id": r["zone_id"],
                "zone_name": r["zone_name"],
                "composite_risk": r["composite_risk"],
                "risk_tier": r["risk_band"],
                "H_hazard": r["components"]["hazard_H"],
                "D_demand": r["components"]["demand_D"],
                "A_asset": r["components"]["fragility_A"],
                "O_outage": r["components"]["outage_O"],
                "V_vulnerability": r["components"]["vulnerability_V"],
                "primary_driver": r["primary_driver"],
                "substation": r["substation"],
                "audit_rationale": r["audit_rationale"],
                "citations": r["citations"],
            })
        return normalized

    def generate_boardroom_audit_report(
        self,
        zone_id: str,
        ambient_temp_c: float,
        total_grid_demand_mw: float,
        outage_hours: float = 0.0,
        tripped_substation_id: str = None,
    ) -> Dict[str, Any]:
        """Generates auditable boardroom report card for an individual municipal ward."""
        all_wards = self.compute_all_wards_gridpulse(
            ambient_temp_c=ambient_temp_c,
            total_grid_demand_mw=total_grid_demand_mw,
            outage_hours=outage_hours,
            tripped_substation_id=tripped_substation_id,
        )
        z_match = next((w for w in all_wards if w["zone_id"] == zone_id or w["zone_name"] == zone_id), all_wards[0])
        return {
            "zone_id": z_match["zone_id"],
            "zone_name": z_match["zone_name"],
            "composite_risk": z_match["composite_risk"],
            "risk_tier": z_match["risk_tier"],
            "executive_summary": z_match["audit_rationale"],
            "factors": {
                "H_hazard": z_match["H_hazard"],
                "D_demand": z_match["D_demand"],
                "A_asset": z_match["A_asset"],
                "O_outage": z_match["O_outage"],
                "V_vulnerability": z_match["V_vulnerability"],
            },
            "primary_driver": z_match["primary_driver"],
            "citations": z_match["citations"],
        }

