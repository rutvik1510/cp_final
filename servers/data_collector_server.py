"""Data Collector A2A server (port 8002). Property / hazard / location / loss tools."""
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
init_server_tracing("data-collector")

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from mock_apis.property_api import lookup_property_characteristics, lookup_loss_history
from mock_apis.hazard_api import lookup_natural_hazards
from mock_apis.location_api import lookup_location_context
from utils.session_store import save as session_save

tracer = get_arize_tracer("data-collector")


def lookup_property(address: str) -> dict:
    with tracer.start_as_current_span("execute_tool [lookup_property]") as span:
        span.set_attribute("openinference.span.kind", "TOOL")
        span.set_attribute("input.value", json.dumps({"address": address}))
        print(f"  [DataCollector] 🏢 Fetching property details for '{address}'")
        res = lookup_property_characteristics(address)
        span.set_attribute("output.value", json.dumps(res))
        return res


def lookup_hazards(latitude: float, longitude: float) -> dict:
    with tracer.start_as_current_span("execute_tool [lookup_hazards]") as span:
        span.set_attribute("openinference.span.kind", "TOOL")
        span.set_attribute("input.value", json.dumps({"latitude": latitude, "longitude": longitude}))
        print(f"  [DataCollector] 🌍 Fetching hazard zones (lat={latitude:.4f}, lon={longitude:.4f})")
        res = lookup_natural_hazards(latitude, longitude)
        span.set_attribute("output.value", json.dumps(res))
        return res


def lookup_location(address: str) -> dict:
    with tracer.start_as_current_span("execute_tool [lookup_location]") as span:
        span.set_attribute("openinference.span.kind", "TOOL")
        span.set_attribute("input.value", json.dumps({"address": address}))
        print(f"  [DataCollector] 📍 Fetching location context for '{address}'")
        res = lookup_location_context(address)
        span.set_attribute("output.value", json.dumps(res))
        return res


def lookup_losses(property_id: str, insured_name: str = "Unknown") -> dict:
    with tracer.start_as_current_span("execute_tool [lookup_losses]") as span:
        span.set_attribute("openinference.span.kind", "TOOL")
        span.set_attribute("input.value", json.dumps({"property_id": property_id, "insured_name": insured_name}))
        print(f"  [DataCollector] 📄 Fetching loss history for property '{property_id}'")
        res = lookup_loss_history(property_id, insured_name)
        span.set_attribute("output.value", json.dumps(res))
        return res


agent = Agent(
    name="property_data_collector",
    description="Collects property, hazard, location, and loss history data for underwriting.",
    model="gemini-2.5-flash",
    instruction="""You are a Property Data Collector agent.

When given a property address, you MUST call ALL FOUR tools in sequence:
1. lookup_property(address)              → building characteristics + coordinates
2. lookup_hazards(latitude, longitude)   → use coordinates from step 1
3. lookup_location(address)              → fire station, crime index
4. lookup_losses(property_id)            → 5-year prior claims
   If insured name is unknown, use 'Unknown' — NEVER ask the user.

Return ALL collected data merged into a single JSON object.
NEVER invent or guess property data. ONLY use tool outputs.
""",
    tools=[lookup_property, lookup_hazards, lookup_location, lookup_losses],
)

app = to_a2a(agent, port=8002)
app.add_middleware(A2ATraceContextMiddleware)


@app.middleware("http")
async def save_property_data_to_session(request: Request, call_next):
    response = await call_next(request)
    if request.method != "POST":
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    try:
        result_json = json.loads(body)
        artifacts = result_json.get("result", {}).get("artifacts", [])
        if artifacts:
            text = artifacts[0].get("parts", [{}])[0].get("text", "")
            text = re.sub(r"^```(?:json)?\s*", "", text.strip())
            text = re.sub(r"\s*```$", "", text.strip())
            prop_data = json.loads(text)

            addr = prop_data.get("address", {})
            street = addr.get("street", "the property") if isinstance(addr, dict) else str(addr)
            prop_type = prop_data.get("characteristics", {}).get("property_type", "commercial property")
            tiv = prop_data.get("insurance_details", {}).get("total_insured_value", 0)

            session_save("current", "property_data", prop_data)
            print("[DataCollector] ✅ Property data saved to session.")

            summary = f"Property data collected for {street} ({prop_type}, TIV ${tiv:,.0f}). Ready for risk assessment."
            artifacts[0]["parts"][0]["text"] = summary
            result_json["result"]["artifacts"] = artifacts
            body = json.dumps(result_json).encode()
    except Exception as e:
        print(f"[DataCollector] Session middleware warning: {e}")

    return StarResponse(content=body, status_code=response.status_code, media_type="application/json")


if __name__ == "__main__":
    print("\n[DataCollector] 🚀 http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="warning")
