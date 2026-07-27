# AI Analysis State and Cache Assessment

**Date:** July 26, 2026
**Scope:** Dashboard AI-analysis panels, repeated-query behavior, Redis caching, and parsed full-text caching

## Executive Summary

OmicsOracle has effective server-side caching for searches, metadata, parsed full text, and raw AI model responses. Redis is active in the reviewed environment, and identical AI requests can avoid duplicate OpenAI calls for seven days.

The dashboard does not currently provide the expected analysis-panel experience. Completed analyses exist only in the rendered DOM. They are not retained in JavaScript state or `sessionStorage`, opening one analysis does not collapse another, and rebuilding search results removes rendered analyses. Running the same search can use the server's search cache, but it does not automatically restore completed analysis panels.

The highest-priority improvement is therefore a frontend analysis-state layer. It should cache structured analysis responses for the browser session, keep at most one panel expanded, restore completed analyses after result rendering, and use the existing Redis AI cache as the cross-session fallback.

## Expected Behavior

1. Opening an analysis for dataset B collapses the analysis for dataset A.
2. A completed analysis remains available in collapsed form throughout the browser-tab session.
3. The user can expand or collapse a completed analysis without making another API request.
4. Re-rendering results, loading more results, or completing full-text enrichment does not lose completed analyses.
5. Repeating the same query restores matching completed analyses automatically.
6. Repeating an identical AI request does not invoke the model again while the server cache entry is valid.

## Current Behavior

| Capability | Status | Finding |
|---|---|---|
| Single expanded analysis | Missing | `analyzeDatasetInline()` opens the selected panel but does not collapse other `.inline-analysis` elements. |
| Expand/collapse completed analysis | Missing | The button is relabeled after completion but has no completed-state toggle behavior. |
| Browser-session persistence | Missing | No analysis map, `sessionStorage`, or equivalent state store exists. |
| Persistence across result rendering | Missing | `displayResults()` replaces the results container HTML and destroys analysis DOM state. |
| Automatic restoration for a repeated query | Missing | Search cards are rebuilt without restoring completed analysis responses. |
| Search result caching | Available | Redis caches equivalent search requests for 24 hours. |
| Duplicate model-call prevention | Available | Redis caches raw AI response text for seven days using a content-derived key. |
| Parsed full-text caching | Available | Parsed documents use a seven-day Redis hot tier and a 90-day compressed-disk warm tier. |

## Evidence Reviewed

The assessment covered these active implementation surfaces:

- `omics_oracle_v2/api/static/dashboard_v2.html`
  - Search and analysis state variables
  - `displayResults()`
  - `loadMoreResults()`
  - `analyzeDatasetInline()`
  - `displayAnalysisInline()`
- `omics_oracle_v2/api/helpers/llm.py`
  - AI cache-key construction
  - Redis lookup and storage
  - GPT-5.6 Responses API invocation
- `omics_oracle_v2/services/analysis_service.py`
  - Prompt composition and structured response parsing
- `omics_oracle_v2/cache/redis_cache.py`
  - Search, metadata, and generic cache operations
- `omics_oracle_v2/cache/parsed_cache.py`
  - Redis and disk parsed-content tiers
- `omics_oracle_v2/lib/search_orchestration/orchestrator.py`
  - Search cache reads and writes

Live Redis inspection found:

- Redis enabled and connected.
- Four `ai_summary:*` AI response entries.
- Six `omics_search:search:*` search entries.
- AI entries stored as Redis strings with approximately seven days remaining when inspected.

No cached analysis text, prompts, API keys, or other sensitive values were read during this inspection.

## Cache Architecture

### Search Results

The search orchestrator constructs a cache identity from the query, search type, maximum GEO results, and maximum publication results. Search entries use the namespaced search cache and normally expire after 24 hours.

A cache hit returns a reconstructed `SearchResult` and marks `cache_hit=True`. This avoids repeating the upstream search, but the dashboard still renders new cards and has no associated analysis-state restoration step.

### AI Model Responses

The AI helper derives a truncated SHA-256 identifier from:

```text
prompt | system_message | model | temperature | reasoning_effort
```

The prompt includes the search query, selected dataset metadata, match context, and available parsed paper content. Dataset identity is therefore represented by the content being hashed even though the GEO accession is not a separate key segment. Accidental cross-dataset collision is not a practical concern at this system's scale.

The cached value contains raw model response text and the model name. The normal analysis service still parses that text into insights and recommendations after a cache hit. The cache prevents duplicate model work, but it does not store browser panel state or automatically deliver completed analyses with search results.

### Publication and GEO Metadata

Redis also caches publication metadata and GEO metadata independently. The configured default lifetimes are:

- Publication metadata: seven days.
- GEO metadata: 30 days.
- Query optimization: 24 hours.

These caches reduce upstream API traffic and do not control dashboard interaction state.

### Parsed Full Text

Parsed publication content has two tiers:

1. Redis hot tier: seven days.
2. Compressed JSON disk tier: 90 days.

The disk tier preserves expensive parsing results after Redis expiry and can repopulate the hot tier. Downloaded PDFs and acquisition records are persisted separately through filesystem and database storage.

## Design Gaps and Risks

### 1. Frontend State Is Coupled to the DOM

The completed analysis response is not retained as structured application state. Any operation that invokes `displayResults()` can remove it, including pagination and result updates. This is the direct cause of lost analyses during a session.

**Impact:** High user-friction and unnecessary `/api/agents/analyze` requests.

### 2. Server Cache and UI Cache Have Different Responsibilities

Redis can prevent another model invocation, but the browser still performs an API round trip and reparses the response. It cannot know that an analysis exists until it asks the server.

**Impact:** Cached requests are cheaper than live model calls but still feel like new analysis operations and cannot restore panel state immediately.

### 3. Generic Redis Methods Do Not Apply Their Documented Prefix

`RedisCache.get()` and `RedisCache.set()` state that keys are automatically prefixed, but they call Redis with the supplied key directly. AI entries are consequently stored as `ai_summary:*` rather than under the configured `omics_search` namespace. The parsed-content hot tier is affected by the same generic method behavior.

**Impact:** Key ownership is less clear, cache statistics omit generic entries, and environments sharing a Redis database have a greater key-collision risk.

### 4. AI Cache Stores an Internal Provider Artifact

The AI cache stores raw model text rather than the complete validated `AIAnalysisResponse`. It saves model cost, but response parsing and service assembly still run on every cache hit.

**Impact:** Moderate maintainability and observability limitation; not a correctness failure.

### 5. Cache Versioning Is Implicit

Prompt changes usually alter the AI key because the complete prompt is hashed, but parser/schema changes do not have an explicit cache schema version.

**Impact:** Old provider responses may be reparsed under new application assumptions until their seven-day TTL expires.

## Recommended Design

### Priority 1: Browser Analysis State

Add a structured in-memory map and mirror it to `sessionStorage`. Do not cache rendered HTML.

A logical entry should contain:

```json
{
  "key": "normalized-query::GSE12345::content-fingerprint::gpt-5.6-terra",
  "query": "normalized query",
  "geoId": "GSE12345",
  "contentFingerprint": "server-provided revision",
  "model": "gpt-5.6-terra",
  "response": {},
  "cachedAt": "ISO-8601 timestamp"
}
```

Track a separate `openAnalysisKey` in memory. Opening one panel collapses the previous panel without deleting its response. Completed buttons should toggle between **Show Analysis** and **Hide Analysis** and must not call the API when a session entry exists.

After every `displayResults()` call, restore matching analyses from structured state. Restored panels should start collapsed unless their key equals `openAnalysisKey`.

Use a bounded session cache, for example 20 to 50 analyses or a conservative serialized-size limit, because browser storage is limited. If storage quota is exceeded, retain in-memory behavior and evict the least recently used session entries.

### Priority 2: Stable Server Fingerprint

Have the backend return an analysis request fingerprint or content revision derived from the same canonical inputs used by the server cache. The browser should use that value instead of approximating content identity from counts such as `fulltext_count`.

This prevents stale browser analyses when paper content changes without changing the result count.

### Priority 3: Redis Namespacing and Versioning

Make generic cache methods consistently apply a namespace, or require callers to supply an explicitly fully qualified key. Use versioned key families such as:

```text
omics:ai:v2:{request_fingerprint}
omics:parsed:v2:{publication_id}:{content_revision}
```

A migration is not required for ephemeral entries: new versioned keys can coexist with old keys until the old TTLs expire.

### Priority 4: Structured AI Cache and Observability

Consider caching the validated analysis response rather than only raw provider text. Include non-sensitive response metadata:

- `cache_hit`
- cache age or creation time
- model
- reasoning effort
- prompt/schema version

Expose cache hit status to logs or API diagnostics, not as a prominent dashboard detail. Never expose cache keys containing raw query or publication text.

### Priority 5: Configurable Retention

Move the hardcoded AI TTL to configuration. Seven days is a reasonable default, but deployments should be able to tune cost, freshness, and Redis capacity independently.

## Proposed Interaction Flow

1. User clicks **AI Analysis**.
2. Dashboard computes or requests the stable analysis fingerprint.
3. Dashboard checks its in-memory/session cache.
4. On a browser-cache hit, it renders immediately and expands the selected panel.
5. On a miss, it calls `/api/agents/analyze`.
6. The backend checks Redis and either returns cached analysis data or invokes the configured GPT-5.6 model.
7. Dashboard stores the structured response and renders it.
8. Opening another analysis collapses the current panel while preserving both responses.
9. A repeated search rebuilds result cards and reattaches matching analyses in collapsed form.

## Acceptance Criteria

- At most one completed analysis panel is expanded at a time.
- Collapsing and reopening a completed panel makes no network request.
- Loading more results does not discard completed analyses already present in the result set.
- Completing a full-text download and re-rendering the cards preserves analyses whose content fingerprint is unchanged.
- Repeating the same query in the same browser tab restores completed analyses without an analysis API request.
- Reloading the tab during the same browser session restores matching analyses from `sessionStorage`.
- A changed dataset content fingerprint causes a browser-cache miss.
- An identical server request produces a Redis hit and does not call the model.
- Redis key families are namespaced and versioned.
- Cache entries never contain API keys or credentials.
- Automated tests cover panel toggling, one-open-panel behavior, result re-render restoration, session restoration, stale fingerprint invalidation, Redis hit behavior, and Redis-unavailable fallback.

## Conclusion

OmicsOracle's backend cache design already avoids much of the expensive repeated work. The missing behavior is primarily frontend state management, not model caching. Implementing structured session analysis state, a single-open-panel controller, and restoration after result rendering will deliver the expected experience. Redis namespacing, explicit versioning, and structured-response caching are worthwhile follow-up improvements for operational clarity and long-term maintainability.
