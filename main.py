"""
main.py
───────
Debug utility: verifies the PromptManager registers all templates correctly.
NOT used by `adk web` — that entry point is agents/agent.py (root_agent).

Run with:
    source venv/bin/activate
    python main.py
"""
from dotenv import load_dotenv
from prompt_manager.manager import PromptManager
from prompt_manager.templates import orchestrator, data_collector, risk_assessor, report_generator

load_dotenv()


def build_prompt_manager() -> PromptManager:
    """Register all versioned prompt templates and return the manager."""
    manager = PromptManager()
    orchestrator.register_all(manager)       # Orchestrator system instruction + user profiling
    data_collector.register_all(manager)     # Data collection ReAct instruction (reference)
    risk_assessor.register_all(manager)      # Fire / NatCat / Occupancy / Building CoT prompts
    report_generator.register_all(manager)   # Report generation few-shot prompt
    return manager


if __name__ == "__main__":
    manager = build_prompt_manager()
    print("PromptManager — registered templates:")
    for agent_name, templates in manager.list_templates().items():
        for template_name, versions in templates.items():
            print(f"  [{agent_name}] {template_name} — versions: {versions}")
