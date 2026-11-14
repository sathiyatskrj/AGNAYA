# %% [markdown]
"""
# AGNAYA: Indoor Temperature Microclimate Calibration & Validation
# Raipur Municipal Corporation & CSPDCL Planning Prototype
#
# MANDATORY DISCLAIMER:
# SIMULATION ONLY – NOT AN OFFICIAL WARNING.
# The data analyzed in this demonstration notebook is SYNTHETIC SAMPLE DATA
# designed for validating the calibration pipeline ahead of physical sensor deployment.
# See docs/PILOT.md for the ground-truth field protocol.
"""

# %%
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Ensure root workspace is in import path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from models.indoor_calibration import IndoorLoggerValidationEngine, ROOF_MATERIAL_FACTORS
from data.raipur_data import RAIPUR_ZONES

print("AGNAYA Validation Harness Initialized.")
print(f"Base Directory: {BASE_DIR}")

# %% [markdown]
"""
## 1. Load Synthetic Logger Dataset
The dataset records 384 hourly readings across 8 households in 4 vulnerable Raipur zones:
- Birgaon Industrial Belt (Z01): High slum density, corrugated galvanized iron (CGI) tin roofs.
- Gudhiyari (Z08): Mixed settlement, tin and asbestos cement roofing.
- Tikrapara (Z05): High density informal settlement, tin and pucca concrete control.
- Urla Industrial Area (Z04): Heavy industrial boundary, tin and clay tile dwellings.
"""

# %%
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_indoor_loggers.csv")
engine = IndoorLoggerValidationEngine()
df_loggers = engine.load_logger_data(DATA_PATH)

print(f"Successfully ingested {len(df_loggers)} observations.")
print("\nDataset Summary by Roof Type:")
summary_by_roof = df_loggers.groupby("roof_type").agg(
    n_houses=("house_id", "nunique"),
    n_obs=("temp_c", "count"),
    mean_indoor_t=("temp_c", "mean"),
    max_indoor_t=("temp_c", "max"),
    mean_rh=("rh", "mean")
).round(2)
print(summary_by_roof)

# %% [markdown]
"""
## 2. Baseline Model Evaluation (TAPAS Default Formulation)
Default TAPAS empirical formula:
$$T_{\\text{indoor}} = T_{\\text{ambient}} + 4.0 \\times \\kappa_{\\text{slum}} - 4.0 \\times \\kappa_{\\text{green}} + \\min(6.5, 0.8 \\times t_{\\text{outage}})$$
Status: ASSUMED / UNCALIBRATED.
"""

# %%
baseline_eval = engine.evaluate_model(df_loggers)

print("=" * 60)
print("BASELINE MODEL ERROR METRICS (UNCALIBRATED):")
print(f"  Mean Absolute Error (MAE):    {baseline_eval['mae']:.3f} °C")
print(f"  Root Mean Square Error (RMSE): {baseline_eval['rmse']:.3f} °C")
print(f"  Mean Bias Error (MBE/Bias):   {baseline_eval['mean_bias_error']:+.3f} °C")
print(f"  R² Goodness of Fit:           {baseline_eval['r2_score']:.3f}")
print("=" * 60)

print("\nBaseline Error Breakdown by Roof Material:")
for roof, stats in baseline_eval["by_roof_type"].items():
    print(f"  {roof:<16}: MAE = {stats['mae']:.2f} °C | RMSE = {stats['rmse']:.2f} °C | Bias = {stats['bias']:+.2f} °C (n={stats['count']})")

# %% [markdown]
"""
## 3. Parameter Calibration (Robust Bounded Optimization)
We calibrate the parametric formulation using SciPy `least_squares` with Cauchy loss:
$$T_{\\text{indoor}} = T_{\\text{ambient}} + \\beta_0 + \\beta_{\\text{roof}} \\cdot w_{\\text{roof}} - \\beta_{\\text{canopy}} \\cdot \\kappa_{\\text{green}} + \\min(\\theta_{\\text{cap}}, \\theta_{\\text{rate}} \\cdot t_{\\text{outage}})$$
"""

# %%
cal_results = engine.calibrate(df_loggers, loss="cauchy")

print("=" * 60)
print("CALIBRATION RESULTS (OPTIMIZED PARAMETERS):")
for param, val in cal_results["calibrated_parameters"].items():
    print(f"  {param:<24}: {val:.3f}")

print("\nCALIBRATED MODEL ERROR METRICS:")
print(f"  Mean Absolute Error (MAE):    {cal_results['calibrated_metrics']['mae']:.3f} °C (Reduction: {cal_results['improvement_pct']['mae_reduction_pct']}%)")
print(f"  Root Mean Square Error (RMSE): {cal_results['calibrated_metrics']['rmse']:.3f} °C (Reduction: {cal_results['improvement_pct']['rmse_reduction_pct']}%)")
print(f"  Mean Bias Error (MBE/Bias):   {cal_results['calibrated_metrics']['mean_bias_error']:+.3f} °C")
print(f"  R² Goodness of Fit:           {cal_results['calibrated_metrics']['r2_score']:.3f}")
print("=" * 60)

print("\nCalibrated Error Breakdown by Roof Material:")
for roof, stats in cal_results["by_roof_type"].items():
    print(f"  {roof:<16}: MAE = {stats['mae']:.2f} °C | RMSE = {stats['rmse']:.2f} °C | Bias = {stats['bias']:+.2f} °C")

# %% [markdown]
"""
## 4. Residual Distribution Analysis
Examines the residual distribution (Predicted - Observed) before and after calibration.
"""

# %%
res_base = np.array(baseline_eval["residuals"])
res_cal = np.array(cal_results["calibrated_metrics"]["mae"])  # summary

print("\nResidual Distribution Statistics:")
print(f"  Baseline 10th-90th Percentile:  [{np.percentile(res_base, 10):.2f}, {np.percentile(res_base, 90):.2f}] °C")
print(f"  Baseline Max Absolute Residual: {baseline_eval['max_abs_error']:.2f} °C")

# %% [markdown]
"""
## 5. Summary & Next Steps for Field Deployment
1. **Verification**: The calibration harness successfully ingests standardized logger CSVs, handles outliers, and converges via robust least squares.
2. **Synthetic Boundary**: The current demonstration utilizes SYNTHETIC sample data (`data/sample_indoor_loggers.csv`).
3. **Operational Transition**: Prior to publishing calibrated coefficients as statutory planning thresholds, field loggers must be physically deployed in 5–10 tin-roof dwellings in accordance with `docs/PILOT.md`.
"""

if __name__ == "__main__":
    print("\nCalibration analysis notebook executed successfully.")
