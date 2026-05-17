"""
mock_apis/hazard_api.py
───────────────────────
Simulates a Natural Hazard Data API (e.g., FEMA flood maps, USGS seismic data).
Returns hazard zone classifications based on geographic coordinates (lat/lon).

Used by: data_collector_server.py → lookup_hazards(lat, lon)
"""


def lookup_natural_hazards(lat: float, lon: float) -> dict:
    """
    Simulated natural hazard data API.
    Returns hazard zone data based on geographic coordinates.
    In a real system this would call FEMA, USGS, etc.
    """
    # Approximate region-based hazard profiles
    # Gulf Coast / Florida (high windstorm/flood)
    if 24 <= lat <= 31 and -98 <= lon <= -80:
        return {
            "flood_zone": "AE",
            "earthquake_zone": "low",
            "wildfire_risk": "none",
            "windstorm_zone": "high",
            "storm_surge_zone": "moderate"
        }
    # California (earthquake)
    if 32 <= lat <= 42 and -125 <= lon <= -114:
        return {
            "flood_zone": "X",
            "earthquake_zone": "very_high",
            "wildfire_risk": "high",
            "windstorm_zone": "low",
            "storm_surge_zone": "none"
        }
    # Pacific Northwest (wildfire/earthquake)
    if 42 <= lat <= 49 and -125 <= lon <= -116:
        return {
            "flood_zone": "X",
            "earthquake_zone": "moderate",
            "wildfire_risk": "high",
            "windstorm_zone": "low",
            "storm_surge_zone": "none"
        }
    # Northeast / Mid-Atlantic
    if 38 <= lat <= 45 and -80 <= lon <= -70:
        return {
            "flood_zone": "X",
            "earthquake_zone": "low",
            "wildfire_risk": "none",
            "windstorm_zone": "moderate",
            "storm_surge_zone": "low"
        }
    # Midwest
    if 36 <= lat <= 48 and -98 <= lon <= -80:
        return {
            "flood_zone": "X",
            "earthquake_zone": "low",
            "wildfire_risk": "minimal",
            "windstorm_zone": "moderate",
            "storm_surge_zone": "none"
        }
    # Default — continental US average
    return {
        "flood_zone": "X",
        "earthquake_zone": "low",
        "wildfire_risk": "minimal",
        "windstorm_zone": "low",
        "storm_surge_zone": "none"
    }
