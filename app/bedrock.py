"""AWS Bedrock wrappers.

Shared file. Two independent functions, low conflict risk:
  - embed_texts  -> Dev A (Titan Embed Text v2)
  - chat         -> Dev B (Nova Pro Converse)  [placeholder below]
"""

from __future__ import annotations

import json
from functools import lru_cache

import boto3

from app import config


@lru_cache(maxsize=1)
def _client():
    return boto3.client("bedrock-runtime", region_name=config.AWS_REGION)


# ---------------------------------------------------------------------------
# Dev A — Titan Embed Text v2
# ---------------------------------------------------------------------------
def embed_text(text: str) -> list[float]:
    """Embed a single string into a 1024-dim vector via Titan Embed Text v2."""
    body = json.dumps({"inputText": text, "dimensions": config.EMBED_DIMENSIONS})
    resp = _client().invoke_model(modelId=config.BEDROCK_EMBED_MODEL_ID, body=body)
    payload = json.loads(resp["body"].read())
    return payload["embedding"]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed many strings. Titan has no batch endpoint, so loop per input."""
    return [embed_text(t) for t in texts]


# ---------------------------------------------------------------------------
# Dev B — Nova Pro Converse  (placeholder; Dev B implements)
# ---------------------------------------------------------------------------
def chat(*args, **kwargs):  # noqa: ANN002, ANN003
    raise NotImplementedError("Nova Pro Converse wrapper is owned by Dev B.")
