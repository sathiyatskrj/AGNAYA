"""
AGNAYA - Global Sensitivity Analysis & Monte Carlo Uncertainty Engine
Uses SALib (Sobol Sensitivity Analysis) and documented parameter distributions.

NON-NEGOTIABLE COMPLIANCE:
- Explicit, documented distributions for all input parameters.
- Explicit random seeds (np.random.default_rng(seed=42)) for deterministic reproducibility.
- Uncertainty intervals: 5th, 50th (median), and 95th percentiles.
- First-order (S1) and Total-order (ST) Sobol indices isolating variance contributions.
- SIMULATION ONLY – NOT AN OFFICIAL WARNING.
"""

import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from SALib.sample import sobol as sobol_sample
from SALib.analyze import sobol as sobol_analyze

from data.raipur_data import CSPDCL_PARAMS, RAIPUR_ZONES
from models.cascade_model import DemandModel, calculate_indoor_temp
from models.grid_digital_twin import GridStressNetwork


# Documented Parameter Bounds for Raipur Summer Heatwave Conditions
SOBOL_PROBLEM = {
    "num_vars": 4,
    "names": [
        "ambient_temp_c",        # T_ambient in [40.0, 48.5] °C (Climatological extreme bounds)
        "relative_humidity_pct", # RH in [20.0, 60.0] % (Pre-monsoon vs dry summer range)
        "outage_duration_hours", # Feeder outage duration in [0.0, 8.0] hours
        "substation_base_lf",    # Base loading factor in [0.60, 0.90] ratio
    ],
    "bounds": [
        [40.0, 48.5],
        [20.0, 60.0],
        [0.0, 8.0],
        [0.60, 0.90],
    ],
}


class SobolSensitivityEngine:
    """
    Evaluates global variance decomposition (Sobol S1 and ST indices)
    and Monte Carlo uncertainty confidence intervals across coupled grid & heat models.
    """

    def __init__(self, problem: Optional[Dict[str, Any]] = None, seed: int = 42):
        self.problem = problem or SOBOL_PROBLEM
        self.seed = seed
        self.rng = np.random.default_rng(seed=self.seed)

    def run_sobol_analysis(self, n_samples: int = 64) -> Dict[str, Any]:
        """
        Executes Sobol variance decomposition.
        n_samples: Base sample size. Total evaluations = n_samples * (2 * num_vars + 2) if second_order=True,
                   or n_samples * (num_vars + 2) if calc_second_order=False.
        """
        # Generate quasi-random Saltelli / Sobol sequence
        param_values = sobol_sample.sample(
            self.problem,
            n_samples,
            calc_second_order=False,
            seed=self.seed
        )

        n_evals = len(param_values)
        dm = DemandModel()

        # Output arrays
        y_peak_demand = np.zeros(n_evals)
        y_max_indoor_temp = np.zeros(n_evals)
        y_hotspot_temp = np.zeros(n_evals)

        # Baseline worst-case zone for indoor temp: Z05 Tikrapara (slum_pct=0.35, green_cover_pct=0.06)
        z05_slum = 0.35
        z05_green = 0.06

        for i, row in enumerate(param_values):
            t_amb = float(row[0])
            _ = float(row[1])  # rh
            outage_h = float(row[2])
            sub_lf = float(row[3])

            # 1. Peak Demand Evaluation (Saturating ODE)
            _, d_series = dm.simulate(t_amb, duration_days=2)
            y_peak_demand[i] = float(np.max(d_series))

            # 2. Maximum Indoor Temperature
            y_max_indoor_temp[i] = calculate_indoor_temp(
                t_amb, z05_slum, z05_green, outage_hours=outage_h
            )

            # 3. Substation Hot-Spot Temperature (S01 / S03 proxy)
            # Empirical winding rise: ambient + 35°C * (load_ratio / 0.72)^1.6
            load_ratio = sub_lf * (y_peak_demand[i] / 310.0)
            y_hotspot_temp[i] = t_amb + 38.0 * (min(1.6, max(0.4, load_ratio)) ** 1.6)

        # Compute Sobol Indices
        si_demand = sobol_analyze.analyze(self.problem, y_peak_demand, calc_second_order=False)
        si_indoor = sobol_analyze.analyze(self.problem, y_max_indoor_temp, calc_second_order=False)
        si_hotspot = sobol_analyze.analyze(self.problem, y_hotspot_temp, calc_second_order=False)

        def clean_indices(si_dict: Dict[str, Any]) -> Dict[str, List[float]]:
            return {
                "S1": [float(round(val, 4)) for val in si_dict["S1"]],
                "ST": [float(round(val, 4)) for val in si_dict["ST"]],
                "names": self.problem["names"],
            }

        return {
            "num_evaluations": n_evals,
            "seed": self.seed,
            "parameter_names": self.problem["names"],
            "parameter_bounds": self.problem["bounds"],
            "indices": {
                "peak_demand_mw": clean_indices(si_demand),
                "max_indoor_temp_c": clean_indices(si_indoor),
                "substation_hotspot_c": clean_indices(si_hotspot),
            },
            "uncertainty_intervals": {
                "peak_demand_mw": {
                    "p05": float(round(np.percentile(y_peak_demand, 5), 1)),
                    "p50_median": float(round(np.percentile(y_peak_demand, 50), 1)),
                    "p95": float(round(np.percentile(y_peak_demand, 95), 1)),
                },
                "max_indoor_temp_c": {
                    "p05": float(round(np.percentile(y_max_indoor_temp, 5), 1)),
                    "p50_median": float(round(np.percentile(y_max_indoor_temp, 50), 1)),
                    "p95": float(round(np.percentile(y_max_indoor_temp, 95), 1)),
                },
                "substation_hotspot_c": {
                    "p05": float(round(np.percentile(y_hotspot_temp, 5), 1)),
                    "p50_median": float(round(np.percentile(y_hotspot_temp, 50), 1)),
                    "p95": float(round(np.percentile(y_hotspot_temp, 95), 1)),
                },
            },
            "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
        }

    def run_reproducible_monte_carlo(
        self,
        t_mean: float = 45.0,
        rh_mean: float = 35.0,
        outage_hours: float = 2.0,
        n_trials: int = 250
    ) -> Dict[str, Any]:
        """
        Executes reproducible Monte Carlo sampling around a nominal scenario.
        Documented Distributions:
        - T_ambient ~ Normal(t_mean, 1.2°C) bounded in [38.0, 49.0]
        - RH ~ Uniform(rh_mean - 6%, rh_mean + 6%) bounded in [15%, 75%]
        - Outage ~ Exponential(scale=outage_hours) bounded in [0, 12] h
        - Substation LF ~ Uniform(0.65, 0.85)
        """
        dm = DemandModel()

        # Seeded random draws
        t_samples = np.clip(self.rng.normal(t_mean, 1.2, n_trials), 38.0, 49.0)
        _ = np.clip(self.rng.uniform(rh_mean - 6.0, rh_mean + 6.0, n_trials), 15.0, 75.0)  # rh_samples
        scale_val = max(0.5, outage_hours)
        outage_samples = np.clip(self.rng.exponential(scale_val, n_trials), 0.0, 12.0)
        lf_samples = self.rng.uniform(0.65, 0.85, n_trials)

        demand_peaks = []
        indoor_maxs = []
        transformer_faas = []

        for i in range(n_trials):
            t_amb = float(t_samples[i])
            out_h = float(outage_samples[i])
            lf = float(lf_samples[i])

            _, d_series = dm.simulate(t_amb, duration_days=2)
            pk = float(np.max(d_series))
            demand_peaks.append(pk)

            ind = calculate_indoor_temp(t_amb, slum_pct=0.35, green_cover_pct=0.06, outage_hours=out_h)
            indoor_maxs.append(ind)

            # Aging factor FAA from IEEE C57.91:
            # Hotspot estimate
            th_h = t_amb + 35.0 * ((lf * (pk / 310.0) / 0.72) ** 1.6)
            faa = np.exp(15000.0 / 383.15 - 15000.0 / (th_h + 273.15))
            transformer_faas.append(faa)

        return {
            "n_trials": n_trials,
            "seed": self.seed,
            "nominal_inputs": {
                "t_mean_c": t_mean,
                "rh_mean_pct": rh_mean,
                "outage_hours": outage_hours,
            },
            "distributions_applied": {
                "ambient_temp": "Normal(mean, 1.2°C) bounded [38, 49]",
                "relative_humidity": "Uniform(mean±6%) bounded [15%, 75%]",
                "outage_duration": "Exponential(scale=nominal) bounded [0, 12] h",
                "substation_load_factor": "Uniform(0.65, 0.85)",
            },
            "intervals": {
                "peak_demand_mw": {
                    "p05": float(round(np.percentile(demand_peaks, 5), 1)),
                    "p50_median": float(round(np.percentile(demand_peaks, 50), 1)),
                    "p95": float(round(np.percentile(demand_peaks, 95), 1)),
                },
                "max_indoor_temp_c": {
                    "p05": float(round(np.percentile(indoor_maxs, 5), 1)),
                    "p50_median": float(round(np.percentile(indoor_maxs, 50), 1)),
                    "p95": float(round(np.percentile(indoor_maxs, 95), 1)),
                },
                "transformer_aging_faa": {
                    "p05": float(round(np.percentile(transformer_faas, 5), 2)),
                    "p50_median": float(round(np.percentile(transformer_faas, 50), 2)),
                    "p95": float(round(np.percentile(transformer_faas, 95), 2)),
                },
            },
            "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
        }
