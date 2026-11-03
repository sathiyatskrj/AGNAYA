# Security Policy & Model Provenance

## 1. Supported Versions

| Version | Supported | Status |
| :--- | :---: | :--- |
| **3.1.x** | :white_check_mark: | Active Security Hardened Baseline |
| 3.0.x | :warning: | Deprecated (Exposed hard-coded key removed in v3.1) |
| < 3.0 | :x: | Unsupported |

---

## 2. Security Incident Disclosure & Key Revocation (P0 Mandatory Action)

### Vulnerability Summary
A third-party CARTO API key (`cb1_4luv_1_702fe094ac8114d4005f2fa3`) was previously committed in plain text in git commit `164051c` within `app.py` and returned publicly via `api.py`.

### Actions Required by Repository Administrator:
1. **Immediate Revocation**: Log in to your CARTO dashboard, revoke `cb1_4luv_1_702fe094ac8114d4005f2fa3`, and generate a new key restricted by HTTP Referrer / Domain.
2. **Keyless Operation**: As of v3.1, AGNAYA automatically falls back to keyless OpenStreetMap and CartoDB Positron / Dark Matter tiles. No secret key is required for full map functionality.
3. **Scrub Git History**: Because git commit history retains deleted lines, execute the following commands on a secure administrative clone to permanently scrub the exposed credential:

```bash
# 1. Install git-filter-repo (if not already installed)
pip install git-filter-repo

# 2. Create a replacement mapping file
echo "cb1_4luv_1_702fe094ac8114d4005f2fa3==>REDACTED_CARTO_KEY" > replace.txt

# 3. Rewrite git history to sanitize the exposed string
git filter-repo --replace-text replace.txt

# 4. Verify working tree and force-push to remote (Coordinate with your team first)
git push origin --force --all
git push origin --force --tags
```
*(Do not run destructive git commands on an active shared branch without team coordination.)*

---

## 3. Microservice Security & Attack Surface Controls

1. **Default Localhost Binding**:
   - `RUN_API.bat` and FastAPI launcher bind to `127.0.0.1` by default, preventing unintended network exposure on local LANs or public Wi-Fi.
2. **Strict CORS Policy**:
   - Wildcard origins with credentials (`allow_origins=["*"]`, `allow_credentials=True`) are disabled. Explicit allowed origins are loaded from `config.py` (`settings.CORS_ORIGINS`).
3. **Pydantic Schema Validation**:
   - Every input parameter (ambient temperature, duration, demand, outage hours, budget, wind speed) enforces explicit numeric bounds (`ge`, `le`) to eliminate buffer overflow, denial of service, and negative values.
4. **Rate Limiting & Error Sanitization**:
   - An in-memory sliding-window rate limiter throttles clients exceeding 120 requests/minute.
   - Global exception handling blocks internal filesystem paths and stack traces from leaking in HTTP 500 responses.
5. **Continuous Secret Scanning**:
   - `.github/workflows/ci.yml` includes an automated `gitleaks` job to reject commits containing secrets or private tokens.

---

## 4. Third-Party Dependency Licenses

All dependencies in `requirements.txt` are verified compatible under permissive open-source licenses:

| Package | Version Baseline | License | Permitted for Open Evaluation |
| :--- | :--- | :--- | :---: |
| `fastapi` | $\ge 0.100.0$ | MIT | :white_check_mark: |
| `pydantic` | $\ge 2.7.0$ | MIT | :white_check_mark: |
| `pydantic-settings` | $\ge 2.0.0$ | MIT | :white_check_mark: |
| `python-dotenv` | $\ge 1.0.0$ | BSD-3-Clause | :white_check_mark: |
| `uvicorn` | $\ge 0.22.0$ | BSD-3-Clause | :white_check_mark: |
| `streamlit` | $\ge 1.28.0$ | Apache 2.0 | :white_check_mark: |
| `numpy` | $\ge 1.24.0$ | BSD-3-Clause | :white_check_mark: |
| `pandas` | $\ge 2.0.0$ | BSD-3-Clause | :white_check_mark: |
| `scipy` | $\ge 1.11.0$ | BSD-3-Clause | :white_check_mark: |
| `networkx` | $\ge 3.2$ | BSD-3-Clause | :white_check_mark: |
| `plotly` | $\ge 5.18.0$ | MIT | :white_check_mark: |
| `folium` | $\ge 0.15.0$ | MIT | :white_check_mark: |
| `streamlit-folium` | $\ge 0.15.0$ | MIT | :white_check_mark: |

*(Note: Unused dependencies `pdfplumber`, `matplotlib`, and `pulp` were removed to minimize attack surface.)*

---

## 5. Model Code Provenance: Original vs. Adapted

To maintain academic and open-source integrity, every module in AGNAYA carries an explicit provenance status:

| Module | Core Functionality | Status | Attribution & Reference |
| :--- | :--- | :---: | :--- |
| [`data/raipur_data.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/data/raipur_data.py) | Raipur grid, water & hospital parameters | **Adapted / Compiled** | Grounded in CSERC FY24-25 Tariff Order & Census of India 2011. |
| [`models/cascade_model.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/cascade_model.py) | Demand ODE & NetworkX dependency graph | **Original** | Built for Raipur inter-infrastructure cascade modeling. |
| [`models/grid_digital_twin.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/grid_digital_twin.py) | Transformer thermal digital twin (IEEE C57.91) | **Adapted** | Adapted from `parisproffitt/GridStressDigitalTwin` (MIT License). |
| [`models/conductor_ampacity.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/conductor_ampacity.py) | Overhead line thermal rating (IEEE 738) | **Adapted** | Adapted from `emliang/Heat-Analysis` (MIT License). |
| [`models/tapas_health.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/tapas_health.py) | HTSI & Tin-roof heat entrapment | **Adapted** | Adapted from `Nihita49/TAPAS` (SIH 2026 Winner). |
| [`models/agents_pipeline.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/agents_pipeline.py) | 3-Stage multi-objective resource dispatch (HiGHS) | **Adapted** | Workflow concepts adapted from `kd365/heatwave-public` (MIT License). |
| [`models/climate_analytics.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/climate_analytics.py) | Gumbel EVT & NWS heat index | **Adapted** | Adapted from `nabilkhondaker/ClimateSim` (MIT License). |
| [`models/grid_power_flow.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/grid_power_flow.py) | DC Power Flow ($P = B\theta$) & Catenary sag | **Adapted** | Adapted from `nabilkhondaker/ClimateSim` & `emliang/Heat-Analysis`. |
| [`models/progressive_heatwave.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/progressive_heatwave.py) | 7-Stage heatwave progression | **Adapted** | Adapted from `parisproffitt/GridStressDigitalTwin`. |
| [`models/system_resilience.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/system_resilience.py) | Continuous resilience curves $Q(t)$ & AUC loss | **Adapted** | Synthesizes formulations from `nabilkhondaker/ClimateSim`. |
| [`models/gridpulse_risk.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/gridpulse_risk.py) | 5-Component risk decomposition & audit cards | **Adapted** | Adapted from `doaamostafa67988/GridPulse-AI`. |
| [`models/trilingual_alerts.py`](file:///C:/Users/Bhumika%20Baghel/.gemini/antigravity-ide/scratch/AGNAYA/models/trilingual_alerts.py) | English, Hindi & Chhattisgarhi warning generation | **Original** | Developed for Raipur disaster response compliance with NDMA / IMD criteria. |

---

## 6. Reporting a Vulnerability

If you discover a security vulnerability or sensitive data exposure issue, please do **NOT** open a public issue.

Email the response team at: **tkrishnamoorthytskrj@gmail.com**

Please include:
- A description of the vulnerability and its potential operational impact.
- Step-by-step instructions or proof-of-concept scripts to reproduce the behavior.
- Any suggested mitigations.
