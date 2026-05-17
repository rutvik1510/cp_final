import os
import json
from dotenv import load_dotenv
from telemetry.arize_setup import init_arize_tracing, get_arize_tracer
from opentelemetry import trace

load_dotenv(override=True)
init_arize_tracing()
tracer = get_arize_tracer("test")

with tracer.start_as_current_span("my_test_span") as span:
    span.set_attribute("openinference.span.kind", "CHAIN")
    print("Span created")
