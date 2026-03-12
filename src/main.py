import asyncio
import json
import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SpanExporter,
    SpanExportResult,
)
from opentelemetry.trace import SpanKind


env = get_environment_variables()


class FilteredConsoleExporter(ConsoleSpanExporter):
    def export(self, spans):
        # só loga spans SERVER (a request em si), ignora os internos do ASGI
        filtered = [s for s in spans if s.kind == SpanKind.SERVER]
        if filtered:
            # return super().export(filtered)
            return super().export([])


def setup_tracing():
    resource = Resource(attributes={
        SERVICE_NAME: "forestgis-api"
    })
    
    if os.getenv("LOCAL_TRACING") is not None:
        # local: use console exporter with filtering to avoid cluttering logs with internal spans
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        exporter = FilteredConsoleExporter()
        processor = SimpleSpanProcessor(exporter)
    else:
        exporter = CloudTraceSpanExporter()
        processor = BatchSpanProcessor(exporter)

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    RequestsInstrumentor().instrument()

setup_tracing()
setup_logging()

handler = logging.StreamHandler()
handler.setFormatter(TraceLogHandler())
logging.basicConfig(handlers=[handler], level=logging.INFO)

# Core Application Instance
app = FastAPI(
    title="Dummy API",
    description="",
)

FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    from middlewares.logging import logging_middleware as _mw
    return await _mw(request, call_next)

init()

