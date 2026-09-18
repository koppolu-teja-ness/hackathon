"""Centralized configuration loaded from environment variables.

Shared by Dev A (ingestion) and Dev B (serving). Coordinate before changing
default values that affect data contracts (e.g. EMBED_DIMENSIONS).
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def _float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


# --- AWS / Bedrock ---
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_CHAT_MODEL_ID = os.getenv("BEDROCK_CHAT_MODEL_ID", "amazon.nova-pro-v1:0")
BEDROCK_EMBED_MODEL_ID = os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")
EMBED_DIMENSIONS = _int("EMBED_DIMENSIONS", 1024)

# --- Crawl limits ---
MAX_PAGES = _int("MAX_PAGES", 20)
MAX_DEPTH = _int("MAX_DEPTH", 3)
REQUEST_TIMEOUT = _int("REQUEST_TIMEOUT", 10)
MAX_RESPONSE_BYTES = _int("MAX_RESPONSE_BYTES", 2_000_000)
CRAWL_DELAY_SECONDS = _float("CRAWL_DELAY_SECONDS", 0.5)
USER_AGENT = os.getenv("USER_AGENT", "HackathonRAGBot/0.1")

# --- Storage ---
DATA_DIR = Path(os.getenv("DATA_DIR", "data/sessions"))

# --- Chunking ---
CHUNK_TARGET_TOKENS = _int("CHUNK_TARGET_TOKENS", 800)
CHUNK_OVERLAP_TOKENS = _int("CHUNK_OVERLAP_TOKENS", 120)


def session_dir(session_id: str) -> Path:
    """Filesystem root for one crawl session's knowledge base."""
    return DATA_DIR / session_id
