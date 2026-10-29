"""
AGNAYA V3.0 - Continuous Infrastructure Resilience Curves & AUC Loss Engine
Synthesizing resilience metrics from ClimateSim (Khondaker)
Tracks Lifeline Performance Q(t), Nadir Q_min, Time-to-Degradation, and AUC Resilience Loss
"""

import numpy as np
from typing import Dict, List, Any
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.raipur_data import RAIPUR_SUBSTATIONS, RAIPUR_ZONES, RAIPUR_WATER_PUMPS, RAIPUR_HOSPITALS, CSPDCL_PARAMS


class SystemResilienceEngine:
    """
    Computes continuous lifeline resilience trajectories Q(t) over a multi-day heatwave:
        Q(t) = 0.45 * Q_power(t) + 0.30 * Q_water(t) + 0.25 * Q_health(t)
    Evaluates:
      - AUC_loss (Area Under the Curve Resilience Loss in Lifeline Deficit Hours)
      - Minimum performance nadir Q_min
      - Time-to-minimum t_deg
      - Recovery time t_rec
    """
    def __init__(self):
        self.normal_mw = CSPDCL_PARAMS["raipur_normal_demand_mw"]  # 310 MW
        self.peak_cap_mw = CSPDCL_PARAMS["raipur_peak_demand_mw"]   # 420 MW
        self.total_hosp_beds = sum(h["emergency_capacity"] for h in RAIPUR_HOSPITALS)
        self.total_pumps = len(RAIPUR_WATER_PUMPS)

    def evaluate_resilience_curves(
        self,
        ambient_peak_c: float,
        duration_days: int = 5,
        n_points: int = 72,
        with_interventions: bool = True,
    ) -> Dict[str, Any]:
        """
        Simulates 72 hours of continuous lifeline operation, comparing Baseline vs. Shielded.
        """
        hours = np.linspace(0, duration_days * 24, n_points)
        
        # Diurnal thermal curve
        diurnal_variation = 6.5
        t_amb_series = ambient_peak_c - diurnal_variation * (1.0 + np.sin((hours - 9) * np.pi / 12.0)) / 2.0

        # Demand series (MW)
        demand_mw = self.normal_mw + (t_amb_series - 35.0) * 18.0 + np.sin((hours - 14) * np.pi / 12.0) * 25.0
        demand_mw = np.clip(demand_mw, self.normal_mw * 0.85, 750.0)

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
            # BASELINE: Power delivery throttles when demand > peak capacity
            shortfall_b = max(0.0, d - self.peak_cap_mw)
            p_ratio_b = max(0.2, (d - shortfall_b * 1.35) / d)
            # Water: without backup, pumps trip when power throttled
            w_ratio_b = max(0.15, p_ratio_b * 0.95)
            # Health: heat stress admissions overload ER beds
            excess_er_b = max(0.0, (t - 40.0) * 12.0 + (1.0 - p_ratio_b) * 60.0)
            h_ratio_b = max(0.1, 1.0 - (excess_er_b / self.total_hosp_beds))

            comp_b = 0.45 * p_ratio_b + 0.30 * w_ratio_b + 0.25 * h_ratio_b
            q_power_base.append(float(p_ratio_b))
            q_water_base.append(float(w_ratio_b))
            q_health_base.append(float(h_ratio_b))
            q_composite_base.append(float(comp_b))

            # SHIELDED: Mobile DG sets boost capacity (+60 MW) + water tankers + cooling shelters
            cap_shielded = self.peak_cap_mw + 65.0
            shortfall_s = max(0.0, d - cap_shielded)
            p_ratio_s = min(1.0, max(0.65, (d - shortfall_s * 0.4) / d))
            # Water tanker fleet maintains water delivery (clamped to 1.0)
            w_ratio_s = min(1.0, max(0.70, p_ratio_s * 0.98))
            # Hospital surge tents and cooling shelters absorb 55% of heatstroke admissions
            excess_er_s = excess_er_b * 0.42
            h_ratio_s = min(1.0, max(0.60, 1.0 - (excess_er_s / (self.total_hosp_beds * 1.35))))

            comp_s = min(1.0, max(0.0, 0.45 * p_ratio_s + 0.30 * w_ratio_s + 0.25 * h_ratio_s))
            q_power_shield.append(float(p_ratio_s))
            q_water_shield.append(float(w_ratio_s))
            q_health_shield.append(float(h_ratio_s))
            q_composite_shield.append(float(comp_s))

        # Trapezoidal numerical integration for AUC Loss (Lifeline Deficit Hours)
        dt = hours[1] - hours[0]
        auc_loss_base = float(np.sum((1.0 - np.array(q_composite_base)) * dt))
        auc_loss_shield = float(np.sum((1.0 - np.array(q_composite_shield)) * dt))
        resilience_gain_pct = min(100.0, max(0.0, round(((auc_loss_base - auc_loss_shield) / max(1e-5, auc_loss_base)) * 100.0, 1)))

        # Critical indices
        q_min_base = float(np.min(q_composite_base))
        q_min_shield = float(np.min(q_composite_shield))
        t_nadir_base = float(hours[int(np.argmin(q_composite_base))])
        t_nadir_shield = float(hours[int(np.argmin(q_composite_shield))])

        return {
            "hours": [round(float(v), 1) for v in hours],
            "ambient_temp_c": [round(float(v), 1) for v in t_amb_series],
            "demand_mw": [round(float(v), 1) for v in demand_mw],
            "baseline": {
                "q_composite": [round(v, 3) for v in q_composite_base],
                "q_power": [round(v, 3) for v in q_power_base],
                "q_water": [round(v, 3) for v in q_water_base],
                "q_health": [round(v, 3) for v in q_health_base],
                "auc_loss_hours": round(auc_loss_base, 1),
                "q_nadir": round(q_min_base, 3),
                "time_to_nadir_h": round(t_nadir_base, 1),
            },
            "shielded": {
                "q_composite": [round(v, 3) for v in q_composite_shield],
                "q_power": [round(v, 3) for v in q_power_shield],
                "q_water": [round(v, 3) for v in q_water_shield],
                "q_health": [round(v, 3) for v in q_health_shield],
                "auc_loss_hours": round(auc_loss_shield, 1),
                "q_nadir": round(q_min_shield, 3),
                "time_to_nadir_h": round(t_nadir_shield, 1),
            },
            "resilience_gain_pct": resilience_gain_pct,
            "disruption_hours_saved": round(max(0.0, auc_loss_base - auc_loss_shield), 1),
        }

    def compare_resilience_curves(self, peak_temp_c: float, duration_days: int = 3) -> Dict[str, Any]:
        """Provides normalized resilience curve comparison for UI and API."""
        ev = self.evaluate_resilience_curves(ambient_peak_c=peak_temp_c, duration_days=duration_days)
        base = ev["baseline"]

        shield = ev["shielded"]
        hrs = ev["hours"]

        b_dict = {
            "time_hours": hrs,
            "Q_t": base["q_composite"],
            "nadir_q": base["q_nadir"],
            "nadir_time_h": base["time_to_nadir_h"],
            "degradation_time_h": base["time_to_nadir_h"],
            "recovery_time_h": float(round(hrs[-1] - base["time_to_nadir_h"], 1)),
            "auc_loss": base["auc_loss_hours"],
            "resilience_index_percent": min(100.0, max(0.0, float(round(float(np.mean(base["q_composite"])) * 100.0, 1)))),
        }

        a_dict = {
            "time_hours": hrs,
            "Q_t": shield["q_composite"],
            "nadir_q": shield["q_nadir"],
            "nadir_time_h": shield["time_to_nadir_h"],
            "degradation_time_h": shield["time_to_nadir_h"],
            "recovery_time_h": float(round(hrs[-1] - shield["time_to_nadir_h"], 1)),
            "auc_loss": shield["auc_loss_hours"],
            "resilience_index_percent": min(100.0, max(0.0, float(round(float(np.mean(shield["q_composite"])) * 100.0, 1)))),
        }

        return {
            "baseline": b_dict,
            "agnaya_shielded": a_dict,
            "shielded": a_dict,
            "loss_reduction_percent": min(100.0, max(0.0, ev["resilience_gain_pct"])),
            "disruption_hours_saved": ev["disruption_hours_saved"],
        }

