"""LLM factory and dotenv loader.

Usage: from llm import get_llm; llm = get_llm()
Set `LLM_PROVIDER` env var to `groq` or `openai` (default: groq).
"""
import os
from dotenv import load_dotenv

# Load .env from project root if present
load_dotenv()


def get_llm(provider: str | None = None):
    """Return an LLM instance based on `provider` or `LLM_PROVIDER` env var.

    Examples:
      - `get_llm()` reads `LLM_PROVIDER` (defaults to `groq`)
      - `get_llm('openai')` returns an OpenAI-backed instance
    """
    prov = (provider or os.getenv("LLM_PROVIDER", "groq")).lower()

    if prov in ("openai", "open_ai", "open-api", "open_api"):
        return get_openai()

    if prov in ("groq", "grog"):
        return get_groq()

    raise ValueError(f"Unknown LLM provider: {prov}")


def get_openai():
    """Return an OpenAI LLM instance. Reads `OPENAI_API_KEY` or `OPEN_API_KEY` from env/.env."""
    from .openai_llm import OpenAILLM

    return OpenAILLM()


def get_groq():
    """Return a Groq LLM instance."""
    from .groq_llm import GroqLLM

    return GroqLLM()
