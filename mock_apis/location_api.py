"""
mock_apis/location_api.py
─────────────────────────
Simulates a Location Context API (e.g., ISO fire protection data, local government APIs).
Returns fire protection class, fire station distance, and crime index for a given address.

Used by: data_collector_server.py → lookup_location(address)
"""


def lookup_location_context(address: str) -> dict:
    """
    Simulated location context API.
    Returns fire protection class, fire station distance, crime index.
    In a real system this would call ISO, local government APIs, etc.
    """
    addr_lower = address.lower()

    # City-based location profiles
    if "houston" in addr_lower or "tx" in addr_lower:
        return {"fire_protection_class": 3, "fire_station_distance_miles": 1.2, "nearest_hydrant_feet": 300, "crime_index": 42}
    if "chicago" in addr_lower or "il" in addr_lower:
        return {"fire_protection_class": 1, "fire_station_distance_miles": 0.3, "nearest_hydrant_feet": 100, "crime_index": 55}
    if "detroit" in addr_lower or "mi" in addr_lower:
        return {"fire_protection_class": 6, "fire_station_distance_miles": 3.8, "nearest_hydrant_feet": 800, "crime_index": 78}
    if "miami" in addr_lower or "fl" in addr_lower:
        return {"fire_protection_class": 2, "fire_station_distance_miles": 0.8, "nearest_hydrant_feet": 200, "crime_index": 61}
    if "san jose" in addr_lower or "ca" in addr_lower:
        return {"fire_protection_class": 2, "fire_station_distance_miles": 0.9, "nearest_hydrant_feet": 150, "crime_index": 38}
    if "new orleans" in addr_lower or "la" in addr_lower:
        return {"fire_protection_class": 5, "fire_station_distance_miles": 2.1, "nearest_hydrant_feet": 600, "crime_index": 82}
    if "portland" in addr_lower or "or" in addr_lower:
        return {"fire_protection_class": 4, "fire_station_distance_miles": 1.9, "nearest_hydrant_feet": 400, "crime_index": 45}
    if "new york" in addr_lower or "ny" in addr_lower:
        return {"fire_protection_class": 1, "fire_station_distance_miles": 0.1, "nearest_hydrant_feet": 50, "crime_index": 48}

    # Default — suburban average
    return {"fire_protection_class": 4, "fire_station_distance_miles": 2.0, "nearest_hydrant_feet": 400, "crime_index": 50}
