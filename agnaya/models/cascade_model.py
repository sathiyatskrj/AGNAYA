"""
AGNAYA - Mathematical Models Engine
Raipur, Chhattisgarh Heatwave Cascade Simulation

Mathematical components:
  1. Differential equation model: electricity demand dynamics (Saturating ODE)
  2. Network theory: infrastructure dependency graph
  3. Monte Carlo simulation: uncertainty quantification
  4. Optimization: intervention allocation under budget constraint

DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
Not endorsed by IMD, NDMA, CSPDCL, or Raipur Municipal Corporation.
"""

import numpy as np
import networkx as nx
from scipy.integrate import odeint
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.raipur_data import (
    RAIPUR_ZONES, RAIPUR_SUBSTATIONS, RAIPUR_WATER_PUMPS,
    RAIPUR_HOSPITALS, HEAT_DEMAND_PARAMS, CSPDCL_PARAMS,
    INTERVENTION_OPTIONS
)


# ═══════════════════════════════════════════════════════════════════════════════
# 0. COMMON STANDARDIZED EMPIRICAL FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_indoor_temp(
    ambient_temp_c: float,
    slum_pct: float,
    green_cover_pct: float,
    outage_hours: float = 0.0
) -> float:
    """
    Empirical simplified microclimatic indoor temperature estimate.
    Status: ASSUMED / SIMPLIFIED ESTIMATE PENDING IN-SITU VALIDATION.

    Formula:
        T_indoor = T_ambient + Delta T_roof - Delta T_canopy + Delta T_outage
    Where:
        Delta T_roof   = 4.0 * slum_pct (radiative thermal entrapment under CGI tin roofs)
        Delta T_canopy = 4.0 * green_cover_pct (vegetative shade buffering)
        Delta T_outage = min(6.5, 0.8 * outage_hours) (thermal accumulation during mechanical cooling loss)
    """
    roof_trap = 4.0 * slum_pct
    canopy_cooling = 4.0 * green_cover_pct
    outage_accumulation = min(6.5, 0.8 * max(0.0, outage_hours)) if outage_hours > 0 else 0.0
    return round(float(ambient_temp_c + roof_trap - canopy_cooling + outage_accumulation), 1)


def classify_risk_band(score_0_to_1: float) -> str:
    """
    Standardized NDMA 4-tier alert classification for simulation:
    - LOW (GREEN): score < 0.45
    - MODERATE (YELLOW): 0.45 <= score < 0.60
    - HIGH (ORANGE): 0.60 <= score < 0.75
    - SEVERE (RED): score >= 0.75
    """
    if score_0_to_1 >= 0.75:
        return "SEVERE"
    if score_0_to_1 >= 0.60:
        return "HIGH"
    if score_0_to_1 >= 0.45:
        return "MODERATE"
    return "LOW"


# ═══════════════════════════════════════════════════════════════════════════════
# 1. DIFFERENTIAL EQUATIONS — Electricity Demand Model (Saturating ODE)
# ═══════════════════════════════════════════════════════════════════════════════

class DemandModel:
    """
    Models electricity demand evolution during an urban heatwave.

    Governing saturating differential equation:
        dD/dt = alpha * mult * max(0, T(t) - T_set) * (D_cap - D(t)) - gamma * (D(t) - D_base)

    Where:
        D(t)   = electricity demand (MW) at time t
        T(t)   = ambient dry-bulb temperature (°C) at time t
        T_set  = cooling activation threshold (27.0°C)
        D_base = baseline normal daytime demand (310.0 MW)
        D_cap  = emergency transmission thermal ceiling (620.0 MW)
        alpha  = cooling sensitivity growth rate (0.0048 h^-1 °C^-1)
        gamma  = demand relaxation rate towards baseload (0.08 h^-1)
        mult   = latent/sensible humidity multiplier (1.12)

    Physical Invariants:
        1. D(t) is strictly bounded in [D_base, D_cap] = [310 MW, 620 MW] for all t.
        2. Contracted summer peak limit = 420.0 MW (CSPDCL tariff threshold).
        3. Shortfall = max(0, D(t) - 420.0 MW), indicating unserved load / rolling outage pressure.
    """
    def __init__(self, D0_mw=None):
        p = HEAT_DEMAND_PARAMS
        self.T0 = p["base_temp_celsius"]
        self.alpha = p["alpha"]
        self.gamma = p.get("gamma", 0.08)
        self.beta = self.gamma  # Alias for backward compatibility
        self.D_cap = p.get("demand_cap_mw", CSPDCL_PARAMS["raipur_emergency_cap_mw"])
        self.statutory_limit_mw = CSPDCL_PARAMS["raipur_peak_demand_mw"]  # 420 MW
        self.humidity_mult = p["humidity_multiplier"]
        self.D0 = D0_mw or CSPDCL_PARAMS["raipur_normal_demand_mw"]

    def temperature_profile(self, t_hours, T_peak, T_night=None):
        """Sinusoidal daily temperature profile with peak at 15:00."""
        if T_night is None:
            T_night = T_peak - 10.0
        T_daily = (T_peak + T_night) / 2.0 + (T_peak - T_night) / 2.0 * np.sin(
            2.0 * np.pi * (t_hours % 24.0 - 9.0) / 24.0
        )
        return T_daily

    def _ode(self, D, t, T_peak, humidity=True):
        T = self.temperature_profile(t, T_peak)
        mult = self.humidity_mult if humidity else 1.0
        cooling_drive = self.alpha * mult * max(0.0, T - self.T0) * (self.D_cap - D)
        relaxation = self.gamma * (D - self.D0)
        return cooling_drive - relaxation

    def simulate(self, T_peak_celsius, duration_days=4, dt_hours=1.0):
        """
        Run the demand ODE for given heatwave scenario.

        Returns:
            t_hours: time array
            D_mw: demand array (MW) bounded within [D0, D_cap]
        """
        t_hours = np.arange(0, duration_days * 24, dt_hours)
        D_init = self.D0
        D_mw = odeint(self._ode, D_init, t_hours, args=(T_peak_celsius,))
        return t_hours, D_mw.flatten()

    def transformer_capacity_at_temp(self, substation, ambient_temp):
        """
        Apply thermal derating to transformer capacity.
        Above 40°C each °C reduces capacity by derating factor.
        """
        derating = HEAT_DEMAND_PARAMS["transformer_derating_pct_per_degC"]
        excess_temp = max(0, ambient_temp - 40.0)
        capacity = substation["capacity_mva"] * (1 - derating / 100 * excess_temp)
        return max(0, capacity)


# ═══════════════════════════════════════════════════════════════════════════════
# 2. NETWORK THEORY — Infrastructure Dependency Graph
# ═══════════════════════════════════════════════════════════════════════════════

class InfrastructureNetwork:
    """
    Builds a directed dependency graph of Raipur's critical infrastructure.

    Nodes: substations, water pumps, hospitals, cooling centres, zones
    Edges: dependency relationships with weights
    """
    def __init__(self):
        self.G = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        G = self.G
        # Add substation nodes
        for s in RAIPUR_SUBSTATIONS:
            G.add_node(s["id"], type="substation", data=s,
                       capacity=s["capacity_mva"],
                       load_factor=s["load_factor_normal"],
                       age=s["age_years"])

        # Add water pump nodes
        for wp in RAIPUR_WATER_PUMPS:
            G.add_node(wp["id"], type="water_pump", data=wp,
                       capacity=wp["capacity_MLD"])
            # Water pumps depend on electricity substations
            G.add_edge(wp["electricity_dependency"], wp["id"],
                       dependency_type="electricity", weight=1.0,
                       critical=not wp["backup_generator"])

        # Add hospital nodes
        for h in RAIPUR_HOSPITALS:
            G.add_node(h["id"], type="hospital", data=h,
                       beds=h["total_beds"], backup_hours=h["backup_hours"])

        # Add zone nodes
        for z in RAIPUR_ZONES:
            G.add_node(z["id"], type="zone", data=z,
                       population=z["population"],
                       vulnerability=self._zone_vulnerability(z))
            # Zones depend on their primary substation
            G.add_edge(z["substation"], z["id"],
                       dependency_type="electricity", weight=1.0, critical=True)
            # Zones depend on their water pump
            G.add_edge(z["water_pump"], z["id"],
                       dependency_type="water", weight=0.8, critical=True)

        # Hospitals depend on zone electricity (via substations)
        for h in RAIPUR_HOSPITALS:
            for zid in h["serves_zones"]:
                z = next(x for x in RAIPUR_ZONES if x["id"] == zid)
                G.add_edge(z["substation"], h["id"],
                           dependency_type="electricity", weight=1.0,
                           critical=(h["backup_hours"] < 6))

    @staticmethod
    def _zone_vulnerability(z):
        """Composite vulnerability index [0, 1]."""
        v = (
            0.30 * min(1.0, z["vulnerable_elderly_pct"] / 0.18) +
            0.25 * min(1.0, z["slum_pct"] / 0.42) +
            0.15 * max(0.0, 1.0 - z["green_cover_pct"] / 0.25) +
            0.15 * max(0.0, 1.0 - z["ac_penetration_pct"]) +
            0.15 * min(1.0, z["avg_building_age_yr"] / 40.0)
        )
        return min(1.0, max(0.0, v))

    def apply_substation_failure(self, failed_substation_id):
        """
        Propagate failure from a substation through the dependency graph.
        Returns dict of affected nodes and their operational status.
        """
        affected = {}
        descendants = nx.descendants(self.G, failed_substation_id)
        for node in descendants:
            node_data = self.G.nodes[node]
            node_type = node_data.get("type", "unknown")
            if node_type == "water_pump":
                has_backup = node_data["data"].get("backup_generator", False)
                affected[node] = {"operational": has_backup, "type": node_type}
            elif node_type == "hospital":
                backup_hrs = node_data.get("backup_hours", 0)
                affected[node] = {
                    "operational": True,
                    "backup_hours_remaining": backup_hrs,
                    "type": node_type,
                }
            else:
                affected[node] = {"operational": False, "type": node_type}
        return affected

    def critical_nodes(self):
        """Identify nodes whose failure affects the most people."""
        centrality = nx.betweenness_centrality(self.G, weight="weight")
        pop_impact = {}
        for node, c in centrality.items():
            ntype = self.G.nodes[node].get("type")
            if ntype == "substation":
                affected_pop = sum(
                    self.G.nodes[n].get("population", 0)
                    for n in nx.descendants(self.G, node)
                    if self.G.nodes[n].get("type") == "zone"
                )
                pop_impact[node] = {
                    "centrality": c,
                    "affected_population": affected_pop,
                    "name": self.G.nodes[node]["data"]["name"],
                }
        return dict(sorted(pop_impact.items(),
                            key=lambda x: x[1]["affected_population"],
                            reverse=True))


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MONTE CARLO SIMULATION
# ═══════════════════════════════════════════════════════════════════════════════

class MonteCarloCascade:
    """
    Runs N_SIM heatwave scenarios with stochastic failures.

    For each simulation:
      - Sample transformer failure probability based on load factor + age + temp
      - Cascade to water, cooling, hospital services
      - Estimate population exposure to heat-infrastructure stress
    """
    def __init__(self, N_sim=1000, seed=42):
        self.N_sim = N_sim
        self.rng = np.random.default_rng(seed)
        self.demand_model = DemandModel()
        self.network = InfrastructureNetwork()

    def _transformer_fail_prob(self, substation, load_fraction, temp_celsius):
        """
        Empirical failure probability formula.
        Based on IEEE transformer aging models adapted for Indian conditions.
        """
        base_rate = 0.02  # 2% base hourly risk during extreme heat
        age_factor = 1.0 + (substation["age_years"] - 15.0) * 0.03
        load_factor = np.exp(max(0.0, load_fraction - 0.85) * 5.0)
        temp_factor = np.exp(max(0.0, temp_celsius - 42.0) * 0.15)
        has_backup = 0.5 if not substation["backup_transformer"] else 1.0
        prob = min(0.95, base_rate * age_factor * load_factor * temp_factor * has_backup)
        return float(prob)

    def _zone_health_risk(self, zone, indoor_temp, power_available, water_available):
        """
        Heuristic Heat-Risk Index [0, 1] per zone.
        Synthesizes vulnerability, thermal stress, and lifeline disruption.
        Status: SIMULATION HEURISTIC - NOT CLINICALLY VALIDATED.
        """
        v = self.network.G.nodes[zone["id"]]["vulnerability"]
        heat_index_risk = min(1.0, max(0.0, (indoor_temp - 36.0) / 14.0))
        power_penalty = 0.20 if not power_available else 0.0
        water_penalty = 0.20 if not water_available else 0.0
        risk = 0.40 * v + 0.40 * heat_index_risk + power_penalty + water_penalty
        return min(1.0, max(0.0, risk))

    def run(self, T_peak, duration_days, interventions=None):
        """
        Run Monte Carlo simulation.

        Args:
            T_peak: peak temperature (°C)
            duration_days: heatwave duration
            interventions: dict of activated interventions {type: units}

        Returns:
            dict with statistical summaries
        """
        if interventions is None:
            interventions = {}

        # Simulate demand trajectory
        t_h, D_mw = self.demand_model.simulate(T_peak, duration_days)
        peak_demand = float(np.max(D_mw))
        cap = CSPDCL_PARAMS["raipur_peak_demand_mw"]  # 420 MW contracted statutory summer limit

        # Power resilience intervention boosts capacity
        if "power_resilience" in interventions:
            cap += interventions["power_resilience"] * INTERVENTION_OPTIONS["power_resilience"]["capacity_mw_per_unit"]
        demand_shortfall_mw = max(0.0, peak_demand - cap)

        results = {
            "power_fail_by_substation": {s["id"]: [] for s in RAIPUR_SUBSTATIONS},
            "water_disruption_zone": {z["id"]: [] for z in RAIPUR_ZONES},
            "health_risk_zone": {z["id"]: [] for z in RAIPUR_ZONES},
            "hospital_overload": {h["id"]: [] for h in RAIPUR_HOSPITALS},
            "population_at_high_risk": [],
            "wards_severed": [],
        }

        for _ in range(self.N_sim):
            sim_pop_risk = 0
            sim_wards_severed = 0

            # Track which substations fail this simulation
            sub_failed = {}
            for s in RAIPUR_SUBSTATIONS:
                _ = self.demand_model.transformer_capacity_at_temp(s, T_peak)
                load_frac = s["load_factor_normal"] * (peak_demand / CSPDCL_PARAMS["raipur_normal_demand_mw"])
                load_frac = min(1.2, load_frac)
                p_fail = self._transformer_fail_prob(s, load_frac, T_peak)
                failed = self.rng.random() < p_fail
                sub_failed[s["id"]] = failed
                results["power_fail_by_substation"][s["id"]].append(int(failed))

            # For each zone assess cascading effects
            for z in RAIPUR_ZONES:
                power_ok = not sub_failed.get(z["substation"], False)
                if "power_resilience" in interventions and not power_ok:
                    power_ok = self.rng.random() < 0.7  # 70% restoration chance

                if not power_ok:
                    sim_wards_severed += 1

                # Water availability
                wp = next(w for w in RAIPUR_WATER_PUMPS if w["id"] == z["water_pump"])
                sub_for_water = wp["electricity_dependency"]
                water_sub_ok = not sub_failed.get(sub_for_water, False)
                water_ok = water_sub_ok or wp["backup_generator"]
                if "water_tankers" in interventions and not water_ok:
                    water_ok = True

                # Estimate indoor temperature using unified formula
                outage_h = 3.0 if not power_ok else 0.0
                indoor_temp = calculate_indoor_temp(
                    ambient_temp_c=T_peak - self.rng.uniform(0.0, 1.5),
                    slum_pct=z["slum_pct"],
                    green_cover_pct=z["green_cover_pct"],
                    outage_hours=outage_h
                )

                # Cooling centre coverage
                cc_effective = False
                if "cooling_centre" in interventions:
                    units = interventions["cooling_centre"]
                    coverage_prob = min(1.0, units * 200.0 / (z["population"] * 0.05))
                    cc_effective = self.rng.random() < coverage_prob

                if cc_effective:
                    indoor_temp -= 2.5

                risk = self._zone_health_risk(z, indoor_temp, power_ok, water_ok)
                results["health_risk_zone"][z["id"]].append(risk)

                water_disruption = int(not water_ok)
                results["water_disruption_zone"][z["id"]].append(water_disruption)

                if risk > 0.60:
                    sim_pop_risk += z["population"] * risk

            results["wards_severed"].append(sim_wards_severed)

            # Hospital demand surge
            for h in RAIPUR_HOSPITALS:
                served_pop = sum(
                    z["population"]
                    for z in RAIPUR_ZONES if z["id"] in h["serves_zones"]
                )
                expected_er = served_pop * 0.001 * max(0.0, (T_peak - 40.0) / 5.0)
                actual_er = self.rng.poisson(max(0.0, expected_er))
                surge_cap = h["emergency_capacity"]
                if "hospital_surge" in interventions:
                    surge_cap += interventions["hospital_surge"] * INTERVENTION_OPTIONS["hospital_surge"]["beds_per_unit"]
                overloaded = int(actual_er > surge_cap)
                results["hospital_overload"][h["id"]].append(overloaded)

            results["population_at_high_risk"].append(sim_pop_risk)

        # Summarize results
        summary = {
            "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
            "T_peak": T_peak,
            "duration_days": duration_days,
            "baseline_demand_mw": CSPDCL_PARAMS["raipur_normal_demand_mw"],
            "statutory_limit_mw": CSPDCL_PARAMS["raipur_peak_demand_mw"],
            "emergency_ceiling_mw": CSPDCL_PARAMS["raipur_emergency_cap_mw"],
            "peak_demand_mw": round(peak_demand, 1),
            "demand_shortfall_mw": round(demand_shortfall_mw, 1),
            "interventions": interventions,
            "substation_failure_prob": {
                sid: float(np.mean(vals))
                for sid, vals in results["power_fail_by_substation"].items()
            },
            "water_disruption_prob": {
                zid: float(np.mean(vals))
                for zid, vals in results["water_disruption_zone"].items()
            },
            "zone_health_risk": {
                zid: {
                    "mean": float(np.mean(vals)),
                    "p10": float(np.percentile(vals, 10)),
                    "p90": float(np.percentile(vals, 90)),
                    "risk_band": classify_risk_band(float(np.mean(vals)))
                }
                for zid, vals in results["health_risk_zone"].items()
            },
            "hospital_overload_prob": {
                hid: float(np.mean(vals))
                for hid, vals in results["hospital_overload"].items()
            },
            "population_at_high_risk": {
                "mean": float(np.mean(results["population_at_high_risk"])),
                "p10": float(np.percentile(results["population_at_high_risk"], 10)),
                "p50": float(np.percentile(results["population_at_high_risk"], 50)),
                "p90": float(np.percentile(results["population_at_high_risk"], 90)),
            },
            "raw_population_at_high_risk": [float(v) for v in results["population_at_high_risk"]],
            "failure_rate_percent": float(round(np.mean([1 if any(results["power_fail_by_substation"][s][i] for s in results["power_fail_by_substation"]) else 0 for i in range(self.N_sim)]) * 100.0, 1)),
            "system_failure_rate_percent": float(round(np.mean([1 if any(results["power_fail_by_substation"][s][i] for s in results["power_fail_by_substation"]) else 0 for i in range(self.N_sim)]) * 100.0, 1)),
            "mean_wards_severed": float(round(np.mean(results["wards_severed"]), 1)),
            "p50_wards_severed": float(round(np.percentile(results["wards_severed"], 50), 1)),
            "p90_wards_severed": float(round(np.percentile(results["wards_severed"], 90), 1)),
            "raw_wards_severed": [int(v) for v in results["wards_severed"]],
        }
        return summary

    def simulate(self, T_peak=44.5, duration_days=5, fail_sub=False, interventions=None):
        """Convenience alias for run()."""
        return self.run(T_peak=T_peak, duration_days=duration_days, interventions=interventions)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. OPTIMIZATION — Budget-Constrained Intervention Selection
# ═══════════════════════════════════════════════════════════════════════════════

class InterventionOptimizer:
    """
    Solves the constrained optimization problem:
        min_x  E[L(x)]   subject to  Cost(x) <= B
    Where x is a vector of integer intervention counts.
    """
    def __init__(self, budget_lakh=50.0, N_sim=150):
        self.budget = budget_lakh
        self.mc = MonteCarloCascade(N_sim=N_sim)

    def _compute_baseline_risk(self, T_peak, duration_days):
        summary = self.mc.run(T_peak, duration_days, interventions={})
        return summary["population_at_high_risk"]["mean"]

    def _evaluate_combination(self, T_peak, duration_days, combo):
        summary = self.mc.run(T_peak, duration_days, interventions=combo)
        cost = sum(
            INTERVENTION_OPTIONS[k]["cost_per_unit_lakh"] * v
            for k, v in combo.items()
        )
        return summary["population_at_high_risk"]["mean"], cost, summary

    def optimize(self, T_peak, duration_days):
        """
        Enumerate candidate intervention combinations and find best under budget.
        Returns list of Pareto-efficient solutions.
        """
        baseline_risk = self._compute_baseline_risk(T_peak, duration_days)
        candidates = []

        # Single-type interventions
        for itype, iopts in INTERVENTION_OPTIONS.items():
            max_units = int(self.budget / iopts["cost_per_unit_lakh"])
            for units in [1, 2, 3, min(5, max_units)]:
                if iopts["cost_per_unit_lakh"] * units > self.budget:
                    continue
                combo = {itype: units}
                risk, cost, summary = self._evaluate_combination(T_peak, duration_days, combo)
                candidates.append({
                    "interventions": combo,
                    "cost_lakh": cost,
                    "risk_population": risk,
                    "risk_reduction_pct": 100.0 * (baseline_risk - risk) / max(baseline_risk, 1.0),
                    "summary": summary,
                })

        # Multi-type combinations (top priority combinations)
        priority_combos = [
            {"power_resilience": 1, "cooling_centre": 2},
            {"power_resilience": 2, "water_tankers": 3},
            {"cooling_centre": 3, "water_tankers": 2, "jal_jeevan": 2},
            {"power_resilience": 1, "cooling_centre": 2, "hospital_surge": 1},
            {"water_tankers": 5, "cooling_centre": 3, "jal_jeevan": 4},
        ]
        for combo in priority_combos:
            cost = sum(INTERVENTION_OPTIONS[k]["cost_per_unit_lakh"] * v
                       for k, v in combo.items())
            if cost > self.budget:
                continue
            risk, cost, summary = self._evaluate_combination(T_peak, duration_days, combo)
            candidates.append({
                "interventions": combo,
                "cost_lakh": cost,
                "risk_population": risk,
                "risk_reduction_pct": 100.0 * (baseline_risk - risk) / max(baseline_risk, 1.0),
                "summary": summary,
            })

        # Sort by risk reduction (descending)
        candidates.sort(key=lambda x: x["risk_reduction_pct"], reverse=True)
        return {"baseline_risk": baseline_risk, "candidates": candidates}


# ═══════════════════════════════════════════════════════════════════════════════
# 5. HEAT HEALTH INDEX — Zone-level composite indicator
# ═══════════════════════════════════════════════════════════════════════════════

def compute_zone_risk_table(T_peak, interventions=None):
    """Compute a summary risk table for all zones at given temperature."""
    if interventions is None:
        interventions = {}
    net = InfrastructureNetwork()
    mc = MonteCarloCascade(N_sim=500)
    summary = mc.run(T_peak, duration_days=4, interventions=interventions)

    rows = []
    for z in RAIPUR_ZONES:
        zid = z["id"]
        sub_fail_p = summary["substation_failure_prob"].get(z["substation"], 0)
        water_fail_p = summary["water_disruption_prob"].get(zid, 0)
        health_risk = summary["zone_health_risk"].get(zid, {}).get("mean", 0)
        vuln = net.G.nodes[zid]["vulnerability"]

        rows.append({
            "Zone ID": zid,
            "Zone Name": z["name"],
            "Population": z["population"],
            "Vulnerability Index": round(vuln, 3),
            "Power Failure Prob (%)": round(sub_fail_p * 100.0, 1),
            "Water Disruption Prob (%)": round(water_fail_p * 100.0, 1),
            "Health Risk Score": round(health_risk, 3),
            "Risk Band": classify_risk_band(health_risk),
            "Slum Population (%)": round(z["slum_pct"] * 100.0, 1),
            "AC Penetration (%)": round(z["ac_penetration_pct"] * 100.0, 1),
            "Elderly (%)": round(z["vulnerable_elderly_pct"] * 100.0, 1),
        })
    return rows, summary
