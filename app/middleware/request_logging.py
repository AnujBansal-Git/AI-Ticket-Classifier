import logging
import time
import uuid

from fastapi import Request


logger = logging.getLogger("api")


async def request_logging_middleware(
    request: Request,
    call_next,
):
    request_id = str(uuid.uuid4())

    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        latency = time.perf_counter() - start_time

        logger.info(
            "request_id=%s method=%s endpoint=%s "
            "status=%s latency=%.3fs",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            latency,
        )

        response.headers["X-Request-ID"] = request_id

        return response

    except Exception:
        latency = time.perf_counter() - start_time

        logger.exception(
            "request_id=%s method=%s endpoint=%s "
            "status=500 latency=%.3fs",
            request_id,
            request.method,
            request.url.path,
            latency,
        )

        raise