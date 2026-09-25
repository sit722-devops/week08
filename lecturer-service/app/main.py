import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from sqlalchemy.exc import OperationalError

from app.db import Base, engine
from app.routers import lecturers
from app.storage import ensure_container_exists


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

SERVICE_NAME = "lecturer-service"

HTTP_REQUESTS_TOTAL = Counter(
    "koalatech_http_requests_total",
    "Total number of HTTP requests.",
    ["service", "method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "koalatech_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["service", "method", "path"],
)


def initialise_database() -> None:
    maximum_attempts = 10
    retry_delay_seconds = 5

    for attempt in range(1, maximum_attempts + 1):
        try:
            Base.metadata.create_all(bind=engine)

            logger.info(
                "Database connection established successfully."
            )

            return

        except OperationalError:
            logger.warning(
                "Database connection failed. Attempt %s of %s.",
                attempt,
                maximum_attempts,
            )

            if attempt == maximum_attempts:
                logger.exception(
                    "Unable to connect to the database."
                )
                raise

            time.sleep(retry_delay_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialise_database()

    try:
        ensure_container_exists()

        logger.info(
            "Azure Blob Storage container is ready."
        )
    except Exception:
        logger.warning(
            "Azure Blob Storage is unavailable. "
            "Profile-photo uploads may fail."
        )

    yield


app = FastAPI(
    title="KoalaTech University Lecturer Service",
    description=(
        "Manages lecturer records and lecturer profile photos "
        "for KoalaTech University."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def prometheus_metrics(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time

    route = request.scope.get("route")
    path = getattr(route, "path", request.url.path)

    HTTP_REQUESTS_TOTAL.labels(
        service=SERVICE_NAME,
        method=request.method,
        path=path,
        status_code=str(response.status_code),
    ).inc()

    HTTP_REQUEST_DURATION_SECONDS.labels(
        service=SERVICE_NAME,
        method=request.method,
        path=path,
    ).observe(duration)

    return response


app.include_router(lecturers.router)


@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {
        "message": (
            "KoalaTech University Lecturer Service is running."
        )
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
    }


@app.get(
    "/metrics",
    include_in_schema=False,
)
def metrics() -> Response:
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
