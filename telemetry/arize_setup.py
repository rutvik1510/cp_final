"""
telemetry/arize_setup.py
────────────────────────
Arize OTel tracing for the Orchestrator process.

Architecture:
  We maintain a DEDICATED TracerProvider solely for Arize spans. This is
  completely separate from ADK's internal TracerProvider. This solves:

  1. ADK replaces the global TracerProvider on startup, orphaning any
     processors we added to the "existing" provider.
  2. ADK spans (call_llm, generate_content) get sent to Arize with missing
     required attributes, causing HTTP 500 rejections.

  Solution:
    - init_arize_tracing() creates _arize_provider (not the global one)
    - get_arize_tracer(name) returns a tracer from _arize_provider
    - All our manual spans (data_collector, risk_assessor, manage_user_profile)
      use get_arize_tracer() — they go directly to Arize
    - ADK spans use ADK's own provider — they never reach Arize

  Trace propagation still works because OTel context (trace_id, span_id) is
  carried by the context manager, not the provider. The A2ATraceContextMiddleware
  in sub-agents extracts the orchestrator's trace context from HTTP headers,
  making sub-agent spans children of the orchestrator's AGENT spans in Arize.
"""
import os
from opentelemetry import trace as trace_api
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

_arize_provider: TracerProvider | None = None


class ExplicitKindFilterExporter(SpanExporter):
    """
    Only forwards spans where openinference.span.kind is explicitly set.
    Validates required attributes per OpenInference spec.
    """

    def __init__(self, delegate: SpanExporter):
        self._delegate = delegate

    def export(self, spans):
        kept = []
        for s in spans:
            attrs = s.attributes or {}
            kind = attrs.get("openinference.span.kind")
            if not kind:
                continue                          # Skip: no explicit kind
            if kind == "LLM":
                continue                          # Skip: ADK LLM spans lack required attrs
            if kind == "TOOL" and "input.value" not in attrs:
                continue                          # Skip: TOOL requires input.value
            kept.append(s)

        if kept:
            return self._delegate.export(kept)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        return self._delegate.shutdown()

    def force_flush(self, timeout_millis: int = 30_000):
        return self._delegate.force_flush(timeout_millis)


def init_arize_tracing() -> None:
    """
    Create a dedicated Arize TracerProvider (NOT the global one).
    Call this once at startup before any other imports.
    """
    global _arize_provider

    space_id = os.getenv("ARIZE_SPACE_ID")
    api_key  = os.getenv("ARIZE_API_KEY")

    if not space_id or not api_key:
        print("[Arize] Credentials not set — tracing disabled.")
        return

    project_name = "commercial-property-underwriting"

    resource = Resource.create({
        "service.name":               project_name,
        "openinference.project.name": project_name,
    })

    otlp_exporter = OTLPSpanExporter(
        endpoint="https://otlp.arize.com/v1/traces",
        headers={
            "space_id": space_id,
            "api_key":  api_key,
        },
    )

    _arize_provider = TracerProvider(resource=resource)
    _arize_provider.add_span_processor(
        SimpleSpanProcessor(ExplicitKindFilterExporter(otlp_exporter))
    )
    print(f"[Arize] Dedicated TracerProvider ready → project: {project_name}")


def get_arize_tracer(name: str):
    """
    Return a tracer from the dedicated Arize provider.
    Use this instead of trace.get_tracer() for all our custom spans.
    Falls back to the global provider if Arize is not initialized.
    """
    if _arize_provider is not None:
        return _arize_provider.get_tracer(name)
    return trace_api.get_tracer(name)
