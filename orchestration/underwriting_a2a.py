"""A2A Agent Card discovery and task sends for the orchestrator (no sub-agent business logic)."""
from __future__ import annotations

import json
import os
import uuid
from typing import Any

import httpx
from a2a.client.card_resolver import A2ACardResolver
from a2a.client.client import ClientConfig
from a2a.client.client_factory import ClientFactory
from a2a.client.middleware import ClientCallContext, ClientCallInterceptor
from a2a.types import AgentCard, Message, Part, Role, Task, TextPart
from a2a.types import TransportProtocol as A2ATransport
from opentelemetry.propagate import inject


def underwriting_agent_base_urls() -> list[str]:
    raw = os.getenv(
        "UNDERWRITING_A2A_BASE_URLS",
        "http://127.0.0.1:8002,http://127.0.0.1:8003,http://127.0.0.1:8004",
    )
    return [u.strip().rstrip("/") for u in raw.split(",") if u.strip()]


class _OtelTraceHeadersInterceptor(ClientCallInterceptor):
    async def intercept(
        self,
        method_name: str,
        request_payload: dict[str, Any],
        http_kwargs: dict[str, Any],
        agent_card: AgentCard | None,
        context: ClientCallContext | None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        headers = dict(http_kwargs.get("headers") or {})
        inject(headers)
        return request_payload, {**http_kwargs, "headers": headers}


def _part_to_text(part: Part) -> str:
    root = part.root
    if isinstance(root, TextPart):
        return root.text or ""
    return ""


def _extract_text_from_client_event(event: Any) -> str:
    if isinstance(event, Message):
        chunks = [_part_to_text(p) for p in event.parts if _part_to_text(p)]
        return "\n".join(chunks) if chunks else str(event)

    if isinstance(event, tuple) and event and isinstance(event[0], Task):
        task: Task = event[0]
        if task.artifacts:
            for art in task.artifacts:
                for p in art.parts:
                    t = _part_to_text(p)
                    if t:
                        return t
        if task.status and task.status.message and task.status.message.parts:
            for p in task.status.message.parts:
                t = _part_to_text(p)
                if t:
                    return t
        return json.dumps(task.model_dump(mode="json", exclude_none=True), indent=2)[:8000]

    return str(event)


async def fetch_agent_catalog(
    http: httpx.AsyncClient,
) -> tuple[dict[str, AgentCard], list[str]]:
    catalog: dict[str, AgentCard] = {}
    errors: list[str] = []
    for base in underwriting_agent_base_urls():
        try:
            card = await A2ACardResolver(http, base).get_agent_card()
            if card.name:
                catalog[card.name] = card
        except Exception as e:
            errors.append(f"{base}: {e}")
    return catalog, errors


def format_agent_catalog_for_llm(
    catalog: dict[str, AgentCard], errors: list[str] | None = None
) -> str:
    lines: list[str] = [
        "## Discovered remote agents (from Agent Cards)",
        "Use `delegate_underwriting_task(agent_name=..., task_message=...)` with the agent name below.",
        "",
    ]
    if errors:
        lines.append("### Discovery warnings")
        lines.extend(f"- {err}" for err in errors)
        lines.append("")
    for _, card in sorted(catalog.items()):
        lines.append(f"### Agent `{card.name}`")
        lines.append(f"- **Description:** {card.description or '(none)'}")
        lines.append(f"- **RPC URL:** {card.url}")
        if card.skills:
            lines.append("- **Skills:**")
            for sk in card.skills:
                sid = getattr(sk, "id", "") or ""
                sname = getattr(sk, "name", "") or ""
                desc = (getattr(sk, "description", "") or "")[:240]
                tags = list(getattr(sk, "tags", None) or [])
                lines.append(f"  - `{sid}` / {sname} tags={tags} — {desc}")
        lines.append("")
    lines.append(
        "### Workflow agent names\n"
        "- `property_data_collector`\n"
        "- `risk_assessment_agent`\n"
        "- `report_generator_agent`\n"
    )
    return "\n".join(lines)


async def send_underwriting_a2a_task(
    http: httpx.AsyncClient,
    card: AgentCard,
    task_message: str,
) -> str:
    cfg = ClientConfig(
        httpx_client=http,
        streaming=False,
        polling=False,
        supported_transports=[A2ATransport.jsonrpc, A2ATransport.http_json],
    )
    client = ClientFactory(cfg).create(card, interceptors=[_OtelTraceHeadersInterceptor()])
    msg = Message(
        message_id=str(uuid.uuid4()),
        role=Role.user,
        parts=[Part(root=TextPart(text=task_message))],
    )
    last = ""
    async for event in client.send_message(request=msg):
        last = _extract_text_from_client_event(event)
    return last or "(empty response from remote agent)"
