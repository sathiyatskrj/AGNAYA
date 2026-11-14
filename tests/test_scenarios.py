"""
AGNAYA - Versioned YAML Scenario & Execution Tests
Verifies scenario loading, Pydantic schema validation, and headless execution.
"""

import os

from agnaya.core.schemas import ScenarioProvenance
from agnaya.services.scenario_runner import ScenarioRunner


def test_scenario_yaml_files_exist():
    """All 3 required scenario YAML files must exist in scenarios/."""
    expected_scenarios = [
        "scenarios/may_2024_all_time_peak.yaml",
        "scenarios/summer_normal_moderate.yaml",
        "scenarios/compound_stress_blackout.yaml",
    ]
    for s_path in expected_scenarios:
        assert os.path.exists(s_path), f"Missing scenario file: {s_path}"


def test_scenario_pydantic_validation():
    """Validates that ScenarioConfig parses and validates YAML contents."""
    s_path = "scenarios/may_2024_all_time_peak.yaml"
    config = ScenarioRunner.load_scenario_from_file(s_path)

    assert config.scenario_id == "SCN-HIST-2024-05-28"
    assert config.provenance == ScenarioProvenance.HISTORICAL_OBSERVED
    assert config.ambient_temp_c == 47.9
    assert config.random_seed == 42
    assert "SIMULATION ONLY – NOT AN OFFICIAL WARNING" in config.disclaimer


def test_headless_scenario_execution():
    """Runs a scenario headless without Streamlit and verifies the output contract."""
    s_path = "scenarios/summer_normal_moderate.yaml"
    config = ScenarioRunner.load_scenario_from_file(s_path)
    result = ScenarioRunner.run_scenario(config)

    assert result.scenario_id == config.scenario_id
    assert result.peak_demand_mw > 310.0
    assert result.resilience_dividend_pct > 0.0
    assert result.disruption_hours_saved >= 0.0
    assert len(result.top_vulnerable_zones) == 3
    assert "SIMULATION ONLY – NOT AN OFFICIAL WARNING" in result.disclaimer
