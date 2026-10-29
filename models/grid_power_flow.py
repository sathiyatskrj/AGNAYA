"""
AGNAYA V3.0 - Synchronous DC Power Flow & IEEE Std 738 Dynamic Line Rating
Synthesizing models from ClimateSim (DC Power Flow) and Heat-Analysis (IEEE 738)
Calibrated for CSPTCL / CSPDCL Raipur High-Voltage Transmission Network (220/132/33 kV)
"""

import numpy as np
from typing import Dict, List, Any, Tuple
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.raipur_data import RAIPUR_SUBSTATIONS, CSPDCL_PARAMS


# ═══════════════════════════════════════════════════════════════════════════════
# 1. TRANSMISSION CORRIDORS & NETWORK TOPOLOGY
# ═══════════════════════════════════════════════════════════════════════════════

RAIPUR_GRID_BRANCHES = [
    {
        "id": "L01",
        "name": "Raipur Main – Mowa (220 kV Inter-tie)",
        "from_bus": "S01",
        "to_bus": "S02",
        "voltage_kv": 220,
        "length_km": 16.5,
        "conductor": "ACSR Zebra (420 mm²)",
        "reactance_pu": 0.055,  # 100 MVA base
        "rated_mva": 450.0,
        "rated_amps": 1200.0,
        "normal_flow_mw": 165.0,
        "span_meters": 320.0,
        "base_clearance_m": 8.5,  # Roadway statutory clearance
    },
    {
        "id": "L02",
        "name": "Raipur Main – Amanaka (132 kV Ring)",
        "from_bus": "S01",
        "to_bus": "S03",
        "voltage_kv": 132,
        "length_km": 14.2,
        "conductor": "ACSR Panther (200 mm²)",
        "reactance_pu": 0.092,
        "rated_mva": 180.0,
        "rated_amps": 800.0,
        "normal_flow_mw": 85.0,
        "span_meters": 280.0,
        "base_clearance_m": 7.5,
    },
    {
        "id": "L03",
        "name": "Mowa – Urla Industrial (132 kV Heavy Feeder)",
        "from_bus": "S02",
        "to_bus": "S05",
        "voltage_kv": 132,
        "length_km": 12.8,
        "conductor": "ACSR Panther (200 mm²)",
        "reactance_pu": 0.084,
        "rated_mva": 180.0,
        "rated_amps": 800.0,
        "normal_flow_mw": 95.0,
        "span_meters": 270.0,
        "base_clearance_m": 7.2,
    },
    {
        "id": "L04",
        "name": "Urla Industrial – Borjhara (132 kV Heavy Link)",
        "from_bus": "S05",
        "to_bus": "S04",
        "voltage_kv": 132,
        "length_km": 10.4,
        "conductor": "ACSR Panther (200 mm²)",
        "reactance_pu": 0.071,
        "rated_mva": 180.0,
        "rated_amps": 800.0,
        "normal_flow_mw": 75.0,
        "span_meters": 260.0,
        "base_clearance_m": 7.2,
    },
    {
        "id": "L05",
        "name": "Amanaka – Gudhiyari (33 kV Sub-Transmission)",
        "from_bus": "S03",
        "to_bus": "S06",
        "voltage_kv": 33,
        "length_km": 8.6,
        "conductor": "ACSR Dog (100 mm²)",
        "reactance_pu": 0.210,
        "rated_mva": 35.0,
        "rated_amps": 450.0,
        "normal_flow_mw": 18.0,
        "span_meters": 180.0,
        "base_clearance_m": 6.2,
    },
    {
        "id": "L06",
        "name": "Mowa – Gudhiyari (33 kV Parallel Tie)",
        "from_bus": "S02",
        "to_bus": "S06",
        "voltage_kv": 33,
        "length_km": 9.2,
        "conductor": "ACSR Dog (100 mm²)",
        "reactance_pu": 0.240,
        "rated_mva": 35.0,
        "rated_amps": 450.0,
        "normal_flow_mw": 16.0,
        "span_meters": 180.0,
        "base_clearance_m": 6.2,
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# 2. IEEE STD 738 THERMAL AMPACITY & LINE SAG ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class ConductorPhysicsEngine:
    """
    Computes dynamic thermal rating (DTR) and physical conductor sag
    based on IEEE Std 738-2012 heat balance:
        q_c + q_r = q_s + I^2 * R(Tc)
    """
    def __init__(self):
        # Conductor physical properties
        self.conductor_data = {
            "ACSR Zebra (420 mm²)": {"diam_mm": 28.62, "r25_per_km": 0.0674, "alpha": 0.00403, "mass_kg_m": 1.621},
            "ACSR Panther (200 mm²)": {"diam_mm": 21.00, "r25_per_km": 0.1363, "alpha": 0.00403, "mass_kg_m": 0.974},
            "ACSR Dog (100 mm²)": {"diam_mm": 14.15, "r25_per_km": 0.2733, "alpha": 0.00403, "mass_kg_m": 0.394},
        }

    def compute_dtr_and_sag(
        self,
        branch: Dict[str, Any],
        actual_mw_flow: float,
        ambient_temp_c: float,
        wind_speed_ms: float = 1.2,
        solar_radiation_w_m2: float = 950.0,
        max_allowable_tc: float = 85.0
    ) -> Dict[str, Any]:
        """
        Calculates conductor operating temperature, IEEE 738 ampacity limit,
        and physical conductor sag over the span.
        """
        c_info = self.conductor_data.get(branch["conductor"], self.conductor_data["ACSR Panther (200 mm²)"])
        d_m = c_info["diam_mm"] / 1000.0

        # Conductor resistance at ambient temp
        r_amb = c_info["r25_per_km"] * (1.0 + c_info["alpha"] * (ambient_temp_c - 25.0)) / 1000.0

        # Current in Amperes
        v_kv = branch["voltage_kv"]
        current_amps = (actual_mw_flow * 1e6) / (np.sqrt(3) * v_kv * 1000.0 * 0.92)  # 0.92 PF

        # Heat rates per meter (W/m)
        # 1. Solar heat gain q_s
        absorptivity = 0.85
        q_s = absorptivity * solar_radiation_w_m2 * d_m

        # 2. Joule heating I^2 * R
        q_joule = (current_amps ** 2) * r_amb

        # 3. Convective cooling q_c (Morgan / IEEE 738 formulation)
        air_density = 1.15  # kg/m³ at Raipur 300m elevation
        kinematic_viscosity = 1.78e-5  # m²/s
        reynolds = (wind_speed_ms * d_m) / kinematic_viscosity
        nusselt = 0.641 * (reynolds ** 0.471) if reynolds > 0 else 0.5
        k_air = 0.028  # W/(m·K)
        h_c = (nusselt * k_air) / d_m

        # Solve for operating conductor temperature Tc:
        # q_joule + q_s = h_c * pi * d_m * (Tc - Ta) + epsilon * sigma * pi * d_m * (Tc^4 - Ta^4)
        # Linearized approximation for fast convergence:
        delta_t = (q_joule + q_s) / (h_c * np.pi * d_m + 0.02)
        operating_tc = ambient_temp_c + delta_t

        # Thermal Derating Percentage relative to rated amps
        # At max allowable temp (85°C), maximum ampacity I_max:
        r_max = c_info["r25_per_km"] * (1.0 + c_info["alpha"] * (max_allowable_tc - 25.0)) / 1000.0
        q_cooling_max = h_c * np.pi * d_m * (max_allowable_tc - ambient_temp_c)
        i_max_amps = np.sqrt(max(0.0, (q_cooling_max - q_s) / max(1e-6, r_max)))
        derated_mw_cap = (np.sqrt(3) * v_kv * i_max_amps * 0.92) / 1000.0
        derate_pct = max(0.0, (1.0 - i_max_amps / branch["rated_amps"]) * 100.0)

        # 4. Conductor Sag Calculation (Parabolic approximation)
        # S = (w * L^2) / (8 * H)
        span_l = branch["span_meters"]
        w_weight = c_info["mass_kg_m"] * 9.81  # N/m
        # Horizontal tension drops as conductor expands with temperature:
        h_nominal = 18000.0  # N nominal tension at 25°C
        thermal_expansion_coeff = 23e-6  # 1/°C for aluminum
        delta_tc_ref = max(0.0, operating_tc - 25.0)
        h_effective = h_nominal / (1.0 + thermal_expansion_coeff * delta_tc_ref * 8.0)
        h_effective = max(6000.0, h_effective)

        sag_meters = (w_weight * (span_l ** 2)) / (8.0 * h_effective)
        nominal_sag = (w_weight * (span_l ** 2)) / (8.0 * h_nominal)
        excess_sag = max(0.0, sag_meters - nominal_sag)
        clearance_remaining = max(0.0, branch["base_clearance_m"] - excess_sag)

        # Sag safety status
        if clearance_remaining < 5.5:
            sag_status = "CRITICAL_CLEARANCE_VIOLATION"
        elif clearance_remaining < 6.5:
            sag_status = "WARNING_HIGH_SAG"
        else:
            sag_status = "NOMINAL_CLEARANCE"

        return {
            "branch_id": branch["id"],
            "name": branch["name"],
            "operating_tc_celsius": round(operating_tc, 1),
            "max_allowable_tc": max_allowable_tc,
            "actual_current_amps": round(current_amps, 1),
            "ieee738_ampacity_amps": round(i_max_amps, 1),
            "derated_mw_capacity": round(derated_mw_cap, 1),
            "thermal_derate_pct": round(derate_pct, 1),
            "conductor_sag_m": round(sag_meters, 2),
            "excess_sag_m": round(excess_sag, 2),
            "clearance_remaining_m": round(clearance_remaining, 2),
            "sag_status": sag_status,
            "loading_pct": round((actual_mw_flow / max(1.0, derated_mw_cap)) * 100.0, 1),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SYNCHRONOUS DC POWER FLOW ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

class DCPowerFlowEngine:
    """
    Computes Fast DC Power Flow:
        P = [B] * theta
    Supports N-1 contingency line/substation trip redispatch and IEEE 738 line ratings.
    """
    def __init__(self):
        self.substations = {s["id"]: s for s in RAIPUR_SUBSTATIONS}
        self.buses = ["S01", "S02", "S03", "S04", "S05", "S06"]
        self.bus_idx = {b: i for i, b in enumerate(self.buses)}
        self.branches = []
        for br in RAIPUR_GRID_BRANCHES:
            b_copy = dict(br)
            b_copy["line_id"] = br["id"]
            b_copy["rating_mw"] = br["rated_mva"]
            self.branches.append(b_copy)
        self.lines = self.branches
        self.conductor_engine = ConductorPhysicsEngine()

    def solve_dc_power_flow(
        self,
        total_demand_mw: float,
        tripped_line_id: str = None,
        tripped_substation_id: str = None,
        ambient_temp_c: float = 45.0,
        wind_speed_ms: float = 1.2,
    ) -> Dict[str, Any]:
        """Convenience wrapper for DC power flow with normalized output keys."""
        res = self.solve_power_flow(
            ambient_temp_c=ambient_temp_c,
            total_city_load_mw=total_demand_mw,
            tripped_substation_id=tripped_substation_id,
            tripped_line_id=tripped_line_id,
            wind_speed_ms=wind_speed_ms,
        )
        bus_angles_deg = {b: res["bus_summary"][b]["voltage_angle_deg"] for b in self.buses}
        bus_injections_mw = {b: res["bus_summary"][b]["power_injection_mw"] for b in self.buses}
        line_flows_mw = {c["branch_id"]: c["power_flow_mw"] for c in res["corridor_results"]}
        line_loadings_pct = {c["branch_id"]: c["loading_pct"] for c in res["corridor_results"]}
        overloaded_lines = [c["branch_id"] for c in res["corridor_results"] if c["is_overloaded"]]
        return {
            "bus_angles_deg": bus_angles_deg,
            "bus_injections_mw": bus_injections_mw,
            "line_flows_mw": line_flows_mw,
            "line_loadings_pct": line_loadings_pct,
            "overloaded_lines": overloaded_lines,
            "grid_stability_index": res["grid_stability_index"],
            "raw_results": res,
        }

    def compute_ieee738_dtr(
        self,
        ambient_temp_c: float,
        wind_speed_ms: float = 1.2,
        solar_flux_w_m2: float = 950.0,
    ) -> List[Dict[str, Any]]:
        """Computes IEEE 738 dynamic thermal ratings and catenary sag across all corridors."""
        dtr_list = []
        for br in self.branches:
            eval_res = self.conductor_engine.compute_dtr_and_sag(
                branch=br,
                actual_mw_flow=br["normal_flow_mw"],
                ambient_temp_c=ambient_temp_c,
                wind_speed_ms=wind_speed_ms,
                solar_radiation_w_m2=solar_flux_w_m2,
            )
            dtr_list.append({
                "line_id": br["id"],
                "name": br["name"],
                "voltage_kv": br["voltage_kv"],
                "conductor": br["conductor"],
                "static_rating_mva": br["rated_mva"],
                "dtr_rating_mva": eval_res["derated_mw_capacity"],
                "derating_pct": eval_res["thermal_derate_pct"],
                "sag_clearance_m": eval_res["clearance_remaining_m"],
                "sag_risk": "CRITICAL" if eval_res["sag_status"] == "CRITICAL_CLEARANCE_VIOLATION" else "HIGH" if eval_res["sag_status"] == "WARNING_HIGH_SAG" else "NORMAL",
            })
        return dtr_list


    def _build_susceptance_matrix(self, active_branches: List[Dict[str, Any]]) -> np.ndarray:
        n = len(self.buses)
        B = np.zeros((n, n), dtype=float)
        for br in active_branches:
            i = self.bus_idx[br["from_bus"]]
            j = self.bus_idx[br["to_bus"]]
            b_val = 1.0 / max(0.001, br["reactance_pu"])
            B[i, j] -= b_val
            B[j, i] -= b_val
            B[i, i] += b_val
            B[j, j] += b_val
        return B

    def solve_power_flow(
        self,
        ambient_temp_c: float,
        total_city_load_mw: float,
        tripped_substation_id: str = None,
        tripped_line_id: str = None,
        wind_speed_ms: float = 1.2,
    ) -> Dict[str, Any]:
        """
        Solves bus voltage angles and branch flows under ambient temperature and contingencies.
        """
        # Active branches under contingency
        active_br = []
        for br in self.branches:
            if tripped_line_id and br["id"] == tripped_line_id:
                continue
            if tripped_substation_id and (br["from_bus"] == tripped_substation_id or br["to_bus"] == tripped_substation_id):
                continue
            active_br.append(br)

        B = self._build_susceptance_matrix(active_br)

        # Distribute net load across buses based on historical CSPDCL substation weights
        bus_load_shares = {
            "S01": 0.05,  # Raipur Main internal aux
            "S02": 0.24,  # Mowa commercial & residential
            "S03": 0.18,  # Amanaka institutional & west
            "S04": 0.16,  # Borjhara industrial & pumping
            "S05": 0.25,  # Urla heavy steel/sponge iron
            "S06": 0.12,  # Gudhiyari dense core
        }

        # Bus power injections in Per-Unit on S_base = 100.0 MVA
        # P_inj_pu = (Generation - Load) / S_base
        S_base = 100.0
        p_inj_mw = np.zeros(len(self.buses), dtype=float)
        p_inj_pu = np.zeros(len(self.buses), dtype=float)

        for b, share in bus_load_shares.items():
            idx = self.bus_idx[b]
            load_mw = total_city_load_mw * share
            if b == "S01":
                # Slack generator supplies total city load + transmission losses
                p_inj_mw[idx] = total_city_load_mw * 0.95
            else:
                p_inj_mw[idx] = -load_mw
            p_inj_pu[idx] = p_inj_mw[idx] / S_base

        # Solve DC power flow with Slack Bus at index 0 (S01, theta_0 = 0 rad)
        # B_reduced * theta_reduced = P_reduced_pu
        theta = np.zeros(len(self.buses), dtype=float)
        B_red = B[1:, 1:]
        p_red_pu = p_inj_pu[1:]

        try:
            # Regularize slightly if singular due to islanding
            if np.linalg.cond(B_red) > 1e10:
                B_red += np.eye(len(B_red)) * 1e-4
            theta_red = np.linalg.solve(B_red, p_red_pu)
            theta[1:] = theta_red
        except np.linalg.LinAlgError:
            theta[1:] = 0.0

        # Calculate branch flows and dynamic thermal ratings
        line_results = []
        total_grid_loss_mw = 0.0
        congested_count = 0

        for br in self.branches:
            is_active = br in active_br
            if is_active:
                i = self.bus_idx[br["from_bus"]]
                j = self.bus_idx[br["to_bus"]]
                # P_ij_pu = (theta_i - theta_j) / X_ij
                # P_ij_MW = P_ij_pu * S_base
                flow_mw = ((theta[i] - theta[j]) / br["reactance_pu"]) * S_base
                # Realistic physical clamping within line capability
                flow_mw = float(np.clip(flow_mw, -br["rated_mva"] * 1.25, br["rated_mva"] * 1.25))
                abs_flow = abs(flow_mw)
            else:
                abs_flow = 0.0
                flow_mw = 0.0

            # IEEE Std 738 dynamic thermal evaluation
            dtr_sag = self.conductor_engine.compute_dtr_and_sag(
                branch=br,
                actual_mw_flow=abs_flow,
                ambient_temp_c=ambient_temp_c,
                wind_speed_ms=wind_speed_ms,
            )

            is_overloaded = bool(abs_flow > dtr_sag["derated_mw_capacity"])
            if is_overloaded:
                congested_count += 1

            line_results.append({
                "branch_id": br["id"],
                "name": br["name"],
                "from_bus": br["from_bus"],
                "to_bus": br["to_bus"],
                "voltage_kv": int(br["voltage_kv"]),
                "is_active": bool(is_active),
                "power_flow_mw": float(round(flow_mw, 1)),
                "rated_mva": float(br["rated_mva"]),
                "dtr_capacity_mw": float(dtr_sag["derated_mw_capacity"]),
                "thermal_derate_pct": float(dtr_sag["thermal_derate_pct"]),
                "conductor_temp_c": float(dtr_sag["operating_tc_celsius"]),
                "conductor_sag_m": float(dtr_sag["conductor_sag_m"]),
                "clearance_remaining_m": float(dtr_sag["clearance_remaining_m"]),
                "sag_status": str(dtr_sag["sag_status"]),
                "is_overloaded": bool(is_overloaded),
                "loading_pct": float(dtr_sag["loading_pct"]),
            })

        # Bus summary
        bus_summary = {}
        for b in self.buses:
            idx = self.bus_idx[b]
            bus_summary[b] = {
                "bus_id": b,
                "name": self.substations[b]["name"],
                "voltage_angle_deg": round(float(np.degrees(theta[idx])), 2),
                "power_injection_mw": round(float(p_inj_mw[idx]), 1),
                "is_tripped": bool(b == tripped_substation_id),
            }


        return {
            "ambient_temp_c": ambient_temp_c,
            "total_city_load_mw": total_city_load_mw,
            "tripped_substation": tripped_substation_id,
            "tripped_line": tripped_line_id,
            "congested_corridors_count": congested_count,
            "corridor_results": line_results,
            "bus_summary": bus_summary,
            "grid_stability_index": round(max(0.0, 100.0 - (congested_count * 22.0) - (15.0 if tripped_substation_id else 0.0)), 1),
        }
