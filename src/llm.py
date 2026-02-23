"""LLM factory — multi-provider support."""

import os
from langchain_openai import ChatOpenAI


def get_llm(temperature: float = 0.1, streaming: bool = False):
    """Create LLM instance from runtime env."""
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL", "mistral-large-3:675b"),
        base_url=os.getenv("LLM_BASE_URL", "https://ollama.com/v1"),
        api_key=os.getenv("LLM_API_KEY", "not-needed") or "not-needed",
        temperature=temperature,
        streaming=streaming,
        request_timeout=120,
    )
