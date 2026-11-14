"""
AGNAYA - Core Pydantic Schemas & Data Provenance Models
Strict mathematical schemas with mandatory data provenance classification.

NON-NEGOTIABLE COMPLIANCE:
- Every parameter carries one status: VERIFIED, DERIVED, ASSUMED, or SYNTHETIC.
- Scenarios are versioned with fixed seeds and explicit provenance classification.
- All outputs contain: "SIMULATION ONLY – NOT AN OFFICIAL WARNING".
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class ProvenanceStatus(str, Enum):
    VERIFIED = "VERIFIED"    # Grounded in primary official documentation/filings with retrieval date
    DERIVED = "DERIVED"      # Numerically computed from verified primary equations or geometries
    ASSUMED = "ASSUMED"      # Standard engineering or planning assumption pending local utility loggers
    SYNTHETIC = "SYNTHETIC"  # Artificial sample data generated for test harnesses and pilot mockups


class DataConfidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ParameterRecord(BaseModel):
    """
    Standardized parameter record matching data/DATA_SOURCES.csv provenance schema.
    """
    entity_type: str
    entity_id: str
    parameter_name: str
    value: Union[float, int, str, bool]
    unit: str
    status: ProvenanceStatus
    source: str
    retrieval_or_publication_date: str
    reference_year: int
    confidence: DataConfidence
    notes: Optional[str] = None


class ScenarioProvenance(str, Enum):
    HISTORICAL_OBSERVED = "HISTORICAL_OBSERVED"        # IMD station recorded extreme (e.g. 47.9°C May 2024)
    CLIMATOLOGICAL_NORMAL = "CLIMATOLOGICAL_NORMAL"    # IMD 30-year summer normal (42.4°C)
    USER_HYPOTHETICAL = "USER_HYPOTHETICAL"            # User-defined scenario exploration
    SYNTHETIC_STRESS_TEST = "SYNTHETIC_STRESS_TEST"    # Compound multi-system failure stress test


class ScenarioConfig(BaseModel):
    """
    Versioned scenario definition for deterministic batch runs and CLI execution.
    """
    version: str = Field("1.0", description="Scenario specification format version")
    scenario_id: str = Field(..., description="Unique alphanumeric scenario identifier")
    name: str = Field(..., description="Human-readable scenario title")
    description: str = Field(..., description="Scenario background and operational context")
    provenance: ScenarioProvenance = Field(..., description="Classification of scenario heat parameters")

    # Meteorological Drivers
    ambient_temp_c: float = Field(..., ge=30.0, le=55.0, description="Peak daytime outdoor temperature in °C")
    relative_humidity_pct: float = Field(..., ge=5.0, le=100.0, description="Afternoon relative humidity in %")
    duration_days: int = Field(..., ge=1, le=14, description="Sustained heatwave duration in days")

    # Infrastructure Contingencies
    power_outage_hours: float = Field(0.0, ge=0.0, le=24.0, description="Feeder outage duration in hours")
    tripped_substation: Optional[str] = Field(None, description="Substation ID under N-1 trip contingency")

    # Reproducibility & Optimization
    random_seed: int = Field(42, ge=1, le=999999, description="Fixed random seed for deterministic execution")
    budget_lakh: float = Field(60.0, ge=0.0, le=1000.0, description="Municipal contingency mitigation budget in Lakhs")
    interventions: Dict[str, int] = Field(default_factory=dict, description="Explicit manual resource allocations")

    disclaimer: str = Field(
        "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
        description="Mandatory legal disclaimer"
    )

    @field_validator("disclaimer")
    @classmethod
    def validate_disclaimer(cls, v: str) -> str:
        if "SIMULATION ONLY" not in v:
            raise ValueError("Mandatory disclaimer 'SIMULATION ONLY' must be present.")
        return v


class SimulationResult(BaseModel):
    """
    Comprehensive output contract for a deterministic simulation execution.
    """
    scenario_id: str
    scenario_name: str
    ambient_temp_c: float
    peak_demand_mw: float
    contracted_capacity_mw: float
    emergency_ceiling_mw: float
    shortfall_mw: float
    transformer_hotspot_c: float
    resilience_dividend_pct: float
    disruption_hours_saved: float
    top_vulnerable_zones: List[Dict[str, Any]]
    allocated_fleet: Dict[str, int]
    budget_spent_lakh: float
    budget_ceiling_lakh: float
    provenance_summary: Dict[str, int]
    disclaimer: str = "SIMULATION ONLY – NOT AN OFFICIAL WARNING"
