from opentelemetry import trace
span = trace.get_current_span()
print(span)
