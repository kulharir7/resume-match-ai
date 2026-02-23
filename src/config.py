"""Configuration loader."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://ollama.com/v1")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "mistral-large-3:675b")
    APP_USER = os.getenv("APP_USER", "admin")
    APP_PASS = os.getenv("APP_PASS", "resume123")
