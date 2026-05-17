import random

MOCK_PROPERTIES = {
    "123 industrial ave, houston, tx": {
        "property_id": "PROP-001",
        "address": {
            "street": "123 Industrial Ave",
            "city": "Houston",
            "state": "TX",
            "zip": "77001",
            "latitude": 29.7604,
            "longitude": -95.3698
        },
        "characteristics": {
            "property_type": "warehouse",
            "construction_type": "joisted_masonry",
            "construction_class": 3,
            "year_built": 1998,
            "year_renovated": 2015,
            "stories": 1,
            "sqft": 50000,
            "roof_type": "metal_deck",
            "roof_age_years": 9,
            "electrical_update_year": 2015,
            "plumbing_update_year": 2015,
            "hvac_update_year": 2018
        },
        "protection": {
            "sprinkler_status": "full_wet_system",
            "sprinkler_coverage_pct": 100,
            "fire_alarm": "central_station_monitored",
            "security_system": "cctv_with_guards",
            "access_control": "badge_entry",
            "backup_power": True
        },
        "occupancy": {
            "business_name": "GlobalTech Distribution LLC",
            "business_type": "wholesale_distribution",
            "occupancy_description": "Electronics and consumer goods distribution",
            "hazardous_materials": False,
            "operates_24_7": True,
            "employee_count": 150,
            "annual_revenue": 45000000
        },
        "location_context": {
            "fire_protection_class": 3,
            "fire_station_distance_miles": 1.2,
            "nearest_hydrant_feet": 300,
            "crime_index": 42,
            "flood_zone": "X",
            "earthquake_zone": "low",
            "wildfire_risk": "minimal",
            "windstorm_zone": "moderate",
            "coastal_distance_miles": 45
        },
        "loss_history": {
            "total_claims_5yr": 1,
            "total_loss_amount_5yr": 45000,
            "claims_free_years": 4,
            "prior_claims": [
                {"date": "2022-03-15", "type": "water_damage", "amount": 45000, "description": "Roof leak during heavy rain"}
            ]
        },
        "insurance_details": {
            "total_insured_value": 25000000,
            "building_value": 15000000,
            "contents_value": 8000000,
            "business_income_value": 2000000,
            "current_carrier": "National Insurance Co.",
            "current_premium": 62000,
            "policy_effective_date": "2026-07-01",
            "deductible": 25000
        }
    },
    "456 commerce blvd, chicago, il": {
        "property_id": "PROP-002",
        "address": {
            "street": "456 Commerce Blvd",
            "city": "Chicago",
            "state": "IL",
            "zip": "60601",
            "latitude": 41.8827,
            "longitude": -87.6233
        },
        "characteristics": {
            "property_type": "office",
            "construction_type": "fire_resistive",
            "construction_class": 6,
            "year_built": 2010,
            "year_renovated": 2021,
            "stories": 12,
            "sqft": 120000,
            "roof_type": "built_up",
            "roof_age_years": 3,
            "electrical_update_year": 2021,
            "plumbing_update_year": 2021,
            "hvac_update_year": 2021
        },
        "protection": {
            "sprinkler_status": "full_wet_system",
            "sprinkler_coverage_pct": 100,
            "fire_alarm": "central_station_monitored",
            "security_system": "cctv_24_7",
            "access_control": "keycard_biometric",
            "backup_power": True
        },
        "occupancy": {
            "business_name": "Midwestern Financial Services Inc.",
            "business_type": "financial_services",
            "occupancy_description": "Corporate office, financial services",
            "hazardous_materials": False,
            "operates_24_7": False,
            "employee_count": 450,
            "annual_revenue": 200000000
        },
        "location_context": {
            "fire_protection_class": 1,
            "fire_station_distance_miles": 0.3,
            "nearest_hydrant_feet": 100,
            "crime_index": 55,
            "flood_zone": "X",
            "earthquake_zone": "low",
            "wildfire_risk": "none",
            "windstorm_zone": "low",
            "coastal_distance_miles": 80
        },
        "loss_history": {
            "total_claims_5yr": 0,
            "total_loss_amount_5yr": 0,
            "claims_free_years": 5,
            "prior_claims": []
        },
        "insurance_details": {
            "total_insured_value": 45000000,
            "building_value": 38000000,
            "contents_value": 5000000,
            "business_income_value": 2000000,
            "current_carrier": "Great Lakes Mutual",
            "current_premium": 85000,
            "policy_effective_date": "2026-01-01",
            "deductible": 50000
        }
    },
    "789 factory rd, detroit, mi": {
        "property_id": "PROP-003",
        "address": {
            "street": "789 Factory Rd",
            "city": "Detroit",
            "state": "MI",
            "zip": "48201",
            "latitude": 42.3314,
            "longitude": -83.0458
        },
        "characteristics": {
            "property_type": "manufacturing",
            "construction_type": "frame",
            "construction_class": 1,
            "year_built": 1975,
            "year_renovated": 2005,
            "stories": 2,
            "sqft": 80000,
            "roof_type": "flat_gravel",
            "roof_age_years": 19,
            "electrical_update_year": 2005,
            "plumbing_update_year": 1998,
            "hvac_update_year": 2010
        },
        "protection": {
            "sprinkler_status": "partial_dry_system",
            "sprinkler_coverage_pct": 60,
            "fire_alarm": "local_alarm_only",
            "security_system": "basic_alarm",
            "access_control": "none",
            "backup_power": False
        },
        "occupancy": {
            "business_name": "Detroit Auto Parts Manufacturing",
            "business_type": "auto_parts_manufacturing",
            "occupancy_description": "Metal stamping and auto parts fabrication with industrial solvents",
            "hazardous_materials": True,
            "operates_24_7": True,
            "employee_count": 300,
            "annual_revenue": 75000000
        },
        "location_context": {
            "fire_protection_class": 6,
            "fire_station_distance_miles": 3.8,
            "nearest_hydrant_feet": 800,
            "crime_index": 78,
            "flood_zone": "AE",
            "earthquake_zone": "low",
            "wildfire_risk": "none",
            "windstorm_zone": "low",
            "coastal_distance_miles": 90
        },
        "loss_history": {
            "total_claims_5yr": 4,
            "total_loss_amount_5yr": 380000,
            "claims_free_years": 0,
            "prior_claims": [
                {"date": "2023-06-10", "type": "fire", "amount": 220000, "description": "Solvent fire in mixing area"},
                {"date": "2022-01-22", "type": "equipment_breakdown", "amount": 85000, "description": "Stamping press failure"},
                {"date": "2021-09-05", "type": "flood", "amount": 45000, "description": "Flash flooding from river overflow"},
                {"date": "2020-11-14", "type": "theft", "amount": 30000, "description": "Copper wire theft"}
            ]
        },
        "insurance_details": {
            "total_insured_value": 18000000,
            "building_value": 8000000,
            "contents_value": 7000000,
            "business_income_value": 3000000,
            "current_carrier": "Industrial Risk Insurers",
            "current_premium": 195000,
            "policy_effective_date": "2026-03-01",
            "deductible": 100000
        }
    },
    "101 retail plaza, miami, fl": {
        "property_id": "PROP-004",
        "address": {
            "street": "101 Retail Plaza",
            "city": "Miami",
            "state": "FL",
            "zip": "33101",
            "latitude": 25.7617,
            "longitude": -80.1918
        },
        "characteristics": {
            "property_type": "retail",
            "construction_type": "reinforced_concrete",
            "construction_class": 5,
            "year_built": 2005,
            "year_renovated": 2019,
            "stories": 2,
            "sqft": 65000,
            "roof_type": "concrete_slab",
            "roof_age_years": 7,
            "electrical_update_year": 2019,
            "plumbing_update_year": 2019,
            "hvac_update_year": 2019
        },
        "protection": {
            "sprinkler_status": "full_wet_system",
            "sprinkler_coverage_pct": 100,
            "fire_alarm": "central_station_monitored",
            "security_system": "cctv_with_guards",
            "access_control": "badge_entry",
            "backup_power": True
        },
        "occupancy": {
            "business_name": "SunCoast Retail Group LLC",
            "business_type": "retail_shopping_complex",
            "occupancy_description": "Mixed retail tenants — clothing, electronics, food court",
            "hazardous_materials": False,
            "operates_24_7": False,
            "employee_count": 200,
            "annual_revenue": 35000000
        },
        "location_context": {
            "fire_protection_class": 2,
            "fire_station_distance_miles": 0.8,
            "nearest_hydrant_feet": 200,
            "crime_index": 61,
            "flood_zone": "VE",
            "earthquake_zone": "low",
            "wildfire_risk": "none",
            "windstorm_zone": "very_high",
            "coastal_distance_miles": 2
        },
        "loss_history": {
            "total_claims_5yr": 2,
            "total_loss_amount_5yr": 195000,
            "claims_free_years": 2,
            "prior_claims": [
                {"date": "2022-09-28", "type": "hurricane_wind", "amount": 165000, "description": "Hurricane Ian roof and facade damage"},
                {"date": "2021-06-05", "type": "water_damage", "amount": 30000, "description": "HVAC condensation leak"}
            ]
        },
        "insurance_details": {
            "total_insured_value": 32000000,
            "building_value": 24000000,
            "contents_value": 6000000,
            "business_income_value": 2000000,
            "current_carrier": "Sunshine State Insurance",
            "current_premium": 145000,
            "policy_effective_date": "2026-06-01",
            "deductible": 75000
        }
    },
    "222 tech park dr, san jose, ca": {
        "property_id": "PROP-005",
        "address": {
            "street": "222 Tech Park Dr",
            "city": "San Jose",
            "state": "CA",
            "zip": "95101",
            "latitude": 37.3382,
            "longitude": -121.8863
        },
        "characteristics": {
            "property_type": "office",
            "construction_type": "steel_frame",
            "construction_class": 5,
            "year_built": 2015,
            "year_renovated": None,
            "stories": 4,
            "sqft": 95000,
            "roof_type": "membrane",
            "roof_age_years": 11,
            "electrical_update_year": 2015,
            "plumbing_update_year": 2015,
            "hvac_update_year": 2020
        },
        "protection": {
            "sprinkler_status": "full_wet_system",
            "sprinkler_coverage_pct": 100,
            "fire_alarm": "central_station_monitored",
            "security_system": "cctv_24_7",
            "access_control": "keycard_biometric",
            "backup_power": True
        },
        "occupancy": {
            "business_name": "SiliconValley Tech Corp",
            "business_type": "technology_company",
            "occupancy_description": "Software development and tech campus",
            "hazardous_materials": False,
            "operates_24_7": False,
            "employee_count": 600,
            "annual_revenue": 500000000
        },
        "location_context": {
            "fire_protection_class": 2,
            "fire_station_distance_miles": 0.9,
            "nearest_hydrant_feet": 150,
            "crime_index": 38,
            "flood_zone": "X",
            "earthquake_zone": "very_high",
            "wildfire_risk": "moderate",
            "windstorm_zone": "low",
            "coastal_distance_miles": 35
        },
        "loss_history": {
            "total_claims_5yr": 1,
            "total_loss_amount_5yr": 22000,
            "claims_free_years": 4,
            "prior_claims": [
                {"date": "2021-10-20", "type": "earthquake_damage", "amount": 22000, "description": "Minor structural cracks from M4.2 earthquake"}
            ]
        },
        "insurance_details": {
            "total_insured_value": 58000000,
            "building_value": 48000000,
            "contents_value": 8000000,
            "business_income_value": 2000000,
            "current_carrier": "Pacific Rim Insurance",
            "current_premium": 175000,
            "policy_effective_date": "2026-01-01",
            "deductible": 100000
        }
    },
    "333 harbor way, new orleans, la": {
        "property_id": "PROP-006",
        "address": {
            "street": "333 Harbor Way",
            "city": "New Orleans",
            "state": "LA",
            "zip": "70112",
            "latitude": 29.9511,
            "longitude": -90.0715
        },
        "characteristics": {
            "property_type": "warehouse",
            "construction_type": "joisted_masonry",
            "construction_class": 3,
            "year_built": 1962,
            "year_renovated": 2010,
            "stories": 1,
            "sqft": 40000,
            "roof_type": "metal_deck",
            "roof_age_years": 14,
            "electrical_update_year": 2010,
            "plumbing_update_year": 2010,
            "hvac_update_year": 2015
        },
        "protection": {
            "sprinkler_status": "none",
            "sprinkler_coverage_pct": 0,
            "fire_alarm": "smoke_detectors_only",
            "security_system": "basic_alarm",
            "access_control": "none",
            "backup_power": False
        },
        "occupancy": {
            "business_name": "Bayou Freight Services",
            "business_type": "freight_storage",
            "occupancy_description": "General merchandise and freight storage near port",
            "hazardous_materials": False,
            "operates_24_7": False,
            "employee_count": 35,
            "annual_revenue": 8000000
        },
        "location_context": {
            "fire_protection_class": 5,
            "fire_station_distance_miles": 2.1,
            "nearest_hydrant_feet": 600,
            "crime_index": 82,
            "flood_zone": "AE",
            "earthquake_zone": "low",
            "wildfire_risk": "none",
            "windstorm_zone": "high",
            "coastal_distance_miles": 5
        },
        "loss_history": {
            "total_claims_5yr": 3,
            "total_loss_amount_5yr": 420000,
            "claims_free_years": 0,
            "prior_claims": [
                {"date": "2021-08-29", "type": "hurricane_wind", "amount": 280000, "description": "Hurricane Ida severe roof damage"},
                {"date": "2021-09-01", "type": "flood", "amount": 120000, "description": "Post-Ida flooding, inventory loss"},
                {"date": "2023-05-12", "type": "theft", "amount": 20000, "description": "Cargo theft from loading dock"}
            ]
        },
        "insurance_details": {
            "total_insured_value": 9500000,
            "building_value": 5000000,
            "contents_value": 3500000,
            "business_income_value": 1000000,
            "current_carrier": "Gulf Coast Mutual",
            "current_premium": 98000,
            "policy_effective_date": "2026-09-01",
            "deductible": 50000
        }
    },
    "444 mill creek rd, portland, or": {
        "property_id": "PROP-007",
        "address": {
            "street": "444 Mill Creek Rd",
            "city": "Portland",
            "state": "OR",
            "zip": "97201",
            "latitude": 45.5051,
            "longitude": -122.6750
        },
        "characteristics": {
            "property_type": "manufacturing",
            "construction_type": "ordinary",
            "construction_class": 2,
            "year_built": 1988,
            "year_renovated": 2018,
            "stories": 1,
            "sqft": 55000,
            "roof_type": "metal",
            "roof_age_years": 6,
            "electrical_update_year": 2018,
            "plumbing_update_year": 2012,
            "hvac_update_year": 2018
        },
        "protection": {
            "sprinkler_status": "full_wet_system",
            "sprinkler_coverage_pct": 100,
            "fire_alarm": "central_station_monitored",
            "security_system": "cctv_with_guards",
            "access_control": "badge_entry",
            "backup_power": False
        },
        "occupancy": {
            "business_name": "Pacific Northwest Wood Products",
            "business_type": "wood_products_manufacturing",
            "occupancy_description": "Furniture and wood products manufacturing",
            "hazardous_materials": True,
            "operates_24_7": False,
            "employee_count": 180,
            "annual_revenue": 28000000
        },
        "location_context": {
            "fire_protection_class": 4,
            "fire_station_distance_miles": 1.9,
            "nearest_hydrant_feet": 400,
            "crime_index": 45,
            "flood_zone": "X",
            "earthquake_zone": "moderate",
            "wildfire_risk": "high",
            "windstorm_zone": "low",
            "coastal_distance_miles": 70
        },
        "loss_history": {
            "total_claims_5yr": 1,
            "total_loss_amount_5yr": 65000,
            "claims_free_years": 3,
            "prior_claims": [
                {"date": "2022-08-18", "type": "fire", "amount": 65000, "description": "Sawdust fire in manufacturing area, contained by sprinklers"}
            ]
        },
        "insurance_details": {
            "total_insured_value": 14000000,
            "building_value": 7000000,
            "contents_value": 5000000,
            "business_income_value": 2000000,
            "current_carrier": "Northwest Industrial Insurance",
            "current_premium": 112000,
            "policy_effective_date": "2026-08-01",
            "deductible": 50000
        }
    },
    "555 downtown st, new york, ny": {
        "property_id": "PROP-008",
        "address": {
            "street": "555 Downtown St",
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "characteristics": {
            "property_type": "mixed_use",
            "construction_type": "fire_resistive",
            "construction_class": 6,
            "year_built": 1948,
            "year_renovated": 2008,
            "stories": 18,
            "sqft": 200000,
            "roof_type": "built_up",
            "roof_age_years": 16,
            "electrical_update_year": 2008,
            "plumbing_update_year": 2008,
            "hvac_update_year": 2015
        },
        "protection": {
            "sprinkler_status": "partial_wet_system",
            "sprinkler_coverage_pct": 75,
            "fire_alarm": "central_station_monitored",
            "security_system": "cctv_24_7",
            "access_control": "keycard_entry",
            "backup_power": True
        },
        "occupancy": {
            "business_name": "Manhattan Property Holdings LLC",
            "business_type": "mixed_use_commercial_residential",
            "occupancy_description": "Ground floor retail, upper floors office and residential",
            "hazardous_materials": False,
            "operates_24_7": True,
            "employee_count": 80,
            "annual_revenue": 12000000
        },
        "location_context": {
            "fire_protection_class": 1,
            "fire_station_distance_miles": 0.1,
            "nearest_hydrant_feet": 50,
            "crime_index": 48,
            "flood_zone": "AE",
            "earthquake_zone": "low",
            "wildfire_risk": "none",
            "windstorm_zone": "moderate",
            "coastal_distance_miles": 3
        },
        "loss_history": {
            "total_claims_5yr": 2,
            "total_loss_amount_5yr": 88000,
            "claims_free_years": 2,
            "prior_claims": [
                {"date": "2021-04-12", "type": "water_damage", "amount": 65000, "description": "Burst pipe on 12th floor, water damage to multiple floors"},
                {"date": "2023-11-08", "type": "vandalism", "amount": 23000, "description": "Ground floor window and facade vandalism"}
            ]
        },
        "insurance_details": {
            "total_insured_value": 85000000,
            "building_value": 72000000,
            "contents_value": 10000000,
            "business_income_value": 3000000,
            "current_carrier": "Empire State Insurance Group",
            "current_premium": 290000,
            "policy_effective_date": "2026-02-01",
            "deductible": 100000
        }
    }
}


def generate_default_property(address: str) -> dict:
    """Generate reasonable default property data for unknown addresses."""
    return {
        "property_id": f"PROP-GEN-{abs(hash(address)) % 9000 + 1000}",
        "address": {
            "street": address,
            "city": "Unknown",
            "state": "XX",
            "zip": "00000",
            "latitude": 39.8283,
            "longitude": -98.5795
        },
        "characteristics": {
            "property_type": "office",
            "construction_type": "ordinary",
            "construction_class": 2,
            "year_built": 1995,
            "year_renovated": 2010,
            "stories": 2,
            "sqft": 25000,
            "roof_type": "flat",
            "roof_age_years": 14,
            "electrical_update_year": 2010,
            "plumbing_update_year": 2010,
            "hvac_update_year": 2012
        },
        "protection": {
            "sprinkler_status": "full_wet_system",
            "sprinkler_coverage_pct": 100,
            "fire_alarm": "central_station_monitored",
            "security_system": "basic_cctv",
            "access_control": "none",
            "backup_power": False
        },
        "occupancy": {
            "business_name": "Unknown Tenant",
            "business_type": "general_office",
            "occupancy_description": "General commercial office use",
            "hazardous_materials": False,
            "operates_24_7": False,
            "employee_count": 50,
            "annual_revenue": 5000000
        },
        "location_context": {
            "fire_protection_class": 4,
            "fire_station_distance_miles": 2.0,
            "nearest_hydrant_feet": 400,
            "crime_index": 50,
            "flood_zone": "X",
            "earthquake_zone": "low",
            "wildfire_risk": "minimal",
            "windstorm_zone": "low",
            "coastal_distance_miles": 100
        },
        "loss_history": {
            "total_claims_5yr": 0,
            "total_loss_amount_5yr": 0,
            "claims_free_years": 5,
            "prior_claims": []
        },
        "insurance_details": {
            "total_insured_value": 5000000,
            "building_value": 3500000,
            "contents_value": 1000000,
            "business_income_value": 500000,
            "current_carrier": "General Commercial Insurance",
            "current_premium": 15000,
            "policy_effective_date": "2026-01-01",
            "deductible": 10000
        }
    }


def lookup_property_characteristics(address: str) -> dict:
    """Robust lookup for mock properties. Falls back to generated defaults for unknown addresses."""
    address_clean = address.lower().replace(",", "").replace(".", "").strip()
    for key, data in MOCK_PROPERTIES.items():
        key_parts = key.split(",")
        # Match on street number + street name (first part)
        if key_parts[0].strip() in address_clean or address_clean.startswith(key_parts[0].strip()):
            return data
        # Also try full key match
        if key in address_clean or address_clean in key:
            return data
    # Fallback: generate reasonable defaults so demo never hard-errors
    return generate_default_property(address)


def lookup_loss_history(property_id: str, insured_name: str) -> dict:
    """Returns loss history for a property by ID."""
    for data in MOCK_PROPERTIES.values():
        if data["property_id"] == property_id:
            return data["loss_history"]
    return {"total_claims_5yr": 0, "total_loss_amount_5yr": 0, "claims_free_years": 5, "prior_claims": []}
