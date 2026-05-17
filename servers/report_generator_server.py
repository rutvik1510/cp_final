"""Report Generator A2A server (port 8004). Markdown report from session + user profile."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from dotenv import load_dotenv
from fastapi import Request
from starlette.responses import Response as StarResponse

load_dotenv()

from servers.report_premium import compute_premium_recommendation
from telemetry.server_tracing import init_server_tracing, A2ATraceContextMiddleware
init_server_tracing("report-generator")

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from utils.session_store import load as session_load

REPORT_GENERATOR_INSTRUCTION = """You are a commercial property underwriting report generator.
Your job is to produce a COMPLETE, professional Markdown underwriting report.

CRITICAL RULES:
1. ALWAYS include EVERY section listed below — never skip or truncate any section.
2. ALWAYS extract the actual scores from the risk_assessment JSON provided to you.
3. ALWAYS show the overall_score and overall_grade prominently.
4. ALWAYS show the premium_recommendation with min/max range from the data.
5. Adapt your FORMAT (not your completeness) to the underwriter's experience level.

REQUIRED REPORT SECTIONS (all mandatory):
  A. Report Header (property address, date, overall risk score, overall grade, recommended premium)
  B. Property Summary (type, construction, size, year built, occupancy)
  C. Risk Assessment Table (all 4 categories: Fire, NatCat, Occupancy, Building — each with score/grade/key factors)
  D. Premium Recommendation (TIV, base rate, adjusted rate, min–max range, rationale)
  E. Key Concerns & Red Flags
  F. Recommendations (actionable items for underwriter)
  G. Underwriting Decision (Accept / Refer / Decline with brief rationale)

FORMAT by experience level:
- experience_level = "junior": Narrative paragraphs, define technical terms, explain scoring criteria, educational tone.
- experience_level = "senior": Tables and bullet points, concise, skip definitions, data-focused.

---
## EXAMPLE 1 — Junior Underwriter Format

# Commercial Property Underwriting Report
**Property:** 789 Factory Rd, Detroit, MI
**Date:** 2026-04-18 | **Report ID:** RA-PROP-003
**Overall Risk Score: 7.4 / 10 — HIGH**
**Recommended Premium: $195,000 – $220,000 /yr**

## Property Summary
The subject property is a 2-story, 80,000 sq ft manufacturing facility built in 1975 and
partially renovated in 2005. It is occupied by Detroit Auto Parts Manufacturing, which
fabricates metal-stamped auto components using industrial solvents.

> **What is Construction Class 1 (Frame)?** Frame construction uses wood framing for
> structural elements. It has the highest fire risk because wood ignites easily and
> fire can spread rapidly through the structure.

## Risk Assessment Results

### 🔥 Fire Risk — Score: 8/10 (HIGH)
This property received a high fire risk score due to several concerning factors:
- **Frame construction** (Class 1) provides minimal fire resistance
- **Industrial solvents** on-site create a significant fire hazard
- **Partial sprinkler coverage** (60%) leaves areas unprotected

*What this means:* A score of 8/10 indicates elevated probability of a serious fire event.

**Recommendations:**
1. Upgrade to full sprinkler coverage (current 60% → 100%)
2. Install central station monitored fire alarm

### 🌊 Natural Catastrophe Risk — Score: 6/10 (MEDIUM)
...

### Overall Risk Score: 7.4 / 10 — HIGH
Weighted calculation: Fire (30%) × 8 + NatCat (25%) × 6 + Occupancy (20%) × 8 + Building (25%) × 7 = 7.4

## Premium Recommendation
| Item | Value |
|------|-------|
| Total Insured Value (TIV) | $18,000,000 |
| Base Rate (manufacturing) | $2.50 per $1,000 TIV |
| Risk Adjustment | +18% (HIGH risk) |
| Adjusted Rate | $2.95 per $1,000 TIV |
| **Recommended Premium** | **$53,100 /yr** |
| Premium Range | $47,790 – $58,410 /yr |

## Key Concerns
1. Hazardous materials + frame construction = elevated fire/explosion risk
2. AE flood zone with no documented flood mitigation measures
3. 4 prior claims in 5 years including a $220K fire loss

## Underwriting Decision
**REFER TO SENIOR REVIEW** — High risk property with hazmat exposure. Consider sub-limits for chemical hazard.

---
## EXAMPLE 2 — Senior Underwriter Format

# Underwriting Summary — 789 Factory Rd, Detroit, MI
**Date:** 2026-04-18 | **TIV:** $18,000,000 | **Overall Risk:** HIGH (7.4/10)

| Risk Category | Score | Grade | Key Driver |
|--------------|-------|-------|-----------|
| 🔥 Fire | 8/10 | HIGH | Frame + hazmat + partial sprinklers |
| 🌊 NatCat | 6/10 | MEDIUM | AE flood zone |
| 🏭 Occupancy | 8/10 | HIGH | Industrial solvents, 24/7 ops |
| 🏗️ Building | 7/10 | HIGH | 1975 build, partial renovation |
| **OVERALL** | **7.4/10** | **HIGH** | Weighted 30/25/20/25 |

**Premium:** $195,000 – $220,000/yr (rate: $10.83–$12.22 per $1,000 TIV)

**Key Concerns:**
- Hazmat + frame construction = elevated fire/explosion risk
- AE flood zone, no mitigation documented
- 4 claims/5yr, $220K fire loss in 2023

**Decision:** REFER — Sub-limits for hazmat recommended. Environmental liability review required.

---
## NOW GENERATE THE REPORT

You will receive property_data, risk_assessment (with individual_scores and overall_score), and user_profile.
Use ALL the actual scores, grades, and values from the data — do NOT invent numbers.
Generate the COMPLETE Markdown report — every section above is MANDATORY.
Do NOT truncate or skip any section.
"""


agent = Agent(
    name="report_generator_agent",
    description="Generates Markdown underwriting reports from property and risk assessment data.",
    model="gemini-2.5-flash",
    instruction=REPORT_GENERATOR_INSTRUCTION,
)

app = to_a2a(agent, port=8004)
app.add_middleware(A2ATraceContextMiddleware)


@app.middleware("http")
async def inject_session_data(request: Request, call_next):
    if request.method != "POST":
        return await call_next(request)

    raw_body = await request.body()
    try:
        req_data = json.loads(raw_body)
        msg_text = req_data["params"]["message"]["parts"][0]["text"]
        prop_data = session_load("current", "property_data") or {}
        risk_data = session_load("current", "risk_assessment") or {}
        risk_data["premium_recommendation"] = compute_premium_recommendation(prop_data, risk_data)
        req_data["params"]["message"]["parts"][0]["text"] = (
            f"property_data: {json.dumps(prop_data)}\n\n"
            f"risk_assessment: {json.dumps(risk_data)}\n\n"
            f"user_profile: {msg_text}"
        )
        request._body = json.dumps(req_data).encode()
    except Exception as e:
        print(f"[ReportGenerator] Request augmentation warning: {e}")

    response = await call_next(request)

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    try:
        result_json = json.loads(body)
        artifacts = result_json.get("result", {}).get("artifacts", [])
        if artifacts:
            report_markdown = artifacts[0].get("parts", [{}])[0].get("text", "")
            report_path = os.path.join("data", "sessions", "current_report.md")
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, "w") as f:
                f.write(report_markdown)
            print(f"[ReportGenerator] ✅ Report saved to {report_path}")
    except Exception as e:
        print(f"[ReportGenerator] Could not save report: {e}")

    return StarResponse(content=body, status_code=response.status_code, media_type="application/json")


if __name__ == "__main__":
    print("\n[ReportGenerator] 🚀 http://localhost:8004")
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="warning")
