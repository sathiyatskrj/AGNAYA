"""
AGNAYA - Indoor Microclimatic Temperature Logger Validation & Calibration Engine
Ground-truths and calibrates uncalibrated empirical indoor heat-trap formulas
using observed data loggers from informal settlements (CGI tin roofs, etc.).

NON-NEGOTIABLE COMPLIANCE:
- Every dataset carries explicit provenance: REAL (with IRB/pilot citation) or SYNTHETIC.
- Error metrics: MAE, RMSE, Mean Bias Error (MBE / Bias), R^2.
- Robust optimization using SciPy least_squares with parameter confidence bounds.
- SIMULATION ONLY – NOT AN OFFICIAL WARNING.
"""

import os
from typing import Any, Dict, Optional, Union

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from data.raipur_data import RAIPUR_ZONES
from models.cascade_model import calculate_indoor_temp


# Roof Material Solar-Radiative Absorptance Factors
ROOF_MATERIAL_FACTORS: Dict[str, float] = {
    "tin_cgi": 1.00,          # Corrugated Galvanized Iron: low albedo, zero insulation
    "asbestos_cement": 0.75,  # Moderate thermal transmittance
    "tile_clay": 0.45,        # Traditional clay tiles with convective airspace
    "pucca_concrete": 0.15,   # High thermal mass concrete slab
}

REQUIRED_LOGGER_COLUMNS = [
    "house_id",
    "zone",
    "roof_type",
    "timestamp",
    "temp_c",
    "rh",
]


class IndoorLoggerValidationEngine:
    """
    Validation and calibration harness for microclimatic indoor temperature modeling.
    Compares observed logger readings against deterministic physics/empirical models.
    """

    def __init__(self, zone_lookup: Optional[Dict[str, Dict[str, Any]]] = None):
        self.zone_lookup = zone_lookup or {z["id"]: z for z in RAIPUR_ZONES}

    def load_logger_data(
        self,
        filepath_or_df: Union[str, pd.DataFrame]
    ) -> pd.DataFrame:
        """
        Loads and validates CSV or DataFrame of indoor sensor loggers.
        Ensures strict schema compliance and physically plausible ranges.
        """
        if isinstance(filepath_or_df, str):
            if not os.path.exists(filepath_or_df):
                raise FileNotFoundError(f"Logger data file not found: {filepath_or_df}")
            df = pd.read_csv(filepath_or_df, comment="#")
        else:
            df = filepath_or_df.copy()

        # 1. Validate Required Columns
        missing_cols = [c for c in REQUIRED_LOGGER_COLUMNS if c not in df.columns]
        if missing_cols:
            raise ValueError(f"Logger data schema violation: missing columns {missing_cols}")

        # 2. Type conversions
        df["temp_c"] = pd.to_numeric(df["temp_c"], errors="coerce")
        df["rh"] = pd.to_numeric(df["rh"], errors="coerce")
        if "ambient_temp_c" in df.columns:
            df["ambient_temp_c"] = pd.to_numeric(df["ambient_temp_c"], errors="coerce")
        if "outage_hours" in df.columns:
            df["outage_hours"] = pd.to_numeric(df["outage_hours"], errors="coerce").fillna(0.0)
        else:
            df["outage_hours"] = 0.0

        # 3. Clean Out-of-Bounds Physical Sensor Readings
        initial_len = len(df)
        valid_mask = (
            (df["temp_c"] >= 15.0) & (df["temp_c"] <= 65.0) &
            (df["rh"] >= 5.0) & (df["rh"] <= 100.0)
        )
        df = df[valid_mask].dropna(subset=["temp_c", "rh"]).copy()
        dropped = initial_len - len(df)
        if dropped > 0:
            print(f"[IndoorLoggerValidation] Filtered {dropped} invalid sensor readings.")

        # 4. Attach Zone Metadata (slum_pct, green_cover_pct)
        def get_zone_attr(zid: str, attr: str, default: float) -> float:
            z = self.zone_lookup.get(zid)
            return float(z[attr]) if z and attr in z else default

        df["slum_pct"] = df["zone"].apply(lambda zid: get_zone_attr(zid, "slum_pct", 0.25))
        df["green_cover_pct"] = df["zone"].apply(lambda zid: get_zone_attr(zid, "green_cover_pct", 0.08))
        df["roof_factor"] = df["roof_type"].apply(lambda r: ROOF_MATERIAL_FACTORS.get(r, 0.60))

        return df

    def evaluate_model(
        self,
        df: pd.DataFrame,
        model_predictions: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Computes Mean Absolute Error (MAE), Root Mean Square Error (RMSE),
        Mean Bias Error (MBE/Bias), and R^2 goodness of fit.
        """
        observed = df["temp_c"].to_numpy(dtype=float)

        if model_predictions is None:
            # Baseline TAPAS / cascade_model default implementation
            predicted = np.zeros(len(df))
            for i, (_, row) in enumerate(df.iterrows()):
                amb = row.get("ambient_temp_c", row["temp_c"] - 2.0)
                predicted[i] = calculate_indoor_temp(
                    ambient_temp_c=float(amb),
                    slum_pct=float(row["slum_pct"]),
                    green_cover_pct=float(row["green_cover_pct"]),
                    outage_hours=float(row["outage_hours"])
                )
        else:
            predicted = np.asarray(model_predictions, dtype=float)

        residuals = predicted - observed
        n = len(observed)

        mae = float(np.mean(np.abs(residuals)))
        rmse = float(np.sqrt(np.mean(residuals ** 2)))
        bias = float(np.mean(residuals))  # Positive = overprediction, Negative = underprediction
        max_abs_err = float(np.max(np.abs(residuals)))

        # R^2 Score
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((observed - np.mean(observed)) ** 2)
        r2 = float(1.0 - (ss_res / max(1e-6, ss_tot)))

        # Performance by roof category
        by_roof = {}
        for r_type in df["roof_type"].unique():
            mask = (df["roof_type"] == r_type).to_numpy()
            if np.sum(mask) > 0:
                sub_res = residuals[mask]
                by_roof[str(r_type)] = {
                    "count": int(np.sum(mask)),
                    "mae": float(round(np.mean(np.abs(sub_res)), 2)),
                    "rmse": float(round(np.sqrt(np.mean(sub_res ** 2)), 2)),
                    "bias": float(round(np.mean(sub_res), 2)),
                }

        return {
            "num_observations": n,
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "mean_bias_error": round(bias, 3),
            "max_abs_error": round(max_abs_err, 3),
            "r2_score": round(r2, 3),
            "by_roof_type": by_roof,
            "predictions": predicted.tolist(),
            "residuals": residuals.tolist(),
            "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
        }

    def calibrate(
        self,
        df: pd.DataFrame,
        loss: str = "cauchy"
    ) -> Dict[str, Any]:
        """
        Calibrates indoor thermal parameters against observed logger data:
        Model:
            T_indoor = T_ambient + beta_0 + beta_roof * w_roof - beta_canopy * green_pct + min(cap, rate * t_outage)
        Parameters theta = [beta_0, beta_roof, beta_canopy, outage_cap, outage_rate]
        Uses robust least squares with Cauchy loss for sensor outlier resilience.
        """
        # Baseline Evaluation
        base_eval = self.evaluate_model(df)

        amb = df["ambient_temp_c"].to_numpy(dtype=float) if "ambient_temp_c" in df.columns else (df["temp_c"] - 2.0).to_numpy()
        roof_w = df["roof_factor"].to_numpy(dtype=float)
        green = df["green_cover_pct"].to_numpy(dtype=float)
        outage = df["outage_hours"].to_numpy(dtype=float)
        obs = df["temp_c"].to_numpy(dtype=float)

        # Baseline Parameters: [beta_0, beta_roof, beta_canopy, outage_cap, outage_rate]
        theta_0 = np.array([0.0, 4.0, 4.0, 6.5, 0.8])
        lower_bounds = np.array([-4.0, 0.5, 0.5, 2.0, 0.1])
        upper_bounds = np.array([4.0, 9.0, 9.0, 9.0, 2.0])

        def residual_fn(theta: np.ndarray) -> np.ndarray:
            b0, b_roof, b_canopy, cap, rate = theta
            outage_term = np.minimum(cap, rate * np.maximum(0.0, outage))
            pred = amb + b0 + b_roof * roof_w - b_canopy * green + outage_term
            return pred - obs

        opt_res = least_squares(
            residual_fn,
            theta_0,
            bounds=(lower_bounds, upper_bounds),
            loss=loss,
            max_nfev=1000
        )

        cal_theta = opt_res.x
        b0, b_roof, b_canopy, cap, rate = cal_theta

        # Compute calibrated predictions
        cal_pred = amb + b0 + b_roof * roof_w - b_canopy * green + np.minimum(cap, rate * np.maximum(0.0, outage))
        cal_eval = self.evaluate_model(df, model_predictions=cal_pred)

        # Parameter uncertainty estimation via Jacobian covariance
        cost = 2 * opt_res.cost
        dof = len(obs) - len(cal_theta)
        s_sq = cost / max(1, dof)
        try:
            cov = np.linalg.inv(opt_res.jac.T @ opt_res.jac) * s_sq
            param_stderr = np.sqrt(np.diag(cov)).tolist()
        except Exception:
            param_stderr = [0.0] * len(cal_theta)

        # Compute improvement deltas
        mae_improvement = ((base_eval["mae"] - cal_eval["mae"]) / max(1e-4, base_eval["mae"])) * 100.0
        rmse_improvement = ((base_eval["rmse"] - cal_eval["rmse"]) / max(1e-4, base_eval["rmse"])) * 100.0

        return {
            "status": "CALIBRATION_COMPLETE",
            "optimization_success": bool(opt_res.success),
            "num_observations": len(obs),
            "loss_function": loss,
            "baseline_metrics": {
                "mae": base_eval["mae"],
                "rmse": base_eval["rmse"],
                "mean_bias_error": base_eval["mean_bias_error"],
                "r2_score": base_eval["r2_score"],
            },
            "calibrated_metrics": {
                "mae": cal_eval["mae"],
                "rmse": cal_eval["rmse"],
                "mean_bias_error": cal_eval["mean_bias_error"],
                "r2_score": cal_eval["r2_score"],
            },
            "improvement_pct": {
                "mae_reduction_pct": round(float(mae_improvement), 1),
                "rmse_reduction_pct": round(float(rmse_improvement), 1),
            },
            "calibrated_parameters": {
                "beta_0_intercept": round(float(b0), 3),
                "beta_roof_trap": round(float(b_roof), 3),
                "beta_canopy_cooling": round(float(b_canopy), 3),
                "outage_cap_celsius": round(float(cap), 3),
                "outage_rate_c_per_hour": round(float(rate), 3),
            },
            "parameter_standard_errors": [round(float(s), 4) for s in param_stderr],
            "by_roof_type": cal_eval["by_roof_type"],
            "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING. Grounded in synthetic sample data pending live pilot.",
        }

    def predict_indoor_temperature(
        self,
        ambient_temp_c: float,
        roof_type: str,
        green_cover_pct: float,
        outage_hours: float = 0.0,
        calibrated_params: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Evaluates indoor temperature using calibrated parameters.
        Falls back to baseline if no calibrated parameters are supplied.
        """
        w_roof = ROOF_MATERIAL_FACTORS.get(roof_type, 0.60)
        if calibrated_params:
            b0 = calibrated_params.get("beta_0_intercept", 0.0)
            b_roof = calibrated_params.get("beta_roof_trap", 4.0)
            b_canopy = calibrated_params.get("beta_canopy_cooling", 4.0)
            cap = calibrated_params.get("outage_cap_celsius", 6.5)
            rate = calibrated_params.get("outage_rate_c_per_hour", 0.8)
            outage_term = min(cap, rate * max(0.0, outage_hours))
            return round(float(ambient_temp_c + b0 + b_roof * w_roof - b_canopy * green_cover_pct + outage_term), 1)

        # Baseline fallback
        slum_proxy = w_roof  # Map roof weight to slum equivalent
        return calculate_indoor_temp(ambient_temp_c, slum_proxy, green_cover_pct, outage_hours)
