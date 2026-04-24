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
    provider = (provider or os.getenv("LLM_PROVIDER", "groq")).lower()

    if provider in ("groq", "grog"):
        return get_groq()
    if provider == "qwen":
       from .qwen_llm import QwenLLM
       return QwenLLM()
    raise ValueError(f"Unknown LLM provider: {provider}")


def get_groq():
    """Return a Groq LLM instance."""
    from .groq_llm import GroqLLM

    return GroqLLM()


# def get_gemini():
#     from .gemini_llm import GeminiLLM

#     return GeminiLLM()

