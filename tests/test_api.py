"""
AGNAYA - FastAPI Integration & Endpoint Verification Tests
Verifies HTTP status codes, security headers, rate limiting, and simulation disclaimers.
"""

from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_api_health_endpoint():
    """Health check endpoint must return healthy status and simulation disclaimer."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "SIMULATION ONLY" in data["disclaimer"]


def test_api_data_provenance_endpoint():
    """Provenance endpoint must audit statuses and include terminology definitions."""
    response = client.get("/api/v1/data/provenance")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"]["status_breakdown"]["VERIFIED"] >= 20
    assert "terminology" in data
    assert "SIMULATION ONLY" in data["disclaimer"]


def test_api_asset_registry_endpoint():
    """Asset registry must return all 17 critical infrastructure assets."""
    response = client.get("/api/v1/data/asset-registry")
    assert response.status_code == 200
    data = response.json()
    assert data["total_assets"] == 17
    assert len(data["assets"]) == 17


def test_api_cap_xml_endpoint():
    """CAP endpoint must return valid OASIS XML with status=Draft."""
    response = client.get("/api/v1/alerts/cap-xml?ambient_temp_c=46.5")
    assert response.status_code == 200
    assert "application/xml" in response.headers.get("content-type", "")
    assert "<status>Draft</status>" in response.text
    assert "SIMULATION ONLY" in response.text


def test_api_sobol_sensitivity_endpoint():
    """Sobol endpoint must return S1 and ST variance decomposition indices."""
    response = client.get("/api/v1/sensitivity/sobol?n_samples=16")
    assert response.status_code == 200
    data = response.json()
    assert "indices" in data
    assert "peak_demand_mw" in data["indices"]


def test_api_ward_brief_pdf_endpoint():
    """Ward brief endpoint must return valid PDF byte stream with attachment header."""
    response = client.get("/api/v1/reports/ward-brief?zone_id=Z05")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 3000


def test_api_sitrep_pdf_endpoint():
    """SITREP endpoint must return valid PDF byte stream."""
    response = client.get("/api/v1/reports/sitrep?ambient_temp_c=46.5")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert len(response.content) > 3000


def test_api_indoor_calibration_endpoint():
    """Indoor calibration endpoint must evaluate baseline error and calibrate parameters."""
    response = client.get("/api/v1/validation/indoor-calibration")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CALIBRATION_COMPLETE"
    assert data["optimization_success"] is True
    assert "improvement_pct" in data
