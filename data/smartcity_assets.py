"""
AGNAYA - Raipur Smart City 3D Asset Provider
Loads and bundles authentic 3D models and skeletal animations from AkshaySharmaDEV/Cycle4Change-SmartCityRaipur.
Provides base64 data URIs for Three.js FBXLoader and OBJLoader.
"""

import base64
from pathlib import Path
from typing import Dict

_CACHED_ASSETS: Dict[str, str] = {}


def get_smartcity_assets() -> Dict[str, str]:
    """Returns a dictionary of base64-encoded verified FBX 7.x assets from Cycle4Change-SmartCityRaipur."""
    global _CACHED_ASSETS
    if _CACHED_ASSETS:
        return _CACHED_ASSETS

    # Robust repository root detection
    repo_root = Path(__file__).resolve().parent
    for _ in range(5):
        if (repo_root / "reference_3d").exists():
            break
        repo_root = repo_root.parent

    base_dir = repo_root / "reference_3d" / "Cycle4Change-SmartCityRaipur"

    asset_paths = {
        "ghadi_chowk": "Cycles4Change/Assets/Models/ghadichowkbuilding.fbx",
        "pro_clocktower": "Cycles4Change/Assets/Models/proclocktower.fbx",
        "mor_raipur": "Cycles4Change/Assets/Models/morraipur.fbx",
        "marine_drive": "Cycles4Change/Assets/Models/marine drive.fbx",
        "traffic_light": "Cycles4Change/Assets/Models/traffic light.fbx",
        "divider_railing": "Cycles4Change/Assets/Models/dividerrailing2.fbx",
        "bicycle": "Cycles4Change/Assets/bicycle_PRO_kit/Models/bicycle_body.fbx",
        "walking_citizen": "Cycles4Change/Assets/Models/Walking.fbx",
        "cycling_rider": "Cycles4Change/Assets/bicycle_PRO_kit/Models/char_anim.fbx",
        "sitting_citizen": "Cycles4Change/Assets/Models/Female Sitting Pose.fbx",
        "apartment": "Cycles4Change/Assets/Models/uploads_files_908281_apartment1.fbx",
        "prius": "Cycles4Change/Assets/Models/Toyota Prius XW30 2010.fbx"
    }

    loaded = {}
    for key, rel_path in asset_paths.items():
        file_path = base_dir / rel_path
        if file_path.exists():
            with open(file_path, "rb") as f:
                loaded[key] = base64.b64encode(f.read()).decode("utf-8")
        else:
            loaded[key] = ""

    _CACHED_ASSETS = loaded
    return _CACHED_ASSETS
