"""
Unit tests for Raipur OpenCityModel and Smart City FBX asset loading.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.raipur_opencitymodel import get_raipur_opencitymodel
from data.smartcity_assets import get_smartcity_assets


def test_raipur_opencitymodel_structure():
    city = get_raipur_opencitymodel()
    assert city["type"] == "CityJSON"
    assert city["version"] == "1.0"
    assert len(city["CityObjects"]) >= 40
    assert "MON_GHADI_CHOWK" in city["CityObjects"]
    assert "CIVIC_MARINE_DRIVE" in city["CityObjects"]
    assert "SUB_S03" in city["CityObjects"]


def test_smartcity_assets_loading():
    assets = get_smartcity_assets()
    expected_keys = [
        "ghadi_chowk",
        "pro_clocktower",
        "mor_raipur",
        "marine_drive",
        "traffic_light",
        "divider_railing",
        "bicycle",
        "walking_citizen",
        "cycling_rider",
        "sitting_citizen",
        "apartment",
        "prius",
    ]
    repo_root = Path(__file__).resolve().parent.parent
    ref_dir = repo_root / "reference_3d" / "Cycle4Change-SmartCityRaipur"

    for k in expected_keys:
        assert k in assets, f"Missing asset {k}"
        assert isinstance(assets[k], str), f"Asset {k} is not a string"
        assert len(assets[k]) > 0, f"Asset {k} is empty"
        if ref_dir.exists():
            # In full local environment with cloned models, verify genuine multi-kilobyte payload
            assert len(assets[k]) > 500, f"Asset {k} payload too short in local environment"
