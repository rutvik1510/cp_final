"""OTel + Arize for sub-agent A2A servers (ports 8002–8004)."""
import os
from opentelemetry import trace as trace_api
from opentelemetry import context as otel_context
from opentelemetry.propagate import extract
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from starlette.middleware.base import BaseHTTPMiddleware

_arize_provider: TracerProvider | None = None


class ExplicitKindFilterExporter(SpanExporter):
    def __init__(self, delegate: SpanExporter):
        self._delegate = delegate

    def export(self, spans):
        kept = []
        for s in spans:
            attrs = s.attributes or {}
            kind = attrs.get("openinference.span.kind")
            if not kind:
                continue
            if kind == "LLM":
                continue
            if kind == "TOOL" and "input.value" not in attrs:
                continue
            kept.append(s)

        if kept:
            return self._delegate.export(kept)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        return self._delegate.shutdown()

    def force_flush(self, timeout_millis: int = 30_000):
        return self._delegate.force_flush(timeout_millis)


class A2ATraceContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method == "POST":
            carrier = {k.lower(): v for k, v in request.headers.items()}
            parent_ctx = extract(carrier)
            token = otel_context.attach(parent_ctx)
            try:
                response = await call_next(request)
            finally:
                otel_context.detach(token)
            return response
        return await call_next(request)


def init_server_tracing(service_name: str) -> TracerProvider | None:
    """Dedicated Arize TracerProvider for a sub-agent process. Call before ADK imports."""
    global _arize_provider

    from dotenv import load_dotenv
    load_dotenv(override=True)

    space_id = os.getenv("ARIZE_SPACE_ID")
    api_key  = os.getenv("ARIZE_API_KEY")

    if not space_id or not api_key:
        print(f"[{service_name}] No Arize credentials — tracing disabled.")
        return None

    resource = Resource.create({
        "service.name":               service_name,
        "openinference.project.name": "commercial-property-underwriting",
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
    print(f"[{service_name}] Arize dedicated TracerProvider ready.")
    return _arize_provider


def get_arize_tracer(name: str):
    if _arize_provider is not None:
        return _arize_provider.get_tracer(name)
    return trace_api.get_tracer(name)
