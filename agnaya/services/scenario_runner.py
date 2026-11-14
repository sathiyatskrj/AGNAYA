"""
AGNAYA - Headless Scenario Runner & CLI Service
Executes versioned YAML simulation scenarios deterministically without Streamlit.

NON-NEGOTIABLE COMPLIANCE:
- Zero Streamlit imports or GUI dependencies.
- Strict Pydantic input validation and output schema conformance.
- Deterministic random seeds enforced.
- Mandatory disclaimer: "SIMULATION ONLY – NOT AN OFFICIAL WARNING".
"""

import argparse
import os
import sys
import yaml
import numpy as np

from agnaya.core.schemas import ScenarioConfig, SimulationResult
from agnaya.core.exceptions import ScenarioValidationError, GridCapacityExceededError
from agnaya.core.logging import get_logger

# Import core simulation models (supporting both installed package and workspace path)
try:
    from agnaya.models.cascade_model import DemandModel
    from agnaya.models.grid_digital_twin import GridStressNetwork
    from agnaya.models.tapas_health import TapasHealthEngine
    from agnaya.models.system_resilience import SystemResilienceEngine
    from agnaya.models.agents_pipeline import DeterministicDispatchPipeline
    from agnaya.data.raipur_data import CSPDCL_PARAMS, INTERVENTION_OPTIONS, get_provenance_summary
except ImportError:
    from models.cascade_model import DemandModel
    from models.grid_digital_twin import GridStressNetwork
    from models.tapas_health import TapasHealthEngine
    from models.system_resilience import SystemResilienceEngine
    from models.agents_pipeline import DeterministicDispatchPipeline
    from data.raipur_data import CSPDCL_PARAMS, INTERVENTION_OPTIONS, get_provenance_summary


logger = get_logger("agnaya.scenario_runner")


class ScenarioRunner:
    """
    Headless execution engine for versioned scenario YAML configurations.
    """

    @classmethod
    def load_scenario_from_file(cls, filepath: str) -> ScenarioConfig:
        """Loads and validates a scenario YAML file."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Scenario configuration file not found: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
        try:
            return ScenarioConfig(**raw_data)
        except Exception as e:
            raise ScenarioValidationError(f"Scenario validation failed for {filepath}: {e}")

    @classmethod
    def run_scenario(cls, config: ScenarioConfig) -> SimulationResult:
        """
        Executes coupled multi-infrastructure cascade simulation for a given scenario.
        Enforces fixed random seeds and unrounded numerical invariants.
        """
        logger.info(f"Executing scenario: {config.name} ({config.scenario_id})")
        logger.info(f"Parameters: T_peak={config.ambient_temp_c}°C, RH={config.relative_humidity_pct}%, Outage={config.power_outage_hours}h, Seed={config.random_seed}")

        # Fix random seed for reproducible stochastic evaluations
        np.random.seed(config.random_seed)

        # 1. Demand Model (Saturating ODE)
        dm = DemandModel()
        _, d_series = dm.simulate(config.ambient_temp_c, config.duration_days)
        peak_d = float(np.max(d_series))
        contracted_limit = float(CSPDCL_PARAMS.get("raipur_peak_demand_mw", 420.0))
        emergency_ceiling = float(CSPDCL_PARAMS.get("raipur_emergency_cap_mw", 620.0))
        shortfall = max(0.0, peak_d - contracted_limit)

        if peak_d > emergency_ceiling:
            raise GridCapacityExceededError(
                f"Peak demand ({peak_d:.1f} MW) exceeded emergency transmission ceiling ({emergency_ceiling} MW)"
            )

        # 2. Transformer Thermal Hotspot (IEEE Std C57.91)
        gsn = GridStressNetwork()
        sub_results = gsn.compute_composite_grid_risk(
            ambient_temp_c=config.ambient_temp_c,
            city_demand_mw=peak_d,
            tripped_substation=config.tripped_substation
        )
        sub_hotspots = [s["hotspot_temp_c"] for s in sub_results if "hotspot_temp_c" in s]
        max_hotspot = max(sub_hotspots) if sub_hotspots else (config.ambient_temp_c + 38.0)

        # 3. TAPAS Heuristic Heat-Risk Index & Indoor Trapping
        the = TapasHealthEngine()
        zones_res = the.compute_ward_hsri(
            ambient_temp_c=config.ambient_temp_c,
            power_outage_hours=config.power_outage_hours
        )
        # Top 3 most vulnerable zones
        sorted_zones = sorted(zones_res, key=lambda z: z.get("hsri_score", 0.0), reverse=True)
        top_vulnerable = [
            {
                "zone_id": z["zone_id"],
                "zone_name": z["zone_name"],
                "hsri_score": z["hsri_score"],
                "risk_band": z["risk_band"],
                "est_indoor_temp_c": z["est_indoor_temp_c"],
                "tin_roof_penalty_c": z.get("tin_roof_penalty_c", 0.0),
            }
            for z in sorted_zones[:3]
        ]

        # 4. Intervention Optimizer (HiGHS MILP)
        if config.interventions:
            allocated_fleet = config.interventions
            total_cost = sum(
                INTERVENTION_OPTIONS.get(k, {}).get("cost_per_unit_lakh", 1.0) * v
                for k, v in allocated_fleet.items()
            )
        else:
            pipeline = DeterministicDispatchPipeline()
            pipe_out = pipeline.run_pipeline(
                ambient_temp_c=config.ambient_temp_c,
                city_demand_mw=peak_d,
                budget_lakh=config.budget_lakh
            )
            dispatch = pipe_out.get("dispatch_solution", {})
            allocated_fleet = dispatch.get("units_allocated", {})
            total_cost = dispatch.get("total_cost_lakh", 0.0)

        # 5. System Resilience Continuous Trajectory Q(t)
        sre = SystemResilienceEngine()
        resil_res = sre.evaluate_resilience_curves(
            ambient_peak_c=config.ambient_temp_c,
            duration_days=config.duration_days,
            with_interventions=True
        )
        saved_hours = resil_res["disruption_hours_saved_unrounded"]
        resil_dividend = resil_res["resilience_gain_pct"]

        # Provenance summary
        prov = get_provenance_summary()
        prov_counts = prov.get("status_breakdown", {})

        result = SimulationResult(
            scenario_id=config.scenario_id,
            scenario_name=config.name,
            ambient_temp_c=config.ambient_temp_c,
            peak_demand_mw=round(peak_d, 1),
            contracted_capacity_mw=contracted_limit,
            emergency_ceiling_mw=emergency_ceiling,
            shortfall_mw=round(shortfall, 1),
            transformer_hotspot_c=round(max_hotspot, 1),
            resilience_dividend_pct=round(resil_dividend, 1),
            disruption_hours_saved=round(saved_hours, 2),
            top_vulnerable_zones=top_vulnerable,
            allocated_fleet=allocated_fleet,
            budget_spent_lakh=round(total_cost, 2),
            budget_ceiling_lakh=config.budget_lakh,
            provenance_summary=prov_counts,
            disclaimer="SIMULATION ONLY – NOT AN OFFICIAL WARNING"
        )
        logger.info(f"Execution complete. Peak demand: {peak_d:.1f} MW, Resilience dividend: +{resil_dividend:.1f}%")
        return result


def main():
    """CLI Entrypoint for headless batch execution."""
    parser = argparse.ArgumentParser(
        description="AGNAYA Headless Scenario Runner — Raipur Heatwave & Grid Digital Twin"
    )
    parser.add_argument(
        "scenario_file",
        help="Path to the scenario YAML file (e.g. scenarios/may_2024_all_time_peak.yaml)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON result to stdout"
    )
    parser.add_argument(
        "--out",
        dest="out_file",
        help="Optional file path to write results JSON"
    )
    args = parser.parse_args()

    try:
        config = ScenarioRunner.load_scenario_from_file(args.scenario_file)
        result = ScenarioRunner.run_scenario(config)

        if args.json or args.out_file:
            res_json = result.model_dump_json(indent=2)
            if args.out_file:
                with open(args.out_file, "w", encoding="utf-8") as f:
                    f.write(res_json)
                print(f"Results successfully written to {args.out_file}")
            if args.json:
                print(res_json)
        else:
            print("=" * 72)
            print(f" AGNAYA SIMULATION REPORT: {result.scenario_name}")
            print(f" Scenario ID: {result.scenario_id} | Ref Ambient: {result.ambient_temp_c}°C")
            print("=" * 72)
            print(f" Peak Electricity Demand:     {result.peak_demand_mw:.1f} MW")
            print(f" CSPDCL Contract Limit:       {result.contracted_capacity_mw:.1f} MW")
            print(f" Transmission Shortfall:      {result.shortfall_mw:.1f} MW")
            print(f" Max Transformer Hot-Spot:    {result.transformer_hotspot_c:.1f} °C")
            print(f" Disruption Hours Saved:      {result.disruption_hours_saved:.2f} h")
            print(f" System Resilience Dividend:  +{result.resilience_dividend_pct:.1f}%")
            print(f" Municipal Budget Allocated:  ₹ {result.budget_spent_lakh:.1f}L / ₹ {result.budget_ceiling_lakh:.1f}L")
            print("-" * 72)
            print(" Top Vulnerable Zones (HSRI Heuristic Score):")
            for z in result.top_vulnerable_zones:
                print(f"   [{z['zone_id']}] {z['zone_name']:<24} HSRI: {z['hsri_score']:.1f} ({z['risk_band']}) | Indoor Temp: {z['est_indoor_temp_c']:.1f}°C")
            print("=" * 72)
            print(f" ⚠️  {result.disclaimer}")
            print("=" * 72)

        sys.exit(0)

    except Exception as e:
        logger.error(f"Execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
