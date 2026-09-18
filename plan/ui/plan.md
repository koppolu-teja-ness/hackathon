# UI (Streamlit) — Implementation Plan

> Derived from [architecture.md](../../architecture.md) (§5 Client, §9 API Contract) and [FINAL_PLAN_IMPROVED.md](../../FINAL_PLAN_IMPROVED.md) (§24 Streamlit UI, Milestone 7).

## Purpose

Single-page Streamlit app and the main demo surface: URL input, crawl status, discovered services, chat, and clickable sources. Talks only to the FastAPI backend over REST.

## Modules

- `streamlit_app.py` — the entire UI (single file is sufficient for the MVP)

## Key Tasks

- [ ] URL input + "Build Knowledge Base" button → `POST /ingest`
- [ ] Poll `GET /ingest/{job_id}`, render progress (`pages_retained / 20`)
- [ ] Render discovered services once the session is ready
- [ ] Chat input → `POST /chat`, render assistant reply
- [ ] Render sources as clickable links under each answer
- [ ] Persist `session_id`, `website_url`, `crawl_job_id`, `messages`, `crawl_status`, `services` in `st.session_state`
- [ ] Treat the backend (SQLite/FAISS) as the source of truth; `session_state` is UI cache only
- [ ] Display errors legibly (invalid URL, crawl failed, zero pages retained)
- [ ] Loading states for crawl + chat requests

## Depends On

`app/` REST API only — no direct Bedrock, FAISS, or SQLite access from the UI.
