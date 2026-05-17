"""Premium recommendation logic used exclusively by the Report Generator A2A service."""


def compute_premium_recommendation(property_data: dict, risk_data: dict) -> dict:
    """Deterministic premium range from TIV, property type, and overall risk score."""
    tiv = property_data.get("insurance_details", {}).get("total_insured_value", 5_000_000)
    p_type = property_data.get("characteristics", {}).get("property_type", "office")
    base_rates = {"warehouse": 1.5, "office": 1.2, "manufacturing": 2.5, "retail": 1.8, "mixed_use": 2.0}
    base_rate = base_rates.get(str(p_type).lower(), 2.0)
    risk_score = risk_data.get("overall_score", 5.0)
    try:
        risk_score = float(risk_score)
    except Exception:
        risk_score = 5.0
    adj_rate = base_rate * (1 + (risk_score - 5) * 0.1)
    rec_prem = round((tiv * adj_rate) / 1000, 2)
    return {
        "adjusted_rate": round(adj_rate, 2),
        "recommended_premium": rec_prem,
        "premium_range": {"min": round(rec_prem * 0.9, 2), "max": round(rec_prem * 1.1, 2)},
    }
