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
from tracing import setup_tracing, get_tracer
setup_tracing(project_name="commercial-property-underwriting-report-generator")
tracer = get_tracer("report-generator-tracer")
from servers.report_premium import compute_premium_recommendation


from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from prompt_manager.manager import PromptManager
from prompt_manager.templates import report_generator

pm = PromptManager()
report_generator.register_all(pm)
REPORT_GENERATOR_INSTRUCTION = pm.get_prompt("report_generator", "report_generation")




agent = Agent(
    name="report_generator_agent",
    description="Generates Markdown underwriting reports from property and risk assessment data.",
    model="gemini-2.5-flash",
    instruction=REPORT_GENERATOR_INSTRUCTION,
    tools=[compute_premium_recommendation],
)

app = to_a2a(agent, port=8004)


@app.middleware("http")
async def save_report_data(request: Request, call_next):
    if request.method != "POST":
        return await call_next(request)

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
