from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import configure_logging
from app.core.rate_limit import InMemoryRateLimitMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await init_db()
    yield


app = FastAPI(
    title="AI Code Reviewer API",
    version="0.1.0",
    description="Production-grade AI pull request reviewer powered by Ollama and LangGraph.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(InMemoryRateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/test-pr", tags=["system"])
async def workflow_test_pr() -> dict[str, str]:
    return {"workflow_test_pr": "active", "branch": "workflow-test-pr"}
