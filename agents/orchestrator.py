import json
import os
from typing import Any

from pydantic import ConfigDict
from google.adk import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext

from user_profile.profile_store import UserProfileStore
from telemetry.arize_setup import get_arize_tracer

tracer = get_arize_tracer("underwriting-agents")

# Calculate path to agent cards
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARDS_DIR = os.path.join(BASE_DIR, "a2a", "agent_cards")

class TracedAgentTool(AgentTool):
    """Wraps ADK's AgentTool to emit manual Arize spans for each delegation."""
    async def run_async(self, *, args: dict[str, Any], tool_context: ToolContext) -> Any:
        with tracer.start_as_current_span(f"a2a:{self.agent.name}") as span:
            span.set_attribute("openinference.span.kind", "AGENT")
            span.set_attribute("agent.name", self.agent.name)
            span.set_attribute("input.value", json.dumps(args))
            try:
                result = await super().run_async(args=args, tool_context=tool_context)
                span.set_attribute("output.value", str(result)[:2000])
                return result
            except Exception as e:
                span.record_exception(e)
                raise


class OrchestratorAgent(Agent):
    """Coordinates user + profile locally; delegates natively to RemoteA2aAgents."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    def __init__(self, prompt_manager: Any, **kwargs):
        system_instruction = prompt_manager.get_prompt("orchestrator", "system_instruction")

        data_collector = RemoteA2aAgent(
            name="property_data_collector",
            agent_card=os.path.join(CARDS_DIR, "data_collector.json")
        )
        risk_assessor = RemoteA2aAgent(
            name="risk_assessment_agent",
            agent_card=os.path.join(CARDS_DIR, "risk_assessor.json")
        )
        report_generator = RemoteA2aAgent(
            name="report_generator_agent",
            agent_card=os.path.join(CARDS_DIR, "report_generator.json")
        )

        super().__init__(
            name="underwriting_orchestrator",
            description="Commercial underwriting coordinator. Delegates to remote A2A agents natively.",
            model="gemini-2.5-flash",
            instruction=system_instruction,
            tools=[
                self.manage_user_profile,
                TracedAgentTool(agent=data_collector),
                TracedAgentTool(agent=risk_assessor),
                TracedAgentTool(agent=report_generator),
            ],
            **kwargs,
        )
        self.profile_store = UserProfileStore()

    # (Delegation functions removed in favor of ADK RemoteA2aAgent delegation)

    async def manage_user_profile(
        self,
        action: str = "get_or_create",
        user_id: str = "default_user",
        experience_level: str = "junior",
        preferred_detail_level: str = "verbose",
        specialization: str = "",
        preferred_format: str = "narrative",
    ) -> str:
        with tracer.start_as_current_span("manage_user_profile") as span:
            span.set_attribute("openinference.span.kind", "TOOL")
            span.set_attribute("input.value", json.dumps({"action": action, "user_id": user_id}))

            if action in ("get_or_create", "get"):
                profile = self.profile_store.get_or_create(user_id)
            elif action == "update":
                profile = self.profile_store.get_profile(user_id) or {"user_id": user_id}
                profile["experience_level"] = experience_level
                profile["preferred_detail_level"] = preferred_detail_level
                if specialization:
                    profile["specialization"] = [s.strip() for s in specialization.split(",")]
                profile["preferred_format"] = preferred_format
                profile["profiling_complete"] = True
                profile["session_count"] = profile.get("session_count", 0) + 1
                self.profile_store.save_profile(user_id, profile)
            else:
                profile = self.profile_store.get_or_create(user_id)

            result = json.dumps(profile)
            span.set_attribute("output.value", result)
            return result
