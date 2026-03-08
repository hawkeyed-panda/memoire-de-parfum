import os
from app.config import settings


def setup_langsmith():
    """
    Configure LangSmith tracing environment variables.
    Call this once at app startup before any LangChain calls.
    """
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.LANGCHAIN_TRACING_V2).lower()
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT

    if settings.LANGCHAIN_TRACING_V2:
        print(f"[LangSmith] Tracing enabled → project: {settings.LANGCHAIN_PROJECT}")
    else:
        print("[LangSmith] Tracing disabled")
