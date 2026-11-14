"""
AGNAYA - Typed Domain Exceptions
Provides explicit, structured exception types across physics, grid, and scenario engines.
"""

from typing import Optional, Dict, Any


class AgnayaError(Exception):
    """Base exception for all AGNAYA simulation and modeling errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ScenarioValidationError(AgnayaError):
    """Raised when a scenario YAML fails schema validation or bounds checking."""
    pass


class GridCapacityExceededError(AgnayaError):
    """Raised when total grid demand exceeds the emergency thermal transmission ceiling."""
    pass


class AssetNotFoundError(AgnayaError):
    """Raised when an infrastructure asset ID does not exist in the grounded registry."""
    pass


class DataProvenanceError(AgnayaError):
    """Raised when an unlabelled parameter or synthetic fallback lacks required provenance tags."""
    pass


class HardwareSafetyError(AgnayaError):
    """Raised when an electrical or thermal safety threshold is breached (e.g. negative sag clearance)."""
    pass
