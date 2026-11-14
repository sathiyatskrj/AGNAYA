"""
AGNAYA - Data Provenance & Rule 5 Guardrail Tests
Verifies DATA_SOURCES.csv audit matrix, terminology definitions, and Rule 5 number guards.
"""

from agnaya.data.raipur_data import (
    get_data_sources_rows,
    get_provenance_summary,
    get_asset_registry,
)
from agnaya.models.llm_explainer import DeterministicNumberGuard, DeterministicNarrativeGenerator


def test_data_sources_matrix_completeness():
    """All parameters must carry one explicit status: VERIFIED, DERIVED, or ASSUMED."""
    rows = get_data_sources_rows()
    assert len(rows) >= 180, f"Expected >= 180 audited parameters, got {len(rows)}"

    valid_statuses = {"VERIFIED", "DERIVED", "ASSUMED", "SYNTHETIC"}
    for r in rows:
        assert r["status"] in valid_statuses, f"Invalid provenance status: {r['status']}"
        assert r["confidence"] in {"HIGH", "MEDIUM", "LOW"}
        assert len(r["source"]) > 3, f"Empty source description for {r['parameter_name']}"

    summary = get_provenance_summary()
    assert summary["status_breakdown"]["VERIFIED"] >= 20
    assert summary["status_breakdown"]["DERIVED"] >= 50
    assert summary["status_breakdown"]["ASSUMED"] >= 90


def test_asset_registry_audit():
    """All 17 critical assets must be audited for physical identifiability and topology link."""
    assets = get_asset_registry()
    assert len(assets) == 17

    for a in assets:
        assert "is_real_identifiable_asset" in a
        assert a["capacity_status"] in {"VERIFIED", "ASSUMED"}
        assert a["link_type"] in {"PHYSICAL", "PLANNING_ASSUMED", "CONCEPTUAL"}


def test_rule_5_deterministic_number_guard():
    """Valid narrative passes; narrative with hallucinated numbers is strictly rejected."""
    inputs = {
        "ambient_temp_c": 46.5,
        "relative_humidity_pct": 28.0,
        "peak_demand_mw": 475.9,
        "contracted_limit_mw": 420.0,
        "emergency_cap_mw": 620.0,
        "shortfall_mw": 55.9,
        "substation_hotspot_c": 118.5,
        "max_indoor_temp_c": 48.9,
        "resilience_dividend_pct": 85.6,
        "disruption_hours_saved": 14.6,
        "top_vulnerable_zone": "Z05 Tikrapara",
    }
    grounded_text = DeterministicNarrativeGenerator.generate_narrative(inputs)
    is_valid, ungrounded = DeterministicNumberGuard.validate(grounded_text, inputs)
    assert is_valid is True, f"Valid narrative failed: {ungrounded}"

    # Injected hallucinated deaths / costs
    hallucinated_text = grounded_text + " In addition, 73 deaths and 412 injuries occurred."
    is_valid_bad, ungrounded_bad = DeterministicNumberGuard.validate(hallucinated_text, inputs)
    assert is_valid_bad is False
    assert 73.0 in ungrounded_bad and 412.0 in ungrounded_bad
