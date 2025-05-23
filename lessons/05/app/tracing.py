from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter # Changed import
from opentelemetry.sdk.trace.export import ConsoleSpanExporter # For debugging, optional
import logging
import os

logger = logging.getLogger('uvicorn.error')

def setup_otel(service_name: str):
    """
    Sets up OpenTelemetry tracing for a given service, exporting via OTLP HTTP JSON.
    """

    # Set the TracerProvider
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(service_name)

    # Configure OTLP HTTP exporter with JSON encoding
    # Default OTLP HTTP port for Jaeger is 4318, endpoint is /v1/traces
    # If using Docker Compose, 'jaeger' might be the service name.
    # Otherwise, replace 'jaeger' with 'localhost' or the actual IP.

    otlp_host = os.getenv("OTLP_COLLECTOR_HOST", "localhost") # Or 'jaeger' if using docker-compose
    otlp_port = int(os.getenv("OTLP_COLLECTOR_PORT", 4318)) # Default OTLP HTTP port

    # OTLP exporter for HTTP, using JSON
    # The default content type for OTLP HTTP/protobuf is 'application/x-protobuf'
    # To send JSON, you might explicitly need to set `preferred_encoding` to `json`
    # However, the Python OTLP HTTP exporter generally handles this based on endpoint and headers.
    # Ensure Jaeger is configured to receive OTLP HTTP JSON.
    otlp_exporter = OTLPSpanExporter(
        endpoint=f"http://{otlp_host}:{otlp_port}/v1/traces",
        headers={"Content-Type": "application/json"}, # Explicitly set JSON content type
        # In a real scenario, you might add: timeout=10, ssl_verify=False etc.
    )

    # Add a BatchSpanProcessor to export spans in batches
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

    # Optional: Add a console exporter for debugging
    # provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    logger.info(f"OpenTelemetry initialized for service: {service_name}, exporting to OTLP HTTP JSON at http://{otlp_host}:{otlp_port}/v1/traces")

