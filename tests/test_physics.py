"""
AGNAYA - Physics & Physical Invariant Tests
Verifies mathematical and thermodynamic invariants across power demand, conductors, and indoor heat traps.
"""

import numpy as np

from agnaya.models.cascade_model import DemandModel, calculate_indoor_temp
from agnaya.models.conductor_ampacity import LinerateAmpacityAdapter
from agnaya.data.raipur_data import CSPDCL_PARAMS


def test_saturating_demand_ode_monotonicity():
    """Demand must monotonically increase with ambient temperature above T_set (27°C)."""
    dm = DemandModel()
    temps = [35.0, 40.0, 42.4, 45.0, 47.9]
    peak_demands = []
    for t in temps:
        _, d_series = dm.simulate(t, duration_days=2)
        peak_demands.append(float(np.max(d_series)))

    for i in range(len(peak_demands) - 1):
        assert peak_demands[i] < peak_demands[i + 1], (
            f"Monotonicity violated: D({temps[i]}°C)={peak_demands[i]} >= D({temps[i+1]}°C)={peak_demands[i+1]}"
        )


def test_demand_saturation_bound():
    """Demand must remain strictly bounded below emergency ceiling (620 MW) even at 55°C."""
    dm = DemandModel()
    _, d_series = dm.simulate(55.0, duration_days=3)
    max_demand = float(np.max(d_series))
    ceiling = CSPDCL_PARAMS["raipur_emergency_cap_mw"]
    assert max_demand <= ceiling, f"Demand {max_demand} MW exceeded transmission ceiling {ceiling} MW"
    assert max_demand > 420.0, "Demand should exceed 420 MW contracted limit under extreme heat"


def test_conductor_ampacity_thermal_derating():
    """Conductor ampacity must decrease as ambient temperature rises (IEEE Std 738)."""
    adapter = LinerateAmpacityAdapter()
    amp_35 = adapter.compute_ampacity("ACSR Zebra", ambient_temp_c=35.0, wind_speed_ms=1.0)
    amp_40 = adapter.compute_ampacity("ACSR Zebra", ambient_temp_c=40.0, wind_speed_ms=1.0)
    amp_48 = adapter.compute_ampacity("ACSR Zebra", ambient_temp_c=47.9, wind_speed_ms=1.0)

    assert amp_35 > amp_40 > amp_48, (
        f"Ampacity failed to derate monotonically: {amp_35} -> {amp_40} -> {amp_48}"
    )


def test_indoor_temperature_material_differential():
    """Slum dwelling with high tin roof density must be hotter than dwelling with high vegetative green cover."""
    t_slum = calculate_indoor_temp(ambient_temp_c=45.0, slum_pct=0.35, green_cover_pct=0.06, outage_hours=2.0)
    t_green = calculate_indoor_temp(ambient_temp_c=45.0, slum_pct=0.05, green_cover_pct=0.25, outage_hours=2.0)

    assert t_slum > t_green, f"Slum indoor temp ({t_slum}°C) not hotter than green area ({t_green}°C)"
    assert t_slum > 45.0, "Slum indoor temp must exceed ambient under solar trapping & power outage"
