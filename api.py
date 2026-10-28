"""
AGNAYA - FastAPI REST Service (V3.0 Enterprise Multi-Model Edition)
Raipur Heatwave Cascading Failure Simulation & Decision Support API

Synthesized Frameworks:
  - kd365/heatwave-public: 3-Agent Collaborative AI Pipeline & MILP Dispatch
  - parisproffitt/GridStressDigitalTwin: 7-Stage Progressive Heatwave Timeline & Transformer Hotspots
  - doaamostafa67988/GridPulse-AI: 5-Component Deterministic Risk Engine & Auditable Report Cards
  - Nihita49/TAPAS: UTCI Biometeorology, Tin-Roof Heat Trap & Trilingual Broadcast Advisories
  - emliang/Heat-Analysis: IEEE Std 738-2012 Dynamic Line Rating (DTR) & Catenary Sag Clearance
  - nabilkhondaker/ClimateSim: Fast DC Power Flow P=B*theta & Continuous System Resilience Curves Q(t)
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data.raipur_data import (
    RAIPUR_ZONES, RAIPUR_SUBSTATIONS, RAIPUR_WATER_PUMPS,
    RAIPUR_HOSPITALS, RAIPUR_CLIMATE, HISTORICAL_HEATWAVES,
    INTERVENTION_OPTIONS, CSPDCL_PARAMS
)
from models.cascade_model import (
    DemandModel, InfrastructureNetwork, MonteCarloCascade,
    InterventionOptimizer, compute_zone_risk_table
)
from models.grid_digital_twin import GridStressNetwork, compute_spatial_load_distribution
from models.tapas_health import TapasHealthEngine, HAP_MEASURES
from models.conductor_ampacity import ConductorThermalAmpacity, RAIPUR_TRANSMISSION_CORRIDORS
from models.agents_pipeline import SpatialClimateAgent, ThreatAssessmentAgent, DispatchCommanderAgent
from models.climate_analytics import ClimateAnalyticsEngine

# V3.0 Synthesized Models
from models.grid_power_flow import DCPowerFlowEngine
from models.progressive_heatwave import ProgressiveHeatwaveSimulator
from models.system_resilience import SystemResilienceEngine
from models.trilingual_alerts import TrilingualAlertGenerator
from models.gridpulse_risk import GridPulseRiskEngine

app = FastAPI(
    title="AGNAYA V3.0 API — Unified Multi-Model Decision Support",
    description="Operational microservice synthesizing 6 research frameworks with CSPTCL grid models, IMD climatology, and Census 2011 for Raipur, Chhattisgarh.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Schemas
class SimulationRequest(BaseModel):
    peak_temp_celsius: float = Field(45.0, ge=35.0, le=55.0)
    duration_days: int = Field(4, ge=1, le=14)
    n_simulations: int = Field(300, ge=50, le=2000)
    interventions: Optional[Dict[str, int]] = Field(default_factory=dict)

class AgentPipelineRequest(BaseModel):
    peak_temp_celsius: float = Field(45.0, ge=35.0, le=55.0)
    relative_humidity_pct: float = Field(35.0, ge=5.0, le=95.0)
    city_demand_mw: float = Field(520.0, ge=200.0, le=1000.0)
    budget_lakh: float = Field(80.0, ge=5.0, le=500.0)
    strategy: str = Field("optimize_coverage", description="Options: 'optimize_coverage', 'optimize_response_time', 'optimize_staged_reserve', 'auto'")

class HtsiRequest(BaseModel):
    ambient_temp_c: float = Field(45.0, ge=35.0, le=55.0)
    power_outage_hours: float = Field(2.0, ge=0.0, le=24.0)

class TrilingualAlertRequest(BaseModel):
    ambient_temp_c: float = Field(45.0, ge=35.0, le=55.0)
    relative_humidity: float = Field(35.0, ge=5.0, le=95.0)
    active_outage_hours: float = Field(2.0, ge=0.0, le=24.0)
    affected_zone: str = Field("Birgaon Slum Belt")

class ResilienceRequest(BaseModel):
    peak_temp_c: float = Field(45.5, ge=38.0, le=52.0)
    duration_days: int = Field(4, ge=1, le=14)

# ── Endpoints
@app.get("/")
def root():
    return {
        "system": "AGNAYA V3.0 Enterprise",
        "city": "Raipur, Chhattisgarh",
        "version": "3.0.0",
        "carto_basemaps": {
            "status": "authenticated",
            "key": "cb1_4luv_1_702fe094ac8114d4005f2fa3",
            "watermark": "none",
            "tile_url": "https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png?key=cb1_4luv_1_702fe094ac8114d4005f2fa3"
        },
        "models_integrated": [
            "GridStressDigitalTwin (7-Stage Timeline & Transformer Hotspots)",
            "GridPulse-AI (5-Component Risk Engine & Boardroom Audit Reports)",
            "TAPAS (UTCI Biometeorology, Tin-Roof Heat Trap & Trilingual Alerts)",
            "Heat-Analysis (IEEE Std 738-2012 Dynamic Line Rating & Sag)",
            "heatwave-public (3-Agent Collaborative AI Pipeline & HiGHS MILP)",
            "ClimateSim (Fast DC Power Flow P=B*theta & Continuous Resilience Curves Q(t))"
        ],
        "endpoints": [
            "/docs",
            "/api/v1/health",
            "/api/v1/grid-flow/dc-power-flow",
            "/api/v1/heatwave/7-stages",
            "/api/v1/resilience/continuous-curve",
            "/api/v1/alerts/trilingual",
            "/api/v1/gridpulse/audit",
            "/api/v1/grid-twin/stress",
            "/api/v1/conductors/ampacity",
            "/api/v1/tapas/htsi",
            "/api/v1/agents/pipeline",
            "/api/v1/climate/return-periods",
            "/api/v1/simulate"
        ]
    }

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "service": "AGNAYA V3.0 Multi-Model Engine"}

# ── 1. Fast DC Power Flow (ClimateSim / Heat-Analysis)
@app.get("/api/v1/grid-flow/dc-power-flow")
def get_dc_power_flow(
    total_demand_mw: float = Query(450.0, description="Total city power demand in MW"),
    tripped_line: Optional[str] = Query(None, description="Optional tripped transmission line ID (e.g. 'LINE_01')"),
    ambient_temp_c: float = Query(45.0, description="Ambient temperature for DTR calculation")
):
    pf = DCPowerFlowEngine()
    flow_res = pf.solve_dc_power_flow(total_demand_mw=total_demand_mw, tripped_line_id=tripped_line)
    dtr_res = pf.compute_ieee738_dtr(ambient_temp_c=ambient_temp_c)
    return {
        "total_demand_mw": total_demand_mw,
        "tripped_line": tripped_line,
        "bus_angles_deg": flow_res["bus_angles_deg"],
        "line_flows_mw": flow_res["line_flows_mw"],
        "line_loadings_pct": flow_res["line_loadings_pct"],
        "overloaded_lines": flow_res["overloaded_lines"],
        "grid_stability_index": flow_res["grid_stability_index"],
        "dynamic_line_ratings": dtr_res,
    }


# ── 2. 7-Stage Progressive Heatwave Timeline (GridStressDigitalTwin)
@app.get("/api/v1/heatwave/7-stages")
def get_progressive_stages(stage_idx: Optional[int] = Query(None, ge=1, le=7)):
    sim = ProgressiveHeatwaveSimulator()
    if stage_idx is not None:
        return sim.get_stage_details(stage_idx)
    return {"stages": sim.get_all_stages()}

# ── 3. Continuous Resilience Curves Q(t) (ClimateSim)
@app.post("/api/v1/resilience/continuous-curve")
def get_resilience_curves(req: ResilienceRequest):
    sre = SystemResilienceEngine()
    comp = sre.compare_resilience_curves(peak_temp_c=req.peak_temp_c, duration_days=req.duration_days)
    return comp

# ── 4. Trilingual Broadcast Advisories & UTCI (TAPAS)
@app.post("/api/v1/alerts/trilingual")
def get_trilingual_alerts(req: TrilingualAlertRequest):
    tag = TrilingualAlertGenerator()
    utci = tag.compute_biomet_utci(ambient_temp_c=req.ambient_temp_c, relative_humidity=req.relative_humidity)
    alerts = tag.generate_trilingual_alerts(
        ambient_temp_c=req.ambient_temp_c,
        relative_humidity=req.relative_humidity,
        active_outage_hours=req.active_outage_hours,
        primary_affected_zone=req.affected_zone
    )
    return {
        "utci_biometeorology": utci,
        "trilingual_broadcasts": alerts
    }

# ── 5. GridPulse 5-Component Risk Engine & Audit Cards (GridPulse-AI)
@app.get("/api/v1/gridpulse/audit")
def get_gridpulse_audit(
    ambient_temp_c: float = Query(45.0),
    total_grid_demand_mw: float = Query(450.0),
    outage_hours: float = Query(2.0),
    zone_id: Optional[str] = Query(None, description="Optional zone ID for individual boardroom report card")
):
    gpr = GridPulseRiskEngine()
    if zone_id:
        return gpr.generate_boardroom_audit_report(
            zone_id=zone_id,
            ambient_temp_c=ambient_temp_c,
            total_grid_demand_mw=total_grid_demand_mw,
            outage_hours=outage_hours
        )
    return {
        "citywide_risk_matrix": gpr.compute_all_wards_gridpulse(
            ambient_temp_c=ambient_temp_c,
            total_grid_demand_mw=total_grid_demand_mw,
            outage_hours=outage_hours
        )
    }

# ── 6. Grid Digital Twin
@app.get("/api/v1/grid-twin/stress")
def get_grid_digital_twin(
    ambient_temp: float = Query(45.0, description="Ambient temperature in °C"),
    city_demand_mw: float = Query(520.0, description="Total city power demand in MW"),
    tripped_substation: Optional[str] = Query(None, description="Optional tripped substation ID (e.g. 'S06')")
):
    g_net = GridStressNetwork()
    sub_states = g_net.compute_composite_grid_risk(ambient_temp, city_demand_mw, tripped_substation)
    spatial_dist = compute_spatial_load_distribution(city_demand_mw)
    return {
        "ambient_temp_celsius": ambient_temp,
        "city_demand_mw": city_demand_mw,
        "tripped_substation": tripped_substation,
        "substations": sub_states,
        "spatial_demand_distribution": spatial_dist
    }

# ── 7. Conductor Ampacity (IEEE 738)
@app.get("/api/v1/conductors/ampacity")
def get_conductor_ampacity(
    ambient_temp: float = Query(45.0, description="Ambient air temperature in °C"),
    wind_speed_ms: float = Query(1.0, description="Crosswind velocity in m/s")
):
    engine = ConductorThermalAmpacity()
    corridors = engine.evaluate_all_corridors(ambient_temp, wind_speed_ms)
    return {
        "ambient_temp_celsius": ambient_temp,
        "wind_speed_ms": wind_speed_ms,
        "corridors": corridors
    }

# ── 8. TAPAS Heat-Health Stress Index
@app.post("/api/v1/tapas/htsi")
def compute_htsi(req: HtsiRequest):
    engine = TapasHealthEngine()
    wards = engine.compute_ward_htsi(req.ambient_temp_c, req.power_outage_hours)
    return {
        "ambient_temp_c": req.ambient_temp_c,
        "power_outage_hours": req.power_outage_hours,
        "ward_assessments": wards
    }

# ── 9. 3-Agent Collaborative AI Pipeline
@app.post("/api/v1/agents/pipeline")
def run_agent_pipeline(req: AgentPipelineRequest):
    a1 = SpatialClimateAgent()
    w_res = a1.run(req.peak_temp_celsius, req.relative_humidity_pct)

    a2 = ThreatAssessmentAgent()
    th_res = a2.run(w_res, req.city_demand_mw)

    a3 = DispatchCommanderAgent()
    d_res = a3.run(th_res, budget_lakh=req.budget_lakh, strategy=req.strategy)

    return {
        "agent_1_spatial_climate": w_res,
        "agent_2_threat_assessment": th_res,
        "agent_3_dispatch_commander": d_res
    }

# ── 10. Climate Return Periods
@app.get("/api/v1/climate/return-periods")
def get_climate_extremes(temp: float = Query(45.0, description="Temperature to check return period for")):
    clim = ClimateAnalyticsEngine()
    rp = clim.compute_return_period(temp)
    curve = clim.generate_return_period_curve()
    return {
        "target_temperature_c": temp,
        "return_period_analysis": rp,
        "return_period_curve": curve
    }

# ── 11. Stochastic Cascade Simulation
@app.post("/api/v1/simulate")
def run_classic_simulation(req: SimulationRequest):
    mc = MonteCarloCascade(N_sim=req.n_simulations)
    summary = mc.run(
        T_peak=req.peak_temp_celsius,
        duration_days=req.duration_days,
        interventions=req.interventions or {}
    )
    return summary
