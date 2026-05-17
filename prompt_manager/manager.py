from datetime import datetime


class _SafeDict(dict):
    """Returns '{key}' for any missing key so format_map never raises KeyError."""
    def __missing__(self, key):
        return "{" + key + "}"


class PromptManager:
    """
    Simple dict-based prompt manager.
    Stores versioned prompt templates for all agents.
    Tracks usage for Arize tracing integration.
    """

    def __init__(self):
        self._templates = {}   # {agent: {template_name: {version: template_str}}}
        self._usage_log = []   # For Arize tracing

    def register(self, agent: str, name: str, version: str, template: str):
        """Register a prompt template."""
        self._templates.setdefault(agent, {}).setdefault(name, {})[version] = template

    def get_prompt(self, agent: str, name: str, variables: dict = None, version: str = "latest") -> str:
        """
        Retrieve and render a prompt template.
        """
        agent_templates = self._templates.get(agent, {})
        template_versions = agent_templates.get(name, {})

        if not template_versions:
            raise ValueError(f"No template found for agent '{agent}' and name '{name}'")

        if version == "latest":
            version = sorted(template_versions.keys())[-1]

        template_str = template_versions.get(version, "")

        # Render with variables — _SafeDict leaves missing {placeholders} intact
        rendered = template_str.format_map(_SafeDict(variables or {}))

        # Log usage (sent to Arize as span attributes)
        self._usage_log.append({
            "agent": agent,
            "template": name,
            "version": version,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return rendered

    def list_templates(self, agent: str = None) -> dict:
        """List all registered templates with their versions."""
        if agent:
            return {agent: {
                name: list(versions.keys())
                for name, versions in self._templates.get(agent, {}).items()
            }}
        return {
            a: {name: list(vers.keys()) for name, vers in templates.items()}
            for a, templates in self._templates.items()
        }

    def get_usage_log(self) -> list:
        """Return prompt usage log for Arize tracing integration."""
        return self._usage_log
