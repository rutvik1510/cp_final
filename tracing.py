import os
import logging
from typing import Optional
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_tracing(
    project_name: str = "my-new-project",
    endpoint: str = "https://otlp.arize.com/v1/traces", # Ensure this includes /v1/traces for standard OTLP
) -> bool:
    """Initialize OpenTelemetry tracing with Arize Cloud export."""
    load_dotenv()
    
    space_id = os.getenv("ARIZE_SPACE_ID")
    api_key = os.getenv("ARIZE_API_KEY")

    if not space_id or not api_key:
        logger.warning("Arize credentials not found. Tracing will be DISABLED.")
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource

        # Identifies this service in the Arize dashboard
        resource = Resource.create(
            {
                "service.name": project_name,
                "service.version": "1.0.0",
                "model_id": project_name,
                "model_version": "1.0.0",
            }
        )

        # Configure OTLP exporter with Arize Cloud headers
        exporter = OTLPSpanExporter(
            endpoint=endpoint.replace("/v1/traces", ""), # GRPC exporter handles the path automatically
            headers={
                "space_id": space_id,
                "api_key": api_key,
            },
        )

        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

        # Auto-instrument LLM SDKs
        _instrument_llm()
        
        logger.info(f"✅ Arize Cloud tracing enabled for project: '{project_name}'")
        return True

    except ImportError as e:
        logger.warning(f"Tracing dependencies not installed: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to configure tracing: {e}")
        return False

def _instrument_llm() -> None:
    """Auto-instruments the LLM SDK."""
    try:
        from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor
        GoogleGenAIInstrumentor().instrument()
        logger.info("✅ LLM SDK auto-instrumented")
    except ImportError:
        logger.warning("openinference-instrumentation-google-genai not installed.")

def get_tracer(name: str = "custom-tracer"):
    """Get a tracer instance for creating manual spans."""
    try:
        from opentelemetry import trace
        return trace.get_tracer(name)
    except ImportError:
        return _NoOpTracer()

class _NoOpTracer:
    def start_as_current_span(self, name, **kwargs): return _NoOpSpan()

class _NoOpSpan:
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def set_attribute(self, key, value): pass
    def set_status(self, status): pass
