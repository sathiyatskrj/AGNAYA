"""
AGNAYA - OpenCityModel (CityJSON) Raipur City Digital Twin Adapter
Conforms to the OpenCityModel / CityJSON LOD1 3D standard (https://github.com/opencitymodel/opencitymodel).
Maps Raipur's 12 municipal wards, CSPTCL 220/132 kV substations, Kharun River 180 MLD water facilities,
and landmark infrastructure into standardized CityJSON building objects and georeferenced coordinates.

MANDATORY DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
"""

from typing import Any, Dict, List
from data.raipur_data import (
    RAIPUR_ZONES, RAIPUR_SUBSTATIONS, RAIPUR_WATER_PUMPS, RAIPUR_HOSPITALS
)

# Reference Datum: Raipur City Center (Jaistambh Chowk / Civil Lines)
RAIPUR_REF_LAT = 21.2514
RAIPUR_REF_LON = 81.6296
LAT_TO_M = 111000.0
LON_TO_M = 103450.0  # at 21.25° N
SCALE_FACTOR = 0.04  # 1 Three.js unit = 25 meters


def geo_to_city_coords(lat: float, lon: float) -> tuple[float, float]:
    """Projects WGS84 lat/lon to local 3D city scene coordinates (X=East, Z=South)."""
    dx_meters = (lon - RAIPUR_REF_LON) * LON_TO_M
    dz_meters = -(lat - RAIPUR_REF_LAT) * LAT_TO_M
    return round(dx_meters * SCALE_FACTOR, 2), round(dz_meters * SCALE_FACTOR, 2)


def get_raipur_opencitymodel() -> Dict[str, Any]:
    """
    Generates an OpenCityModel CityJSON dataset for Raipur, Chhattisgarh.
    Returns LOD1 building geometries, landuse boundaries, and infrastructure assets.
    """
    city_objects: Dict[str, Any] = {}
    vertices: List[List[float]] = []

    def add_box_geometry(
        obj_id: str,
        obj_type: str,
        cx: float,
        cz: float,
        w: float,
        d: float,
        h: float,
        attributes: Dict[str, Any]
    ):
        """Helper to create CityJSON Solid / Building box in vertices list."""
        base_idx = len(vertices)
        hw, hd = w / 2, d / 2
        # 8 vertices of a box
        # Bottom: 0: -w,-d, 1: +w,-d, 2: +w,+d, 3: -w,+d
        # Top:    4: -w,-d, 5: +w,-d, 6: +w,+d, 7: -w,+d
        box_pts = [
            [cx - hw, 0.0, cz - hd],
            [cx + hw, 0.0, cz - hd],
            [cx + hw, 0.0, cz + hd],
            [cx - hw, 0.0, cz + hd],
            [cx - hw, h, cz - hd],
            [cx + hw, h, cz - hd],
            [cx + hw, h, cz + hd],
            [cx - hw, h, cz + hd],
        ]
        vertices.extend([[round(v[0], 2), round(v[1], 2), round(v[2], 2)] for v in box_pts])

        # 6 faces of box
        boundaries = [
            [[base_idx + 0, base_idx + 3, base_idx + 2, base_idx + 1]],  # Bottom
            [[base_idx + 4, base_idx + 5, base_idx + 6, base_idx + 7]],  # Top (Roof)
            [[base_idx + 0, base_idx + 1, base_idx + 5, base_idx + 4]],  # North Wall
            [[base_idx + 1, base_idx + 2, base_idx + 6, base_idx + 5]],  # East Wall
            [[base_idx + 2, base_idx + 3, base_idx + 7, base_idx + 6]],  # South Wall
            [[base_idx + 3, base_idx + 0, base_idx + 4, base_idx + 7]],  # West Wall
        ]

        city_objects[obj_id] = {
            "type": obj_type,
            "attributes": attributes,
            "geometry": [
                {
                    "type": "Solid",
                    "lod": "1",
                    "boundaries": [boundaries]
                }
            ],
            "center": [cx, h / 2, cz],
            "dimensions": [w, h, d]
        }

    # 1. Generate Substation Infrastructure Assets
    for sub in RAIPUR_SUBSTATIONS:
        cx, cz = geo_to_city_coords(sub["lat"], sub["lon"])
        h = 10.0 if sub["voltage_kv"] == 220 else 7.5
        w, d = (16.0, 14.0) if sub["voltage_kv"] == 220 else (12.0, 10.0)
        add_box_geometry(
            obj_id=f"SUB_{sub['id']}",
            obj_type="Building",
            cx=cx, cz=cz, w=w, d=d, h=h,
            attributes={
                "name": sub["name"],
                "class": "ElectricalSubstation",
                "voltage_kv": sub["voltage_kv"],
                "capacity_mva": sub["capacity_mva"],
                "roofType": "switchyard_gantry",
                "lat": sub["lat"],
                "lon": sub["lon"],
                "source": "CSPTCL Grid Directory"
            }
        )

    # 2. Generate Water Treatment Plants & Pumping Stations
    for wp in RAIPUR_WATER_PUMPS:
        cx, cz = geo_to_city_coords(wp["lat"], wp["lon"])
        h = 9.0 if wp["capacity_MLD"] >= 100 else 6.0
        w, d = (18.0, 14.0) if wp["capacity_MLD"] >= 100 else (12.0, 10.0)
        add_box_geometry(
            obj_id=f"WTP_{wp['id']}",
            obj_type="Building",
            cx=cx, cz=cz, w=w, d=d, h=h,
            attributes={
                "name": wp["name"],
                "class": "WaterTreatmentPlant",
                "capacity_MLD": wp["capacity_MLD"],
                "roofType": "filtration_reservoir",
                "lat": wp["lat"],
                "lon": wp["lon"],
                "source": "RMC Water Supply Master Plan"
            }
        )

    # 3. Generate Hospital Complexes
    for hosp in RAIPUR_HOSPITALS:
        cx, cz = geo_to_city_coords(hosp["lat"], hosp["lon"])
        h = 16.0 if "Ambedkar" in hosp["name"] or "AIIMS" in hosp["name"] else 12.0
        w, d = (24.0, 18.0)
        add_box_geometry(
            obj_id=f"HOSP_{hosp['id']}",
            obj_type="Building",
            cx=cx, cz=cz, w=w, d=d, h=h,
            attributes={
                "name": hosp["name"],
                "class": "Hospital",
                "bed_capacity": hosp.get("bed_capacity", 300),
                "roofType": "medical_trauma_cross",
                "lat": hosp["lat"],
                "lon": hosp["lon"],
                "source": "Chhattisgarh Health Department"
            }
        )

    # 4. Generate Zonal Settlements (12 Raipur Planning Zones)
    for z in RAIPUR_ZONES:
        cx, cz = geo_to_city_coords(z["lat"], z["lon"])
        is_slum = z["slum_pct"] >= 0.25
        building_count = 14 if is_slum else 10

        # Cluster of buildings in this zone
        for i in range(building_count):
            ox = cx + ((i % 4) - 1.5) * 8.0 + ((i // 4) * 2.5)
            oz = cz + ((i // 4) - 1.0) * 8.5
            w = 5.0 + (i % 3) * 1.5 if is_slum else 8.0 + (i % 4) * 2.0
            d = 5.0 + (i % 2) * 2.0 if is_slum else 8.0 + (i % 3) * 2.0
            h = 4.0 + (i % 2) * 1.5 if is_slum else 10.0 + (i % 5) * 4.5

            roof_type = "corrugated_tin" if is_slum else "flat_concrete"
            add_box_geometry(
                obj_id=f"BLD_{z['id']}_{i:02d}",
                obj_type="Building",
                cx=ox, cz=oz, w=w, d=d, h=h,
                attributes={
                    "zone_id": z["id"],
                    "zone_name": z["name"],
                    "class": "InformalSettlement" if is_slum else "ResidentialCommercial",
                    "roofType": roof_type,
                    "slum_pct": z["slum_pct"],
                    "tin_roof_penalty_c": 4.5 if is_slum else 1.2,
                    "source": "OpenCityModel / RMC Census 2011"
                }
            )

    return {
        "type": "CityJSON",
        "version": "1.0",
        "citymodel_name": "OpenCityModel - Raipur City Digital Twin (Chhattisgarh)",
        "metadata": {
            "georeference": {
                "datum": "WGS84",
                "epsg": 4979,
                "center_lat": RAIPUR_REF_LAT,
                "center_lon": RAIPUR_REF_LON,
                "scale_units_per_meter": SCALE_FACTOR
            },
            "total_buildings": len(city_objects),
            "lod": "1",
            "specification": "https://github.com/opencitymodel/opencitymodel",
            "provenance": "CSERC FY24-25, CSPTCL 220/132 kV Directory, RMC Water Master Plan"
        },
        "CityObjects": city_objects,
        "vertices": vertices
    }
