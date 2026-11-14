# AGNAYA Field Pilot Protocol: In-Situ Indoor Microclimate Logging
## Ground-Truthing Urban Heat Entrapment in Informal Settlements of Raipur, Chhattisgarh

**Document ID:** AGNAYA-PROT-2026-01  
**Version:** 1.0 (Draft for Institutional / Community Review)  
**Status:** DRAFT PILOT PROTOCOL – SIMULATION & RESEARCH PLANNING ONLY  
**Target City:** Raipur, Chhattisgarh (Birgaon Industrial Belt, Gudhiyari, Tikrapara, Urla)  
**Target Season:** Pre-monsoon Summer (April 15 – June 15)  

---

## 1. Executive Summary & Purpose

Urban heat models routinely rely on outdoor 2-meter air temperature ($T_{\text{ambient}}$) measured at regional synoptic weather stations (such as IMD Station #42809 at Mana Airport). However, vulnerable urban residents—particularly the ~30% living in informal settlements (*bastis*)—spend over 80% of their heatwave exposure hours inside single-room dwellings characterized by uninsulated corrugated galvanized iron (CGI) tin roofing, minimal thermal mass, and zero convective cross-ventilation.

During heatwaves, solar surface temperatures on unshaded CGI sheets can exceed 65°C, radiating severe longwave infrared heat directly into the living space. When local power distribution feeders trip or load-shedding is enforced, ceiling fans and desert coolers immediately cease, creating acute, lethal indoor heat traps where internal air temperatures can surpass ambient conditions by 3°C to 7°C.

The purpose of this pilot protocol is to deploy **5 to 10 low-cost calibrated temperature and relative humidity (T/RH) dataloggers** inside representative informal dwellings across Raipur. Ground-truth data collected from this pilot will calibrate AGNAYA's empirical indoor thermal equations, replacing uncalibrated synthetic assumptions with validated microclimatic transfer coefficients.

---

## 2. Sensor Hardware Specifications

To ensure scientific rigor, high data recovery rates, and minimal disruption to participating households, sensor hardware must adhere to the following technical specifications:

| Parameter | Specification Requirement | Recommended COTS Examples |
| :--- | :--- | :--- |
| **Temperature Range** | $-20^\circ\text{C}$ to $+70^\circ\text{C}$ | Elitech RC-51 / Govee H5074 / HOBO MX1101 |
| **Temperature Accuracy** | $\pm 0.3^\circ\text{C}$ (within $+20^\circ\text{C}$ to $+55^\circ\text{C}$) | Factory calibrated or 2-point ice/dry bath verified |
| **Humidity Range & Accuracy** | $10\%$ to $95\%$ RH; $\pm 2.5\%$ RH | Capacitive polymer humidity sensor |
| **Sampling Interval** | Configurable: **15 minutes** (96 readings/day) | Provides diurnal curve & power-cut thermal lag |
| **Memory Capacity** | Non-volatile flash $\ge 32,000$ data points | $\ge 120$ days autonomous recording at 15-min rate |
| **Power Supply** | User-replaceable lithium coin cell (CR2032/CR2450) | $\ge 6$ months battery operational endurance |
| **Data Extraction** | Bluetooth Low Energy (BLE) or Direct USB | Wireless offload without dismounting sensor |
| **Form Factor / Ingress** | Compact ($< 60 \times 40 \times 15\text{ mm}$), $< 40\text{ g}$, IP54 | Tamper-resistant casing with lanyard/bracket mount |

---

## 3. Site Selection & Household Cohort

The pilot targets **8 primary intervention homes** and **2 control homes** distributed across four zones identified in AGNAYA's vulnerability atlas:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       RAIPUR PILOT DEPLOYMENT SITES                         │
├────────────────────┬───────┬────────────┬─────────────┬─────────────────────┤
│ Ward / Zone        │ Zone  │ Target Homes│ Roof Type   │ Environmental Note  │
├────────────────────┼───────┼────────────┼─────────────┼─────────────────────┤
│ Birgaon Industrial │ Z01   │ 2 Homes    │ CGI Tin     │ Industrial heat UHI │
│ Gudhiyari          │ Z08   │ 2 Homes    │ 1 Tin, 1 AC │ Dense railway fringe│
│ Tikrapara          │ Z05   │ 2 Homes    │ 1 Tin, 1 Pu │ Urban core informal │
│ Urla Industrial    │ Z04   │ 2 Homes    │ 1 Tin, 1 Tile│ Heavy fabrication  │
│ Control Site 1     │ Z06   │ 1 Home     │ Pucca RCC   │ Multistory masonry  │
│ Control Site 2     │ Z02   │ 1 Home     │ Pucca RCC   │ Ventilated concrete │
└────────────────────┴───────┴────────────┴─────────────┴─────────────────────┘
```

### Household Selection Criteria
1. **Structural Archetype:** Single-story ground-floor dwelling with uninsulated corrugated iron (*tin pathara*) or asbestos sheet roofing.
2. **Occupancy Profile:** Occupied by at least one high-risk resident (elderly $\ge 60$, pregnant woman, young children, or outdoor daily-wage worker).
3. **Power Reliability:** Connected to a standard CSPDCL low-tension residential distribution feeder with historical summer tripping susceptibility.
4. **Willingness to Participate:** Voluntary consent given following bilingual community engagement.

---

## 4. Informed Consent & Ethical Guidelines

Prior to sensor installation, field teams must strictly follow this informed consent protocol:

1. **Language & Clarity:** Written and verbal explanations must be provided in **Chhattisgarhi** and **Hindi**.
2. **No Collection of Personally Identifiable Information (PII):** Household identities are anonymized with unique alpha-numeric hashes (`H01_BIRGAON_01`, `H02_BIRGAON_02`). No resident names, phone numbers, or exact street numbers are stored in data repositories.
3. **Complete Freedom to Withdraw:** Participating households may withdraw from the study at any time without penalty. Sensors will be retrieved immediately upon request.
4. **Community Benefit & Reciprocity:** Participating households receive a token of appreciation (e.g., high-efficiency rechargeable LED solar study light, oral rehydration salts (ORS) kit, and a bilingual heat-health guide).
5. **No Interference with Living Space:** Sensors must be placed so they do not obstruct daily household activities or prayer areas.

---

## 5. Sensor Placement Protocol

Precise physical placement is crucial to prevent micro-artifacts from cooking stoves, fans, or direct sunlight:

```
              ┌──────────────────────────────────────────────────┐
              │             CGI TIN ROOF (~65°C Peak)            │
              └────────────────────────┬─────────────────────────┘
                                       │ 
                     [ Radiation Barrier / 0.5m Gap ]
                                       │
                      ==================================  <-- Ceiling Fan
                                       │
                                       ▼
                     ┌───────────────────────────────────┐
                     │         BREATHING ZONE            │
                     │      Height: 1.2 m to 1.5 m       │
                     │  -------------------------------  │
                     │      [ SENSOR MOUNTED HERE ]      │
                     │   (Interior Partition / Bed Head) │
                     └───────────────────────────────────┘
                                       ▲
                                       │
                        Min 2.0 m      │     Min 1.0 m
                       from Chulha /   │    from Windows /
                       Cooking Stove   │    Exterior Doors
                                       │
              ────────────────────────────────────────────────────
                               FLOOR LEVEL
```

### Strict Placement Rules:
1. **Vertical Height:** Fixed between **1.2 meters and 1.5 meters** above finished floor level (representing the standing/sitting breathing zone of occupants).
2. **Horizontal Clearances:**
   - **Cooking Source Clearance:** Minimum **2.0 meters** horizontal separation from LPG stoves, kerosene burners, or traditional biomass *chulhas*.
   - **Direct Radiation Clearance:** Minimum **0.5 meters** below the roof plane; mounted on an interior partition wall, never directly touching exterior sunlit sheet metal.
   - **Door/Window Clearance:** Minimum **1.0 meter** away from open exterior doorways or windows to avoid measuring transient outdoor gust drafts.
   - **Cooling Appliance Clearance:** Not placed directly in the concentrated air-jet of a desert cooler or table fan.

---

## 6. Deployment Schedule & Field Logistics

The pilot spans **4 weeks (28 days)** during peak summer:

* **Week 0 (Preparation & Baseline):**
  - Sensor calibration check: 24-hour side-by-side verification in a controlled room to record intra-sensor variance ($\le \pm 0.2^\circ\text{C}$).
  - Community liaison and household visits; informed consent execution.
* **Weeks 1–3 (Active Monitoring):**
  - Sensors logging continuously at **15-minute intervals**.
  - Weekly field officer visit: BLE wireless data offload, visual inspection, household check-in.
  - Concurrent logging of CSPDCL 11 kV feeder outage logs and Open-Meteo / IMD Mana airport temperature.
* **Week 4 (Retrieval & Synthesis):**
  - Final data download, sensor dismounting, gratitude kit distribution.
  - Comprehensive data cleaning and ingestion into AGNAYA calibration engine.

---

## 7. Data Ingestion & Quality Control (QC)

Data extracted from physical loggers is formatted according to AGNAYA's standardized CSV schema:

```csv
house_id,zone,roof_type,timestamp,temp_c,rh,ambient_temp_c,outage_hours,provenance
H01_BIRGAON_01,Z01,tin_cgi,2026-05-15T14:00:00+05:30,49.2,32.4,45.8,1.5,REAL_PILOT
```

### Automated Quality Control Steps:
1. **Range Validation:** Flag readings where $T < 15^\circ\text{C}$ or $T > 65^\circ\text{C}$, or $\text{RH} < 5\%$ or $\text{RH} > 100\%$.
2. **Thermal Spike Filter:** Reject isolated temperature jumps $> 4.0^\circ\text{C}$ across a single 15-minute interval unless accompanied by documented cooking activity or sudden power loss.
3. **Outage Reconciliation:** Match timestamps against CSPDCL 11 kV substation trip records to isolate forced heat accumulation during grid blackout hours.

---

## 8. Integration with AGNAYA Calibration Engine

Field data is directly processed by [`models/indoor_calibration.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/indoor_calibration.py):

1. **Baseline Model Evaluation:**
   Calculates MAE, RMSE, and Mean Bias Error (MBE) of the uncalibrated TAPAS formulation against measured ground truth.
2. **Parameter Optimization:**
   Optimizes $\theta = [\beta_0, \beta_{\text{roof}}, \beta_{\text{canopy}}, \theta_{\text{cap}}, \theta_{\text{rate}}]$ via robust bounded least squares:
   $$T_{\text{indoor}} = T_{\text{ambient}} + \beta_0 + \beta_{\text{roof}} \cdot w_{\text{roof}} - \beta_{\text{canopy}} \cdot \kappa_{\text{green}} + \min(\theta_{\text{cap}}, \theta_{\text{rate}} \cdot t_{\text{outage}})$$
3. **Production Model Update:**
   Updates [`data/raipur_data.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/data/raipur_data.py) and [`data/DATA_SOURCES.csv`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/data/DATA_SOURCES.csv), elevating parameter statuses from `ASSUMED` to `VERIFIED (FIELD PILOT)`.

---

## 9. Regulatory & Ethical Disclaimer

> **SIMULATION & RESEARCH PLANNING ONLY:**  
> This protocol is designed solely for empirical research and scientific validation of urban heat vulnerability tools. It does not constitute a municipal directive, regulatory mandate, or medical surveillance system. All field implementations require local ethical clearance and voluntary consent from participating residents.

