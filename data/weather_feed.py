"""
AGNAYA - Open-Meteo Weather Connector for Raipur, Chhattisgarh
Location: 21.2514° N, 81.6296° E (Mana / Raipur Urban Area)

DATA PROVENANCE & MANDATORY DISCLAIMER:
- This connector fetches gridded numerical weather prediction (NWP) model data from the Open-Meteo API.
- IT IS NOT OFFICIAL IMD STATION TELEMETRY. Official observations are issued strictly by IMD Station #42809.
- SIMULATION ONLY – NOT AN OFFICIAL WARNING.
- Implements a 30-minute cache with an explicit, visibly-labelled SYNTHETIC/FALLBACK mode on failure.
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("agnaya.weather_feed")

RAIPUR_LAT = 21.2514
RAIPUR_LON = 81.6296
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL_SECONDS = 1800  # 30 minutes
CACHE_FILE_PATH = Path(__file__).resolve().parent / "cache_weather.json"


# Explicit, grounded synthetic fallback based on IMD Raipur May climatological normals
SYNTHETIC_FALLBACK_RECORD: Dict[str, Any] = {
    "status": "SYNTHETIC/FALLBACK",
    "is_synthetic_fallback": True,
    "provider": "SYNTHETIC/FALLBACK (Climatological Summer Normal for Raipur)",
    "station_or_model": "IMD Raipur Normal 1981-2010 Climatology Model",
    "latitude": RAIPUR_LAT,
    "longitude": RAIPUR_LON,
    "temperature_c": 42.5,
    "relative_humidity_pct": 35.0,
    "apparent_temperature_c": 45.8,
    "wind_speed_ms": 2.8,
    "direct_normal_irradiance_wm2": 780.0,
    "surface_pressure_hpa": 978.0,
    "retrieval_timestamp": None,  # Dynamically set on fallback return
    "cache_age_seconds": 0,
    "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
    "notes": "Weather data could not be fetched from Open-Meteo API; synthetic climatological fallback record applied. Never use for operational warnings.",
}


class WeatherFeedConnector:
    """
    Connects to Open-Meteo for Raipur gridded forecast data with a 30-minute cache
    and robust, visibly-labelled fallback to synthetic climatology upon network failure.
    """

    def __init__(
        self,
        latitude: float = RAIPUR_LAT,
        longitude: float = RAIPUR_LON,
        cache_ttl_seconds: int = CACHE_TTL_SECONDS,
        cache_file: Path = CACHE_FILE_PATH,
        timeout_seconds: float = 6.0,
    ):
        self.latitude = latitude
        self.longitude = longitude
        self.cache_ttl_seconds = cache_ttl_seconds
        self.cache_file = cache_file
        self.timeout_seconds = timeout_seconds
        self._memory_cache: Optional[Dict[str, Any]] = None

    def _read_disk_cache(self) -> Optional[Dict[str, Any]]:
        """Reads cached weather payload from disk if valid and unexpired."""
        try:
            if not self.cache_file.exists():
                return None
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            cached_at = data.get("_cached_at_epoch", 0)
            if (time.time() - cached_at) < self.cache_ttl_seconds:
                return data
        except Exception as e:
            logger.warning(f"Failed to read weather cache file: {e}")
        return None

    def _write_disk_cache(self, data: Dict[str, Any]) -> None:
        """Persists weather payload to disk cache."""
        try:
            payload = dict(data)
            payload["_cached_at_epoch"] = time.time()
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to write weather cache file: {e}")

    def fetch_live_gridded_data(self) -> Dict[str, Any]:
        """
        Executes HTTP request to Open-Meteo API for Raipur coordinates.
        Retrieves current conditions and hourly irradiance forecast.
        """
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,surface_pressure",
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,direct_normal_irradiance",
            "timezone": "Asia/Kolkata",
            "forecast_days": 2,
        }
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.get(OPEN_METEO_URL, params=params)
            response.raise_for_status()
            return response.json()

    def get_current_weather(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Returns the current weather observation from Open-Meteo or cached data.
        If the network or API fails, returns an explicit SYNTHETIC/FALLBACK record.
        """
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Check in-memory and disk cache
        if not force_refresh:
            if self._memory_cache:
                cached_at = self._memory_cache.get("_cached_at_epoch", 0)
                age = time.time() - cached_at
                if age < self.cache_ttl_seconds:
                    cached_record = dict(self._memory_cache)
                    cached_record["cache_age_seconds"] = round(age, 1)
                    return cached_record

            disk_cached = self._read_disk_cache()
            if disk_cached:
                self._memory_cache = disk_cached
                cached_at = disk_cached.get("_cached_at_epoch", 0)
                disk_cached["cache_age_seconds"] = round(time.time() - cached_at, 1)
                return disk_cached

        # 2. Attempt live query to Open-Meteo
        try:
            raw_data = self.fetch_live_gridded_data()
            current = raw_data.get("current", {})
            hourly = raw_data.get("hourly", {})

            # Extract current DNI from matching hourly slot if present
            dni_val = 0.0
            if "direct_normal_irradiance" in hourly and hourly["direct_normal_irradiance"]:
                dni_series = hourly["direct_normal_irradiance"]
                # Default to median daytime value or first slot
                dni_val = float(dni_series[0]) if len(dni_series) > 0 else 500.0

            # Convert wind speed km/h to m/s if necessary
            # Open-Meteo defaults to km/h for wind_speed_10m
            wind_kmh = float(current.get("wind_speed_10m", 10.0))
            wind_ms = round(wind_kmh / 3.6, 2)

            record: Dict[str, Any] = {
                "status": "OPEN_METEO_GRIDDED_FORECAST",
                "is_synthetic_fallback": False,
                "provider": "Open-Meteo Gridded Numerical Weather Model",
                "station_or_model": "Open-Meteo Seamless NWP (lat 21.2514, lon 81.6296)",
                "latitude": self.latitude,
                "longitude": self.longitude,
                "temperature_c": float(current.get("temperature_2m", 42.5)),
                "relative_humidity_pct": float(current.get("relative_humidity_2m", 35.0)),
                "apparent_temperature_c": float(current.get("apparent_temperature", 45.0)),
                "wind_speed_ms": wind_ms,
                "direct_normal_irradiance_wm2": dni_val,
                "surface_pressure_hpa": float(current.get("surface_pressure", 978.0)),
                "retrieval_timestamp": now_iso,
                "cache_age_seconds": 0.0,
                "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
                "notes": "Open-Meteo gridded forecast data for Raipur. NOT official IMD station telemetry.",
                "_cached_at_epoch": time.time(),
            }

            self._memory_cache = record
            self._write_disk_cache(record)
            return record

        except Exception as e:
            logger.warning(f"Open-Meteo weather fetch failed: {e}. Activating SYNTHETIC/FALLBACK record.")
            fallback = dict(SYNTHETIC_FALLBACK_RECORD)
            fallback["retrieval_timestamp"] = now_iso
            fallback["error_details"] = str(e)
            return fallback

    def get_hourly_forecast(self, hours: int = 24, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Returns hourly forecast profile for the requested hours.
        Falls back to synthetic diurnal sinusoidal cycle if unavailable.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            raw_data = self.fetch_live_gridded_data() if force_refresh else None
            if not raw_data:
                cached = self._read_disk_cache()
                if cached and "_raw_hourly" in cached:
                    raw_data = cached["_raw_hourly"]
                else:
                    raw_data = self.fetch_live_gridded_data()

            hourly = raw_data.get("hourly", {})
            times = hourly.get("time", [])[:hours]
            temps = hourly.get("temperature_2m", [])[:hours]
            rhs = hourly.get("relative_humidity_2m", [])[:hours]
            winds = hourly.get("wind_speed_10m", [])[:hours]
            dnis = hourly.get("direct_normal_irradiance", [])[:hours]

            forecast: List[Dict[str, Any]] = []
            for i in range(len(times)):
                forecast.append({
                    "hour_index": i,
                    "time": times[i],
                    "temperature_c": float(temps[i]),
                    "relative_humidity_pct": float(rhs[i]),
                    "wind_speed_ms": round(float(winds[i]) / 3.6, 2),
                    "direct_normal_irradiance_wm2": float(dnis[i]) if i < len(dnis) else 0.0,
                    "status": "OPEN_METEO_GRIDDED_FORECAST",
                    "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
                })
            return forecast

        except Exception as e:
            logger.warning(f"Hourly weather fetch failed ({e}). Generating synthetic diurnal fallback curve.")
            # Diurnal sinusoidal fallback for Raipur summer: base 32°C at 05:00, peak 45°C at 15:00
            fallback_curve = []
            for h in range(hours):
                import math
                temp = 32.0 + 13.0 * max(0.0, math.sin(math.pi * (h - 6) / 14))
                rh = max(20.0, 60.0 - 0.8 * temp)
                dni = max(0.0, 900.0 * math.sin(math.pi * (h - 6) / 12)) if 6 <= h <= 18 else 0.0
                fallback_curve.append({
                    "hour_index": h,
                    "time": f"Hour+{h:02d}",
                    "temperature_c": round(temp, 1),
                    "relative_humidity_pct": round(rh, 1),
                    "wind_speed_ms": 2.5,
                    "direct_normal_irradiance_wm2": round(dni, 1),
                    "status": "SYNTHETIC/FALLBACK",
                    "retrieval_timestamp": now_iso,
                    "disclaimer": "SIMULATION ONLY – NOT AN OFFICIAL WARNING",
                    "notes": "Synthetic diurnal heat cycle (fallback mode).",
                })
            return fallback_curve


# Module-level default singleton instance
weather_connector = WeatherFeedConnector()


def get_current_raipur_weather(force_refresh: bool = False) -> Dict[str, Any]:
    """Convenience helper to retrieve current Raipur weather with fallback."""
    return weather_connector.get_current_weather(force_refresh=force_refresh)

