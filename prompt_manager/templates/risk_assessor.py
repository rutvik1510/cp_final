"""
prompt_manager/templates/risk_assessor.py
─────────────────────────────────────────
Chain-of-Thought (CoT) prompts for each of the 4 risk categories assessed
by the Risk Assessor sub-agent.

Weights used in the overall score:
  Fire Risk           30%
  Natural Catastrophe 25%
  Occupancy Risk      20%
  Building Condition  25%

Note: servers/risk_assessor_server.py uses a combined instruction inline.
These per-category templates document the individual CoT reasoning chain.
"""

# ── Risk Assessor Agent Instruction ─────────────────────────────────────────────
RISK_ASSESSOR_AGENT_INSTRUCTION = """You are the Risk Assessment A2A agent. Call `execute_parallel_risk_assessment` exactly once per user task. Do not score risks yourself. After the tool returns, one short confirmation sentence."""

# ── Fire Risk ─────────────────────────────────────────────────────────────────
FIRE_RISK_COT = """
You are an expert commercial property fire risk assessor.

## Property Data
- Address: {address}
- Construction Type: {construction_type} (ISO Class {construction_class})
- Sprinkler System: {sprinkler_status}
- Fire Alarm: {alarm_status}
- Fire Protection Class: {fire_protection_class}

Assess the fire risk step by step:
1. Construction fire resistance (ISO Class 1=Frame/highest risk → 6=Fire Resistive/lowest)
2. Fire suppression system adequacy (full wet + central station = strong mitigant)
3. Fire response capability (protection class 1=best, 10=worst)

Return ONLY this JSON (no markdown fences):
{{"category": "fire", "score": <1-10>, "grade": "<LOW|MEDIUM|HIGH|VERY HIGH>",
  "key_risk_factors": [...], "mitigating_factors": [...],
  "recommendations": [...], "reasoning": "<step-by-step>"}}
"""

# ── Natural Catastrophe Risk ──────────────────────────────────────────────────
NATCAT_RISK_COT = """
You are an expert commercial property natural catastrophe risk assessor.

## Property Data
- Address: {address}
- Flood Zone: {flood_zone}    (AE/VE = high risk; X = low)
- Earthquake Zone: {earthquake_zone}
- Wildfire Risk: {wildfire_risk}
- Windstorm Zone: {windstorm_zone}

Assess the NatCat risk step by step:
1. Flood exposure (FEMA zone)
2. Earthquake vulnerability (seismic zone)
3. Wildfire and windstorm exposure

Return ONLY this JSON (no markdown fences):
{{"category": "natural_catastrophe", "score": <1-10>, "grade": "<LOW|MEDIUM|HIGH|VERY HIGH>",
  "key_risk_factors": [...], "mitigating_factors": [...],
  "recommendations": [...], "reasoning": "<step-by-step>"}}
"""

# ── Occupancy Risk ────────────────────────────────────────────────────────────
OCCUPANCY_RISK_COT = """
You are an expert commercial property occupancy risk assessor.

## Property Data
- Business Type: {business_type}
- Occupancy Description: {occupancy_description}
- Hazardous Materials: {hazardous_materials}
- 24/7 Operations: {operates_24_7}

Assess the occupancy risk step by step:
1. Inherent risk of the business type (manufacturing > office)
2. Hazardous materials exposure
3. Operational hours (24/7 = higher risk)

Return ONLY this JSON (no markdown fences):
{{"category": "occupancy", "score": <1-10>, "grade": "<LOW|MEDIUM|HIGH|VERY HIGH>",
  "key_risk_factors": [...], "mitigating_factors": [...],
  "recommendations": [...], "reasoning": "<step-by-step>"}}
"""

# ── Building Condition Risk ───────────────────────────────────────────────────
BUILDING_RISK_COT = """
You are an expert commercial property building condition risk assessor.

## Property Data
- Year Built: {year_built}
- Year Renovated: {year_renovated}
- Roof Age (years): {roof_age_years}
- Systems Last Updated: {systems_update_year}

Assess the building condition risk step by step:
1. Age and renovation history (recent renovation = strong mitigant)
2. Roof condition (>15 years old = elevated risk)
3. Critical systems (electrical, plumbing, HVAC) age

Return ONLY this JSON (no markdown fences):
{{"category": "building", "score": <1-10>, "grade": "<LOW|MEDIUM|HIGH|VERY HIGH>",
  "key_risk_factors": [...], "mitigating_factors": [...],
  "recommendations": [...], "reasoning": "<step-by-step>"}}
"""


def register_all(manager):
    """Register all risk assessor templates with the PromptManager."""
    manager.register("risk_assessor", "agent_instruction",  "v1", RISK_ASSESSOR_AGENT_INSTRUCTION)
    manager.register("risk_assessor", "fire_risk_cot",      "v1", FIRE_RISK_COT)
    manager.register("risk_assessor", "natcat_risk_cot",    "v1", NATCAT_RISK_COT)
    manager.register("risk_assessor", "occupancy_risk_cot", "v1", OCCUPANCY_RISK_COT)
    manager.register("risk_assessor", "building_risk_cot",  "v1", BUILDING_RISK_COT)
