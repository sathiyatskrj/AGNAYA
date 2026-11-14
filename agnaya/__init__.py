"""
AGNAYA - Adaptive Geospatial Network for Heatwave Analytics and Yield Assessment
Raipur, Chhattisgarh | Municipal & Grid Operations Twin

Grounded Scientific Research Framework:
- IEEE Std 738-2012 Dynamic Line Rating
- IEEE Std C57.91-2011 Clause 7 Arrhenius Transformer Aging
- CSERC Tariff Order FY 2024–25 Grounded Baseline Demand
- IIT Roorkee HSRI (Nature Sci Rep 2026) & TAPAS Biometeorology (UTCI / WBGT)
- SciPy HiGHS Mixed-Integer Linear Programming (MILP) Dispatch
- OASIS Common Alerting Protocol (CAP v1.2) Standard XML Export
- ReportLab Publication-Quality Ward Briefs & SITREP Reporting
- SALib Sobol Global Variance Sensitivity Analysis

MANDATORY REGULATORY DISCLAIMER:
SIMULATION ONLY – NOT AN OFFICIAL WARNING.
Not endorsed by IMD, NDMA, CSPDCL, or Raipur Municipal Corporation.
"""

__version__ = "3.1.0"
__author__ = "AGNAYA Research Team"

from agnaya.core.schemas import (
    ProvenanceStatus,
    DataConfidence,
    ParameterRecord,
    ScenarioProvenance,
    ScenarioConfig,
    SimulationResult,
)
from agnaya.core.exceptions import (
    AgnayaError,
    ScenarioValidationError,
    GridCapacityExceededError,
    AssetNotFoundError,
    DataProvenanceError,
    HardwareSafetyError,
)
from agnaya.core.logging import get_logger

__all__ = [
    "__version__",
    "ProvenanceStatus",
    "DataConfidence",
    "ParameterRecord",
    "ScenarioProvenance",
    "ScenarioConfig",
    "SimulationResult",
    "AgnayaError",
    "ScenarioValidationError",
    "GridCapacityExceededError",
    "AssetNotFoundError",
    "DataProvenanceError",
    "HardwareSafetyError",
    "get_logger",
]
