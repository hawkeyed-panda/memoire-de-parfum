from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings

if not settings.LANGCHAIN_TRACING_V2:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
from app.db.postgres import init_db
from app.cache.redis_client import close_redis
from app.graph.neo4j_client import close_neo4j
from app.rag.weaviate_client import close_weaviate
from app.rag.ingest import ingest_documents
from app.graph.seed_graph import seed_graph_if_empty
from app.errors.exceptions import MemoireBaseException

from app.api.routes import auth, questionnaire, fragrance, refine, user


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print(f"[Startup] Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    api_key = settings.OPENAI_API_KEY
    if not api_key or api_key.startswith("sk-your") or api_key == "":
        print("[WARNING] OPENAI_API_KEY is not set — LLM calls will fail. "
              "Set a real key in .env to use the fragrance pipeline.")

    if not settings.LANGCHAIN_TRACING_V2:
        print("[Startup] LangSmith tracing disabled (no valid API key).")

    await init_db()
    await seed_graph_if_empty()
    await ingest_documents()
    print("[Startup] All services ready.")
    yield
    # Shutdown
    await close_redis()
    await close_neo4j()
    await close_weaviate()
    print("[Shutdown] All connections closed.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Global exception handler ---
@app.exception_handler(MemoireBaseException)
async def memoire_exception_handler(request: Request, exc: MemoireBaseException):
    return JSONResponse(
        status_code=500,
        content={"error": exc.code, "message": exc.message},
    )


# --- Health check ---
@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# --- Routers ---
app.include_router(auth.router)
app.include_router(questionnaire.router)
app.include_router(fragrance.router)
app.include_router(refine.router)
app.include_router(user.router)

