"""
AGNAYA - Transmission Corridor & Conductor Thermal Ampacity Engine
Based on IEEE Std 738-2012 (from Heat-Analysis / emliang)
Models temperature-dependent line ratings (TDLR) for CSPTCL transmission corridors in Raipur.
"""

import numpy as np
from typing import Dict, List, Any

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
        "normal_flow_mw": 340.0
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
        "normal_flow_mw": 115.0
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
        "normal_flow_mw": 98.0
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
        "normal_flow_mw": 35.0
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
        "normal_flow_mw": 32.0
    }
]


class ConductorThermalAmpacity:
    """
    IEEE 738-2012 Heat Balance for Overhead Conductors:
        q_c (convection) + q_r (radiation) = q_s (solar heating) + I^2 * R(Tc)

    At extreme heat, elevated ambient air and high solar radiation
    drastically reduce permissible current I_max to avoid conductor sag & annealing.
    """
    def __init__(self):
        self.ref_ambient_c = 40.0
        self.solar_flux_w_m2 = 950.0  # Intense summer solar radiation in Raipur (May/June)

    def compute_ieee738_ampacity(
        self,
        ambient_temp_c: float,
        wind_speed_ms: float = 1.0,
        max_cond_temp_c: float = 75.0,
        conductor_type: str = "ACSR Zebra",
        rated_current_amps: float = 1050.0
    ) -> float:
        """
        IEEE 738-2012 steady-state thermal ampacity rating (in Amperes).
        """
        if ambient_temp_c >= max_cond_temp_c:
            derated_ratio = 0.20
        else:
            rated_delta_t = max(5.0, max_cond_temp_c - self.ref_ambient_c)
            actual_delta_t = max(2.0, max_cond_temp_c - ambient_temp_c)
            wind_factor = max(0.6, (wind_speed_ms / 1.0) ** 0.5)
            derated_ratio = np.sqrt(actual_delta_t / rated_delta_t) * wind_factor
            derated_ratio = min(1.05, max(0.20, derated_ratio))

        return float(round(rated_current_amps * derated_ratio, 1))

    def calculate_derated_ampacity(self, corridor: Dict[str, Any], ambient_temp_c: float, wind_speed_ms: float = 1.0) -> Dict[str, Any]:
        """
        Computes permissible line current and megawatt throughput under heat stress.
        """
        tc_max = corridor["max_conductor_temp_c"]  # 75°C
        rated_i = corridor["rated_current_amps"]
        voltage = corridor["voltage_kv"]

        # If ambient reaches or exceeds max allowable conductor temperature, ampacity approaches 0
        if ambient_temp_c >= tc_max:
            derated_ratio = 0.20
        else:
            # Heat dissipation delta
            rated_delta_t = tc_max - self.ref_ambient_c  # 35°C delta under standard rating
            actual_delta_t = max(2.0, tc_max - ambient_temp_c)

            # Natural/low forced convection scaling (IEEE 738 simplified form)
            wind_factor = max(0.6, (wind_speed_ms / 1.0) ** 0.5)
            derated_ratio = np.sqrt(actual_delta_t / rated_delta_t) * wind_factor
            derated_ratio = min(1.05, max(0.20, derated_ratio))

        derated_amps = rated_i * derated_ratio
        # Three-phase MW capacity: P = sqrt(3) * V_kV * I_amps * power_factor / 1000
        pf = 0.90
        derated_mw = (np.sqrt(3) * voltage * derated_amps * pf) / 1000.0
        rated_mw = (np.sqrt(3) * voltage * rated_i * pf) / 1000.0
        derate_pct = (1.0 - (derated_amps / rated_i)) * 100.0

        # Sag and clearance risk index (0 to 1)
        sag_risk = min(1.0, max(0.0, (ambient_temp_c - 40.0) / 10.0 + (corridor["normal_flow_mw"] / max(1.0, derated_mw) - 0.75)))

        return {
            "corridor_id": corridor["id"],
            "name": corridor["name"],
            "voltage_kv": voltage,
            "conductor_type": corridor["conductor_type"],
            "rated_capacity_mw": round(rated_mw, 1),
            "derated_capacity_mw": round(derated_mw, 1),
            "derating_percentage": round(max(0.0, derate_pct), 1),
            "derated_amps": round(derated_amps, 1),
            "normal_flow_mw": corridor["normal_flow_mw"],
            "loading_percentage": round((corridor["normal_flow_mw"] / max(1.0, derated_mw)) * 100.0, 1),
            "sag_clearance_risk": round(sag_risk, 2),
            "status": "CRITICAL" if corridor["normal_flow_mw"] > derated_mw else "WARNING" if corridor["normal_flow_mw"] > 0.85 * derated_mw else "OK"
        }

    def evaluate_all_corridors(self, ambient_temp_c: float, wind_speed_ms: float = 1.0) -> List[Dict[str, Any]]:
        return [self.calculate_derated_ampacity(c, ambient_temp_c, wind_speed_ms) for c in RAIPUR_TRANSMISSION_CORRIDORS]
