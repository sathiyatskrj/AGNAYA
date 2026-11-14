# AGNAYA: Scientific & Technical Roadmap

This roadmap documents research expansions, external data integrations, and advanced features currently out of scope or deferred to avoid fabricating parameters without primary source evidence.

---

## 1. Full AC Power Flow via `pandapower`
- **Current Implementation:** Linearized DC Power Flow ($P = B' \theta$) with empirical series susceptance on a 100 MVA system base.
- **Why Deferred:** Authentic Newton-Raphson AC power flow requires verified bus voltage magnitudes ($V$), reactive power demands ($Q$), branch resistance-to-reactance ratios ($R/X$), shunt admittances ($B_{sh}$), and tap-changer positions across all 220/132/33 kV substations. Fabricating these parameters produces misleading voltage stability metrics.
- **Requirements for Activation:**
  1. CSPTCL State Load Despatch Centre (SLDC) official network line parameters and conductor test reports.
  2. Substation bus reactive power and power factor logs.
  3. Transformer tap-changer schedules and excitation impedances.

---

## 2. Full 70-Ward Administrative Boundary GIS Integration
- **Current Implementation:** 12 illustrative urban planning zones aggregating Raipur's ~1.12M urban population.
- **Why Deferred:** Official Raipur Municipal Corporation (RMC) 70-ward Shapefiles / GeoJSON boundaries with ward-level Census 2021/2024 micro-demographics are not openly published with verified polygon geometries.
- **Requirements for Activation:**
  1. Official RMC 70-ward boundary GIS layer (EPSG:4326).
  2. Ward-level slum population counts, roof type distributions, and age demographics from RMC administrative records.

---

## 3. In-Situ Indoor Temperature Field Calibration (Phase 4 Pilot Hook Implemented)
- **Current Status:** Calibration pipeline (`models/indoor_calibration.py`), standardized CSV schema (`data/sample_indoor_loggers.csv`), demonstration calibration script (`notebooks/01_indoor_temperature_calibration.py`), and field pilot protocol ([`docs/PILOT.md`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/docs/PILOT.md)) completed.
- **Physical Pilot Activation Requirements:**
  1. Institutional ethical review / community approval with ward committees in Birgaon, Gudhiyari, Tikrapara, and Urla.
  2. Procurement and deployment of 8–10 calibrated BLE/USB temperature/RH data loggers ($\pm 0.3^\circ\text{C}$ accuracy) in tin-roof dwellings during pre-monsoon peak heat (April 15 – June 15).
  3. Ingestion of raw field CSVs into `IndoorLoggerValidationEngine` to upgrade empirical coefficients from `ASSUMED` to `VERIFIED (FIELD PILOT)`.

---

## 4. Clinically Calibrated Heat-Health Mortality & Morbidity Models
- **Current Implementation:** Relative risk tiers (`GUARDED`, `ELEVATED`, `HIGH`, `CRITICAL`) and contributing factor rankings based on the IIT Roorkee *Nature Scientific Reports* (2026) Heuristic Heat-Risk Index ($HSRI = HI \times VI \times EI$). Uncalibrated absolute mortality counts have been removed from primary UI and API responses.
- **Why Deferred:** Estimating daily excess deaths and emergency admissions requires city-specific distributed lag non-linear models (DLNM) calibrated against historical daily civil registration mortality records and hospital admission registries.
- **Requirements for Activation:**
  1. Collaborative data agreement with Dr. B.R. Ambedkar Memorial Hospital and AIIMS Raipur for heat-related illness registries.
  2. Raipur Municipal Corporation daily birth and death registry data across consecutive summer seasons (2018–2025).

---

## 5. Live SCADA / Telemetry Streaming
- **Current Implementation:** User scenario simulation and hourly Open-Meteo gridded forecast connector.
- **Why Deferred:** Real-time utility grid operations require authenticated ICCP (Inter-Control Center Communications Protocol) or IEC 60870-5-104 feeds from CSPTCL SLDC.

