# Tests — Implementation Plan

> Derived from [architecture.md](../../architecture.md) (§10 Security Architecture) and [FINAL_PLAN_IMPROVED.md](../../FINAL_PLAN_IMPROVED.md) (§33 Evaluation Set, §35 Verification Checklist, Milestone 8).

## Purpose

Verify crawler safety/limits, URL canonicalization, retrieval/evidence-gate behavior, and flow routing correctness against the evaluation set.

## Modules

- `test_crawler.py` — max pages/depth, `robots.txt` respected, SSRF + redirect revalidation, non-HTML skipped, crawl-failure handling
- `test_canonicalizer.py` — host lowercasing, fragment/tracking-param stripping, trailing-slash normalization, relative URL resolution, dedupe
- `test_retrieval.py` — top-k search, service-scoped filter with fallback, evidence gate pass/fail thresholds
- `test_flows.py` — full ordered cascade incl. greeting-prefix stripping, compound-message handling, follow-up pronoun resolution
- `test_questions.json` — evaluation set: greeting, service_list, service_detail, follow_up, general_qa, unsupported/pricing, fallback, paraphrase/near-match, prompt-injection-in-page-content

## Key Tasks

- [ ] Cover every row of the evaluation set
- [ ] Zero-retained-page sites must fail clearly, never produce a "ready" session
- [ ] Redirect to a disallowed host must be rejected even if the original URL was allowed
- [ ] Prompt-injection text embedded in scraped content must not be followed by the model/prompt layer
- [ ] Fallback must fire when the evidence gate score is below threshold

## Depends On

`ingest/` and `app/` (imports the modules under test).
