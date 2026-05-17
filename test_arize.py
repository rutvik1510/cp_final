"""
test_arize.py — Quick diagnostic: sends ONE test span to Arize and prints the HTTP result.
Run: source venv/bin/activate && python test_arize.py
"""
import os, time
from dotenv import load_dotenv
load_dotenv()

space_id = os.getenv("ARIZE_SPACE_ID")
api_key  = os.getenv("ARIZE_API_KEY")

print(f"ARIZE_SPACE_ID : {space_id[:12]}..." if space_id else "ARIZE_SPACE_ID : NOT SET")
print(f"ARIZE_API_KEY  : {api_key[:12]}..."  if api_key  else "ARIZE_API_KEY  : NOT SET")

if not space_id or not api_key:
    print("\nERROR: credentials missing in .env — cannot test")
    exit(1)

# ── Build a TracerProvider that prints export errors ───────────────────────────
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry import trace

resource = Resource.create({
    "service.name": "commercial-property-underwriting",
    "openinference.project.name": "commercial-property-underwriting",
})

exporter = OTLPSpanExporter(
    endpoint="https://otlp.arize.com/v1/traces",
    headers={
        "space_id": space_id,
        "api_key":  api_key,
    },
)

provider = TracerProvider(resource=resource)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))   # shows in terminal
provider.add_span_processor(SimpleSpanProcessor(exporter))                # sends to Arize
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("arize-test")

print("\nCreating a test span and sending to Arize...")
with tracer.start_as_current_span("arize_connectivity_test") as span:
    span.set_attribute("openinference.span.kind", "CHAIN")
    span.set_attribute("test", True)
    span.set_attribute("message", "hello from cp_final diagnostic")
    time.sleep(0.1)

provider.force_flush()
print("\nDone. Check Arize dashboard (Spans tab, last 5 min) for 'arize_connectivity_test'.")
print("If you see it → OTel export is working. If not → credentials or endpoint issue.")
