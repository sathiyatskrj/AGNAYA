"""
AGNAYA - FastAPI REST Service (V3.1 Hardened Security & Multi-Model Edition)
Raipur Heatwave Cascading Failure Simulation & Decision Support API

DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
Not endorsed by IMD, NDMA, CSPDCL, or Raipur Municipal Corporation.

Synthesized Frameworks:
  - kd365/heatwave-public: 3-Stage Multi-Objective Decision Support & MILP Dispatch
  - parisproffitt/GridStressDigitalTwin: 7-Stage Progressive Heatwave Timeline & Transformer Hotspots
  - doaamostafa67988/GridPulse-AI: 5-Component Deterministic Risk Engine & Auditable Report Cards
  - Nihita49/TAPAS: UTCI Biometeorology, Tin-Roof Heat Trap & Trilingual Advisories
  - emliang/Heat-Analysis: IEEE Std 738-2012 Dynamic Line Rating (DTR) & Catenary Sag Clearance
  - nabilkhondaker/ClimateSim: Fast DC Power Flow P=B*theta & Continuous System Resilience Curves Q(t)
"""

import time
from collections import defaultdict
from typing import Dict, List, Optional, Any
import sys, os

from fastapi import FastAPI, Query, HTTPException, Request, Depends, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import settings
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

# Synthesized Models
from models.grid_power_flow import DCPowerFlowEngine
from models.progressive_heatwave import ProgressiveHeatwaveSimulator
from models.system_resilience import SystemResilienceEngine
from models.trilingual_alerts import TrilingualAlertGenerator
from models.gridpulse_risk import GridPulseRiskEngine

app = FastAPI(
    title="AGNAYA V3.1 API — Heatwave & Grid Resilience Simulation",
    description="Operational microservice simulating cross-infrastructure cascades under extreme urban heat in Raipur, Chhattisgarh. SIMULATION ONLY – NOT AN OFFICIAL WARNING.",
    version="3.1.0"
)

# ── 1. Secure CORS Configuration (Explicit origins, never wildcard credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ── 2. In-Memory Sliding-Window Rate Limiter & Safe Error Middleware
_request_records = defaultdict(list)

@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    # Rate limiting
    if settings.RATE_LIMIT_PER_MINUTE > 0:
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        # Keep requests within the last 60 seconds
        recent = [t for t in _request_records[client_ip] if now - t < 60.0]
        if len(recent) >= settings.RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Too many requests. Please slow down.",
                    "status": "rate_limited"
                }
            )
        recent.append(now)
        _request_records[client_ip] = recent

    try:
        response = await call_next(request)
        return response
    except HTTPException:
        raise
    except Exception as exc:
        # Safe error response: do not leak filesystem paths or internal stack traces
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal server error occurred while executing the simulation.",
                "status": "error"
            }
        )

# ── 3. Optional API Key Security Header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    if settings.API_KEY:
        if not api_key or api_key != settings.API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized. A valid X-API-Key header is required.",
            )
    return api_key

# ── 4. Strictly Validated Pydantic Schemas
class SimulationRequest(BaseModel):
    peak_temp_celsius: float = Field(45.0, ge=35.0, le=55.0, description="Peak heatwave ambient temperature (°C)")
    duration_days: int = Field(4, ge=1, le=14, description="Heatwave duration in days")
    n_simulations: int = Field(300, ge=50, le=2000, description="Monte Carlo sample iterations")
    interventions: Optional[Dict[str, int]] = Field(default_factory=dict, description="Deployed intervention counts")

class AgentPipelineRequest(BaseModel):
    peak_temp_celsius: float = Field(45.0, ge=35.0, le=55.0, description="Ambient peak temperature (°C)")
    relative_humidity_pct: float = Field(35.0, ge=5.0, le=95.0, description="Relative humidity (%)")
    city_demand_mw: float = Field(520.0, ge=200.0, le=1200.0, description="Aggregate city active load in MW")
    budget_lakh: float = Field(80.0, ge=5.0, le=500.0, description="Emergency municipal allocation budget in Lakh INR")
    strategy: str = Field("optimize_coverage", description="Options: 'optimize_coverage', 'optimize_response_time', 'optimize_staged_reserve', 'auto'")

class HtsiRequest(BaseModel):
    ambient_temp_c: float = Field(45.0, ge=35.0, le=55.0, description="Ambient temperature (°C)")
    power_outage_hours: float = Field(2.0, ge=0.0, le=72.0, description="Duration of feeder power outage in hours")

class TrilingualAlertRequest(BaseModel):
    ambient_temp_c: float = Field(45.0, ge=35.0, le=55.0, description="Ambient temperature (°C)")
    relative_humidity: float = Field(35.0, ge=5.0, le=95.0, description="Relative humidity (%)")
    active_outage_hours: float = Field(2.0, ge=0.0, le=72.0, description="Active power outage duration in hours")
    affected_zone: str = Field("Birgaon Slum Belt", max_length=100, description="Zone or locality descriptor")

class ResilienceRequest(BaseModel):
    peak_temp_c: float = Field(45.5, ge=35.0, le=55.0, description="Scenario peak temperature (°C)")
    duration_days: int = Field(4, ge=1, le=14, description="Simulation horizon in days")

# ── 5. Endpoints
@app.get("/")
def root():
    """System information root endpoint without exposed credentials."""
    return {
        "system": "AGNAYA V3.1 Enterprise Simulation Service",
        "city": "Raipur, Chhattisgarh",
        "version": "3.1.0",
        "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING. Research and operational planning prototype.",
        "basemap_service": {
            "mode": "authenticated_carto" if settings.CARTO_API_KEY else "keyless_osm_positron_fallback",
            "has_custom_key": bool(settings.CARTO_API_KEY),
        },
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
    return {
        "status": "healthy",
        "service": "AGNAYA V3.1 Multi-Model Simulation Engine",
        "rate_limiting": "enabled" if settings.RATE_LIMIT_PER_MINUTE > 0 else "disabled",
        "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
    }

# ── 1. Fast DC Power Flow
@app.get("/api/v1/grid-flow/dc-power-flow", dependencies=[Depends(verify_api_key)])
def get_dc_power_flow(
    total_demand_mw: float = Query(450.0, ge=100.0, le=1200.0, description="Total city power demand in MW"),
    tripped_line: Optional[str] = Query(None, description="Optional tripped line ID (e.g. 'LINE_01')"),
    ambient_temp_c: float = Query(45.0, ge=30.0, le=55.0, description="Ambient temperature for DTR calculation")
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
        "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
    }

# ── 2. 7-Stage Progressive Heatwave Timeline
@app.get("/api/v1/heatwave/7-stages", dependencies=[Depends(verify_api_key)])
def get_progressive_stages(stage_idx: Optional[int] = Query(None, ge=1, le=7)):
    sim = ProgressiveHeatwaveSimulator()
    if stage_idx is not None:
        res = sim.get_stage_details(stage_idx)
        res["disclaimer"] = "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
        return res
    return {
        "stages": sim.get_all_stages(),
        "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
    }

# ── 3. Continuous Resilience Curves Q(t)
@app.post("/api/v1/resilience/continuous-curve", dependencies=[Depends(verify_api_key)])
def get_resilience_curves(req: ResilienceRequest):
    sre = SystemResilienceEngine()
    comp = sre.compare_resilience_curves(peak_temp_c=req.peak_temp_c, duration_days=req.duration_days)
    comp["disclaimer"] = "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
    return comp

# ── 4. Trilingual Advisories & UTCI
@app.post("/api/v1/alerts/trilingual", dependencies=[Depends(verify_api_key)])
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
        "trilingual_broadcasts": alerts,
        "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING. Draft preview only."
    }

# ── 5. GridPulse 5-Component Risk Engine
@app.get("/api/v1/gridpulse/audit", dependencies=[Depends(verify_api_key)])
def get_gridpulse_audit(
    ambient_temp_c: float = Query(45.0, ge=30.0, le=55.0),
    total_grid_demand_mw: float = Query(450.0, ge=100.0, le=1200.0),
    outage_hours: float = Query(2.0, ge=0.0, le=72.0),
    zone_id: Optional[str] = Query(None, description="Optional zone ID (e.g. 'Z01')")
):
    gpr = GridPulseRiskEngine()
    if zone_id:
        res = gpr.generate_boardroom_audit_report(
            zone_id=zone_id,
            ambient_temp_c=ambient_temp_c,
            total_grid_demand_mw=total_grid_demand_mw,
            outage_hours=outage_hours
        )
        res["disclaimer"] = "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
        return res
    return {
        "citywide_risk_matrix": gpr.compute_all_wards_gridpulse(
            ambient_temp_c=ambient_temp_c,
            total_grid_demand_mw=total_grid_demand_mw,
            outage_hours=outage_hours
        ),
        "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
    }

# ── 6. Grid Digital Twin
@app.get("/api/v1/grid-twin/stress", dependencies=[Depends(verify_api_key)])
def get_grid_digital_twin(
    ambient_temp: float = Query(45.0, ge=30.0, le=55.0, description="Ambient temperature in °C"),
    city_demand_mw: float = Query(520.0, ge=100.0, le=1200.0, description="Total city power demand in MW"),
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
        "spatial_demand_distribution": spatial_dist,
        "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
    }

# ── 7. Conductor Ampacity (IEEE 738)
@app.get("/api/v1/conductors/ampacity", dependencies=[Depends(verify_api_key)])
def get_conductor_ampacity(
    ambient_temp: float = Query(45.0, ge=30.0, le=55.0, description="Ambient air temperature in °C"),
    wind_speed_ms: float = Query(1.0, ge=0.1, le=30.0, description="Crosswind velocity in m/s")
):
    engine = ConductorThermalAmpacity()
    corridors = engine.evaluate_all_corridors(ambient_temp, wind_speed_ms)
    return {
        "ambient_temp_celsius": ambient_temp,
        "wind_speed_ms": wind_speed_ms,
        "corridors": corridors,
        "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
    }

# ── 8. TAPAS Heat-Health Stress Index
@app.post("/api/v1/tapas/htsi", dependencies=[Depends(verify_api_key)])
def compute_htsi(req: HtsiRequest):
    engine = TapasHealthEngine()
    wards = engine.compute_ward_htsi(req.ambient_temp_c, req.power_outage_hours)
    return {
        "ambient_temp_c": req.ambient_temp_c,
        "power_outage_hours": req.power_outage_hours,
        "ward_assessments": wards,
        "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
    }

# ── 9. Multi-Stage Pipeline & Dispatch Optimization
@app.post("/api/v1/agents/pipeline", dependencies=[Depends(verify_api_key)])
def run_agent_pipeline(req: AgentPipelineRequest):
    a1 = SpatialClimateAgent()
    w_res = a1.run(req.peak_temp_celsius, req.relative_humidity_pct)

    a2 = ThreatAssessmentAgent()
    th_res = a2.run(w_res, req.city_demand_mw)

    a3 = DispatchCommanderAgent()
    d_res = a3.run(th_res, budget_lakh=req.budget_lakh, strategy=req.strategy)

    return {
        "stage_1_spatial_climate": w_res,
        "stage_2_threat_assessment": th_res,
        "stage_3_dispatch_commander": d_res,
        "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
    }

# ── 10. Climate Return Periods
@app.get("/api/v1/climate/return-periods", dependencies=[Depends(verify_api_key)])
def get_climate_extremes(temp: float = Query(45.0, ge=30.0, le=55.0, description="Temperature to check return period for")):
    clim = ClimateAnalyticsEngine()
    rp = clim.compute_return_period(temp)
    curve = clim.generate_return_period_curve()
    return {
        "target_temperature_c": temp,
        "return_period_analysis": rp,
        "return_period_curve": curve,
        "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
    }

# ── 11. Stochastic Cascade Simulation
@app.post("/api/v1/simulate", dependencies=[Depends(verify_api_key)])
def run_classic_simulation(req: SimulationRequest):
    mc = MonteCarloCascade(N_sim=req.n_simulations)
    summary = mc.run(
        T_peak=req.peak_temp_celsius,
        duration_days=req.duration_days,
        interventions=req.interventions or {}
    )
    summary["disclaimer"] = "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
    return summary
