
import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.routes import router


# 1. Create the logs folder
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


# 2. Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - %(levelname)s - "
        "%(name)s - %(message)s"
    ),
    handlers=[
        logging.FileHandler(
            LOG_DIR / "app.log",
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ],
)

logger = logging.getLogger(__name__)


# 3. Create the FastAPI application
app = FastAPI(
    title="Indian Companies Intelligence API",
    description=(
        "API for answering questions about "
        "Indian companies using RAG."
    ),
    version="1.0.0",
)


# 4. Handle invalid request data
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    logger.warning(
        "Request validation failed: %s %s",
        request.method,
        request.url.path
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request. Please check your input."
        }
    )


# 5. Handle unexpected application errors
@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):
    logger.error(
        "Unexpected error on %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__)
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. "
                      "Please try again."
        }
    )


# 6. Register the existing API routes
app.include_router(router, prefix="/api")


# 7. Log when the root endpoint is accessed
@app.get("/")
def root():
    logger.info("Root endpoint accessed")

    return {
        "message": "Indian Companies Intelligence API is running"
    }


