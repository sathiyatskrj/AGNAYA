# 🌡️⚡🏥 AGNAYA v3.0 — Raipur Heatwave & Grid Digital Twin
### *Adaptive Geospatial Network for Heatwave Analytics and Yield Assessment*
**Civil Protection & Utility Operations Center for Raipur, Chhattisgarh**

---

## 1. Executive Summary & Purpose

**AGNAYA** is an advanced mathematical early-warning and decision-support platform designed specifically for **Raipur, Chhattisgarh, India**.

It unifies the theoretical and engineering breakthroughs of six leading open-source heatwave, power grid, and climate intelligence projects into an integrated urban disaster resilience system grounded in real Chhattisgarh state parameters:

| Reference Repository | Integrated Scientific Framework in AGNAYA |
|---|---|
| **`kd365/heatwave-public`** | **3-Agent Collaborative AI Pipeline**: Ingestion Agent $\to$ Threat Assessment Agent $\to$ Autonomous Dispatch Commander (MILP optimization). |
| **`parisproffitt/GridStressDigitalTwin`** | **Transformer Thermal Digital Twin**: IEEE C57.91 winding hot-spot temperature, top-oil thermal rise, spatial neighbor overload propagation. |
| **`doaamostafa67988/GridPulse-AI`** | **5-Factor Grid Heat Risk Engine & Spatial Load Reweighting**: Redistribution of aggregate grid demand based on industrial density (Urla/Birgaon vs domestic zones). |
| **`Nihita49/TAPAS`** | **Heat–Health Stress Index (HTSI) & Tin-Roof Factor**: Epidemiological relative risk ($RR_{\text{mortality}}$), excess deaths, informal settlement tin-roof heat entrapment, and automated Heat Action Plan (HAP) library. |
| **`emliang/Heat-Analysis`** | **IEEE Std 738-2012 Conductor Thermal Ampacity**: Temperature-dependent line ratings (TDLR) and sag clearance hazard for CSPTCL transmission corridors. |
| **`nabilkhondaker/ClimateSim`** | **Extreme Value Theory (EVT) & Biometeorology**: Gumbel distribution for Raipur heatwave return periods, NWS Heat Index (Rothfusz), and Wet Bulb Globe Temperature (WBGT). |

---

## 2. Real-World Chhattisgarh Grounded Data

Extracted directly from CSERC tariff filings, CSPTCL engineering documents, and Census data:
- **Baseline Demand**: 310 MW (Normal season) up to 620 MW (Peak summer grid ceiling).
- **Substations**: Raipur Main (220/132 kV, 500 MVA), Mowa GSS (132/33 kV, 200 MVA), Amanaka (132/33 kV, 160 MVA), Pandri (33/11 kV, 80 MVA), Khamardih (33/11 kV, 50 MVA), Gudhiyari (33/11 kV, 60 MVA).
- **Transmission Corridors**: Bhilai-Raipur 220kV D/C, Raipur-Mowa 132kV, Raipur-Amanaka 132kV, Mowa-Pandri 33kV, Amanaka-Gudhiyari 33kV.
- **Urban Demographics**: 12 Raipur zones including high-slum industrial belts (Birgaon, Urla with 42% slum population and 6% AC penetration) and low-slum high-canopy areas (Civil Lines, Shankar Nagar).

---

## 3. Mathematical Modules & Architecture

```
AGNAYA/
├── app.py                      # Interactive Streamlit Digital Twin (9 Operational Tabs)
├── api.py                      # FastAPI REST Microservice (v3.0 endpoints)
├── styles.css                  # Municipal & Utility Design System
├── agnaya_launcher.py          # Standalone In-Process Launcher
├── AGNAYA.spec                 # PyInstaller Packaging Specification
├── test_system.py              # 12-Stage Scientific Verification Suite
├── requirements.txt            # Dependency Specification
├── RUN_AGNAYA.bat              # 1-Click Windows Batch Runner for Dashboard
├── RUN_API.bat                 # 1-Click Windows Batch Runner for FastAPI Server
├── .streamlit/
│   └── config.toml             # Neutral Dark Theme Configuration
├── assets/
│   ├── agnaya_logo.png         # Official Project Logo
│   └── agnaya_logo.ico         # Executable Application Icon
├── data/
│   ├── __init__.py
│   └── raipur_data.py          # Grounded GIS, grid, substation, hospital, and climate data
└── models/
    ├── __init__.py
    ├── cascade_model.py        # Continuous ODE Demand & Monte Carlo Cascades
    ├── grid_digital_twin.py    # Transformer Hotspots & Spatial Neighbor Overload Stress
    ├── tapas_health.py         # Heat-Health Stress Index (HTSI) & Tin-Roof Trap
    ├── conductor_ampacity.py   # IEEE 738 Overhead Line Rating (Heat-Analysis)
    ├── agents_pipeline.py      # 3-Agent Collaborative AI & HiGHS MILP Dispatch
    ├── climate_analytics.py    # Gumbel EVT Return Periods & Heat Index
    ├── grid_power_flow.py      # Synchronous DC Power Flow (P = B*theta)
    ├── progressive_heatwave.py # 7-Stage Progressive Lifecycle Simulator
    ├── system_resilience.py    # Continuous Resilience Curves Q(t) & AUC Loss
    ├── trilingual_alerts.py    # Multi-Lingual Civil Protection Advisories
    └── gridpulse_risk.py       # 5-Component Deterministic Risk Engine
```

---

## 4. Key Mathematical Formulations

### A. IEEE C57.91 Transformer Hotspot & Aging
$$\Theta_H = \Theta_A + \Delta\Theta_{TO,\text{rated}}\left(\frac{I}{I_{\text{rated}}}\right)^{0.8} + \Delta\Theta_{H,\text{rated}}\left(\frac{I}{I_{\text{rated}}}\right)^{0.8}$$
$$\text{Aging Acceleration Factor } V = \exp\left[\frac{15000}{383.15} - \frac{15000}{\Theta_H + 273.15}\right]$$

### B. IEEE Std 738 Conductor Thermal Ampacity
$$I_{\text{derated}} = I_{\text{rated}} \cdot \sqrt{\frac{T_{c,\text{max}} - T_a}{T_{c,\text{max}} - 40.0}} \cdot \left(\frac{V_{\text{wind}}}{1.0}\right)^{0.5}$$

### C. TAPAS Heat-Health Stress Index (HTSI) & Tin-Roof Trap
$$\text{HTSI} = \frac{\text{Hazard} \times \text{Exposure} \times \text{Vulnerability}}{\text{Adaptive Capacity}} \times 100$$
$$T_{\text{indoor}} = T_a + 4.0 \cdot \text{KutchaRoofFactor} - 4.0 \cdot \text{GreenCover} + \min(6.5, 0.8 \cdot \text{OutageHours})$$
$$RR_{\text{mortality}} = 1.0 + 0.85 \cdot \left(\frac{\text{HTSI}}{100}\right)^{1.8}$$

### D. 3-Agent Collaborative MILP Dispatch (HiGHS Solver)
$$\max_{\mathbf{x}} \; \sum_{k} \text{Benefit}_k \cdot x_k \quad \text{s.t.} \quad \sum_{k} \text{Cost}_k \cdot x_k \le B, \quad x_k \in \mathbb{Z}_{\ge 0}$$
Supports 3 strategic doctrines:
1. `optimize_coverage`: Maximizes total protected population across all vulnerable wards.
2. `optimize_response_time`: Prioritizes emergency mobile units (DG sets & water tankers) to CRITICAL zones.
3. `optimize_staged_reserve`: 70% active deployment, 30% strategic mobile reserve staged at central depots.

### E. Gumbel Extreme Value Theory (EVT) Return Periods
$$F(T) = \exp\left(-\exp\left(-\frac{T - \mu}{\beta}\right)\right), \quad T_{\text{return}} = \frac{1}{1 - F(T)}$$
Fitted to Raipur historical annual maximums ($\mu = 43.1^\circ\text{C}, \beta = 1.25^\circ\text{C}$).

---

## 5. Live Services & Execution

Both services are active and verified on localhost:

| Service | Address | Features |
|---|---|---|
| **Streamlit Interactive UI** | `http://localhost:8501` | 7 interactive tabs: Executive Dashboard, Geospatial Risk Map, Grid Digital Twin & Lines, Heat-Health (TAPAS) & HAP, 3-Agent AI Pipeline, Monte Carlo Cascades, and Climate Extremes & EVT. |
| **FastAPI REST Service** | `http://127.0.0.1:8000` | High-performance JSON API. |
| **Interactive Swagger API Docs** | `http://127.0.0.1:8000/docs` | Test endpoints: `/api/v1/grid-twin/stress`, `/api/v1/conductors/ampacity`, `/api/v1/tapas/htsi`, `/api/v1/agents/pipeline`, `/api/v1/climate/return-periods`. |

### 1-Click Launchers for Windows
- Double-click [`RUN_AGNAYA.bat`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/RUN_AGNAYA.bat) to launch the Streamlit Dashboard.
- Double-click [`RUN_API.bat`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/RUN_API.bat) to launch the FastAPI server.
