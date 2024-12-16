from fastapi import Depends, FastAPI, Request
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import logging
from opentelemetry import trace
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.propagate import inject
import uuid
from app.routers import recipes

import watchtower
import boto3
"""
boto3_client = boto3.client('logs', region_name='us-east-1')
# Configure CloudWatch logging
cloudwatch_handler = watchtower.CloudWatchLogHandler(
    # boto3_session=boto3.Session(region_name="us-east-1"),
    boto3_client=boto3_client,
    log_group="recipe_management_logs",
    stream_name="application_logs"
)

# Add CloudWatch handler to the root logger
logging.getLogger().addHandler(cloudwatch_handler)
logging.info("CloudWatch Logging is configured.")
"""
# Configure global logging without hardcoding `correlation_id`
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

# Define a custom logger adapter to handle `correlation_id`
class CorrelationIdAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        correlation_id = self.extra.get("correlation_id", "N/A")
        return f"[Correlation-ID: {correlation_id}] {msg}", kwargs

# Create a logger instance with adapter
logger = CorrelationIdAdapter(logging.getLogger(__name__), {"correlation_id": "N/A"})

# Initialize OpenTelemetry
tracer_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "recipe_management"}))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Export spans to the console
span_exporter = ConsoleSpanExporter()
span_processor = SimpleSpanProcessor(span_exporter)
tracer_provider.add_span_processor(span_processor)

app = FastAPI(
    title="Recipe Management API",
    description="API for managing and retrieving recipes"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=['*'],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for correlation ID and logging
@app.middleware("http")
async def add_correlation_id_and_logging(request: Request, call_next):
    correlation_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    # Update the logger's correlation_id for this request
    logger.extra["correlation_id"] = correlation_id

    # Log the incoming request
    logger.info(f"Incoming request: {request.method} {request.url}")

    # Start OpenTelemetry span
    with trace.get_tracer(__name__).start_as_current_span(
        f"{request.method} {request.url}",
        attributes={"correlation_id": correlation_id}
    ):
        response = await call_next(request)

    # Log the outgoing response
    logger.info(f"Outgoing response: {response.status_code}")
    return response

# Include routers
app.include_router(recipes.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)