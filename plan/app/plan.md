# App (Backend) — Implementation Plan

> Derived from [architecture.md](../../architecture.md) (§5, §8, §9, DFD processes 4.0–7.0) and [FINAL_PLAN_IMPROVED.md](../../FINAL_PLAN_IMPROVED.md) (Milestones 1, 5, 6, 8).

## Purpose

FastAPI backend exposing `/ingest`, `/chat`, `/sessions`, `/analytics`. Hosts the Bedrock clients, the deterministic flow router, the RAG/retrieval service, and SQLite persistence.

## Modules

- `config.py` — env/config (AWS region, model IDs, crawl/retrieval limits)
- `bedrock.py` — Nova Pro Converse API call + Titan Embed Text v2 call
- `sessions.py` — session lifecycle (create/read/update `session_id`, status)
- `vectorstore.py` — FAISS `IndexFlatIP` wrapper: build/load/persist/search per session
- `retrieval.py` — query embedding, top-k search, evidence gate
- `rag.py` — grounded prompt (untrusted-evidence framing), Nova Pro call, citation extraction
- `flows.py` — deterministic router cascade (`greeting → service_list → service_detail → follow_up → general_qa → fallback`)
- `analytics.py` — aggregates `flow_events`/`messages` into a report
- `db.py` — SQLite schema + access (`sessions`, `crawl_jobs`, `messages`, `flow_events`, `documents`)
- `main.py` — FastAPI app wiring routes to the above

## Key Tasks

- [ ] Nova Pro + Titan Embed smoke tests
- [ ] SQLite schema for all five tables
- [ ] `POST /ingest` — create session, kick off bounded crawl job
- [ ] `GET /ingest/{job_id}` — crawl status polling
- [ ] `vectorstore.py` — build/load/persist FAISS index per session
- [ ] `retrieval.py` — embed query, FAISS top 8–12, optional `service` filter, evidence gate threshold
- [ ] `rag.py` — grounded system prompt with prompt-injection defenses, cite only sources actually used
- [ ] `flows.py` — ordered rule cascade + greeting-prefix stripping + session state (`current_service`, `last_flow`, `last_sources`)
- [ ] `POST /chat` — route → retrieve → generate → persist message + flow_event
- [ ] `GET /sessions/{session_id}` — transcript + crawl status + services
- [ ] `GET /analytics/report` — pages crawled/failed, chunks, fallback rate, latency, top sources
- [ ] Keep AWS credentials server-side only; never expose to the client

## Depends On

`ingest/` (produces chunks + manifest), AWS Bedrock, filesystem session data under `data/sessions/`.
