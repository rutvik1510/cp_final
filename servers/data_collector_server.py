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

from tracing import setup_tracing, get_tracer
setup_tracing(project_name="commercial-property-underwriting-data-collector")
tracer = get_tracer("data-collector-tracer")

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from mock_apis.property_api import lookup_property_characteristics, lookup_loss_history
from mock_apis.hazard_api import lookup_natural_hazards
from mock_apis.location_api import lookup_location_context
from prompt_manager.manager import PromptManager
from prompt_manager.templates import data_collector

pm = PromptManager()
data_collector.register_all(pm)
instruction = pm.get_prompt("data_collector", "data_collection_react")



def lookup_property(address: str) -> dict:
    print(f"  [DataCollector] 🏢 Fetching property details for '{address}'")
    res = lookup_property_characteristics(address)
    return res


def lookup_hazards(latitude: float, longitude: float) -> dict:
    print(f"  [DataCollector] 🌍 Fetching hazard zones (lat={latitude:.4f}, lon={longitude:.4f})")
    res = lookup_natural_hazards(latitude, longitude)
    return res


def lookup_location(address: str) -> dict:
    print(f"  [DataCollector] 📍 Fetching location context for '{address}'")
    res = lookup_location_context(address)
    return res


def lookup_losses(property_id: str, insured_name: str = "Unknown") -> dict:
    print(f"  [DataCollector] 📄 Fetching loss history for property '{property_id}'")
    res = lookup_loss_history(property_id, insured_name)
    return res


agent = Agent(
    name="property_data_collector",
    description="Collects property, hazard, location, and loss history data for underwriting.",
    model="gemini-2.5-flash",
    instruction=instruction,
    tools=[lookup_property, lookup_hazards, lookup_location, lookup_losses],
)

app = to_a2a(agent, port=8002)





if __name__ == "__main__":
    print("\n[DataCollector] 🚀 http://localhost:8002")
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="warning")
