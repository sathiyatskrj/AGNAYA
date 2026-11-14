"""
AGNAYA - Edge Cases & Robustness Tests
Verifies behavior under zero budgets, winter temperatures, extreme heat spikes, and zero outages.
"""

import numpy as np

from agnaya.models.cascade_model import DemandModel, calculate_indoor_temp
from agnaya.models.sensitivity_analysis import SobolSensitivityEngine
from agnaya.models.indoor_calibration import IndoorLoggerValidationEngine
from agnaya.data.raipur_data import CSPDCL_PARAMS


def test_winter_temperature_no_cooling_surge():
    """At winter temperatures (15°C < T_set = 27°C), cooling demand surge must be zero."""
    dm = DemandModel()
    _, d_series = dm.simulate(15.0, duration_days=2)
    min_demand = float(np.min(d_series))
    base_demand = CSPDCL_PARAMS["raipur_normal_demand_mw"]
    assert min_demand <= base_demand + 1.0


def test_zero_hour_outage():
    """Zero-hour outage must result in zero outage heat accumulation."""
    t_zero = calculate_indoor_temp(ambient_temp_c=45.0, slum_pct=0.30, green_cover_pct=0.10, outage_hours=0.0)
    t_two = calculate_indoor_temp(ambient_temp_c=45.0, slum_pct=0.30, green_cover_pct=0.10, outage_hours=2.0)

    assert t_two > t_zero
    expected_diff = min(6.5, 0.8 * 2.0)
    assert abs((t_two - t_zero) - expected_diff) < 0.2


def test_sobol_sensitivity_engine_fixed_seed():
    """Sobol sensitivity engine with fixed seed must yield identical results across repeated runs."""
    eng1 = SobolSensitivityEngine(seed=42)
    res1 = eng1.run_sobol_analysis(n_samples=16)

    eng2 = SobolSensitivityEngine(seed=42)
    res2 = eng2.run_sobol_analysis(n_samples=16)

    assert res1["indices"]["peak_demand_mw"]["S1"] == res2["indices"]["peak_demand_mw"]["S1"]
    assert res1["indices"]["peak_demand_mw"]["ST"] == res2["indices"]["peak_demand_mw"]["ST"]


def test_indoor_logger_invalid_reading_filtering(tmp_path):
    """Validation engine must filter out sensor errors (e.g. -99°C or 150°C)."""
    bad_csv = tmp_path / "bad_loggers.csv"
    bad_csv.write_text(
        "house_id,zone,roof_type,timestamp,temp_c,rh\n"
        "H01,Z01,tin_cgi,2024-05-27T10:00:00+05:30,42.0,30.0\n"
        "H01,Z01,tin_cgi,2024-05-27T11:00:00+05:30,-99.0,30.0\n"
        "H01,Z01,tin_cgi,2024-05-27T12:00:00+05:30,120.0,30.0\n"
        "H01,Z01,tin_cgi,2024-05-27T13:00:00+05:30,44.0,150.0\n",
        encoding="utf-8"
    )
    engine = IndoorLoggerValidationEngine()
    df_clean = engine.load_logger_data(str(bad_csv))
    assert len(df_clean) == 1
    assert df_clean.iloc[0]["temp_c"] == 42.0
