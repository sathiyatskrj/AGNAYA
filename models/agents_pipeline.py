"""
AGNAYA - 3-Agent Collaborative Autonomous Pipeline
Inspired by heatwave-public (kd365)
Engineered for Raipur, Chhattisgarh Heatwave Disaster Response
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from scipy.optimize import milp, LinearConstraint, Bounds
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.raipur_data import (
    RAIPUR_ZONES, RAIPUR_SUBSTATIONS, RAIPUR_WATER_PUMPS,
    RAIPUR_HOSPITALS, INTERVENTION_OPTIONS, CSPDCL_PARAMS
)
from models.grid_digital_twin import GridStressNetwork
from models.tapas_health import TapasHealthEngine


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT 1: SPATIAL & CLIMATE INGESTION AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class SpatialClimateAgent:
    """
    Agent 1: Ingests macro-climate projections, computes local microclimatic
    Urban Heat Island (UHI) adjustments, and calculates Wet Bulb Globe Temperature (WBGT).
    """
    def __init__(self):
        self.name = "Spatial Climate Ingestion Agent"

    def run(self, peak_temp_c: float, relative_humidity_pct: float = 35.0) -> List[Dict[str, Any]]:
        spatial_weather = []
        for z in RAIPUR_ZONES:
            # UHI calculation based on concrete fraction vs green canopy cover
            concrete_density = (1.0 - z["green_cover_pct"])
            uhi_differential = round((concrete_density * 3.5) - (z["green_cover_pct"] * 2.0), 2)
            local_apparent_t = round(peak_temp_c + uhi_differential, 1)

            # Simplified outdoor WBGT estimate (Stull formula proxy)
            tw = peak_temp_c * np.arctan(0.151977 * (relative_humidity_pct + 8.313659)**0.5) + np.arctan(peak_temp_c + relative_humidity_pct) - np.arctan(relative_humidity_pct - 1.676331) + 0.00391838 * (relative_humidity_pct**1.5) * np.arctan(0.023101 * relative_humidity_pct) - 4.686035
            wbgt = round(0.7 * tw + 0.3 * local_apparent_t, 1)

            # Nighttime minimum temperature (if night stays warm, recovery is impaired)
            night_min = round(local_apparent_t - 9.5, 1)
            nighttime_penalty = (night_min >= 31.0)

            spatial_weather.append({
                "zone_id": z["id"],
                "zone_name": z["name"],
                "base_temp_c": peak_temp_c,
                "uhi_differential_c": uhi_differential,
                "effective_apparent_temp_c": local_apparent_t,
                "est_wbgt_c": wbgt,
                "night_min_temp_c": night_min,
                "nighttime_non_recovery": nighttime_penalty,
                "wbgt_risk": "EXTREME" if wbgt >= 32.0 else "HIGH" if wbgt >= 29.0 else "MODERATE"
            })

        return spatial_weather


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT 2: THREAT ASSESSMENT & CASCADE SYNTHESIS AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class ThreatAssessmentAgent:
    """
    Agent 2: Synthesizes spatial weather signals, grid digital twin stress,
    water pumping dependency, and socioeconomic vulnerability.
    Formula (adapted from heatwave-public and GridPulse-AI):
      Threat = 0.45 * Weather + 0.25 * Grid_Stress + 0.15 * Water_Risk + 0.15 * Vulnerability
               + Aggravating_Nighttime_Penalty (+0.10)
    """
    def __init__(self):
        self.name = "Threat Assessment Agent"
        self.grid_twin = GridStressNetwork()
        self.health_engine = TapasHealthEngine()

    def run(self, spatial_weather: List[Dict[str, Any]], city_demand_mw: float) -> List[Dict[str, Any]]:
        # Run digital twin for grid
        avg_temp = np.mean([w["effective_apparent_temp_c"] for w in spatial_weather])
        grid_states = {s["substation_id"]: s for s in self.grid_twin.compute_composite_grid_risk(avg_temp, city_demand_mw)}

        scored_threats = []
        for w in spatial_weather:
            zid = w["zone_id"]
            zone_data = next(z for z in RAIPUR_ZONES if z["id"] == zid)

            # 1. Weather Component (non-linear scaling)
            t_eff = w["effective_apparent_temp_c"]
            weather_comp = min(1.0, max(0.0, (t_eff - 38.0) / 10.0))

            # 2. Grid Stress Component
            sub_id = zone_data["substation"]
            sub_stress = grid_states.get(sub_id, {}).get("composite_risk_score", 0.5)

            # 3. Water Dependency Component
            wp_id = zone_data["water_pump"]
            wp = next((p for p in RAIPUR_WATER_PUMPS if p["id"] == wp_id), None)
            water_risk = 0.7 if (wp and not wp["backup_generator"]) else 0.2

            # 4. Socioeconomic Vulnerability Component
            vuln_comp = (
                0.35 * (zone_data["slum_pct"] / 0.42) +
                0.35 * (zone_data["vulnerable_elderly_pct"] / 0.18) +
                0.30 * (1.0 - zone_data["ac_penetration_pct"])
            )
            vuln_comp = min(1.0, vuln_comp)

            # 5. Nighttime aggravating factor
            night_penalty = 0.10 if w["nighttime_non_recovery"] else 0.0

            # Composite Threat Score [0, 1] with balanced weights to preserve ward differentiation
            raw_threat = (
                0.35 * weather_comp +
                0.25 * sub_stress +
                0.15 * water_risk +
                0.15 * vuln_comp +
                night_penalty * 0.5
            )
            threat_score = round(min(0.95, max(0.15, raw_threat)), 3)

            if threat_score >= 0.75:
                threat_level = "CRITICAL"
            elif threat_score >= 0.55:
                threat_level = "HIGH"
            elif threat_score >= 0.35:
                threat_level = "MEDIUM"
            else:
                threat_level = "LOW"

            scored_threats.append({
                "zone_id": zid,
                "zone_name": zone_data["name"],
                "population": zone_data["population"],
                "apparent_temp_c": t_eff,
                "wbgt_c": w["est_wbgt_c"],
                "substation_id": sub_id,
                "substation_stress": round(sub_stress, 2),
                "water_pump_id": wp_id,
                "threat_score": round(threat_score, 3),
                "threat_level": threat_level,
                "components": {
                    "weather": round(weather_comp, 2),
                    "grid": round(sub_stress, 2),
                    "water": round(water_risk, 2),
                    "vulnerability": round(vuln_comp, 2),
                    "nighttime_penalty": night_penalty
                }
            })

        return scored_threats


# ═══════════════════════════════════════════════════════════════════════════════
# AGENT 3: DISPATCH COMMANDER & AUTONOMOUS OPTIMIZATION AGENT
# ═══════════════════════════════════════════════════════════════════════════════

class DispatchCommanderAgent:
    """
    Agent 3: Reads the synthesized threat map, selects an optimization strategy,
    and formulates a mathematical Mixed-Integer Linear Program (MILP) to assign emergency resources.
    Strategies:
      1. 'optimize_coverage': MILP maximizing protected citizens across all zones.
      2. 'optimize_response_time': Fast greedy dispatch targeted at CRITICAL zones.
      3. 'optimize_staged_reserve': 70% active deployment, 30% strategic emergency reserves.
    """
    def __init__(self):
        self.name = "Autonomous Dispatch Commander"

    def run(
        self,
        scored_threats: List[Dict[str, Any]],
        budget_lakh: float = 80.0,
        strategy: str = "optimize_coverage"
    ) -> Dict[str, Any]:
        critical_count = sum(1 for t in scored_threats if t["threat_level"] == "CRITICAL")
        high_count = sum(1 for t in scored_threats if t["threat_level"] == "HIGH")

        # Auto-recommend strategy if set to auto
        if strategy == "auto":
            if critical_count >= 4:
                strategy = "optimize_coverage"
            elif critical_count in [1, 2, 3]:
                strategy = "optimize_response_time"
            else:
                strategy = "optimize_staged_reserve"

        if strategy == "optimize_coverage":
            dispatch_plan = self._solve_milp_coverage(scored_threats, budget_lakh)
        elif strategy == "optimize_response_time":
            dispatch_plan = self._solve_greedy_response(scored_threats, budget_lakh)
        else:
            dispatch_plan = self._solve_staged_reserve(scored_threats, budget_lakh)

        return {
            "strategy_selected": strategy,
            "budget_lakh": budget_lakh,
            "critical_zones_count": critical_count,
            "high_zones_count": high_count,
            "dispatch_plan": dispatch_plan
        }

    def _solve_milp_coverage(self, threats: List[Dict[str, Any]], budget_lakh: float) -> Dict[str, Any]:
        """
        Formulates and solves integer linear programming problem via HiGHS MILP solver.
        """
        int_types = list(INTERVENTION_OPTIONS.keys())
        costs = np.array([INTERVENTION_OPTIONS[k]["cost_per_unit_lakh"] for k in int_types])
        benefits = np.array([INTERVENTION_OPTIONS[k]["effectiveness_score"] * 15000.0 for k in int_types])

        # Minimize negative benefit (equivalent to maximizing benefit)
        c = -benefits

        # Budget constraint: sum(cost * x) <= budget_lakh
        A = costs.reshape(1, -1)
        b_u = np.array([budget_lakh])
        b_l = np.array([-np.inf])
        constraints = LinearConstraint(A, b_l, b_u)

        # Upper bounds per intervention type
        ub = np.array([
            5,   # Mobile DG sets available in state inventory
            12,  # Cooling centres
            20,  # Water tankers
            5,   # Hospital surge
            20   # Jal Jeevan kiosks
        ])
        bounds = Bounds(0, ub)
        integrality = np.ones(len(int_types))  # Integer decision variables

        res = milp(c=c, constraints=constraints, integrality=integrality, bounds=bounds)

        if res.success:
            sol = np.round(res.x).astype(int)
            allocations = {int_types[i]: int(sol[i]) for i in range(len(int_types))}
            total_cost = float(np.sum(costs * sol))
            protected = int(-res.fun / 1.5)
        else:
            allocations = {k: 0 for k in int_types}
            total_cost = 0.0
            protected = 0

        # Assign assets to priority zones
        sorted_threats = sorted(threats, key=lambda t: t["threat_score"], reverse=True)
        zone_assignments = []
        for i, t in enumerate(sorted_threats):
            assigned = []
            if i < allocations.get("power_resilience", 0):
                assigned.append("1x Mobile DG Set (2.5 MW)")
            if i < allocations.get("cooling_centre", 0):
                assigned.append("1x Public Cooling Centre")
            if i < allocations.get("water_tankers", 0):
                assigned.append("2x Water Tankers Fleet")
            if i < allocations.get("jal_jeevan", 0):
                assigned.append("1x Solar Hydration Kiosk")

            zone_assignments.append({
                "zone_id": t["zone_id"],
                "zone_name": t["zone_name"],
                "threat_level": t["threat_level"],
                "threat_score": t["threat_score"],
                "assigned_interventions": assigned
            })

        return {
            "solver_status": "Optimal_HiGHS",
            "total_cost_lakh": round(total_cost, 1),
            "units_allocated": allocations,
            "zone_assignments": zone_assignments,
            "estimated_citizens_shielded": min(int(sum(t['population'] for t in threats)), protected)
        }

    def _solve_greedy_response(self, threats: List[Dict[str, Any]], budget_lakh: float) -> Dict[str, Any]:
        """Greedy rapid deployment focused exclusively on highest-threat zones."""
        sorted_threats = sorted(threats, key=lambda t: t["threat_score"], reverse=True)
        rem_budget = budget_lakh
        allocations = {k: 0 for k in INTERVENTION_OPTIONS.keys()}
        zone_assignments = []

        for t in sorted_threats:
            assigned = []
            if t["threat_level"] in ["CRITICAL", "HIGH"]:
                if rem_budget >= 18.0 and allocations["power_resilience"] < 4:
                    allocations["power_resilience"] += 1
                    rem_budget -= 18.0
                    assigned.append("1x Mobile DG Set")
                if rem_budget >= 4.5:
                    allocations["cooling_centre"] += 1
                    rem_budget -= 4.5
                    assigned.append("1x Cooling Centre")
                if rem_budget >= 2.4:
                    allocations["water_tankers"] += 2
                    rem_budget -= 2.4
                    assigned.append("2x Water Tankers")

            zone_assignments.append({
                "zone_id": t["zone_id"],
                "zone_name": t["zone_name"],
                "threat_level": t["threat_level"],
                "threat_score": t["threat_score"],
                "assigned_interventions": assigned
            })

        total_cost = budget_lakh - rem_budget
        return {
            "solver_status": "Greedy_Optimal",
            "total_cost_lakh": round(total_cost, 1),
            "units_allocated": allocations,
            "zone_assignments": zone_assignments,
            "estimated_citizens_shielded": int(sum(t["population"] for t in threats if t["threat_level"] == "CRITICAL") * 0.85)
        }

    def _solve_staged_reserve(self, threats: List[Dict[str, Any]], budget_lakh: float) -> Dict[str, Any]:
        """Two-phase split deployment: 70% active deployed, 30% held in mobile reserve."""
        active_budget = budget_lakh * 0.70
        reserve_budget = budget_lakh * 0.30

        plan = self._solve_milp_coverage(threats, active_budget)
        reserve_units = {
            "mobile_dg_standby": int(reserve_budget / 18.0),
            "water_tankers_standby": int((reserve_budget % 18.0) / 1.2)
        }
        plan["reserve_staged"] = reserve_units
        plan["strategy_note"] = "30% resources pre-staged at Telibandha Central Depot for rapid dispatch on substation tripping."
        return plan
