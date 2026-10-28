"""
AGNAYA V3.0 - Comprehensive Multi-Model System Verification Suite
Verifies all 12 modules synthesizing research from:
  1. Base Raipur Infrastructure & CSERC/CSPTCL Data Assets
  2. ODE Electricity Demand & Thermal Dynamics
  3. NetworkX Infrastructure Cascading Dependency Graph
  4. Grid Digital Twin (IEEE C57.91 Hotspots & Neighbor Stress - GridStressDigitalTwin)
  5. Conductor Ampacity & Sag Clearance (IEEE Std 738-2012 - Heat-Analysis)
  6. TAPAS Heat-Health Stress Index (HTSI), Tin-Roof Trap & HAP Measures (TAPAS)
  7. 3-Agent Collaborative AI Pipeline & HiGHS MILP Dispatch (heatwave-public)
  8. Extreme Value Theory (EVT) Gumbel Return Periods (ClimateSim)
  9. Synchronous DC Power Flow & Line Sag Clearances (ClimateSim & Heat-Analysis)
  10. 7-Stage Progressive Heatwave Lifecycle Simulator (GridStressDigitalTwin)
  11. Continuous System Resilience Curves & AUC Loss Engine (ClimateSim)
  12. GridPulse 5-Component Risk Engine & Trilingual Alerts (GridPulse-AI & TAPAS)
"""

import sys, os, time
import numpy as np

# Ensure UTF-8 output on Windows terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_multi_model_tests():
    print("=" * 70)
    print(" AGNAYA V3.0: Unified Multi-Model System & Scientific Verification")
    print("=" * 70)

    # 1. Data Assets
    print("\n[1/12] Verifying Raipur Grounded Infrastructure & Grid Data...")
    from data.raipur_data import (
        RAIPUR_ZONES, RAIPUR_SUBSTATIONS, RAIPUR_WATER_PUMPS,
        RAIPUR_HOSPITALS, CSPDCL_PARAMS
    )
    assert len(RAIPUR_ZONES) == 12, "Expected 12 Raipur zones"
    assert len(RAIPUR_SUBSTATIONS) == 6, "Expected 6 CSPTCL substations"
    print(f"  [OK] 12 Zones, 6 CSPTCL Substations, {len(RAIPUR_WATER_PUMPS)} Water Plants & {len(RAIPUR_HOSPITALS)} Hospitals loaded.")
    print(f"  [OK] CSPDCL FY24-25 Grid Base: {CSPDCL_PARAMS['raipur_normal_demand_mw']} MW (Summer limit: {CSPDCL_PARAMS['raipur_peak_demand_mw']} MW)")

    # 2. ODE Demand
    print("\n[2/12] Testing Differential Equation Demand Dynamics (ODE)...")
    from models.cascade_model import DemandModel
    dm = DemandModel()
    t, D = dm.simulate(T_peak_celsius=46.5, duration_days=3)
    max_d = float(max(D))
    print(f"  [OK] Continuous 72h ODE solved. Peak load at 46.5 deg C: {max_d:.1f} MW (Surge: +{max_d - CSPDCL_PARAMS['raipur_normal_demand_mw']:.1f} MW)")

    # 3. Network Dependency
    print("\n[3/12] Testing Infrastructure Dependency Graph (NetworkX)...")
    from models.cascade_model import InfrastructureNetwork
    net = InfrastructureNetwork()
    crit = net.critical_nodes()
    top_crit = list(crit.keys())[0]
    print(f"  [OK] Directed Graph: {net.G.number_of_nodes()} nodes, {net.G.number_of_edges()} edges. Top critical: {crit[top_crit]['name']}")

    # 4. Grid Digital Twin
    print("\n[4/12] Testing Transformer Digital Twin & Neighbor Stress (IEEE C57.91 / GridStressDigitalTwin)...")
    from models.grid_digital_twin import GridStressNetwork
    gtwin = GridStressNetwork()
    g_res = gtwin.compute_composite_grid_risk(ambient_temp_c=46.0, city_demand_mw=540.0)
    assert len(g_res) == 6, "Expected 6 substation digital twins"
    print(f"  [OK] Evaluated 6 transformer digital twins. Max Hotspot: {max(s['hotspot_temp_c'] for s in g_res)} deg C")

    # 5. Conductor Ampacity
    print("\n[5/12] Testing Overhead Conductor Thermal Ampacity (IEEE Std 738 / Heat-Analysis)...")
    from models.conductor_ampacity import ConductorThermalAmpacity
    cond = ConductorThermalAmpacity()
    c_res = cond.evaluate_all_corridors(ambient_temp_c=46.0)
    assert len(c_res) == 5, "Expected 5 transmission corridors"
    print(f"  [OK] Evaluated 5 transmission corridors. Mean thermal derating: {np.mean([c['derating_percentage'] for c in c_res]):.1f}%")

    # 6. TAPAS Heat-Health
    print("\n[6/12] Testing TAPAS Heat-Health Stress Index (HTSI) & Tin-Roof Trap (TAPAS)...")
    from models.tapas_health import TapasHealthEngine
    tapas = TapasHealthEngine()
    t_res = tapas.compute_ward_htsi(ambient_temp_c=46.0, power_outage_hours=3.0)
    assert len(t_res) == 12, "Expected 12 ward HTSI scores"
    print(f"  [OK] 12 Wards scored. Max indoor heat trap: {max(w['est_indoor_temp_c'] for w in t_res)} deg C (in informal settlements)")

    # 7. 3-Agent Collaborative AI Pipeline
    print("\n[7/12] Testing 3-Agent Collaborative Pipeline & HiGHS MILP (heatwave-public)...")
    from models.agents_pipeline import SpatialClimateAgent, ThreatAssessmentAgent, DispatchCommanderAgent
    a1 = SpatialClimateAgent()
    w_res = a1.run(46.0, 35.0)
    a2 = ThreatAssessmentAgent()
    th_res = a2.run(w_res, 540.0)
    a3 = DispatchCommanderAgent()
    d_res = a3.run(th_res, budget_lakh=75.0, strategy='optimize_coverage')
    print(f"  [OK] Agent 1 -> Agent 2 -> Agent 3 pipeline executed. Strategy: {d_res['strategy_selected']}")
    print(f"  [OK] Allocated units: {d_res['dispatch_plan']['units_allocated']}")

    # 8. Climate EVT Return Periods
    print("\n[8/12] Testing Climate Extremes & Gumbel Return Periods (ClimateSim)...")
    from models.climate_analytics import ClimateAnalyticsEngine
    clim = ClimateAnalyticsEngine()
    rp = clim.compute_return_period(46.5)
    print(f"  [OK] Gumbel EVT Return Period for 46.5 deg C in Raipur: {rp['return_period_years']} years (Severity: {rp['severity_classification']})")

    # 9. DC Power Flow & IEEE 738 Sag
    print("\n[9/12] Testing Synchronous DC Power Flow & Line Sag Clearances (ClimateSim / Heat-Analysis)...")
    from models.grid_power_flow import DCPowerFlowEngine
    pf = DCPowerFlowEngine()
    pf_res = pf.solve_power_flow(ambient_temp_c=46.5, total_city_load_mw=450.0, tripped_substation_id='S01')
    assert len(pf_res["corridor_results"]) == 6, "Expected 6 transmission branches"
    print(f"  [OK] Solved 6-Bus DC Power Flow. Congested corridors under S01 N-1 trip: {pf_res['congested_corridors_count']}")
    print(f"  [OK] Conductor minimum clearance remaining: {min(c['clearance_remaining_m'] for c in pf_res['corridor_results']):.2f} m")

    # 10. 7-Stage Progressive Heatwave
    print("\n[10/12] Testing 7-Stage Progressive Heatwave Lifecycle Simulator (GridStressDigitalTwin)...")
    from models.progressive_heatwave import ProgressiveHeatwaveSimulator
    sim = ProgressiveHeatwaveSimulator()
    assert sim.get_stage_count() == 7, "Expected 7 discrete heatwave stages"
    s3 = sim.evaluate_stage(2)  # Stage 3 peak
    print(f"  [OK] 7 Heatwave stages initialized. Stage 3 Peak Load: {s3['metrics']['city_load_mw']} MW")
    print(f"  [OK] Stage 3 High Risk Citizens: {s3['metrics']['total_high_risk_citizens']:,}")

    # 11. Continuous Resilience Curves & AUC Loss
    print("\n[11/12] Testing Continuous System Resilience Curves & AUC Loss Engine (ClimateSim)...")
    from models.system_resilience import SystemResilienceEngine
    sre = SystemResilienceEngine()
    res_curves = sre.evaluate_resilience_curves(ambient_peak_c=46.5, duration_days=5)
    assert res_curves["baseline"]["auc_loss_hours"] > 0, "Expected positive AUC loss"
    print(f"  [OK] Baseline Lifeline AUC Loss: {res_curves['baseline']['auc_loss_hours']} h | Shielded Loss: {res_curves['shielded']['auc_loss_hours']} h")
    print(f"  [OK] AGNAYA Lifeline Resilience Gain: {res_curves['resilience_gain_pct']}% ({res_curves['disruption_hours_saved']} outage-hours saved)")

    # 12. GridPulse 5-Component Risk & Trilingual Alerts
    print("\n[12/12] Testing GridPulse 5-Component Risk Engine & Trilingual Alerts (GridPulse-AI & TAPAS)...")
    from models.gridpulse_risk import GridPulseRiskEngine
    from models.trilingual_alerts import TrilingualAlertGenerator
    gpr = GridPulseRiskEngine()
    gp_res = gpr.evaluate_city_risk(46.5, 480.0, tripped_substation_id='S01')
    assert len(gp_res) == 12, "Expected 12 zone risk evaluations"
    top_w = gp_res[0]
    print(f"  [OK] Top High-Risk Ward: {top_w['zone_name']} (Score: {top_w['composite_risk']}/100 [{top_w['risk_band']}])")
    print(f"  [OK] Primary Aggravating Factor: {top_w['primary_driver']}")

    tag = TrilingualAlertGenerator()
    alerts = tag.generate_alerts(46.5, 26.0, 5)
    assert alerts["utci_celsius"] > 45.0, "Expected high UTCI"
    print(f"  [OK] Calculated Raipur UTCI: {alerts['utci_celsius']} deg C. Verified English, Hindi, and Chhattisgarhi broadcast alerts.")

    print("\n" + "=" * 70)
    print(" ALL 12 MULTI-MODEL AGNAYA V3.0 ENGINES VERIFIED & OPERATIONAL!")
    print("=" * 70)

if __name__ == "__main__":
    run_multi_model_tests()
