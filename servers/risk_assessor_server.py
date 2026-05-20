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

from tracing import setup_tracing, get_tracer
setup_tracing(project_name="commercial-property-underwriting-risk-assessor")
tracer = get_tracer("risk-assessor-tracer")
from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from servers.risk_category_engine import run_parallel_category_assessments
from prompt_manager.manager import PromptManager
from prompt_manager.templates import risk_assessor

pm = PromptManager()
risk_assessor.register_all(pm)
instruction = pm.get_prompt("risk_assessor", "agent_instruction")



def record_risk_span(span_name: str, result: dict, address: str, prompt_template: str):
    with tracer.start_as_current_span(span_name) as span:
        span.set_attribute("openinference.span.kind", "TOOL")
        span.set_attribute("input.value", json.dumps({"address": address, "template": prompt_template}))
        span.set_attribute("output.value", json.dumps(result))
        
        span.set_attribute("risk_category", result.get("category", ""))
        span.set_attribute("property_address", address)
        span.set_attribute("prompt_template", prompt_template)
        span.set_attribute("prompt_version", "v1")
        span.set_attribute("risk_score", result.get("score", 0))
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


async def execute_parallel_risk_assessment(property_data: str) -> str:
    prop = json.loads(property_data)
    assessment = await run_parallel_category_assessments(prop)
    
    # Emit the custom OpenTelemetry spans for Arize tracing
    emit_risk_spans(assessment, prop)
    
    return json.dumps(assessment)


agent = Agent(
    name="risk_assessment_agent",
    description="Commercial property risk service; parallel internal evaluators.",
    model="gemini-2.5-flash",
    instruction=instruction,
    tools=[execute_parallel_risk_assessment],
)

app = to_a2a(agent, port=8003)





if __name__ == "__main__":
    print("\n[RiskAssessor] 🚀 http://localhost:8003")
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="warning")
