# OmicsOracle: Complete Search Query Flow Diagram

**Date:** November 2, 2025  
**Purpose:** Comprehensive visualization of the end-to-end search query processing pipeline

---

## 🎯 **Executive Summary**

OmicsOracle processes user queries through **7 distinct stages** to deliver comprehensive results combining GEO datasets, publications, and full-text content:

```
User Query → Query Processing → Parallel Search → Result Merging → 
Enrichment → Full-text Retrieval → AI Analysis → Display
```

---

## 📊 **High-Level Flow (Simplified for Presentations)**

### **Version 1: Ultra-Simple (Best for Non-Technical Audiences)**

```
┌─────────────────────────────────────────────────────────┐
│         USER INPUT (Frontend Dashboard)                │
│     "Find RNA-seq datasets for diabetes"               │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│    QUERY PROCESSING (NLP + Optimization)                │
│    • Extract entities: disease, study_type, organism    │
│    • Expand synonyms: diabetes → "diabetes mellitus"    │
│    • Detect query type: keyword, GEO ID, or hybrid      │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│         PARALLEL SEARCH (3 sources)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   GEO    │  │  PubMed  │  │ OpenAlex │              │
│  │ Datasets │  │ Articles │  │  Papers  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│    RESULT MERGING & RANKING                             │
│    • Deduplicate across sources                         │
│    • Rank by relevance (BM25 + semantic)                │
│    • Link datasets ↔ publications                       │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│    ENRICHMENT (Optional)                                │
│    • Citation discovery (papers citing datasets)        │
│    • Full-text download (PDF/PMC)                       │
│    • Content parsing (tables, figures, methods)         │
│    • AI analysis (GPT-4 summarization)                  │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│         FRONTEND DISPLAY                                │
│    • Dataset cards with metadata                        │
│    • Publication cards with abstracts                   │
│    • Download buttons for PDFs                          │
│    • AI-generated summaries                             │
└─────────────────────────────────────────────────────────┘
```

---

### **Version 2: Expanded (Shows Download & AI Features Explicitly)**

```
┌─────────────────────────────────────────────────────────┐
│         USER INPUT (Frontend Dashboard)                 │
│     "Find RNA-seq datasets for diabetes"                │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│    QUERY PROCESSING (NLP + Optimization)                │
│    • Biomedical entity extraction (diseases, genes)     │
│    • Synonym expansion + query optimization             │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│         PARALLEL SEARCH (3 sources)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │   GEO    │  │  PubMed  │  │ OpenAlex │               │
│  │ Datasets │  │ Articles │  │  Papers  │               │
│  └──────────┘  └──────────┘  └──────────┘               │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│    RESULT MERGING & RANKING                             │
│    • Deduplicate by DOI/PMID                            │
│    • Rank by relevance (BM25 scoring)                   │
│    • Link datasets ↔ publications                       │
└────────────────┬────────────────────────────────────────┘
                 ↓
         ┌───────┴───────┐
         │               │
         ▼               ▼
┌──────────────┐  ┌──────────────────────────────────────┐
│   DISPLAY    │  │   ENRICHMENT (User Clicks "Enrich")  │
│   RESULTS    │  │                                      │
│ (Immediate)  │  │  Step 1: Citation Discovery          │
│              │  │    • Find papers citing datasets     │
│              │  │    • Multi-source search (PMC, etc.) │
│              │  │                                      │
│              │  │  Step 2: Full-text Download          │
│              │  │    • PMC XML (best quality)          │
│              │  │    • Open access PDFs                │
│              │  │    • Publisher sources               │
│              │  │                                      │
│              │  │  Step 3: Content Parsing             │
│              │  │    • Extract methods, results        │
│              │  │    • Parse tables & figures          │
│              │  │                                      │
│              │  │  Step 4: AI Analysis (GPT-4)         │
│              │  │    • Generate summaries              │
│              │  │    • Extract key findings            │
│              │  │    • Quality scoring                 │
│              │  └──────────────┬───────────────────────┘
│              │                 │                       │
│              │◄────────────────┘                       │    
│              │          ↓                              │
│   • Dataset cards with metadata & scores               │
│   • Publication cards with abstracts                   │
│   • PDF download buttons                               │
│   • AI-generated summaries (if enriched)               │
│   • Citing papers with quality scores                  │
└────────────────────────────────────────────────────────┘
```

**Use Version 2 when:**
- Demoing the platform's advanced features
- Technical audience that wants implementation details
- Highlighting competitive advantages (AI + full-text)

---

### **Version 3: Two-Slide Split (Most Flexible)**

**Slide 1: Core Search Pipeline**
```
┌─────────────────────────────────────────────────────────┐
│  1. USER QUERY                                          │
│     "diabetes RNA-seq"                                  │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  2. QUERY PROCESSING                                    │
│     NER → Synonym Expansion → Optimization             │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  3. PARALLEL SEARCH                                     │
│     GEO + PubMed + OpenAlex                            │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  4. RESULTS                                             │
│     Datasets + Publications (ranked & linked)          │
└─────────────────────────────────────────────────────────┘
```

**Slide 2: Enrichment Pipeline (Optional)**
```
User clicks "Enrich" on a dataset
        ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 1: Citation Discovery                            │
│  Find papers citing this dataset (PMC, Semantic Scholar)│
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 2: Full-text Download                            │
│  Download PDFs/XML from PMC, Unpaywall, publishers     │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 3: Content Parsing                               │
│  Extract methods, results, tables, figures             │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  STEP 4: AI Analysis (GPT-4)                           │
│  • One-sentence summary                                │
│  • Key findings extraction                             │
│  • Quality scoring (0.0-1.0)                           │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  ENRICHED RESULTS                                       │
│  • 5-10 citing papers with AI summaries                │
│  • Downloadable PDFs                                   │
│  • Quality scores for filtering                        │
└─────────────────────────────────────────────────────────┘
```


---

## 🔬 **Detailed Technical Flow**

### **STAGE 1: User Input → API Gateway**

```
┌──────────────────────────────────────────────────────────────┐
│ FRONTEND (dashboard_v2.html)                                │
│                                                              │
│ User enters: "diabetes RNA-seq human"                       │
│ Selects filters:                                            │
│   ✓ Organism: Homo sapiens                                 │
│   ✓ Study type: Expression profiling by high throughput... │
│   ✓ Max results: 20                                        │
│                                                              │
│ [Search Button] clicked                                     │
│                                                              │
│ JavaScript:                                                  │
│   fetch('POST /api/agents/search', {                        │
│     body: JSON.stringify({                                  │
│       search_terms: ["diabetes RNA-seq human"],            │
│       filters: {                                            │
│         organism: "Homo sapiens",                           │
│         study_type: "Expression profiling..."               │
│       },                                                     │
│       max_results: 20,                                      │
│       enable_semantic: false                                │
│     })                                                       │
│   })                                                         │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ API GATEWAY (api/routes/agents.py)                          │
│                                                              │
│ @router.post("/search")                                     │
│ async def execute_search(request: SearchRequest):           │
│     # Receives:                                             │
│     # - search_terms: List[str]                             │
│     # - filters: Optional[Dict]                             │
│     # - max_results: int                                    │
│     # - enable_semantic: bool                               │
│                                                              │
│     original_query = " ".join(request.search_terms)         │
│     # → "diabetes RNA-seq human"                            │
└──────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/api/static/dashboard_v2.html` (Frontend UI)
- `omics_oracle_v2/api/routes/agents.py` (API endpoint)

---

### **STAGE 2: Query Processing & Optimization**

```
┌──────────────────────────────────────────────────────────────┐
│ QUERY ANALYZER (lib/query/analyzer.py)                      │
│                                                              │
│ Input: "diabetes RNA-seq human"                             │
│                                                              │
│ Step 1: Detect query type                                   │
│   detect_query_type(query)                                  │
│   → Type: "KEYWORD" (not a GEO ID like GSE12345)           │
│                                                              │
│ Step 2: Extract components                                  │
│   components = {                                            │
│     'disease': 'diabetes',                                  │
│     'technology': 'RNA-seq',                                │
│     'organism': 'human'                                     │
│   }                                                          │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ NLP PROCESSING (lib/nlp/)                                   │
│                                                              │
│ Step 1: Biomedical NER (biomedical_ner.py)                 │
│   ner = BiomedicalNER()                                     │
│   entities = ner.extract_entities("diabetes RNA-seq human") │
│                                                              │
│   Output: {                                                 │
│     'diseases': ['diabetes', 'diabetes mellitus'],         │
│     'genes': [],                                            │
│     'organisms': ['human', 'Homo sapiens'],                │
│     'techniques': ['RNA-seq', 'RNA sequencing']            │
│   }                                                          │
│                                                              │
│ Step 2: Query Expansion (query_expander.py)                │
│   expander = QueryExpander()                                │
│   expanded = expander.expand_with_synonyms(entities)        │
│                                                              │
│   Output: "diabetes OR 'diabetes mellitus' AND             │
│            'RNA-seq' OR 'RNA sequencing' AND               │
│            human OR 'Homo sapiens'"                         │
│                                                              │
│ Step 3: Query Optimization (query/optimizer.py)            │
│   optimizer = QueryOptimizer()                              │
│   optimized = optimizer.optimize(query, entities)           │
│                                                              │
│   Output: {                                                 │
│     'original': 'diabetes RNA-seq human',                   │
│     'optimized': 'diabetes[All Fields] AND RNA-seq[...] AND Homo sapiens[Organism]',
│     'entities': {...},                                      │
│     'confidence': 0.92                                      │
│   }                                                          │
└──────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/lib/query/analyzer.py` - Query type detection
- `omics_oracle_v2/lib/nlp/biomedical_ner.py` - Entity extraction (diseases, genes, organisms)
- `omics_oracle_v2/lib/nlp/query_expander.py` - Synonym expansion
- `omics_oracle_v2/lib/query/optimizer.py` - Query optimization

---

### **STAGE 3: Search Orchestration (Parallel Search)**

```
┌──────────────────────────────────────────────────────────────┐
│ SEARCH ORCHESTRATOR (lib/search/orchestrator.py)            │
│                                                              │
│ config = OrchestratorConfig(                                │
│     enable_geo=True,                                        │
│     enable_pubmed=True,                                     │
│     enable_openalex=True,                                   │
│     max_results_per_source=20                               │
│ )                                                            │
│                                                              │
│ orchestrator = SearchOrchestrator(config)                   │
│ result = await orchestrator.search(                         │
│     query="diabetes RNA-seq Homo sapiens",                  │
│     max_results=20                                          │
│ )                                                            │
│                                                              │
│ Launches 3 parallel searches:                               │
│   ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│   │ GEO Search │  │   PubMed   │  │  OpenAlex  │            │
│   └──────┬─────┘  └──────┬─────┘  └──────┬─────┘            │
│          │                │                │                 │
│          ▼                ▼                ▼                 │
└──────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/lib/search/orchestrator.py` - Main search coordinator

---

### **STAGE 3a: GEO Dataset Search**

```
┌──────────────────────────────────────────────────────────────┐
│ GEO CLIENT (lib/geo/client.py)                              │
│                                                              │
│ Step 1: Check Redis Cache                                   │
│   cache_key = f"geo:search:{query_hash}"                    │
│   cached = await redis.get(cache_key)                       │
│   if cached:                                                │
│       return cached_results  # 1000x speedup!              │
│                                                              │
│ Step 2: Build GEO-specific query                           │
│   geo_query = GEOQueryBuilder().build_query(                │
│       query="diabetes",                                     │
│       filters={                                             │
│           "organism": "Homo sapiens",                       │
│           "study_type": "Expression profiling by high..."   │
│       }                                                      │
│   )                                                          │
│                                                              │
│   Result: "diabetes[All Fields] AND                         │
│            Homo sapiens[Organism] AND                       │
│            gse[Entry Type] AND                              │
│            Expression profiling by high throughput sequencing[Study Type]"
│                                                              │
│ Step 3: Search NCBI GEO Database                           │
│   esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
│   params = {                                                │
│       "db": "gds",                                          │
│       "term": geo_query,                                    │
│       "retmax": 500,                                        │
│       "retmode": "json"                                     │
│   }                                                          │
│                                                              │
│   response = await http_client.get(esearch_url, params)    │
│                                                              │
│   Result: {                                                 │
│       "esearchresult": {                                    │
│           "count": "142",                                   │
│           "idlist": [                                       │
│               "200123456",  # GDS ID                        │
│               "200123457",                                  │
│               ...                                           │
│           ]                                                  │
│       }                                                      │
│   }                                                          │
│                                                              │
│ Step 4: Fetch Detailed Metadata                            │
│   geo_ids = extract_gse_ids(idlist)  # GSE123456, ...      │
│                                                              │
│   datasets = await batch_get_metadata(                      │
│       geo_ids=geo_ids[:20],  # Limit to max_results        │
│       max_concurrent=5                                      │
│   )                                                          │
│                                                              │
│   For each dataset:                                         │
│     esummary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
│     params = {"db": "gds", "id": geo_id}                   │
│     metadata = parse_geo_metadata(response)                 │
│                                                              │
│   Result: [                                                 │
│       GEODataset(                                           │
│           geo_id="GSE251935",                               │
│           title="RNA-seq of diabetes patients",            │
│           organism="Homo sapiens",                          │
│           pubmed_id="38376465",                             │
│           summary="...",                                    │
│           samples_count=24,                                 │
│           platform="GPL24676"                               │
│       ),                                                     │
│       ...  # 19 more datasets                              │
│   ]                                                          │
│                                                              │
│ Step 5: Cache results                                      │
│   await redis.setex(cache_key, ttl=3600, value=results)    │
└──────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/lib/geo/client.py` - NCBI GEO API client
- `omics_oracle_v2/lib/geo/query_builder.py` - Build Entrez queries
- `omics_oracle_v2/lib/geo/models.py` - GEO dataset models

**External APIs:**
- NCBI E-utilities: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`

---

### **STAGE 3b: PubMed Publication Search**

```
┌──────────────────────────────────────────────────────────────┐
│ PUBMED CLIENT (lib/publications/pubmed_client.py)           │
│                                                              │
│ Step 1: Search PubMed                                       │
│   esearch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
│   params = {                                                │
│       "db": "pubmed",                                       │
│       "term": "diabetes AND RNA-seq",                       │
│       "retmax": 20,                                         │
│       "retmode": "json"                                     │
│   }                                                          │
│                                                              │
│   Result: {"idlist": ["38376465", "38778058", ...]}        │
│                                                              │
│ Step 2: Fetch Article Metadata                             │
│   efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
│   params = {                                                │
│       "db": "pubmed",                                       │
│       "id": ",".join(pmids),                                │
│       "retmode": "xml"                                      │
│   }                                                          │
│                                                              │
│   Result: [                                                 │
│       Publication(                                          │
│           pmid="38376465",                                  │
│           title="Transcriptomic analysis of diabetes",     │
│           authors=["Smith J", "Doe A"],                    │
│           journal="Nature",                                 │
│           year=2024,                                        │
│           abstract="...",                                   │
│           doi="10.1038/...",                                │
│           pmc_id="PMC10876543"                              │
│       ),                                                     │
│       ...  # 19 more publications                          │
│   ]                                                          │
└──────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/lib/publications/pubmed_client.py` - PubMed API client

---

### **STAGE 3c: OpenAlex Search**

```
┌──────────────────────────────────────────────────────────────┐
│ OPENALEX CLIENT (lib/publications/openalex_client.py)       │
│                                                              │
│ Step 1: Search OpenAlex                                     │
│   url = "https://api.openalex.org/works"                    │
│   params = {                                                │
│       "filter": "title.search:diabetes RNA-seq",            │
│       "per_page": 20,                                       │
│       "sort": "cited_by_count:desc"                         │
│   }                                                          │
│                                                              │
│   Result: {                                                 │
│       "results": [                                          │
│           {                                                 │
│               "id": "https://openalex.org/W4321...",       │
│               "title": "...",                               │
│               "doi": "10.1038/...",                         │
│               "open_access": {                              │
│                   "is_oa": true,                            │
│                   "oa_url": "https://..."                   │
│               },                                            │
│               "cited_by_count": 142                         │
│           },                                                 │
│           ...                                               │
│       ]                                                      │
│   }                                                          │
└──────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/lib/publications/openalex_client.py` - OpenAlex API client

---

### **STAGE 4: Result Merging & Ranking**

```
┌──────────────────────────────────────────────────────────────┐
│ RESULT AGGREGATOR (lib/search/orchestrator.py)              │
│                                                              │
│ Step 1: Collect results from all sources                    │
│   geo_results = [20 GEO datasets]                           │
│   pubmed_results = [20 PubMed articles]                     │
│   openalex_results = [20 OpenAlex papers]                   │
│                                                              │
│ Step 2: Deduplicate publications                            │
│   # Merge PubMed + OpenAlex by DOI/PMID                    │
│   unique_pubs = deduplicate_by_doi(                         │
│       pubmed_results + openalex_results                     │
│   )                                                          │
│   # Result: 35 unique publications (5 duplicates removed)   │
│                                                              │
│ Step 3: Link datasets ↔ publications                        │
│   for dataset in geo_results:                               │
│       if dataset.pubmed_id:                                 │
│           pub = find_publication(dataset.pubmed_id)         │
│           dataset.linked_publication = pub                  │
│           pub.linked_datasets.append(dataset)               │
│                                                              │
│   # Result: 15/20 datasets linked to publications          │
│                                                              │
│ Step 4: Rank by relevance                                  │
│   # BM25 keyword scoring                                    │
│   for item in [geo_results + unique_pubs]:                  │
│       item.relevance_score = bm25_score(                    │
│           query="diabetes RNA-seq",                         │
│           document=item.title + item.description            │
│       )                                                      │
│                                                              │
│   # Sort by score                                           │
│   ranked_datasets = sorted(geo_results, key=lambda x: x.relevance_score, reverse=True)
│   ranked_pubs = sorted(unique_pubs, key=lambda x: x.relevance_score, reverse=True)
│                                                              │
│ Step 5: Return combined results                            │
│   return SearchResponse(                                    │
│       datasets=ranked_datasets[:20],                        │
│       publications=ranked_pubs[:20],                        │
│       total_datasets=142,                                   │
│       total_publications=1543,                              │
│       query_time_ms=2847                                    │
│   )                                                          │
└──────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/lib/search/orchestrator.py` - Result aggregation & ranking
- `omics_oracle_v2/lib/search/ranker.py` - BM25 relevance scoring

---

### **STAGE 5: Enrichment (Optional - User Click)**

```
┌──────────────────────────────────────────────────────────────┐
│ USER CLICKS "Enrich" BUTTON on a dataset card               │
│                                                              │
│ Frontend sends:                                             │
│   POST /api/agents/enrich-fulltext                          │
│   {                                                          │
│       "datasets": [selected_dataset],                       │
│       "include_citing_papers": true,                        │
│       "max_papers": 5,                                      │
│       "download_fulltext": true                             │
│   }                                                          │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ CITATION DISCOVERY (lib/citations/geo_citation_pipeline.py) │
│                                                              │
│ Input: GSE251935 (has pubmed_id: 38376465)                 │
│                                                              │
│ Step 1: Find papers citing this dataset's publication       │
│   citation_client = CitationClient()                        │
│   citing_papers = await citation_client.find_citing_papers( │
│       pubmed_id="38376465",                                 │
│       max_results=100                                       │
│   )                                                          │
│                                                              │
│   Sources checked:                                          │
│     1. PubMed Central (PMC) citations                       │
│     2. OpenCitations API                                    │
│     3. Semantic Scholar API                                 │
│     4. Europe PMC                                           │
│                                                              │
│   Result: [                                                 │
│       Citation(pmid="39123456", title="..."),              │
│       Citation(pmid="39123457", title="..."),              │
│       ...  # 47 citing papers found                        │
│   ]                                                          │
│                                                              │
│ Step 2: Fetch metadata for citing papers                   │
│   enriched_citations = await batch_fetch_metadata(          │
│       pmids=[c.pmid for c in citing_papers[:5]]            │
│   )                                                          │
└──────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/lib/citations/geo_citation_pipeline.py` - Citation discovery
- `omics_oracle_v2/lib/citations/discovery_client.py` - Multi-source citation search

---

### **STAGE 6: Full-Text Retrieval**

```
┌──────────────────────────────────────────────────────────────┐
│ FULLTEXT MANAGER (lib/fulltext/manager.py)                  │
│                                                              │
│ For each publication (original + citing papers):            │
│                                                              │
│ Step 1: Check local cache                                   │
│   cache_path = f"data/fulltext/parsed/{pmid}.json"         │
│   if exists(cache_path):                                    │
│       return load_cached_content(cache_path)                │
│                                                              │
│ Step 2: Download from best source                          │
│   sources_priority = [                                      │
│       "PMC_XML",      # PubMed Central (best quality)      │
│       "PMC_PDF",      # PMC PDF fallback                   │
│       "Unpaywall",    # Open access repositories           │
│       "Publisher"     # Direct from publisher              │
│   ]                                                          │
│                                                              │
│   for source in sources_priority:                           │
│       try:                                                  │
│           content = await download_fulltext(                │
│               pmid=pmid,                                    │
│               source=source                                 │
│           )                                                  │
│           if content:                                       │
│               break                                         │
│       except:                                               │
│           continue  # Try next source                       │
│                                                              │
│ Step 3: Parse content                                       │
│   if source == "PMC_XML":                                   │
│       parser = JATSXMLParser()                              │
│       parsed = parser.parse(content)                        │
│       # Extracts: title, abstract, methods, results,       │
│       #           discussion, tables, figures, references   │
│                                                              │
│   elif source.endswith("_PDF"):                             │
│       parser = PDFParser()                                  │
│       parsed = parser.parse(content)                        │
│       # Uses: PyMuPDF, pdfplumber for text extraction      │
│                                                              │
│   Result: {                                                 │
│       "pmid": "38376465",                                   │
│       "title": "...",                                       │
│       "abstract": "...",                                    │
│       "sections": {                                         │
│           "methods": "...",                                 │
│           "results": "...",                                 │
│           "discussion": "..."                               │
│       },                                                     │
│       "tables": [                                           │
│           {"caption": "...", "data": [[...]], ...},        │
│           ...                                               │
│       ],                                                     │
│       "figures": [...],                                     │
│       "references": [...]                                   │
│   }                                                          │
│                                                              │
│ Step 4: Save to cache                                      │
│   save_to_cache(cache_path, parsed)                        │
│   update_cache_db(pmid, parsed_metadata)                   │
└──────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/lib/fulltext/manager.py` - Main full-text orchestrator
- `omics_oracle_v2/lib/fulltext/downloaders/pmc_downloader.py` - PMC XML/PDF download
- `omics_oracle_v2/lib/fulltext/downloaders/unpaywall_downloader.py` - Open access PDFs
- `omics_oracle_v2/lib/fulltext/parsers/jats_parser.py` - Parse PMC XML
- `omics_oracle_v2/lib/fulltext/parsers/pdf_parser.py` - Parse PDFs
- `omics_oracle_v2/lib/fulltext/cache_db.py` - SQLite cache management

---

### **STAGE 7: AI Analysis (Optional)**

```
┌──────────────────────────────────────────────────────────────┐
│ AI ENRICHMENT (lib/ai/enrichment_agent.py)                  │
│                                                              │
│ Input: Full-text content from STAGE 6                       │
│                                                              │
│ Step 1: Extract key information                            │
│   extractor = InformationExtractor()                        │
│   key_info = extractor.extract({                            │
│       "methods": parsed.sections.methods,                   │
│       "results": parsed.sections.results,                   │
│       "tables": parsed.tables                               │
│   })                                                         │
│                                                              │
│   Result: {                                                 │
│       "sample_size": 24,                                    │
│       "methodology": "RNA-seq using Illumina NovaSeq",     │
│       "key_findings": [                                     │
│           "1234 differentially expressed genes",            │
│           "Pathway enrichment in glucose metabolism"        │
│       ],                                                     │
│       "datasets_mentioned": ["GSE123456"]                   │
│   }                                                          │
│                                                              │
│ Step 2: Generate AI summary (GPT-4)                        │
│   prompt = f"""                                             │
│   Summarize this biomedical research paper:                 │
│   Title: {parsed.title}                                    │
│   Abstract: {parsed.abstract}                               │
│   Methods: {parsed.sections.methods[:1000]}                │
│   Results: {parsed.sections.results[:1000]}                │
│                                                              │
│   Provide:                                                  │
│   1. One-sentence summary                                   │
│   2. Key findings (3-5 bullet points)                       │
│   3. Methodology overview                                   │
│   4. Clinical implications                                  │
│   """                                                        │
│                                                              │
│   summary = await gpt4_client.complete(prompt)              │
│                                                              │
│   Result: {                                                 │
│       "one_sentence": "Study identifies 1234 genes...",     │
│       "key_findings": ["...", "...", "..."],               │
│       "methodology": "RNA-seq with 24 diabetic patients",  │
│       "implications": "Potential therapeutic targets..."    │
│   }                                                          │
│                                                              │
│ Step 3: Quality scoring                                    │
│   quality_score = calculate_quality({                       │
│       "has_methods": True,                                  │
│       "has_tables": len(parsed.tables) > 0,                │
│       "has_figures": len(parsed.figures) > 0,              │
│       "word_count": len(full_text.split()),                │
│       "citation_count": citation_count                      │
│   })                                                         │
│                                                              │
│   # Score: 0.0-1.0 (0.85 = high quality)                   │
└──────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/lib/ai/enrichment_agent.py` - AI-powered analysis
- `omics_oracle_v2/lib/ai/gpt_client.py` - GPT-4 API wrapper

---

### **STAGE 8: Frontend Display**

```
┌──────────────────────────────────────────────────────────────┐
│ RESPONSE TO FRONTEND                                         │
│                                                              │
│ {                                                            │
│   "datasets": [                                             │
│     {                                                        │
│       "geo_id": "GSE251935",                                │
│       "title": "RNA-seq of diabetes patients",             │
│       "organism": "Homo sapiens",                           │
│       "samples_count": 24,                                  │
│       "pubmed_id": "38376465",                              │
│       "relevance_score": 0.94,                              │
│       "linked_publication": {                               │
│         "pmid": "38376465",                                 │
│         "title": "Transcriptomic analysis...",             │
│         "abstract": "...",                                  │
│         "has_fulltext": true,                               │
│         "pdf_available": true                               │
│       },                                                     │
│       "citing_papers": [                                    │
│         {                                                   │
│           "pmid": "39123456",                               │
│           "title": "Follow-up study...",                    │
│           "ai_summary": "This paper extends...",           │
│           "quality_score": 0.87,                            │
│           "fulltext_available": true                        │
│         },                                                   │
│         ...  # 4 more citing papers                        │
│       ]                                                      │
│     },                                                       │
│     ...  # 19 more datasets                                │
│   ],                                                         │
│   "publications": [                                         │
│     {                                                        │
│       "pmid": "38778058",                                   │
│       "title": "Another diabetes study",                    │
│       "relevance_score": 0.89,                              │
│       "cited_by_count": 142,                                │
│       "open_access": true,                                  │
│       "pdf_url": "https://..."                              │
│     },                                                       │
│     ...  # 19 more publications                            │
│   ],                                                         │
│   "query_info": {                                           │
│     "original_query": "diabetes RNA-seq human",             │
│     "optimized_query": "diabetes[All Fields] AND...",      │
│     "query_time_ms": 2847,                                  │
│     "total_datasets_found": 142,                            │
│     "total_publications_found": 1543,                       │
│     "cache_hits": 15,                                       │
│     "cache_misses": 25                                      │
│   }                                                          │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ FRONTEND RENDERING (dashboard_v2.html)                      │
│                                                              │
│ JavaScript processes response:                              │
│                                                              │
│ 1. Display dataset cards                                    │
│    for dataset in response.datasets:                        │
│        create_dataset_card({                                │
│            title: dataset.title,                            │
│            organism: dataset.organism,                      │
│            samples: dataset.samples_count,                  │
│            score: dataset.relevance_score,                  │
│            buttons: [                                       │
│                "View on NCBI",                              │
│                "Enrich with Papers",                        │
│                "Download PDFs"                              │
│            ]                                                 │
│        })                                                    │
│                                                              │
│ 2. Display publication cards                                │
│    for pub in response.publications:                        │
│        create_publication_card({                            │
│            title: pub.title,                                │
│            abstract: pub.abstract,                          │
│            pmid: pub.pmid,                                  │
│            has_pdf: pub.pdf_available,                     │
│            buttons: [                                       │
│                "View Abstract",                             │
│                "Download PDF",                              │
│                "View Full-Text"                             │
│            ]                                                 │
│        })                                                    │
│                                                              │
│ 3. Show enrichment data (if available)                     │
│    if dataset.citing_papers:                                │
│        show_citing_papers_modal(dataset.citing_papers)      │
│        show_ai_summaries(dataset.citing_papers)            │
│                                                              │
│ 4. Display query statistics                                │
│    update_stats_panel({                                     │
│        total_datasets: 142,                                 │
│        total_publications: 1543,                            │
│        query_time: "2.8s",                                  │
│        cache_hit_rate: "37.5%"                              │
│    })                                                        │
└──────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/api/static/dashboard_v2.html` - Frontend UI
- `omics_oracle_v2/api/static/js/search.js` - Search handling JavaScript

---

## 🔄 **Alternative Search Paths**

### **Path 1: GEO ID Direct Lookup**

```
User enters: "GSE251935"
     ↓
Query Analyzer detects: GEO_ID type
     ↓
SKIP search → Direct metadata fetch
     ↓
geo_client.get_dataset("GSE251935")
     ↓
Return single dataset with full metadata
```

**Time:** ~1 second (vs. 3-5s for full search)

---

### **Path 2: Semantic Search Mode**

```
User enables "Semantic Search" toggle
     ↓
Query Processing includes:
  - SapBERT biomedical embeddings
  - Semantic similarity scoring
  - Vector database search (Qdrant)
     ↓
Results ranked by:
  - Keyword relevance (BM25) × 0.3
  - Semantic similarity × 0.7
     ↓
More context-aware results
```

**Files:**
- `omics_oracle_v2/lib/nlp/sapbert_expander.py` - Semantic expansion
- `omics_oracle_v2/lib/search/semantic_ranker.py` - Vector similarity

---

## 📊 **Performance Metrics**

| Stage | Typical Time | Bottleneck | Cache Impact |
|-------|--------------|------------|--------------|
| **Query Processing** | 100-200ms | NER model inference | None |
| **GEO Search** | 1-3s | NCBI API latency | **1000x speedup** |
| **PubMed Search** | 500ms-2s | NCBI API | **100x speedup** |
| **OpenAlex Search** | 300-800ms | API rate limits | **50x speedup** |
| **Result Merging** | 50-100ms | Deduplication | None |
| **Citation Discovery** | 2-5s | Multiple API calls | **10x speedup** |
| **Full-text Download** | 5-30s per paper | Network + parsing | **Instant** if cached |
| **AI Analysis** | 3-8s per paper | GPT-4 API | **Instant** if cached |

**Total end-to-end:**
- **First query**: 3-10 seconds (cold cache)
- **Cached query**: 0.1-0.5 seconds (**1000x faster!**)

---

## 🗄️ **Caching Strategy**

```
┌─────────────────────────────────────────────────────────────┐
│ REDIS CACHE (Primary - In-memory)                          │
│                                                             │
│ geo:search:{query_hash} → GEO search results (1h TTL)     │
│ pubmed:search:{query_hash} → PubMed results (1h TTL)      │
│ citation:{pmid} → Citing papers list (24h TTL)            │
│ metadata:{geo_id} → Dataset metadata (7d TTL)             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ SQLITE CACHE (Persistent)                                  │
│                                                             │
│ fulltext_cache table:                                       │
│   - publication_id (primary key)                           │
│   - source_type (PMC/PDF/etc.)                             │
│   - content_hash                                            │
│   - parsed_date                                             │
│   - quality_score                                           │
│   - file_path (to JSON file)                               │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ FILE SYSTEM CACHE (Full-text content)                      │
│                                                             │
│ data/fulltext/parsed/{pmid}.json → Parsed content          │
│ data/pdfs/{geo_id}/{pmid}.pdf → Downloaded PDFs            │
│ data/cache/embeddings/{doc_id}.npy → Vector embeddings     │
└─────────────────────────────────────────────────────────────┘
```

**Files:**
- `omics_oracle_v2/lib/infrastructure/redis_client.py` - Redis operations
- `omics_oracle_v2/lib/fulltext/cache_db.py` - SQLite cache DB

---

## 🎯 **Key Takeaways**

1. **7-Stage Pipeline**: User → Query Processing → Parallel Search → Merging → Enrichment → Full-text → AI → Display

2. **3 Parallel Search Sources**: GEO, PubMed, OpenAlex (merged & deduplicated)

3. **Redis Caching**: 1000x speedup for repeated queries

4. **Flexible Enrichment**: Optional citation discovery + full-text + AI analysis

5. **Smart Linking**: Automatic dataset ↔ publication associations

6. **Multi-level Caching**: Redis (fast) → SQLite (persistent) → Filesystem (content)

7. **Progressive Enhancement**: Base search is fast, enrichment adds value without blocking

---

## 📁 **File Structure Summary**

```
omics_oracle_v2/
├── api/
│   ├── routes/
│   │   └── agents.py                  # API endpoints (search, enrich)
│   └── static/
│       └── dashboard_v2.html          # Frontend UI
│
├── lib/
│   ├── query/
│   │   ├── analyzer.py                # Query type detection
│   │   └── optimizer.py               # Query optimization
│   │
│   ├── nlp/
│   │   ├── biomedical_ner.py          # Entity extraction
│   │   ├── query_expander.py          # Synonym expansion
│   │   └── sapbert_expander.py        # Semantic expansion
│   │
│   ├── search/
│   │   ├── orchestrator.py            # Main search coordinator
│   │   ├── ranker.py                  # BM25 relevance scoring
│   │   └── semantic_ranker.py         # Vector similarity
│   │
│   ├── geo/
│   │   ├── client.py                  # NCBI GEO API client
│   │   ├── query_builder.py           # Entrez query builder
│   │   └── models.py                  # GEO data models
│   │
│   ├── publications/
│   │   ├── pubmed_client.py           # PubMed API client
│   │   └── openalex_client.py         # OpenAlex API client
│   │
│   ├── citations/
│   │   ├── geo_citation_pipeline.py   # Citation discovery
│   │   └── discovery_client.py        # Multi-source citations
│   │
│   ├── fulltext/
│   │   ├── manager.py                 # Full-text orchestrator
│   │   ├── downloaders/
│   │   │   ├── pmc_downloader.py      # PMC XML/PDF download
│   │   │   └── unpaywall_downloader.py # Open access PDFs
│   │   ├── parsers/
│   │   │   ├── jats_parser.py         # PMC XML parsing
│   │   │   └── pdf_parser.py          # PDF parsing
│   │   └── cache_db.py                # SQLite cache
│   │
│   ├── ai/
│   │   ├── enrichment_agent.py        # AI analysis
│   │   └── gpt_client.py              # GPT-4 wrapper
│   │
│   └── infrastructure/
│       └── redis_client.py            # Redis caching
│
└── data/
    ├── fulltext/parsed/               # Cached full-text content
    ├── pdfs/                          # Downloaded PDFs
    └── cache/                         # Vector embeddings
```

---

**Last Updated:** November 2, 2025  
**Version:** 1.0  
**Status:** Production-ready ✅
