"""Risk Assessor A2A server (port 8003). Parallel internal scoring + session summaries."""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from dotenv import load_dotenv
from fastapi import Request
from starlette.responses import Response as StarResponse

load_dotenv()

from telemetry.server_tracing import init_server_tracing, get_arize_tracer, A2ATraceContextMiddleware
init_server_tracing("risk-assessor")

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from servers.risk_category_engine import run_parallel_category_assessments
from utils.session_store import load as session_load, save as session_save

tracer = get_arize_tracer("risk-assessor")


def record_risk_span(span_name: str, result: dict, address: str, prompt_template: str):
    with tracer.start_as_current_span(span_name) as span:
        span.set_attribute("risk_category", result.get("category", "unknown"))
        span.set_attribute("property_address", address)
        span.set_attribute("prompt_template", prompt_template)
        span.set_attribute("prompt_version", "v1")
        span.set_attribute("risk_score", float(result.get("score", 0)))
        span.set_attribute("risk_grade", result.get("grade", "UNKNOWN"))


def emit_risk_spans(assessment_result: dict, property_data: dict):
    address = property_data.get("address", {})
    street = address.get("street", "unknown") if isinstance(address, dict) else str(address)
    span_map = {
        "fire": ("fire_risk_assessment", "fire_risk_cot"),
        "natural_catastrophe": ("natcat_risk_assessment", "natcat_risk_cot"),
        "occupancy": ("occupancy_risk_assessment", "occupancy_risk_cot"),
        "building": ("building_risk_assessment", "building_risk_cot"),
    }
    for score_entry in assessment_result.get("individual_scores", []):
        category = score_entry.get("category", "")
        if category in span_map:
            span_name, template = span_map[category]
            record_risk_span(span_name, score_entry, street, template)


async def execute_parallel_risk_assessment(_: str = "") -> str:
    prop = session_load("current", "property_data")
    if not prop:
        return "No property_data in session. Run the Property Data Collector agent first."

    assessment = await run_parallel_category_assessments(prop)
    session_save("current", "risk_assessment", assessment)
    return (
        "Parallel risk assessment complete. "
        "Full JSON saved server-side for the Report Generator agent."
    )


agent = Agent(
    name="risk_assessment_agent",
    description="Commercial property risk service; parallel internal evaluators.",
    model="gemini-2.5-flash",
    instruction=(
        "You are the Risk Assessment A2A agent. Call `execute_parallel_risk_assessment` exactly once "
        "per user task. Do not score risks yourself. After the tool returns, one short confirmation sentence."
    ),
    tools=[execute_parallel_risk_assessment],
)

app = to_a2a(agent, port=8003)
app.add_middleware(A2ATraceContextMiddleware)


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    if request.method != "POST":
        return await call_next(request)

    raw_body = await request.body()
    try:
        req_data = json.loads(raw_body)
        msg_text = req_data["params"]["message"]["parts"][0]["text"]
        prop_data = session_load("current", "property_data")
        if prop_data:
            req_data["params"]["message"]["parts"][0]["text"] = (
                f"Property data for risk assessment:\n{json.dumps(prop_data)}\n\nInstructions: {msg_text}"
            )
            request._body = json.dumps(req_data).encode()
    except Exception as e:
        print(f"[RiskAssessor] Request augmentation warning: {e}")

    response = await call_next(request)

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    try:
        result_json = json.loads(body)
        artifacts = result_json.get("result", {}).get("artifacts", [])
        assessment = session_load("current", "risk_assessment")

        if assessment and isinstance(assessment, dict) and assessment.get("individual_scores"):
            prop_data = session_load("current", "property_data") or {}
            emit_risk_spans(assessment, prop_data)
            overall = assessment.get("overall_score", "?")
            grade = assessment.get("overall_grade", "?")
            scores = {s["category"]: s["score"] for s in assessment.get("individual_scores", [])}
            summary = (
                f"Risk assessment complete. Overall: {overall}/10 ({grade}). "
                f"Fire: {scores.get('fire', '?')}, NatCat: {scores.get('natural_catastrophe', '?')}, "
                f"Occupancy: {scores.get('occupancy', '?')}, Building: {scores.get('building', '?')}. "
                "Ready to generate underwriting report."
            )
            if artifacts:
                artifacts[0]["parts"][0]["text"] = summary
                result_json["result"]["artifacts"] = artifacts
            body = json.dumps(result_json).encode()
    except Exception as e:
        print(f"[RiskAssessor] Session middleware warning: {e}")

    return StarResponse(content=body, status_code=response.status_code, media_type="application/json")


if __name__ == "__main__":
    print("\n[RiskAssessor] 🚀 http://localhost:8003")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="warning")
