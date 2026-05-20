"""Internal parallel risk scoring (GenAI); used only by the risk A2A server."""
from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any

from google.genai import Client
from prompt_manager.manager import PromptManager
from prompt_manager.templates import risk_assessor

pm = PromptManager()
risk_assessor.register_all(pm)

MODEL_ID = "gemini-2.5-flash"


def _genai_client() -> Client:
    if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true":
        return Client(
            vertexai=True,
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION")
        )
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY must be set for risk assessment.")
    return Client(api_key=key)


def _parse_json_object(text: str) -> dict[str, Any] | None:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    try:
        return json.loads(text)
    except Exception:
        return None


def _category_prompt(category: str, property_data: dict[str, Any]) -> str:
    vars_dict = {"address": "unknown"}
    if isinstance(property_data.get("address"), dict):
        vars_dict["address"] = property_data["address"].get("street", "unknown")
    elif isinstance(property_data.get("address"), str):
        vars_dict["address"] = property_data["address"]
        
    chars = property_data.get("characteristics", {})
    vars_dict["construction_type"] = chars.get("construction_type", "unknown")
    vars_dict["construction_class"] = chars.get("construction_class", "unknown")
    vars_dict["sprinkler_status"] = chars.get("sprinkler_status", "unknown")
    vars_dict["alarm_status"] = chars.get("alarm_status", "unknown")
    vars_dict["fire_protection_class"] = chars.get("fire_protection_class", "unknown")
    
    loc = property_data.get("location_context", {})
    vars_dict["flood_zone"] = loc.get("flood_zone", "unknown")
    vars_dict["earthquake_zone"] = loc.get("earthquake_zone", "unknown")
    vars_dict["wildfire_risk"] = loc.get("wildfire_risk", "unknown")
    vars_dict["windstorm_zone"] = loc.get("windstorm_zone", "unknown")
    
    occ = property_data.get("occupancy", {})
    vars_dict["business_type"] = occ.get("business_type", "unknown")
    vars_dict["occupancy_description"] = occ.get("occupancy_description", "unknown")
    vars_dict["hazardous_materials"] = occ.get("hazardous_materials", "unknown")
    vars_dict["operates_24_7"] = occ.get("operates_24_7", "unknown")
    
    vars_dict["year_built"] = chars.get("year_built", "unknown")
    vars_dict["year_renovated"] = chars.get("year_renovated", "unknown")
    vars_dict["roof_age_years"] = chars.get("roof_age_years", "unknown")
    vars_dict["systems_update_year"] = chars.get("systems_update_year", "unknown")

    template_name_map = {
        "fire": "fire_risk_cot",
        "natural_catastrophe": "natcat_risk_cot",
        "occupancy": "occupancy_risk_cot",
        "building": "building_risk_cot"
    }
    t_name = template_name_map[category]
    return pm.get_prompt("risk_assessor", t_name, variables=vars_dict)


async def _evaluate_category(client: Client, category: str, property_data: dict[str, Any]) -> dict[str, Any]:
    prompt = _category_prompt(category, property_data)
    resp = await client.aio.models.generate_content(model=MODEL_ID, contents=prompt)
    text = getattr(resp, "text", None) or ""
    if not text and getattr(resp, "candidates", None):
        try:
            cand = resp.candidates[0]
            if cand.content and cand.content.parts:
                text = cand.content.parts[0].text or ""
        except Exception:
            pass
    parsed = _parse_json_object(text)
    if not parsed or "score" not in parsed:
        return {
            "category": category,
            "score": 5,
            "grade": "MEDIUM",
            "key_risk_factors": ["Assessment parse failure — defaulted"],
            "mitigating_factors": [],
            "recommendations": ["Re-run assessment"],
            "reasoning": "The model output could not be parsed as JSON.",
        }
    return parsed


def _weighted_overall(individual: list[dict[str, Any]]) -> tuple[float, str]:
    weights = {
        "fire": 0.30,
        "natural_catastrophe": 0.25,
        "occupancy": 0.20,
        "building": 0.25,
    }
    total = 0.0
    wsum = 0.0
    for row in individual:
        cat = row.get("category", "")
        w = weights.get(cat, 0.25)
        try:
            sc = float(row.get("score", 5))
        except Exception:
            sc = 5.0
        total += w * sc
        wsum += w
    overall = round(total / wsum, 2) if wsum else 5.0
    if overall <= 3:
        g = "LOW"
    elif overall <= 6:
        g = "MEDIUM"
    elif overall <= 8:
        g = "HIGH"
    else:
        g = "VERY HIGH"
    return overall, g


async def run_parallel_category_assessments(property_data: dict[str, Any]) -> dict[str, Any]:
    client = _genai_client()
    cats = ("fire", "natural_catastrophe", "occupancy", "building")
    rows = await asyncio.gather(*(_evaluate_category(client, c, property_data) for c in cats))
    overall_score, overall_grade = _weighted_overall(list(rows))
    return {
        "individual_scores": list(rows),
        "overall_score": overall_score,
        "overall_grade": overall_grade,
    }
