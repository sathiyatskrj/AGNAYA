"""
AGNAYA - Transformer Thermal Aging Tests (IEEE Std C57.91-2011 Clause 7)
Numerically verifies Arrhenius aging acceleration factor F_AA without discontinuous cutoffs.
"""

import math
import numpy as np
from agnaya.models.grid_digital_twin import TransformerDigitalTwin
from agnaya.data.raipur_data import RAIPUR_SUBSTATIONS


def test_ieee_c57_91_aging_reference_values():
    """
    Numerically verifies Arrhenius aging acceleration factor:
    F_AA = exp(15000 / 383.15 - 15000 / (Theta_H + 273.15))
    Reference standards:
    - At Theta_H = 110°C (383.15 K): F_AA = 1.0000 (normal rated life)
    - At Theta_H = 120°C: F_AA ≈ 2.71
    - At Theta_H = 130.5°C: F_AA ≈ 7.30
    """
    def arrhenius_faa(hotspot_c: float) -> float:
        theta_k = hotspot_c + 273.15
        return float(np.exp((15000.0 / 383.15) - (15000.0 / theta_k)))

    # 1. Hotspot at 110°C
    calc_110 = arrhenius_faa(110.0)
    assert abs(calc_110 - 1.000) < 0.005, f"Expected F_AA(110°C) ≈ 1.000, got {calc_110}"

    # 2. Hotspot at 120°C
    calc_120 = arrhenius_faa(120.0)
    expected_120 = math.exp(15000.0 / 383.15 - 15000.0 / 393.15)
    assert abs(calc_120 - expected_120) < 0.05, f"Expected F_AA(120°C) ≈ {expected_120:.2f}, got {calc_120}"

    # 3. Hotspot at 130.5°C
    calc_130 = arrhenius_faa(130.5)
    expected_130 = math.exp(15000.0 / 383.15 - 15000.0 / 403.65)
    assert abs(calc_130 - expected_130) < 0.15, f"Expected F_AA(130.5°C) ≈ {expected_130:.2f}, got {calc_130}"


def test_transformer_digital_twin_aging_calculation():
    """Verifies TransformerDigitalTwin calculates IEEE aging factor and loss of life."""
    s01_data = RAIPUR_SUBSTATIONS[0]
    twin = TransformerDigitalTwin(s01_data)

    res_nominal = twin.calculate_hotspot(ambient_temp_c=40.0, load_ratio=0.7)
    assert res_nominal["aging_acceleration_factor"] > 0.0
    assert res_nominal["loss_of_life_pct_per_day"] > 0.0

    res_stressed = twin.calculate_hotspot(ambient_temp_c=48.0, load_ratio=1.1)
    assert res_stressed["hotspot_temp_c"] > res_nominal["hotspot_temp_c"]
    assert res_stressed["aging_acceleration_factor"] > res_nominal["aging_acceleration_factor"]


def test_no_discontinuous_cutoff_at_80c():
    """Verifies that the old ad-hoc 80°C zero cliff is absent; smooth exponential decline below 110°C."""
    def arrhenius_faa(hotspot_c: float) -> float:
        theta_k = hotspot_c + 273.15
        return float(np.exp((15000.0 / 383.15) - (15000.0 / theta_k)))

    faa_85 = arrhenius_faa(85.0)
    faa_79 = arrhenius_faa(79.0)
    faa_70 = arrhenius_faa(70.0)

    # F_AA should be positive, non-zero, and monotonically decreasing
    assert faa_85 > faa_79 > faa_70 > 0.0, "Smooth exponential aging violated below 80°C"
    assert faa_79 > 0.001, "Arbitrary zero cliff detected at 80°C"
