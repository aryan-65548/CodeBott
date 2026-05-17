from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.utils.logger import get_logger
from backend.config.settings import settings

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("Code Review AI Agent starting up")
    logger.info(f"Model: {settings.groq_model}")
    logger.info(f"Docs: http://localhost:{settings.app_port}/docs")
    yield
    # shutdown
    logger.info("Code Review AI Agent shutting down")

app = FastAPI(
    title="Code Review AI Agent",
    description="AI-powered code review for GitHub PRs, commits, and issues using Groq LLM",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug,
    )