# Ingest Service — Implementation Plan

> Derived from [architecture.md](../../architecture.md) (§2–4, DFD processes 1.0–3.3) and [FINAL_PLAN_IMPROVED.md](../../FINAL_PLAN_IMPROVED.md) (Milestones 2–4).

## Purpose

Turns a user-supplied URL into a bounded set of cleaned, chunked, service-labeled documents ready for embedding: validate → canonicalize → BFS-crawl (max 20 pages, robots.txt + SSRF safe) → clean HTML → detect services → chunk with heading context.

## Modules

- `url_validator.py` — scheme/host allow-list, SSRF checks (block localhost/private/internal IPs)
- `canonicalizer.py` — lowercase host, strip fragments/tracking params, normalize trailing slash, resolve relative URLs, dedupe
- `robots.py` — fetch/parse `robots.txt`, allow/deny per URL
- `crawler.py` — bounded BFS (`MAX_PAGES=20`, `MAX_DEPTH`), redirect revalidation, link extraction
- `extractor.py` — HTML cleaning, title/heading/main-content extraction
- `service_detector.py` — deterministic service catalog detection (URL patterns, headings, nav labels)
- `chunker.py` — heading-aware chunking (~700–900 tokens, ~100–150 overlap)
- `pipeline.py` — orchestrates the above per session, writes to `data/sessions/<session_id>/`

## Key Tasks

- [ ] Validate URL scheme (http/https only) and allowed host
- [ ] SSRF-safe checks, including revalidating every redirect target
- [ ] `robots.txt` check before each fetch
- [ ] Canonicalize + dedupe URLs against `visited_urls`
- [ ] BFS crawl enforcing max pages/depth, timeout, response-size limit
- [ ] Skip non-HTML/binary responses
- [ ] Clean HTML and extract title/headings/main content
- [ ] Build the service catalog deterministically (no per-page LLM calls)
- [ ] Chunk with heading context retained; attach document/chunk metadata (`crawl_session_id`, `source_url`, `service`)
- [ ] Persist `raw/` and `cleaned/` pages per session
- [ ] Hand chunks to `app.bedrock` (embeddings) + `app.vectorstore` (FAISS build)
- [ ] Handle crawl failures gracefully; never mark a session "ready" with zero retained pages
- [ ] Write `manifest.json` summarizing the run

## Depends On

`app/bedrock.py` (embeddings), `app/vectorstore.py` (FAISS index), `app/db.py` (session/crawl_job persistence)
