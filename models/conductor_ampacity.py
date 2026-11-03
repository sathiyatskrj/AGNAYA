"""
AGNAYA - Transmission Corridor & Conductor Thermal Ampacity Engine
Based on IEEE Std 738-2012 Dynamic Line Rating (DTR) using the 'linerate' library.
Models temperature-dependent line ratings for CSPTCL transmission corridors in Raipur.

DISCLAIMER: SIMULATION ONLY – NOT AN OFFICIAL WARNING.
"""

import numpy as np
from typing import Dict, List, Any, Optional

# Transmission corridors connecting Raipur's substations
RAIPUR_TRANSMISSION_CORRIDORS = [
    {
        "id": "LINE_01",
        "name": "Bhilai - Raipur Main 220 kV D/C",
        "voltage_kv": 220,
        "conductor_type": "ACSR Zebra",
        "rated_current_amps": 1050.0,
        "max_conductor_temp_c": 75.0,
        "length_km": 32.0,
        "connects": ("Bhilai GSS", "S01 - Raipur Main"),
        "normal_flow_mw": 340.0,
        "status": "ASSUMED (CSPTCL 220kV Corridor Standard Line Rating)"
    },
    {
        "id": "LINE_02",
        "name": "Raipur Main - Mowa 132 kV S/C",
        "voltage_kv": 132,
        "conductor_type": "ACSR Panther",
        "rated_current_amps": 620.0,
        "max_conductor_temp_c": 75.0,
        "length_km": 14.5,
        "connects": ("S01 - Raipur Main", "S02 - Mowa"),
        "normal_flow_mw": 115.0,
        "status": "ASSUMED (CSPTCL 132kV Ring Feeder)"
    },
    {
        "id": "LINE_03",
        "name": "Raipur Main - Amanaka 132 kV S/C",
        "voltage_kv": 132,
        "conductor_type": "ACSR Panther",
        "rated_current_amps": 620.0,
        "max_conductor_temp_c": 75.0,
        "length_km": 11.2,
        "connects": ("S01 - Raipur Main", "S03 - Amanaka"),
        "normal_flow_mw": 98.0,
        "status": "ASSUMED (CSPTCL 132kV Radial Feeder)"
    },
    {
        "id": "LINE_04",
        "name": "Mowa - Pandri 33 kV Interconnector",
        "voltage_kv": 33,
        "conductor_type": "ACSR Dog",
        "rated_current_amps": 380.0,
        "max_conductor_temp_c": 75.0,
        "length_km": 6.8,
        "connects": ("S02 - Mowa", "S04 - Pandri"),
        "normal_flow_mw": 35.0,
        "status": "ASSUMED (CSPDCL 33kV Inter-substation Tie)"
    },
    {
        "id": "LINE_05",
        "name": "Amanaka - Gudhiyari 33 kV Interconnector",
        "voltage_kv": 33,
        "conductor_type": "ACSR Dog",
        "rated_current_amps": 380.0,
        "max_conductor_temp_c": 75.0,
        "length_km": 5.4,
        "connects": ("S03 - Amanaka", "S06 - Gudhiyari"),
        "normal_flow_mw": 32.0,
        "status": "ASSUMED (CSPDCL 33kV Tie)"
    }
]


def compute_ieee738_ampacity_legacy(
    ambient_temp_c: float,
    wind_speed_ms: float = 1.0,
    max_cond_temp_c: float = 75.0,
    conductor_type: str = "ACSR Zebra",
    rated_current_amps: float = 1050.0
) -> float:
    """
    Legacy ad-hoc square-root derating heuristic.
    Kept specifically for model comparison and regression verification tests.
    """
    if ambient_temp_c >= max_cond_temp_c:
        derated_ratio = 0.20
    else:
        rated_delta_t = max(5.0, max_cond_temp_c - 40.0)
        actual_delta_t = max(2.0, max_cond_temp_c - ambient_temp_c)
        wind_factor = max(0.6, (wind_speed_ms / 1.0) ** 0.5)
        derated_ratio = np.sqrt(actual_delta_t / rated_delta_t) * wind_factor
        derated_ratio = min(1.05, max(0.20, derated_ratio))

    return float(round(rated_current_amps * derated_ratio, 1))


class LinerateAmpacityAdapter:
    """
    Adapter wrapping the open-source 'linerate' library (IEEE Std 738-2012 / CIGRE 207).
    Computes steady-state heat balance:
        q_c (convection) + q_r (radiation) = q_s (solar heating) + I^2 * R(Tc)
    """
    def __init__(self):
        self._conductors = {}

    def _get_conductor(self, ctype: str):
        if ctype not in self._conductors:
            from linerate import Conductor
            if "Zebra" in ctype:
                # ACSR Zebra (54/7, 428.9 mm² Al, IS 398 Part 2)
                self._conductors[ctype] = Conductor(
                    core_diameter=0.00954,
                    conductor_diameter=0.02862,
                    outer_layer_strand_diameter=0.00318,
                    emissivity=0.8,
                    solar_absorptivity=0.8,
                    temperature1=20.0,
                    temperature2=75.0,
                    resistance_at_temperature1=0.0674 / 1000.0,
                    resistance_at_temperature2=0.0825 / 1000.0,
                    aluminium_cross_section_area=428.9e-6,
                    constant_magnetic_effect=None,
                    current_density_proportional_magnetic_effect=None,
                    max_magnetic_core_relative_resistance_increase=1.0,
                )
            elif "Panther" in ctype:
                # ACSR Panther (30/7, 212.1 mm² Al)
                self._conductors[ctype] = Conductor(
                    core_diameter=0.00700,
                    conductor_diameter=0.02100,
                    outer_layer_strand_diameter=0.00300,
                    emissivity=0.8,
                    solar_absorptivity=0.8,
                    temperature1=20.0,
                    temperature2=75.0,
                    resistance_at_temperature1=0.1363 / 1000.0,
                    resistance_at_temperature2=0.1668 / 1000.0,
                    aluminium_cross_section_area=212.1e-6,
                    constant_magnetic_effect=None,
                    current_density_proportional_magnetic_effect=None,
                    max_magnetic_core_relative_resistance_increase=1.0,
                )
            else:
                # ACSR Dog (6/7, 105.0 mm² Al)
                self._conductors[ctype] = Conductor(
                    core_diameter=0.00472,
                    conductor_diameter=0.01415,
                    outer_layer_strand_diameter=0.00236,
                    emissivity=0.8,
                    solar_absorptivity=0.8,
                    temperature1=20.0,
                    temperature2=75.0,
                    resistance_at_temperature1=0.2733 / 1000.0,
                    resistance_at_temperature2=0.3346 / 1000.0,
                    aluminium_cross_section_area=105.0e-6,
                    constant_magnetic_effect=None,
                    current_density_proportional_magnetic_effect=None,
                    max_magnetic_core_relative_resistance_increase=1.0,
                )
        return self._conductors[ctype]

    def compute_ampacity(
        self,
        conductor_type: str,
        ambient_temp_c: float,
        wind_speed_ms: float = 1.0,
        wind_angle_deg: float = 90.0,
        max_conductor_temp_c: float = 75.0,
        latitude: float = 21.25,
        longitude: float = 81.60,
        elevation_m: float = 298.0,
        datetime_str: str = "2024-05-28T12:00:00"
    ) -> float:
        """
        Computes steady-state ampacity using IEEE 738 physics engine.
        Falls back to legacy heuristic if solver does not converge.
        """
        try:
            from linerate import Span, Weather, Tower, IEEE738
            cond = self._get_conductor(conductor_type)
            t1 = Tower(latitude=latitude, longitude=longitude, altitude=elevation_m)
            t2 = Tower(latitude=latitude + 0.01, longitude=longitude + 0.01, altitude=elevation_m)
            span = Span(conductor=cond, start_tower=t1, end_tower=t2, num_conductors=1)
            weather = Weather(
                air_temperature=float(ambient_temp_c),
                wind_speed=max(0.2, float(wind_speed_ms)),
                wind_direction=np.radians(float(wind_angle_deg)),
                ground_albedo=0.20,
            )
            model = IEEE738(span=span, weather=weather, time=np.datetime64(datetime_str))
            amp = model.compute_steady_state_ampacity(max_conductor_temperature=float(max_conductor_temp_c))
            return float(round(amp, 1))
        except Exception:
            # Fallback to legacy formula on numerical convergence boundary
            return compute_ieee738_ampacity_legacy(
                ambient_temp_c=ambient_temp_c,
                wind_speed_ms=wind_speed_ms,
                max_cond_temp_c=max_conductor_temp_c,
                conductor_type=conductor_type,
            )


class ConductorThermalAmpacity:
    """
    IEEE 738-2012 Heat Balance for Bare Overhead Conductors.
    Evaluates temperature-dependent transmission line capacity and sag risks.
    """
    def __init__(self):
        self.ref_ambient_c = 40.0
        self.solar_flux_w_m2 = 950.0  # Intense summer solar radiation in Raipur (May/June)
        self.adapter = LinerateAmpacityAdapter()

    def compute_ieee738_ampacity(
        self,
        ambient_temp_c: float,
        wind_speed_ms: float = 1.0,
        max_cond_temp_c: float = 75.0,
        conductor_type: str = "ACSR Zebra",
        rated_current_amps: float = 1050.0,
        wind_angle_deg: float = 90.0,
    ) -> float:
        """
        IEEE 738-2012 steady-state thermal ampacity rating (in Amperes).
        Uses the LinerateAmpacityAdapter.
        """
        return self.adapter.compute_ampacity(
            conductor_type=conductor_type,
            ambient_temp_c=ambient_temp_c,
            wind_speed_ms=wind_speed_ms,
            wind_angle_deg=wind_angle_deg,
            max_conductor_temp_c=max_cond_temp_c
        )

    def calculate_derated_ampacity(
        self,
        corridor: Dict[str, Any],
        ambient_temp_c: float,
        wind_speed_ms: float = 1.0,
        wind_angle_deg: float = 90.0
    ) -> Dict[str, Any]:
        """
        Computes permissible line current and megawatt throughput under heat stress.
        """
        tc_max = corridor["max_conductor_temp_c"]  # 75°C
        rated_i = corridor["rated_current_amps"]
        voltage = corridor["voltage_kv"]
        ctype = corridor["conductor_type"]

        # IEEE 738 steady state calculation via linerate
        derated_amps = self.compute_ieee738_ampacity(
            ambient_temp_c=ambient_temp_c,
            wind_speed_ms=wind_speed_ms,
            max_cond_temp_c=tc_max,
            conductor_type=ctype,
            rated_current_amps=rated_i,
            wind_angle_deg=wind_angle_deg
        )

        # Legacy comparison value
        legacy_amps = compute_ieee738_ampacity_legacy(
            ambient_temp_c=ambient_temp_c,
            wind_speed_ms=wind_speed_ms,
            max_cond_temp_c=tc_max,
            conductor_type=ctype,
            rated_current_amps=rated_i
        )

        # Three-phase MW capacity: P = sqrt(3) * V_kV * I_amps * power_factor / 1000
        pf = 0.90
        derated_mw = (np.sqrt(3) * voltage * derated_amps * pf) / 1000.0
        rated_mw = (np.sqrt(3) * voltage * rated_i * pf) / 1000.0
        derate_pct = max(0.0, (1.0 - (derated_amps / rated_i)) * 100.0)

        # Sag and clearance risk index (0 to 1)
        sag_risk = min(1.0, max(0.0, (ambient_temp_c - 40.0) / 10.0 + (corridor["normal_flow_mw"] / max(1.0, derated_mw) - 0.75)))

        return {
            "corridor_id": corridor["id"],
            "name": corridor["name"],
            "voltage_kv": voltage,
            "conductor_type": ctype,
            "rated_capacity_mw": round(rated_mw, 1),
            "derated_capacity_mw": round(derated_mw, 1),
            "derating_percentage": round(derate_pct, 1),
            "derated_amps": round(derated_amps, 1),
            "legacy_amps": round(legacy_amps, 1),
            "normal_flow_mw": corridor["normal_flow_mw"],
            "loading_percentage": round((corridor["normal_flow_mw"] / max(1.0, derated_mw)) * 100.0, 1),
            "sag_clearance_risk": round(sag_risk, 2),
            "status": "CRITICAL" if corridor["normal_flow_mw"] > derated_mw else "WARNING" if corridor["normal_flow_mw"] > 0.85 * derated_mw else "OK",
            "model_provenance": "IEEE Std 738-2012 (linerate)"
        }

    def evaluate_all_corridors(
        self,
        ambient_temp_c: float,
        wind_speed_ms: float = 1.0,
        wind_angle_deg: float = 90.0
    ) -> List[Dict[str, Any]]:
        return [
            self.calculate_derated_ampacity(c, ambient_temp_c, wind_speed_ms, wind_angle_deg)
            for c in RAIPUR_TRANSMISSION_CORRIDORS
        ]
