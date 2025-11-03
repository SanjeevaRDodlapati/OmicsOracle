# OmicsOracle Cache Performance Issues - Diagnosis & Fixes

**Date:** November 2, 2025  
**Issue:** Slow repeated searches and paper downloads despite caching implementation

---

## 🔍 **Diagnosis Summary**

### ✅ **What's Working:**
1. **Redis server** - Running properly (5.64 MB used, 1685 keys)
2. **GEO metadata cache** - 962 datasets cached with 30-day TTL
3. **PDF filesystem cache** - 48 PDFs downloaded (101.8 MB)

### ❌ **Critical Problems Found:**

| Component | Status | Impact |
|-----------|--------|--------|
| **Search result cache** | 🔴 BROKEN | Only 2 queries cached (should be hundreds) |
| **Parsed content cache** | 🔴 EMPTY | 0 files in `data/fulltext/parsed/` |
| **AI analysis cache** | 🔴 BROKEN | SQLite database not being used |
| **Publication cache** | 🔴 EMPTY | 0 keys in Redis |

---

## 🐛 **Root Causes**

### **Problem 1: Search Results Not Being Cached**

**Location:** `omics_oracle_v2/lib/search_engines/geo/client.py:424`

**Current behavior:**
```python
# Cache results in Redis
if self.settings.use_cache:
    await self.redis_cache.set_search_result(
        query=query,
        search_type="geo",
        result=result,
        max_results=max_results,
    )
```

**Issue:** `result` is a `SearchResult` object, but Redis cache expects a dict!

**Evidence:**
```bash
$ redis-cli --scan --pattern "omics_search:search:*"
# Only 2 results:
omics_search:search:geo:7e77e73de469099e8695b0dead7d3a54
omics_search:search:auto:991fa9931d62c72d87d768eb3d47fa9a
```

**Fix:**
```python
# Cache results in Redis (convert to dict first!)
if self.settings.use_cache:
    await self.redis_cache.set_search_result(
        query=query,
        search_type="geo",
        result=result.dict(),  # ← ADD .dict() or .model_dump()
        max_results=max_results,
    )
```

---

### **Problem 2: Parsed Content Not Being Saved**

**Location:** `omics_oracle_v2/lib/pipelines/url_collection/manager.py:1075`

**Current behavior:**
```python
# STEP 4: Cache the parsed content
await cache.save(
    publication_id=publication.id,
    content=parsed_content,
    source_type="pmc_xml" if result.source == "pmc" else "pdf",
    file_path=str(result.file_path) if result.file_path else None,
)
```

**Issue:** `cache.save()` might be failing silently due to:
1. Directory permissions
2. SQLite connection issues
3. Exception handling suppressing errors

**Evidence:**
```bash
$ ls -la data/fulltext/parsed/
# EMPTY - no .json files!
```

**Fix:** Add error logging and create directory:
```python
# Ensure directory exists
parsed_dir = Path("data/fulltext/parsed")
parsed_dir.mkdir(parents=True, exist_ok=True)

# STEP 4: Cache the parsed content with error handling
try:
    await cache.save(
        publication_id=publication.id,
        content=parsed_content,
        source_type="pmc_xml" if result.source == "pmc" else "pdf",
        file_path=str(result.file_path) if result.file_path else None,
    )
    logger.info(f"[OK] Cached parsed content: {publication.id}")
except Exception as e:
    logger.error(f"[ERROR] Failed to cache parsed content for {publication.id}: {e}")
    # Continue anyway - don't block the pipeline
```

---

### **Problem 3: AI Analysis Cache Not Being Used**

**Location:** `omics_oracle_v2/services/analysis_service.py:475`

**Current behavior:**
```python
cached_data = await parsed_cache.get(pmid)
if cached_data:
    content_data = cached_data.get("content", {})
    # ... use cached data
```

**Issue:** 
1. `parsed_cache` is not initialized properly (no SQLite DB)
2. No fallback if cache fails
3. Always re-analyzing papers even if already done

**Evidence:**
```bash
$ find data -name "*parsed*cache*.db"
# No database found!
```

**Fix:** Initialize cache properly:
```python
from omics_oracle_v2.cache.parsed_cache import get_parsed_cache

# Initialize with explicit DB path
cache_db = Path("data/cache/parsed_content_cache.db")
cache_db.parent.mkdir(parents=True, exist_ok=True)

parsed_cache = get_parsed_cache(db_path=cache_db)

# Check if initialized
if not parsed_cache:
    logger.warning("Parsed cache not available - AI analysis will be slower")
```

---

## 🔧 **Immediate Fixes**

### **Fix 1: Enable Search Result Caching**

**File:** `omics_oracle_v2/lib/search_engines/geo/client.py`

**Line 424-432:**
```python
# OLD (BROKEN):
await self.redis_cache.set_search_result(
    query=query,
    search_type="geo",
    result=result,  # ← Problem: Pydantic object, not dict!
    max_results=max_results,
)

# NEW (FIXED):
await self.redis_cache.set_search_result(
    query=query,
    search_type="geo",
    result=result.model_dump(),  # ← Convert to dict for JSON serialization
    max_results=max_results,
)
```

---

### **Fix 2: Create Parsed Content Cache Directory**

**File:** `omics_oracle_v2/lib/pipelines/url_collection/manager.py`

**Add at top of `parse_full_text()` function:**
```python
async def parse_full_text(self, publication):
    """Parse downloaded full-text with caching."""
    
    # CRITICAL FIX: Ensure cache directories exist
    from pathlib import Path
    
    parsed_dir = Path("data/fulltext/parsed")
    parsed_dir.mkdir(parents=True, exist_ok=True)
    
    cache_db_dir = Path("data/cache")
    cache_db_dir.mkdir(parents=True, exist_ok=True)
    
    # Rest of function...
```

---

### **Fix 3: Add Cache Hit/Miss Logging**

**File:** `omics_oracle_v2/cache/redis_cache.py`

**Line 215-220 (change from DEBUG to INFO):**
```python
# OLD:
logger.debug(f"Cache HIT for query: {query[:50]}")

# NEW:
logger.info(f"✓ Cache HIT for query: {query[:50]}")  # ← Change to INFO level
```

**Line 223:**
```python
# OLD:
logger.debug(f"Cache MISS for query: {query[:50]}")

# NEW:
logger.info(f"✗ Cache MISS for query: {query[:50]}")  # ← Change to INFO level
```

---

## 📊 **Expected Performance After Fixes**

| Operation | Before (Cold) | After (Cached) | Speedup |
|-----------|---------------|----------------|---------|
| **Search "diabetes"** | 3-5s | **0.1-0.3s** | **15-50x** |
| **Download 5 PDFs** | 30-60s | **0.5s** (filesystem) | **60-120x** |
| **AI analysis (5 papers)** | 25-40s | **1-2s** (cached summaries) | **15-40x** |
| **Total pipeline** | 60-105s | **2-5s** | **20-50x** |

---

## 🧪 **Testing the Fixes**

### **Test 1: Search Caching**
```python
from omics_oracle_v2.lib.search_engines.geo.client import GEOClient
import asyncio
import time

async def test_search_cache():
    client = GEOClient()
    query = "diabetes RNA-seq"
    
    # First search (cold)
    start = time.time()
    result1 = await client.search(query, max_results=20)
    time1 = time.time() - start
    print(f"Cold cache: {time1:.2f}s")
    
    # Second search (warm)
    start = time.time()
    result2 = await client.search(query, max_results=20)
    time2 = time.time() - start
    print(f"Warm cache: {time2:.2f}s")
    
    speedup = time1 / time2
    print(f"Speedup: {speedup:.1f}x")
    assert speedup > 10, "Cache not working!"

asyncio.run(test_search_cache())
```

**Expected output:**
```
Cold cache: 3.42s
✓ Cache HIT for query: diabetes RNA-seq
Warm cache: 0.12s
Speedup: 28.5x
```

---

### **Test 2: Check Parsed Content Cache**
```bash
# After running enrichment, check:
ls -lh data/fulltext/parsed/

# Should see .json files like:
# 38376465.json  (PMID)
# 39123456.json
```

---

### **Test 3: Redis Keys Count**
```bash
# Before fixes:
redis-cli --scan --pattern "omics_search:search:*" | wc -l
# Output: 2

# After fixes (after 10 searches):
redis-cli --scan --pattern "omics_search:search:*" | wc -l
# Output: 10+ (one per unique query)
```

---

## 🚀 **Deployment Steps**

1. **Stop the API server** (if running)
   ```bash
   pkill -f "uvicorn omics_oracle_v2.api.main"
   ```

2. **Create cache directories**
   ```bash
   mkdir -p data/fulltext/parsed
   mkdir -p data/cache
   chmod 755 data/fulltext/parsed
   chmod 755 data/cache
   ```

3. **Apply code fixes** (see Fix 1-3 above)

4. **Clear old broken cache** (optional)
   ```bash
   redis-cli FLUSHDB  # Removes all Redis keys
   ```

5. **Restart API server**
   ```bash
   ./start_omics_oracle.sh
   ```

6. **Test caching**
   - Search for "diabetes" twice
   - Check logs for "✓ Cache HIT"
   - Verify `data/fulltext/parsed/` has JSON files

---

## 📈 **Monitoring Cache Health**

### **Check Redis Stats:**
```bash
redis-cli INFO stats | grep hits
# keyspace_hits: Should increase with each cached request
# keyspace_misses: Should be low compared to hits

redis-cli INFO keyspace
# db0:keys=... Should grow as more queries are made
```

### **Check Filesystem Cache:**
```bash
# PDFs downloaded
du -sh data/pdfs/
# Should grow over time

# Parsed content
find data/fulltext/parsed -name "*.json" | wc -l
# Should increase as papers are analyzed
```

### **Check Application Logs:**
```bash
tail -f logs/omics_api.log | grep -i cache
# Should see:
# ✓ Cache HIT for query: diabetes
# [OK] Cached parsed content: 38376465
```

---

## 🎯 **Success Metrics**

After implementing fixes, you should see:

✅ **Search cache hit rate >70%** for repeated queries  
✅ **Parsed content cache >50 files** after enrichment runs  
✅ **Redis keys >100** (search + metadata)  
✅ **Second identical search <0.5s** (vs 3-5s first time)  
✅ **AI analysis uses cached summaries** (instant vs 5-8s per paper)

---

## 🔗 **Related Files**

- `omics_oracle_v2/lib/search_engines/geo/client.py` - GEO search with Redis cache
- `omics_oracle_v2/cache/redis_cache.py` - Redis caching implementation
- `omics_oracle_v2/cache/parsed_cache.py` - Parsed content SQLite cache
- `omics_oracle_v2/lib/pipelines/url_collection/manager.py` - Full-text download & parsing
- `omics_oracle_v2/services/analysis_service.py` - AI analysis service
- `test_cache_diagnostic.py` - Cache diagnostic tool (run this to verify fixes)

---

**Last Updated:** November 2, 2025  
**Status:** Issues identified, fixes documented, ready for implementation
