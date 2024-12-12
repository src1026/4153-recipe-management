import logging
import uuid
from fastapi import Request

logger = logging.getLogger(__name__)

async def correlation_id_middleware(request: Request, call_next):
    # generate a new correlation id
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id

    logger.info(f"Start Request: {request.url.path}, Correlation ID: {correlation_id}")

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id

    logger.info(f"End Request: {request.url.path}, Correlation ID: {correlation_id}")
    return response
