"""
AGNAYA V3.0 - Continuous Infrastructure Resilience Curves & AUC Loss Engine
Tracks Lifeline Performance Q(t), Nadir Q_min, Time-to-Degradation, and AUC Resilience Loss.
Coupled with the physics-grounded saturating DemandModel ODE.

DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
Comparative simulation model for decision support and planning analysis only.
"""

import numpy as np
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.raipur_data import (
    RAIPUR_WATER_PUMPS,
    RAIPUR_HOSPITALS, CSPDCL_PARAMS
)
from models.cascade_model import DemandModel


class SystemResilienceEngine:
    """
    Computes continuous lifeline resilience trajectories Q(t) over a multi-day heatwave:
        Q(t) = 0.45 * Q_power(t) + 0.30 * Q_water(t) + 0.25 * Q_health(t)

    Evaluates:
      - Lifeline Loss (AUC Loss in Lifeline Deficit Hours):
            AUC_loss = integral_0^T [ 1.0 - Q(t) ] dt
      - Disruption Hours Saved:
            Delta_AUC = AUC_loss_base - AUC_loss_shield
      - Resilience Improvement Dividend (%):
            (Delta_AUC / AUC_loss_base) * 100%
      - Minimum performance nadir Q_min
      - Time-to-minimum nadir t_deg
    """
    def __init__(self):
        self.normal_mw = CSPDCL_PARAMS["raipur_normal_demand_mw"]     # 310 MW
        self.peak_cap_mw = CSPDCL_PARAMS["raipur_peak_demand_mw"]      # 420 MW contracted statutory limit
        self.emergency_cap_mw = CSPDCL_PARAMS.get("raipur_emergency_cap_mw", 620.0)
        self.total_hosp_beds = sum(h["emergency_capacity"] for h in RAIPUR_HOSPITALS)
        self.total_pumps = len(RAIPUR_WATER_PUMPS)
        self.demand_model = DemandModel()

    def evaluate_resilience_curves(
        self,
        ambient_peak_c: float,
        duration_days: int = 5,
        n_points: int = 72,
        with_interventions: bool = True,
    ) -> Dict[str, Any]:
        """
        Simulates continuous lifeline operation over the specified duration,
        comparing Baseline (unshielded) vs. Shielded (AGNAYA interventions).
        Uses exact unrounded numerical integration.
        """
        hours = np.linspace(0, duration_days * 24, n_points)

        # Diurnal thermal curve
        diurnal_variation = 6.5
        t_amb_series = ambient_peak_c - diurnal_variation * (1.0 + np.sin((hours - 9.0) * np.pi / 12.0)) / 2.0

        # Coupled Demand trajectory from saturating ODE
        t_sim, d_sim = self.demand_model.simulate(
            T_peak_celsius=ambient_peak_c,
            duration_days=duration_days,
            dt_hours=1.0
        )
        demand_mw = np.interp(hours, t_sim, d_sim)

        # ── 1. BASELINE RUN (Zero Interventions)
        q_power_base = []
        q_water_base = []
        q_health_base = []
        q_composite_base = []

        # ── 2. SHIELDED RUN (AGNAYA Interventions Activated)
        q_power_shield = []
        q_water_shield = []
        q_health_shield = []
        q_composite_shield = []

        for h, t, d in zip(hours, t_amb_series, demand_mw):
            # BASELINE: Power delivery throttles when demand > contracted peak capacity (420 MW)
            shortfall_b = max(0.0, d - self.peak_cap_mw)
            p_ratio_b = max(0.20, (d - shortfall_b * 1.35) / max(1.0, d))
            # Water: without backup power, pumps trip when power throttled
            w_ratio_b = max(0.15, p_ratio_b * 0.95)
            # Health: emergency admissions stress ER bed capacity
            excess_er_b = max(0.0, (t - 40.0) * 12.0 + (1.0 - p_ratio_b) * 60.0)
            h_ratio_b = max(0.10, 1.0 - (excess_er_b / max(1.0, self.total_hosp_beds)))

            comp_b = 0.45 * p_ratio_b + 0.30 * w_ratio_b + 0.25 * h_ratio_b
            q_power_base.append(float(p_ratio_b))
            q_water_base.append(float(w_ratio_b))
            q_health_base.append(float(h_ratio_b))
            q_composite_base.append(float(comp_b))

            # SHIELDED: Mobile DG sets boost capacity (+65 MW) + water tankers + cooling shelters
            cap_shielded = self.peak_cap_mw + 65.0
            shortfall_s = max(0.0, d - cap_shielded)
            p_ratio_s = min(1.0, max(0.65, (d - shortfall_s * 0.40) / max(1.0, d)))
            # Water tanker fleet maintains water delivery
            w_ratio_s = min(1.0, max(0.70, p_ratio_s * 0.98))
            # Hospital surge tents and cooling shelters absorb excess heat illness
            excess_er_s = excess_er_b * 0.42
            h_ratio_s = min(1.0, max(0.60, 1.0 - (excess_er_s / (self.total_hosp_beds * 1.35))))

            comp_s = min(1.0, max(0.0, 0.45 * p_ratio_s + 0.30 * w_ratio_s + 0.25 * h_ratio_s))
            q_power_shield.append(float(p_ratio_s))
            q_water_shield.append(float(w_ratio_s))
            q_health_shield.append(float(h_ratio_s))
            q_composite_shield.append(float(comp_s))

        # Numerical trapezoidal integration on unrounded series
        # NumPy 2.0+ uses np.trapezoid; older uses np.trapz
        trap_func = getattr(np, 'trapezoid', getattr(np, 'trapz', None))
        if trap_func is not None:
            auc_loss_base = float(trap_func(1.0 - np.array(q_composite_base), hours))
            auc_loss_shield = float(trap_func(1.0 - np.array(q_composite_shield), hours))
        else:
            dt = hours[1] - hours[0]
            auc_loss_base = float(np.sum((1.0 - np.array(q_composite_base)) * dt))
            auc_loss_shield = float(np.sum((1.0 - np.array(q_composite_shield)) * dt))

        # Consistent arithmetic from identical unrounded values
        disruption_hours_saved = max(0.0, auc_loss_base - auc_loss_shield)
        resilience_gain_pct = (disruption_hours_saved / max(1e-5, auc_loss_base)) * 100.0

        # Critical indices
        q_min_base = float(np.min(q_composite_base))
        q_min_shield = float(np.min(q_composite_shield))
        t_nadir_base = float(hours[int(np.argmin(q_composite_base))])
        t_nadir_shield = float(hours[int(np.argmin(q_composite_shield))])

        return {
            "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
            "metric_definition": "Lifeline Loss (Deficit Hours) = integral_0^T [ 1.0 - Q(t) ] dt across power (45%), water (30%), and health (25%) lifelines.",
            "hours": [round(float(v), 1) for v in hours],
            "ambient_temp_c": [round(float(v), 1) for v in t_amb_series],
            "demand_mw": [round(float(v), 1) for v in demand_mw],
            "baseline": {
                "q_composite": [round(v, 3) for v in q_composite_base],
                "q_power": [round(v, 3) for v in q_power_base],
                "q_water": [round(v, 3) for v in q_water_base],
                "q_health": [round(v, 3) for v in q_health_base],
                "auc_loss_hours": round(auc_loss_base, 2),
                "auc_loss_hours_unrounded": auc_loss_base,
                "q_nadir": round(q_min_base, 3),
                "time_to_nadir_h": round(t_nadir_base, 1),
            },
            "shielded": {
                "q_composite": [round(v, 3) for v in q_composite_shield],
                "q_power": [round(v, 3) for v in q_power_shield],
                "q_water": [round(v, 3) for v in q_water_shield],
                "q_health": [round(v, 3) for v in q_health_shield],
                "auc_loss_hours": round(auc_loss_shield, 2),
                "auc_loss_hours_unrounded": auc_loss_shield,
                "q_nadir": round(q_min_shield, 3),
                "time_to_nadir_h": round(t_nadir_shield, 1),
            },
            "disruption_hours_saved": round(disruption_hours_saved, 2),
            "disruption_hours_saved_unrounded": disruption_hours_saved,
            "resilience_gain_pct": round(resilience_gain_pct, 1),
        }

    def compare_resilience_curves(self, peak_temp_c: float, duration_days: int = 3) -> Dict[str, Any]:
        """Provides normalized resilience curve comparison for UI and API."""
        return self.evaluate_resilience_curves(ambient_peak_c=peak_temp_c, duration_days=duration_days)
