"""
AGNAYA - Deterministic Multi-Stage Dispatch Pipeline
Formerly designated '3-Agent AI Pipeline' - clarifies deterministic optimization architecture:
  Stage 1: Spatial Microclimate Ingestion (UHI & WBGT calculation)
  Stage 2: Threat Assessment & Cascade Synthesis (Grid + Water + Demographic vulnerability)
  Stage 3: Resource Dispatch Commander (SciPy HiGHS Mixed-Integer Linear Programming)

DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
Deterministic mathematical optimization for civic planning and disaster response simulation.
"""

import numpy as np
from typing import Dict, List, Any
from scipy.optimize import milp, LinearConstraint, Bounds
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.raipur_data import (
    RAIPUR_ZONES, RAIPUR_WATER_PUMPS,
    INTERVENTION_OPTIONS
)
from models.grid_digital_twin import GridStressNetwork
from models.tapas_health import TapasHealthEngine


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: SPATIAL & CLIMATE INGESTION
# ═══════════════════════════════════════════════════════════════════════════════

class SpatialClimateStage:
    """
    Stage 1: Ingests macro-climate projections, computes local microclimatic
    Urban Heat Island (UHI) adjustments, and calculates Wet Bulb Globe Temperature (WBGT).
    """
    def __init__(self):
        self.name = "Spatial Climate Ingestion Stage"

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

            # Nighttime minimum temperature
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


# Backward compatibility alias
SpatialClimateAgent = SpatialClimateStage


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: THREAT ASSESSMENT & CASCADE SYNTHESIS
# ═══════════════════════════════════════════════════════════════════════════════

class ThreatAssessmentStage:
    """
    Stage 2: Synthesizes spatial weather signals, grid digital twin stress,
    water pumping dependency, and socioeconomic vulnerability.
    """
    def __init__(self):
        self.name = "Threat Assessment Stage"
        self.grid_twin = GridStressNetwork()
        self.health_engine = TapasHealthEngine()

    def run(self, spatial_weather: List[Dict[str, Any]], city_demand_mw: float) -> List[Dict[str, Any]]:
        avg_temp = np.mean([w["effective_apparent_temp_c"] for w in spatial_weather])
        grid_states = {s["substation_id"]: s for s in self.grid_twin.compute_composite_grid_risk(avg_temp, city_demand_mw)}

        scored_threats = []
        for w in spatial_weather:
            zid = w["zone_id"]
            zone_data = next(z for z in RAIPUR_ZONES if z["id"] == zid)

            # 1. Weather Component
            t_eff = w["effective_apparent_temp_c"]
            weather_comp = min(1.0, max(0.0, (t_eff - 38.0) / 10.0))

            # 2. Grid Stress Component
            sub_id = zone_data["substation"]
            sub_stress = grid_states.get(sub_id, {}).get("composite_risk_score", 0.5)

            # 3. Water Dependency Component
            pump_id = zone_data["water_pump"]
            pump_data = next((p for p in RAIPUR_WATER_PUMPS if p["id"] == pump_id), None)
            water_risk = 0.8 if (pump_data and not pump_data["backup_generator"]) else 0.3

            # 4. Socioeconomic Vulnerability Component
            slum_factor = zone_data["slum_pct"]
            elderly_factor = zone_data["vulnerable_elderly_pct"] / 0.18
            ac_lack = 1.0 - zone_data["ac_penetration_pct"]
            socio_vuln = min(1.0, 0.40 * slum_factor + 0.35 * elderly_factor + 0.25 * ac_lack)

            # Composite Threat Calculation
            threat = (
                0.40 * weather_comp +
                0.25 * sub_stress +
                0.15 * water_risk +
                0.20 * socio_vuln
            )
            if w["nighttime_non_recovery"]:
                threat = min(1.0, threat + 0.08)

            threat_score = round(threat * 100.0, 1)

            if threat_score >= 70.0:
                tier = "CRITICAL"
                rec_action = "Deploy Emergency Mobile DG Sets & Water Tankers Immediate Priority"
            elif threat_score >= 55.0:
                tier = "HIGH"
                rec_action = "Activate Cooling Shelter & Door-to-Door ORS Distribution"
            elif threat_score >= 40.0:
                tier = "MODERATE"
                rec_action = "Monitor Substation Load & Issue Ward Hydration Advisory"
            else:
                tier = "LOW"
                rec_action = "Standard Summer Precautions"

            scored_threats.append({
                "zone_id": zid,
                "zone_name": zone_data["name"],
                "population": zone_data["population"],
                "substation": sub_id,
                "threat_score": threat_score,
                "threat_level": tier,
                "weather_stress": round(weather_comp, 2),
                "grid_stress": round(sub_stress, 2),
                "water_risk": round(water_risk, 2),
                "vulnerability": round(socio_vuln, 2),
                "primary_action": rec_action
            })

        return sorted(scored_threats, key=lambda x: x["threat_score"], reverse=True)


# Backward compatibility alias
ThreatAssessmentAgent = ThreatAssessmentStage


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3: RESOURCE DISPATCH COMMANDER (HiGHS MILP OPTIMIZATION)
# ═══════════════════════════════════════════════════════════════════════════════

class ResourceDispatchStage:
    """
    Stage 3: Autonomous Resource Dispatch Commander.
    Solves a Mixed-Integer Linear Program (MILP) to allocate limited municipal
    intervention assets under budget and inventory constraints.
    """
    def __init__(self):
        self.name = "Resource Dispatch Stage (HiGHS MILP)"

    def run(self, threats: List[Dict[str, Any]], budget_lakh: float = 50.0, strategy: str = "optimize_coverage") -> Dict[str, Any]:
        critical_count = sum(1 for t in threats if t["threat_level"] == "CRITICAL")
        high_count = sum(1 for t in threats if t["threat_level"] == "HIGH")

        if strategy == "optimize_coverage":
            dispatch_plan = self._solve_milp_coverage(threats, budget_lakh)
        elif strategy == "greedy_high_risk":
            dispatch_plan = self._solve_greedy_response(threats, budget_lakh)
        else:
            dispatch_plan = self._solve_staged_reserve(threats, budget_lakh)

        return {
            "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
            "strategy_selected": strategy,
            "budget_lakh": budget_lakh,
            "critical_zones_count": critical_count,
            "high_zones_count": high_count,
            "dispatch_plan": dispatch_plan
        }

    def _solve_milp_coverage(self, threats: List[Dict[str, Any]], budget_lakh: float) -> Dict[str, Any]:
        int_types = list(INTERVENTION_OPTIONS.keys())
        costs = np.array([INTERVENTION_OPTIONS[k]["cost_per_unit_lakh"] for k in int_types])
        benefits = np.array([INTERVENTION_OPTIONS[k]["effectiveness_score"] * 15000.0 for k in int_types])

        c = -benefits
        A = costs.reshape(1, -1)
        b_u = np.array([budget_lakh])
        b_l = np.array([-np.inf])
        constraints = LinearConstraint(A, b_l, b_u)

        ub = np.array([
            5,   # Mobile DG sets available
            12,  # Cooling centres
            20,  # Water tankers
            5,   # Hospital surge
            20   # Jal Jeevan kiosks
        ])
        bounds = Bounds(0, ub)
        integrality = np.ones(len(int_types))

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

        sorted_threats = sorted(threats, key=lambda t: t["threat_score"], reverse=True)
        zone_assignments = []
        for i, t in enumerate(sorted_threats):
            assigned = []
            if i < allocations.get("power_resilience", 0):
                assigned.append("1x Mobile DG Set (2 MW)")
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
        sorted_threats = sorted(threats, key=lambda t: t["threat_score"], reverse=True)
        rem_budget = budget_lakh
        allocations = {k: 0 for k in INTERVENTION_OPTIONS.keys()}
        zone_assignments = []

        for t in sorted_threats:
            assigned = []
            if t["threat_level"] in ["CRITICAL", "HIGH"]:
                if rem_budget >= 8.0 and allocations["power_resilience"] < 4:
                    allocations["power_resilience"] += 1
                    rem_budget -= 8.0
                    assigned.append("1x Mobile DG Set")
                if rem_budget >= 2.5:
                    allocations["cooling_centre"] += 1
                    rem_budget -= 2.5
                    assigned.append("1x Cooling Centre")
                if rem_budget >= 1.6:
                    allocations["water_tankers"] += 2
                    rem_budget -= 1.6
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
        active_budget = budget_lakh * 0.70
        reserve_budget = budget_lakh * 0.30

        plan = self._solve_milp_coverage(threats, active_budget)
        reserve_units = {
            "mobile_dg_standby": int(reserve_budget / 8.0),
            "water_tankers_standby": int((reserve_budget % 8.0) / 0.8)
        }
        plan["reserve_staged"] = reserve_units
        plan["strategy_note"] = "30% resources pre-staged at Telibandha Central Depot for rapid dispatch on substation tripping."
        return plan


# Backward compatibility alias
DispatchCommanderAgent = ResourceDispatchStage


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class DeterministicDispatchPipeline:
    """
    Coordinates the 3-stage deterministic optimization pipeline:
    Stage 1: Spatial Climate Ingestion
    Stage 2: Threat Assessment & Cascade Synthesis
    Stage 3: Resource Dispatch Commander (MILP)
    """
    def __init__(self):
        self.stage1 = SpatialClimateStage()
        self.stage2 = ThreatAssessmentStage()
        self.stage3 = ResourceDispatchStage()

    def run_pipeline(
        self,
        ambient_temp_c: float,
        city_demand_mw: float,
        budget_lakh: float = 50.0,
        strategy: str = "optimize_coverage"
    ) -> Dict[str, Any]:
        weather = self.stage1.run(ambient_temp_c)
        threats = self.stage2.run(weather, city_demand_mw)
        dispatch = self.stage3.run(threats, budget_lakh, strategy)

        return {
            "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
            "ambient_temp_c": ambient_temp_c,
            "city_demand_mw": city_demand_mw,
            "weather_signals": weather,
            "threat_assessment": threats,
            "dispatch_solution": dispatch
        }


# Backward compatibility alias
AgentsPipeline = DeterministicDispatchPipeline
