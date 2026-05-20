"""
agents/agent.py — ADK Web entry (`root_agent`).
Order: load_dotenv → init_arize_tracing → OrchestratorAgent + PromptManager.
"""
import os
import sys

# Ensure the project root is on sys.path when ADK imports this file directly
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from dotenv import load_dotenv
load_dotenv(override=True)

from tracing import setup_tracing, get_tracer
setup_tracing(project_name="commercial-property-underwriting-orchestrator")
# ── Step 3: Build the Orchestrator ─────────────────────────────────────────────
from agents.orchestrator import OrchestratorAgent
from prompt_manager.manager import PromptManager
from prompt_manager.templates import orchestrator

# PromptManager: versioned prompt registry used by the OrchestratorAgent.
# Sub-agent servers (data_collector, risk_assessor, report_generator)
# define their instructions inline via to_a2a — they do NOT use PromptManager.
manager = PromptManager()
orchestrator.register_all(manager)

# root_agent is the name ADK Web looks for to start the conversation loop.
root_agent = OrchestratorAgent(prompt_manager=manager)
