"""Owned by Dev A (see TEAM_PLAN.md). Real crawl -> clean -> chunk -> embed -> index pipeline.

This stub only defines the integration contract Dev B's app/main.py depends on, so
POST /ingest can be wired end-to-end today and swapped to the real pipeline at
Integration Checkpoint 1 without changing the caller.
"""
from pathlib import Path


class IngestionNotImplemented(NotImplementedError):
    """Raised until Dev A's real crawl pipeline (Milestones 2-4) lands."""


def run_ingestion(session_id: str, url: str, session_dir: Path) -> dict:
    """Crawl `url`, build chunks + embeddings, and persist them under `session_dir`.

    Expected return shape (see architecture.md Section 8/9):
        {
          "pages_discovered": int,
          "pages_retained": int,
          "pages_failed": int,
          "chunks": int,
          "services": list[str],
        }
    Must write session_dir/{raw/,cleaned/,index.faiss,chunks.json,manifest.json}.
    """
    raise IngestionNotImplemented(
        "ingest.pipeline.run_ingestion is not implemented yet (Dev A, Milestones 2-4). "
        "app/main.py falls back to cloning data/sessions/fixture_demo so Dev B's "
        "retrieval/flow/UI work is testable end-to-end in the meantime."
    )
