"""
AGNAYA - Grid Digital Twin & Pulse Stress Engine
Inspired by GridStressDigitalTwin (parisproffitt) and GridPulse-AI (doaamostafa67988)
Adapted for CSPTCL / CSPDCL Electrical Network in Raipur, Chhattisgarh
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.raipur_data import RAIPUR_SUBSTATIONS, CSPDCL_PARAMS, RAIPUR_ZONES


# ═══════════════════════════════════════════════════════════════════════════════
# 1. PIECEWISE LINEAR & UTILITY SCALING
# ═══════════════════════════════════════════════════════════════════════════════

def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def piecewise_linear(x: float, x0: float, x1: float) -> float:
    """Map x into [0, 1] linearly between x0 and x1, clamped outside."""
    if x <= x0:
        return 0.0
    if x >= x1:
        return 1.0
    return (x - x0) / (x1 - x0)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. TRANSFORMER THERMAL DIGITAL TWIN (IEEE C57.91 HOTSPOT MODEL)
# ═══════════════════════════════════════════════════════════════════════════════

class TransformerDigitalTwin:
    """
    Physics-inspired digital twin of high-voltage transmission and distribution
    substations in Raipur.

    Computes:
      - Top-oil temperature rise (Delta Theta_TO)
      - Winding hot-spot temperature rise (Delta Theta_H)
      - Relative aging rate (V = exp[ (15000 / 383) - (15000 / (Theta_H + 273)) ])
    """
    def __init__(self, substation_data: Dict[str, Any]):
        self.sub = substation_data
        self.name = substation_data["name"]
        self.capacity_mva = substation_data["capacity_mva"]
        self.voltage_kv = substation_data["voltage_kv"]
        self.age_years = substation_data["age_years"]
        self.has_backup = substation_data["backup_transformer"]

        # Cooling & temperature rise parameters calibrated by voltage, capacity, and transformer age
        cooling_profiles = {
            "S01": {"to_rise": 38.0, "h_rise": 20.0},  # 220 kV dual-bank OFAF, high efficiency cooling
            "S02": {"to_rise": 42.0, "h_rise": 22.0},  # 132 kV ONAF standard
            "S03": {"to_rise": 48.0, "h_rise": 26.0},  # 132 kV 35-year legacy unit, radiator scaling
            "S04": {"to_rise": 44.0, "h_rise": 24.0},  # 33 kV commercial distribution GSS
            "S05": {"to_rise": 43.0, "h_rise": 23.0},  # 33 kV industrial feeder GSS
            "S06": {"to_rise": 50.0, "h_rise": 28.0},  # 33 kV 30-year legacy unit in dense core, high ambient thermal trap
        }
        prof = cooling_profiles.get(substation_data["id"], {"to_rise": 45.0, "h_rise": 25.0})
        self.delta_theta_to_rated = prof["to_rise"]
        self.delta_theta_h_rated = prof["h_rise"]
        self.oil_exponent_m = 0.8
        self.winding_exponent_n = 0.8

    def calculate_hotspot(self, ambient_temp_c: float, load_ratio: float) -> Dict[str, float]:
        """
        Calculates transformer internal temperatures for given ambient and load ratio.
        """
        # Top-oil temperature
        top_oil_rise = self.delta_theta_to_rated * (load_ratio ** self.oil_exponent_m)
        top_oil_temp = ambient_temp_c + top_oil_rise

        # Winding hotspot temperature
        hotspot_rise = self.delta_theta_h_rated * (load_ratio ** self.winding_exponent_n)
        hotspot_temp = top_oil_temp + hotspot_rise

        # IEEE relative aging acceleration factor (Normal life = 1.0 at 110°C hotspot)
        if hotspot_temp > 80.0:
            aging_factor = np.exp((15000.0 / 383.15) - (15000.0 / (hotspot_temp + 273.15)))
        else:
            aging_factor = 0.1

        # Insulation life consumption per hour (nominal life = 180,000 hours)
        loss_of_life_pct_per_day = (aging_factor * 24.0 / 180000.0) * 100.0

        return {
            "ambient_temp_c": ambient_temp_c,
            "load_ratio": round(load_ratio, 3),
            "top_oil_temp_c": round(top_oil_temp, 1),
            "hotspot_temp_c": round(hotspot_temp, 1),
            "aging_acceleration_factor": round(aging_factor, 2),
            "loss_of_life_pct_per_day": round(loss_of_life_pct_per_day, 4),
            "status": "CRITICAL" if hotspot_temp >= 120.0 else "WARNING" if hotspot_temp >= 105.0 else "NORMAL"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SPATIAL NEIGHBOR STRESS & LOAD TRANSFER NETWORK
# ═══════════════════════════════════════════════════════════════════════════════

class GridStressNetwork:
    """
    Substation topology with electrical tie-lines for neighbor stress
    and N-1 contingency load-transfer modeling.
    """
    def __init__(self):
        self.substations = {s["id"]: s for s in RAIPUR_SUBSTATIONS}
        # Inter-substation tie lines (transmission & 33kV interconnects)
        self.neighbors: Dict[str, List[str]] = {
            "S01": ["S02", "S03", "S06"],  # Raipur Main ties to Mowa, Amanaka, Gudhiyari
            "S02": ["S01", "S04"],         # Mowa ties to Raipur Main and Pandri
            "S03": ["S01", "S06"],         # Amanaka ties to Raipur Main and Gudhiyari
            "S04": ["S02", "S05"],         # Pandri ties to Mowa and Khamardih
            "S05": ["S04", "S01"],         # Khamardih ties to Pandri and Raipur Main
            "S06": ["S01", "S03"],         # Gudhiyari ties to Raipur Main and Amanaka
        }
        self.twins = {sid: TransformerDigitalTwin(data) for sid, data in self.substations.items()}

    def compute_neighbor_stress(self, load_map: Dict[str, float]) -> Dict[str, float]:
        """
        Calculates fraction of electrically adjacent substations exceeding 85% load.
        """
        neighbor_stress = {}
        for sid, adj_list in self.neighbors.items():
            if not adj_list:
                neighbor_stress[sid] = 0.0
                continue
            stressed_count = sum(1 for n in adj_list if load_map.get(n, 0.0) >= 0.85)
            neighbor_stress[sid] = stressed_count / len(adj_list)
        return neighbor_stress

    def compute_composite_grid_risk(
        self,
        ambient_temp_c: float,
        city_demand_mw: float,
        tripped_substation: str = None
    ) -> List[Dict[str, Any]]:
        """
        Evaluates digital twin state and composite risk for all substations.
        Simulates load rerouting if a substation has tripped.
        """
        normal_city_demand = CSPDCL_PARAMS["raipur_normal_demand_mw"]
        demand_scaling = city_demand_mw / normal_city_demand

        # Substation-specific thermal load characteristics
        sub_load_profiles = {
            "S01": {"base_lf": 0.55, "slope": 0.16},  # 500 MVA 220 kV bulk transmission infeed
            "S02": {"base_lf": 0.62, "slope": 0.24},  # 200 MVA 132 kV Mowa commercial/hosp
            "S03": {"base_lf": 0.70, "slope": 0.28},  # 160 MVA 132 kV Amanaka institutional
            "S04": {"base_lf": 0.72, "slope": 0.36},  # 80 MVA 33 kV Pandri commercial market AC surge
            "S05": {"base_lf": 0.64, "slope": 0.25},  # 50 MVA 33 kV Khamardih mixed
            "S06": {"base_lf": 0.78, "slope": 0.44},  # 60 MVA 33 kV Gudhiyari dense slum/core (heavily loaded)
        }

        # Step 1: Base load calculation with authentic engineering variance
        loads: Dict[str, float] = {}
        for sid, s in self.substations.items():
            prof = sub_load_profiles.get(sid, {"base_lf": s["load_factor_normal"], "slope": 0.30})
            calculated_lf = prof["base_lf"] + prof["slope"] * (demand_scaling - 1.0)
            loads[sid] = round(max(0.40, min(1.30, calculated_lf)), 3)

        # Step 2: Handle trip and load redistribution
        if tripped_substation and tripped_substation in self.substations:
            spilled_load_mva = self.substations[tripped_substation]["capacity_mva"] * loads[tripped_substation]
            loads[tripped_substation] = 0.0  # tripped
            adj = self.neighbors.get(tripped_substation, [])
            if adj:
                transfer_per_neighbor = spilled_load_mva / len(adj)
                for n in adj:
                    extra_ratio = transfer_per_neighbor / self.substations[n]["capacity_mva"]
                    loads[n] = round(min(1.35, loads[n] + extra_ratio), 3)

        # Step 3: Compute neighbor stress
        neighbor_stress = self.compute_neighbor_stress(loads)

        # Step 4: Calculate comprehensive metrics
        results = []
        for sid, s in self.substations.items():
            load_ratio = loads[sid]
            n_stress = neighbor_stress[sid]

            # Digital twin thermal run
            twin = self.twins[sid]
            thermal = twin.calculate_hotspot(ambient_temp_c, load_ratio)

            # Piecewise risk components (GridStressDigitalTwin formula)
            load_comp = piecewise_linear(load_ratio, 0.70, 0.95)
            temp_comp = piecewise_linear(ambient_temp_c, 38.0, 48.0)
            neigh_comp = clamp(n_stress)

            # GridPulse-AI inspired composite weight
            # 50% load stress, 30% ambient thermal stress, 20% spatial neighbor congestion
            composite_score = clamp(0.50 * load_comp + 0.30 * temp_comp + 0.20 * neigh_comp)

            level = "CRITICAL" if composite_score >= 0.70 else "ELEVATED" if composite_score >= 0.40 else "NORMAL"

            results.append({
                "substation_id": sid,
                "name": s["name"],
                "voltage_kv": s["voltage_kv"],
                "capacity_mva": s["capacity_mva"],
                "load_ratio": round(load_ratio, 3),
                "load_mw_approx": round(load_ratio * s["capacity_mva"] * 0.9, 1),
                "neighbor_stress_frac": round(n_stress, 2),
                "hotspot_temp_c": thermal["hotspot_temp_c"],
                "top_oil_temp_c": thermal["top_oil_temp_c"],
                "aging_factor": thermal["aging_acceleration_factor"],
                "composite_risk_score": round(composite_score, 3),
                "risk_level": level,
                "tripped": (sid == tripped_substation)
            })

        return results


# ═══════════════════════════════════════════════════════════════════════════════
# 4. SPATIAL DEMAND REWEIGHTING (FROM GRIDPULSE-AI)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_spatial_load_distribution(total_demand_mw: float) -> List[Dict[str, Any]]:
    """
    Applies infrastructure density reweighting (as used in GridPulse-AI)
    to distribute Raipur's aggregate city demand to individual zones.
    Heavy industrial zones (Urla, Birgaon) receive higher power allocations.
    """
    zone_weights = []
    for z in RAIPUR_ZONES:
        # Industrial and high population wards have higher connected infrastructure density
        weight = z["population"] * (1.8 if "Industrial" in z["name"] or z["id"] in ["Z01", "Z02"] else 1.0)
        zone_weights.append(weight)

    total_weight = sum(zone_weights)
    distribution = []
    for z, w in zip(RAIPUR_ZONES, zone_weights):
        allocated_mw = total_demand_mw * (w / total_weight)
        distribution.append({
            "zone_id": z["id"],
            "zone_name": z["name"],
            "allocated_demand_mw": round(allocated_mw, 1),
            "demand_share_pct": round((w / total_weight) * 100, 2),
            "substation_assigned": z["substation"]
        })

    return distribution
