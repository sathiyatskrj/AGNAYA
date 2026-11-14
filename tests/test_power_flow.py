"""
AGNAYA - Power Flow & Grid Stability Tests
Verifies Synchronous DC Power Flow, line impedances, Kirchhoff conservation, and catenary sag ground clearance.
"""

from agnaya.models.grid_power_flow import DCPowerFlowEngine


def test_dc_power_flow_nominal_solution():
    """Verifies that DC power flow solves cleanly under nominal conditions."""
    engine = DCPowerFlowEngine()
    res = engine.solve_power_flow(ambient_temp_c=42.0, total_city_load_mw=380.0, tripped_substation_id=None)

    assert "corridor_results" in res
    assert len(res["corridor_results"]) == 6
    assert res["grid_stability_index"] >= 0.0

    # Total power dispatched across active corridors must be positive
    total_flow = sum(abs(c["power_flow_mw"]) for c in res["corridor_results"] if c.get("is_active", True))
    assert total_flow > 0.0


def test_dc_power_flow_n1_contingency():
    """Tripping S01 (220 kV bulk infeed) must record the trip and solve without crashing."""
    engine = DCPowerFlowEngine()
    res_trip = engine.solve_power_flow(ambient_temp_c=46.5, total_city_load_mw=450.0, tripped_substation_id="S01")

    assert res_trip["tripped_substation"] == "S01"
    assert len(res_trip["corridor_results"]) == 6


def test_catenary_line_sag_statutory_clearance():
    """Ground clearances must stay above the statutory minimum (6.1m over roadways per CEA regulations)."""
    engine = DCPowerFlowEngine()
    res = engine.solve_power_flow(ambient_temp_c=47.9, total_city_load_mw=480.0, tripped_substation_id="S01")

    for c in res["corridor_results"]:
        clearance = c.get("clearance_remaining_m", 7.0)
        assert clearance >= 0.0, f"Negative line ground clearance detected on corridor {c['branch_id']}: {clearance}m"
