from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from backend.api.routes import router
from backend.api.middleware import RequestLoggingMiddleware
from backend.api.error_handlers import (
    validation_exception_handler,
    internal_error_handler,
)
from backend.db.database import init_db
from backend.utils.logger import get_logger
from backend.config.settings import settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Code Review AI Agent starting up")
    logger.info(f"Model: {settings.groq_model}")
    logger.info(f"Docs: http://localhost:{settings.app_port}/docs")
    await init_db()
    yield
    logger.info("Code Review AI Agent shutting down")


app = FastAPI(
    title="Code Review AI Agent",
    description="AI-powered code review for GitHub PRs, commits, and issues using Groq LLM",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(500, internal_error_handler)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )