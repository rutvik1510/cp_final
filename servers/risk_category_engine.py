"""Internal parallel risk scoring (GenAI); used only by the risk A2A server."""
from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any

from google.genai import Client

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


def _category_prompt(category: str, property_json: str) -> str:
    common = (
        f"You assess ONLY the **{category}** risk for commercial property underwriting.\n"
        f"Property JSON:\n{property_json}\n\n"
        "Return STRICT JSON only (no markdown fences), one object with keys:\n"
        '{"category": "<id>", "score": <1-10 int>, "grade": "<LOW|MEDIUM|HIGH|VERY HIGH>", '
        '"key_risk_factors": ["<=3 short"], "mitigating_factors": ["<=3 short"], '
        '"recommendations": ["<=2 short"], "reasoning": "<=2 sentences>"}\n'
    )
    guides = {
        "fire": (
            "Focus: construction_type, construction_class, sprinkler_status, fire_alarm, "
            "fire_protection_class. ISO Class 1=frame highest risk; wet sprinklers + alarm mitigate."
        ),
        "natural_catastrophe": (
            "Focus: flood_zone, earthquake_zone, wildfire_risk, windstorm_zone. "
            "Flood AE/VE higher; X lower."
        ),
        "occupancy": (
            "Focus: business_type, hazardous_materials, operates_24_7. "
            "Manufacturing + hazmat higher; office lower."
        ),
        "building": (
            "Focus: year_built, year_renovated, roof_age_years. Old + no renovation higher."
        ),
    }
    return common + guides[category] + f'\nUse "category": "{category}".'


async def _evaluate_category(client: Client, category: str, property_data: dict[str, Any]) -> dict[str, Any]:
    prompt = _category_prompt(category, json.dumps(property_data))
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
