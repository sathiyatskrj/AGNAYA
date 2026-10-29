"""
AGNAYA - Climate Analytics & Extreme Value Engine
Inspired by ClimateSim (nabilkhondaker)
Models Extreme Value Theory (EVT), Gumbel return periods, and Heat Index for Raipur, Chhattisgarh.
"""

import numpy as np
from typing import Dict, List, Any


class ClimateAnalyticsEngine:
    """
    Computes climate extremes, return periods, and biometeorological heat indices
    for Raipur based on IMD climatological normals.
    """
    def __init__(self):
        # Gumbel parameters fitted to historical Raipur annual maximum temperatures (1970 - 2024)
        # Location (mu) = 43.1°C, Scale (beta) = 1.25°C
        self.mu = 43.1
        self.beta = 1.25

    def compute_return_period(self, temp_c: float) -> Dict[str, Any]:
        """
        Calculates exceedance probability and return period in years using Gumbel Extreme Value distribution:
            F(x) = exp(-exp(-(x - mu) / beta))
            Return_Period (years) = 1 / (1 - F(x))
        """
        z = (temp_c - self.mu) / self.beta
        cdf = np.exp(-np.exp(-z))
        exceedance_prob = 1.0 - cdf

        if exceedance_prob <= 0.0001:
            return_period_years = 1000.0
        else:
            return_period_years = 1.0 / exceedance_prob

        return {
            "temperature_c": temp_c,
            "annual_exceedance_probability": round(float(exceedance_prob), 4),
            "exceedance_pct": round(float(exceedance_prob) * 100.0, 2),
            "return_period_years": round(float(return_period_years), 1),
            "severity_classification": "HISTORIC_RECORD" if temp_c >= 47.5 else "RARE_EXTREME" if temp_c >= 45.5 else "FREQUENT_HEATWAVE" if temp_c >= 43.5 else "NORMAL_SUMMER"
        }

    def generate_return_period_curve(self) -> List[Dict[str, Any]]:
        """Generates points along the extreme temperature return period curve (40°C to 49°C)."""
        curve = []
        for t in np.arange(41.0, 49.2, 0.5):
            curve.append(self.compute_return_period(round(float(t), 1)))
        return curve

    @staticmethod
    def calculate_nws_heat_index(temp_c: float, relative_humidity_pct: float) -> float:
        """
        Calculates the National Weather Service (NWS) Heat Index via Rothfusz regression.
        Input: Temperature in °C, Relative Humidity in %.
        Output: Apparent temperature in °C.
        """
        # Convert C to F
        T = (temp_c * 9.0 / 5.0) + 32.0
        R = relative_humidity_pct

        # Simple formula first
        hi_f = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (R * 0.094))

        if hi_f >= 80.0:
            # Full Rothfusz regression equation
            hi_f = (
                -42.379
                + 2.04901523 * T
                + 10.14333127 * R
                - 0.22475541 * T * R
                - 0.00683783 * T * T
                - 0.05481717 * R * R
                + 0.00122874 * T * T * R
                + 0.00085282 * T * R * R
                - 0.00000199 * T * T * R * R
            )
            # Adjustments
            if R < 13.0 and 80.0 <= T <= 112.0:
                adj = ((13.0 - R) / 4.0) * np.sqrt((17.0 - abs(T - 95.0)) / 17.0)
                hi_f -= adj
            elif R > 85.0 and 80.0 <= T <= 87.0:
                adj = ((R - 85.0) / 10.0) * ((87.0 - T) / 5.0)
                hi_f += adj

        # Convert back to Celsius
        hi_c = (hi_f - 32.0) * 5.0 / 9.0
        return round(hi_c, 1)
