# AI Analysis State and Cache Assessment

**Date:** July 26, 2026
**Scope:** Dashboard AI-analysis panels, repeated-query behavior, PDF preview, result and analysis export, Redis caching, and parsed full-text caching

## Executive Summary

OmicsOracle has effective server-side caching for searches, metadata, parsed full text, and raw AI model responses. Redis is active in the reviewed environment, and identical AI requests can avoid duplicate OpenAI calls for seven days.

The dashboard does not currently provide the expected analysis-panel experience. Completed analyses exist only in the rendered DOM. They are not retained in JavaScript state or `sessionStorage`, opening one analysis does not collapse another, and rebuilding search results removes rendered analyses. Running the same search can use the server's search cache, but it does not automatically restore completed analysis panels.

The highest-priority improvement is therefore a frontend analysis-state layer. It should cache structured analysis responses for the browser session, keep at most one panel expanded, restore completed analyses after result rendering, and use the existing Redis AI cache as the cross-session fallback.

Downloaded PDFs are currently available to the analysis pipeline but not to dashboard users. The preferred preview experience is a responsive document drawer: a right-side viewer on desktop and a full-screen viewer on narrow screens. This keeps the dataset and AI analysis in context, supports multiple papers, and avoids the cramped reading experience of a banner or small modal.

Export should be available at two distinct scopes: the complete returned search and each completed AI analysis. Search exports should prioritize interoperable JSON and CSV; analysis exports should prioritize structured JSON and readable Markdown, with browser print-to-PDF as a presentation option. Export must operate on structured state rather than rendered DOM text.

## Expected Behavior

1. Opening an analysis for dataset B collapses the analysis for dataset A.
2. A completed analysis remains available in collapsed form throughout the browser-tab session.
3. The user can expand or collapse a completed analysis without making another API request.
4. Re-rendering results, loading more results, or completing full-text enrichment does not lose completed analyses.
5. Repeating the same query restores matching completed analyses automatically.
6. Repeating an identical AI request does not invoke the model again while the server cache entry is valid.
7. Users can export all results returned by the current search, not only the cards currently visible.
8. Users can export a completed AI analysis without rerunning it.

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
| Downloaded PDF preview | Missing | Cards show PDF counts, but no authenticated PDF-serving route or preview UI exists. |
| Whole-search export | Missing | Search data is retained in browser memory, but no results export action exists. |
| AI analysis export | Partial/legacy | A JSON export scrapes `analysis-content.innerText`; it is not connected to structured inline-analysis state and may export the wrong or incomplete analysis. |

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
- `omics_oracle_v2/api/models/responses.py`
  - Full-text response data and local `pdf_path` fields
- `omics_oracle_v2/api/main.py`
  - Static-file mounts and current file-response routes
- `omics_oracle_v2/api/models/responses.py`
  - Structured search, dataset, publication, and report response fields

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

### 6. Downloaded Papers Cannot Be Inspected in the Dashboard

Dataset cards display the number of downloaded PDFs and whether they are available for AI analysis, but they do not provide a preview action. Response models contain local `pdf_path` values, while the API has no dedicated route for securely serving a downloaded paper. A filesystem path must not be converted directly into a public URL.

**Impact:** Users cannot verify source material, compare AI claims with the paper, or identify a wrong/corrupt download without leaving the application and locating files manually.

### 7. Export Is Incomplete and Coupled to Rendered HTML

The dashboard has a legacy **Export Report** action for the separate analysis section. It constructs JSON from `selectedDataset`, `analysis-content.innerText`, the current time, and the current user. Inline analyses are rendered in per-card containers, so this function is not a reliable representation of the active analysis. DOM text also loses response structure, model metadata, and distinctions between analysis, insights, and recommendations.

There is no export for search results. The browser already holds the full response returned by the search endpoint in `lastSearchResponse` and up to 1,000 datasets in `allSearchResults`, while only a subset is displayed. Exporting `currentResults` would silently omit results that have not yet been revealed with **Load More**.

**Impact:** Researchers cannot reliably move ranked results into statistical tools, preserve reproducible analysis artifacts, or share an AI result without copying rendered text manually.

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

### Priority 6: Responsive PDF Document Drawer

Add a **View Papers** action beside the existing PDF status when one or more files are available. The recommended presentation is:

- Desktop: a resizable right-side drawer occupying approximately 40-55% of the viewport, with the result card and AI analysis still visible on the left.
- Tablet and mobile: a full-screen document viewer with a clear back/close control.
- Multiple PDFs: a compact paper selector showing title, publication identifier, source, and download status. Selecting a paper changes the active preview without closing the drawer.
- Viewer: use the browser's native PDF renderer through an `iframe` or `object` initially. Provide **Open in New Tab** and **Download** fallbacks when inline rendering is unavailable.
- State: remember the selected paper and drawer width in memory for the current tab. Do not automatically reopen the drawer after a new search or page reload.

A centered modal is acceptable only as a short-term implementation. It blocks comparison with the analysis and becomes awkward for long documents. An expanded bar or banner is not recommended because a readable paper requires substantial vertical and horizontal space. Embedding a viewer inside every result card is also not recommended because it would destabilize card layout and create multiple expensive PDF renderers.

The drawer should connect evidence to analysis without trying to synchronize them prematurely. A later enhancement can allow analysis citations or paper references to open the relevant PDF, but page-level deep linking should wait until the backend reliably records page numbers or text coordinates.

#### Required API Contract

Do not expose or accept arbitrary filesystem paths. Add authenticated endpoints based on an opaque paper/acquisition identifier, for example:

```text
GET /api/papers/{paper_id}/content
GET /api/datasets/{geo_id}/papers
```

The metadata endpoint should return only browser-safe fields such as `paper_id`, title, PMID/PMCID/DOI, source, page count when known, and preview availability. It should not return the server's local `pdf_path`.

The content endpoint should:

- Resolve `paper_id` through persisted acquisition metadata.
- Verify that the resolved file remains inside the configured PDF storage root.
- Require the same authorization policy as the associated dataset or analysis.
- Return `Content-Type: application/pdf` and `Content-Disposition: inline` with a sanitized filename.
- Support HTTP range requests so browser viewers can seek through large papers efficiently.
- Reject missing, stale, non-PDF, and magic-byte-invalid files with explicit status codes.
- Use a restrictive content security policy and `X-Content-Type-Options: nosniff`.
- Avoid logging local paths, credentials, signed URLs, or paper content.

Only legally acquired files from the configured open-access or institutional providers should be previewable. The preview route must not broaden provider access or bypass source terms.

#### Preview Caching

The PDF file is already persistent storage and should not be copied into `sessionStorage`, local storage, or Redis. Let the browser use normal HTTP caching and range requests. Use conservative headers for authenticated content, for example private revalidation rather than a public shared cache. Revocation or deletion must make the content endpoint unavailable immediately.

### Priority 7: Structured Search and Analysis Export

Add an **Export** menu to the search-results header and an export action to each completed analysis panel. Keep the scopes explicit so users understand what will be downloaded.

#### Whole-Search Export

The initial implementation can run entirely in the browser because the dashboard requests up to 1,000 results in one response. Export the complete returned set from `lastSearchResponse` or `allSearchResults`, not the currently displayed `currentResults` slice.

Offer these formats:

- **CSV - All returned datasets:** one row per dataset with stable scalar columns such as rank, GEO ID, title, organism, platform, sample count, relevance score, publication date, PubMed IDs, citation count, PDF count, processing status, and match reasons. Encode list fields with a documented delimiter or JSON string.
- **JSON - Complete search:** a versioned, lossless export containing query, search terms, filters, query-processing context, total returned, dataset metadata, publication metadata, execution timestamp, and application/export schema version.

The menu label should state the scope, for example **Export 347 returned results**, even if only 50 cards are visible. If the backend reports more matches than it returned because of a limit, the export must say **returned results**, not **all matches**. A future server-side export job can support result sets beyond the response cap.

Do not include parsed full-text sections, local `pdf_path` values, user/authentication objects, cache keys, internal search logs, or credentials by default. Source publication identifiers and public source URLs are appropriate to include. An optional diagnostics export can be a separate, clearly labeled action for administrators.

#### Individual AI Analysis Export

Export from the structured analysis response retained by the proposed analysis state map. Never scrape `innerText` or serialized rendered HTML.

Offer these formats:

- **Markdown:** a readable report containing query, dataset identity, generated analysis, key insights, recommendations, model, generation time, and source-paper identifiers.
- **JSON:** the complete validated `AIAnalysisResponse` plus a versioned provenance envelope containing dataset/content fingerprint, query, model configuration, generated/cached timestamp, and application version.
- **Print / Save as PDF:** provide a print-optimized analysis view and invoke the browser print dialog. Defer server-generated PDF reports until branding, pagination, and archival requirements justify the added rendering dependency.

The export action should remain available when a restored analysis is collapsed and must not call `/api/agents/analyze` again. Use a filename such as:

```text
omicsoracle-analysis-GSE12345-2026-07-26.md
omicsoracle-search-breast-cancer-rna-seq-2026-07-26.csv
```

Sanitize filenames, cap their length, and use UTC timestamps inside exported metadata. Display model-generated content as such and include a concise notice that results require scientific review.

#### Combined Research Package

After search and per-analysis export are stable, consider an optional ZIP package for a reproducible handoff:

```text
manifest.json
datasets.csv
search.json
analyses/GSE12345.md
analyses/GSE67890.md
```

Include only analyses already completed for the current search. Do not trigger missing analyses during export and do not bundle downloaded PDFs by default because file size, licensing, and institutional-access terms vary. A PDF manifest with identifiers and legal source links is safer than copying documents into the package.

#### Export State and Caching

Exports are derived artifacts and do not need Redis entries. Generate small exports client-side from structured state. Revoke object URLs immediately after download. If server-side jobs are later introduced for very large exports, store short-lived job metadata separately and enforce the same authorization and data-minimization policy as the source search.

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
10. User selects **View Papers** on a dataset with downloaded PDFs.
11. Dashboard fetches paper metadata and opens the responsive document drawer.
12. The selected PDF streams through the authenticated content endpoint using range requests.
13. User can switch papers, compare the paper with the analysis, open it in a new tab, download it, or close the drawer without changing analysis state.
14. User opens the search-header **Export** menu and selects CSV or JSON for all returned results.
15. Dashboard builds the export from the complete structured search response, independent of how many cards are visible.
16. User exports a completed analysis as Markdown, JSON, or through a print-optimized view without another model request.

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
- A dataset with downloaded papers exposes a **View Papers** action; a dataset without papers does not.
- The desktop preview opens in a side drawer and the mobile preview opens full-screen without overflowing or covering controls.
- Users can switch among multiple downloaded papers without creating multiple embedded viewers.
- Closing the preview releases the embedded document and returns focus to the button that opened it.
- Keyboard users can open, navigate, and close the viewer; the close action supports `Escape` and has an accessible label.
- The PDF endpoint supports `HEAD` and byte-range requests and returns correct PDF headers.
- The PDF endpoint never accepts a local path and rejects traversal, unknown IDs, unauthorized access, files outside the storage root, and invalid PDF content.
- Local filesystem paths are absent from browser-facing paper metadata.
- Previewing a PDF does not duplicate it in Redis or browser storage.
- The search header reports the exact export scope and exports all returned datasets, including results not yet displayed by **Load More**.
- Search CSV has deterministic column order, stable UTF-8 encoding, escaped formulas, and correct quoting for commas, quotes, and newlines.
- Search JSON and analysis JSON contain an explicit schema version and enough provenance to interpret the artifact later.
- Per-analysis Markdown and JSON are generated from structured response state, not DOM text or HTML.
- Exporting a restored or collapsed analysis makes no network or model request.
- Exports omit parsed full text, local paths, authentication data, credentials, cache keys, and internal logs by default.
- Filenames are sanitized and deterministic enough to associate artifacts with their query or GEO dataset.
- Empty searches, partial responses, Unicode metadata, multiple PubMed IDs, and spreadsheet-formula-like values are covered by automated export tests.
- Object URLs are revoked after client-side downloads, and repeated exports do not leak browser memory.

## Conclusion

OmicsOracle's backend cache design already avoids much of the expensive repeated work. The missing analysis behavior is primarily frontend state management, not model caching. Implementing structured session analysis state, a single-open-panel controller, and restoration after result rendering will deliver the expected analysis experience.

Downloaded-paper preview is a separate but complementary usability improvement. A responsive document drawer backed by an authenticated, identifier-based, range-capable PDF endpoint gives researchers a practical way to validate AI output against source material without exposing local storage paths. Redis namespacing, explicit versioning, and structured-response caching remain worthwhile follow-up improvements for operational clarity and long-term maintainability.

Structured export completes the research workflow by making searches reusable in downstream tools and AI analyses preservable as reviewable artifacts. The implementation should replace the legacy DOM-scraping export with explicit search-level and analysis-level actions, versioned schemas, provenance, and conservative field filtering.
