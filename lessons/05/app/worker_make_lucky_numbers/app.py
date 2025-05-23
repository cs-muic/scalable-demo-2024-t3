# app.py
from celery import Celery
from . import celeryconfig
import os
import random
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.sdk.environment_variables import (
    OTEL_EXPORTER_OTLP_ENDPOINT,
)

from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from celery.signals import worker_process_init
from celery.utils.log import get_logger

app = Celery('lucky-numbers-worker')
app.config_from_object(celeryconfig)

@worker_process_init.connect(weak=False)
def init_celery_tracing(*args, **kwargs):
    log = get_logger(__name__)
    log.info("Worker spawned (pid: %s)", os.getpid())
    log.info("(pid: %s) OTLP_ENDPOINT: %s", os.getpid(),
        os.environ.get(OTEL_EXPORTER_OTLP_ENDPOINT)
    )
    resource = Resource(attributes={
        SERVICE_NAME: "worker"
    })

    trace_provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(
        OTLPSpanExporter()
    )
    trace_provider.add_span_processor(processor)
    trace.set_tracer_provider(trace_provider)

    CeleryInstrumentor().instrument()

@app.task
def generate_lucky_numbers(n):
    """
    Generates a list of n lucky numbers between 1 and 1000.
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer.")

    return [random.randint(1, 1000) for _ in range(n)]

