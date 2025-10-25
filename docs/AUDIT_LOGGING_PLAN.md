# Audit Logging & Scraper Provenance Plan

## Problem Statement
When LLMs use Brave Search MCP and Playwright MCP directly, we need a complete audit trail of:
1. **All pages visited** - including intermediate navigation steps
2. **All sources found** - where actual residency/citizenship knowledge came from
3. **All artifacts collected** - HTML, PDFs, screenshots, etc.
4. **Complete reproducibility** - so another LLM or human can follow the exact path

## Challenge
With plain scripts, logging is automatic. With LLMs, we rely on the LLM to "remember" to use separate logging tools after each action.

---

## Two-Table Strategy

### Table 1: `sources` - Knowledge Sources
**Purpose**: Record sites where actual residency/citizenship knowledge or documents are sourced from.

**Schema**:
```sql
CREATE TABLE sources (
  id INTEGER PRIMARY KEY,
  url TEXT NOT NULL,
  title TEXT,
  source_type TEXT CHECK(source_type IN ('official', 'legal', 'professional', 'news', 'community')),
  language TEXT,
  credibility_rating INTEGER CHECK(credibility_rating BETWEEN 1 AND 5),
  date_accessed TEXT DEFAULT CURRENT_TIMESTAMP,
  notes TEXT,
  http_status INTEGER,
  mime_type TEXT,
  dedupe_hash TEXT UNIQUE  -- SHA256 of normalized URL
);

CREATE INDEX idx_sources_url ON sources(url);
CREATE INDEX idx_sources_type ON sources(source_type);
CREATE INDEX idx_sources_credibility ON sources(credibility_rating);
```

**Usage**: Used by LLMs to record *final* sources that contain actual knowledge.

---

### Table 2: `scraper_audit_trail` - Complete Journey
**Purpose**: Record EVERY page visited, including intermediate navigation, for full reproducibility.

**Schema**:
```sql
CREATE TABLE scraper_audit_trail (
  id INTEGER PRIMARY KEY,
  job_run_id INTEGER REFERENCES job_run(id),
  tool_call_id INTEGER,

  -- What happened
  action_type TEXT CHECK(action_type IN ('search', 'fetch', 'navigate', 'click', 'extract', 'screenshot')),
  tool_name TEXT,  -- 'brave_search', 'playwright_navigate', 'fetch_url', etc.

  -- Target
  url TEXT,
  search_query TEXT,

  -- Result
  http_status INTEGER,
  mime_type TEXT,
  page_title TEXT,

  -- Timing
  started_at TEXT DEFAULT CURRENT_TIMESTAMP,
  finished_at TEXT,
  duration_ms INTEGER,

  -- Result classification
  is_source BOOLEAN DEFAULT 0,  -- 1 if this became a "source" (inserted into sources table)
  source_id INTEGER REFERENCES sources(id),  -- link to sources table if is_source=1

  -- Evidence
  artifact_path TEXT,  -- path to saved HTML/PDF/screenshot
  artifact_type TEXT,  -- 'html', 'pdf', 'screenshot', 'json'
  artifact_size_bytes INTEGER,
  artifact_sha256 TEXT,

  -- Context
  parent_trail_id INTEGER REFERENCES scraper_audit_trail(id),  -- previous step in chain
  session_id TEXT,  -- group related scraping actions
  llm_task_description TEXT,  -- what the LLM was trying to do

  -- Status
  status TEXT CHECK(status IN ('success', 'error', 'timeout', 'skipped')) DEFAULT 'success',
  error_message TEXT,

  -- Metadata
  user_agent TEXT,
  request_headers_json TEXT,
  response_headers_json TEXT,

  UNIQUE(tool_call_id, url, started_at)  -- prevent exact duplicates
);

CREATE INDEX idx_audit_session ON scraper_audit_trail(session_id);
CREATE INDEX idx_audit_job ON scraper_audit_trail(job_run_id);
CREATE INDEX idx_audit_source ON scraper_audit_trail(source_id);
CREATE INDEX idx_audit_parent ON scraper_audit_trail(parent_trail_id);
CREATE INDEX idx_audit_url ON scraper_audit_trail(url);
CREATE INDEX idx_audit_timestamp ON scraper_audit_trail(started_at);
```

---

### Table 3: `job_run` - Top-Level Tasks
**Purpose**: Group scraping sessions by user task/goal.

**Schema**:
```sql
CREATE TABLE job_run (
  id INTEGER PRIMARY KEY,
  started_at TEXT DEFAULT CURRENT_TIMESTAMP,
  finished_at TEXT,
  user_task TEXT,  -- natural language task description
  agent_session_id TEXT,
  country TEXT,
  pathway_type TEXT,
  status TEXT CHECK(status IN ('running', 'completed', 'failed', 'timeout')) DEFAULT 'running',
  total_pages_visited INTEGER DEFAULT 0,
  total_sources_found INTEGER DEFAULT 0,
  total_artifacts_saved INTEGER DEFAULT 0,
  error_count INTEGER DEFAULT 0
);

CREATE INDEX idx_job_country ON job_run(country);
CREATE INDEX idx_job_status ON job_run(status);
```

---

### Table 4: `tool_call` - Individual LLM Tool Invocations
**Purpose**: Record every tool call made by the LLM.

**Schema**:
```sql
CREATE TABLE tool_call (
  id INTEGER PRIMARY KEY,
  job_run_id INTEGER REFERENCES job_run(id),
  tool_name TEXT,
  args_json TEXT,  -- JSON of arguments passed
  started_at TEXT DEFAULT CURRENT_TIMESTAMP,
  finished_at TEXT,
  status TEXT CHECK(status IN ('ok', 'error')) DEFAULT 'ok',
  error_msg TEXT,
  result_summary TEXT  -- brief summary of result
);

CREATE INDEX idx_tool_job ON tool_call(job_run_id);
CREATE INDEX idx_tool_name ON tool_call(tool_name);
```

---

## CLI Tools for Audit Logging

### Phase 1: Manual Logging (Immediate Need)

#### `cli/audit_start_job.py`
Start a new job run and return job_run_id for subsequent logging.

**Usage**:
```bash
python cli/audit_start_job.py --task "Research Italy digital nomad visa" --country Italy --pathway digital_nomad
# Output: job_run_id: 42
```

---

#### `cli/audit_log_page.py`
Log a page visit to the audit trail.

**Usage**:
```bash
python cli/audit_log_page.py \
  --job-id 42 \
  --action fetch \
  --tool brave_web_search \
  --url "https://vistoperitalia.esteri.it/home/en" \
  --status 200 \
  --title "Italy Visa Information" \
  --artifact-path "data/raw/italy_visa_info.html" \
  --artifact-type html \
  --session-id "italy-dn-research-001"
```

**Options**:
- `--is-source`: Mark this as a knowledge source (also inserts into sources table)
- `--parent-id`: Link to previous trail entry (for navigation chains)
- `--search-query`: If this was a search action

---

#### `cli/audit_mark_source.py`
Mark an audit trail entry as a knowledge source and insert into sources table.

**Usage**:
```bash
python cli/audit_mark_source.py \
  --trail-id 123 \
  --source-type official \
  --credibility 5 \
  --notes "Official Italy immigration ministry site"
```

**Effect**:
- Creates entry in `sources` table
- Updates `scraper_audit_trail.is_source = 1`
- Links via `source_id`

---

#### `cli/audit_log_tool_call.py`
Log an LLM tool call.

**Usage**:
```bash
python cli/audit_log_tool_call.py \
  --job-id 42 \
  --tool brave_web_search \
  --args '{"query": "Italy digital nomad visa 2025", "count": 10}' \
  --status ok \
  --result-summary "Found 10 results, 3 official sources"
```

---

#### `cli/audit_finish_job.py`
Mark a job run as complete and compute statistics.

**Usage**:
```bash
python cli/audit_finish_job.py --job-id 42 --status completed
```

**Effect**:
- Sets `finished_at`
- Computes totals (pages visited, sources found, artifacts)
- Updates status

---

#### `cli/audit_query.py`
Query the audit trail.

**Usage**:
```bash
# Show all pages visited for a job
python cli/audit_query.py job 42

# Show navigation chain for a specific page
python cli/audit_query.py chain --trail-id 123

# Show all sources found for a country
python cli/audit_query.py sources --country Italy

# Export full audit trail for a job
python cli/audit_query.py export --job-id 42 --format json --output italy_audit.json
```

---

#### `cli/audit_replay.py`
Generate a reproducible script from audit trail.

**Usage**:
```bash
python cli/audit_replay.py --job-id 42 --output replay_italy_dn_research.sh
```

**Output**: Bash script that reproduces the exact scraping journey:
```bash
#!/bin/bash
# Job 42: Research Italy digital nomad visa
# Started: 2025-10-25 10:00:00

# Step 1: Search
brave_search "Italy digital nomad visa 2025"

# Step 2: Visit official site
curl -o italy_visa.html "https://vistoperitalia.esteri.it/home/en"

# Step 3: Navigate to requirements page
playwright navigate "https://vistoperitalia.esteri.it/requirements"

# ... etc
```

---

### Phase 2: Automatic Logging via MCP Wrapper (Future)

#### Option A: Fork Brave/Playwright MCP Servers
Fork the existing MCP servers and add logging middleware to automatically log every call.

**Advantages**:
- Automatic logging, no LLM cooperation needed
- Complete coverage, no omissions
- Full control over logging logic

**Disadvantages**:
- Need to maintain forks
- Updates to upstream servers require merging

**Priority**: BACKLOG (see below)

---

#### Option B: Build Proxy MCP Server
Build a proxy MCP server that wraps Brave and Playwright MCPs and adds logging.

**Architecture**:
```
Claude Code <-> Proxy MCP Server <-> Brave MCP
                      |               <-> Playwright MCP
                      |
                      v
                  SQLite Database
```

**Advantages**:
- No forking needed
- Can wrap any MCP server
- Clean separation of concerns

**Disadvantages**:
- Additional complexity
- Potential latency

**Priority**: BACKLOG

---

#### Option C: Strict LLM Instructions + Manual Tools
Use strict system prompts that require LLMs to log after EVERY web action.

**Prompt Template**:
```
CRITICAL: After EVERY web search, fetch, or navigation, you MUST:
1. Log the page to audit trail using `cli/audit_log_page.py`
2. If the page contains useful knowledge, mark it as a source using `cli/audit_mark_source.py`
3. Save any artifacts (HTML, PDF) to data/raw/ with unique names
4. Update the job run statistics

Failure to log will result in incomplete audit trail and irreproducible research.
```

**Advantages**:
- Can implement immediately
- No additional infrastructure
- Works with existing MCPs

**Disadvantages**:
- Relies on LLM compliance
- Risk of omissions if LLM "forgets"

**Priority**: IMMEDIATE (Phase 1)

---

## Implementation Priorities

### Phase 1: Manual Logging (This Week)
**Goal**: LLMs can log their actions, we verify completeness manually.

**Tasks**:
1. [ ] Add `job_run`, `tool_call`, `scraper_audit_trail` tables to schema
2. [ ] Build `cli/audit_start_job.py`
3. [ ] Build `cli/audit_log_page.py`
4. [ ] Build `cli/audit_mark_source.py`
5. [ ] Build `cli/audit_finish_job.py`
6. [ ] Build `cli/audit_query.py`
7. [ ] Create strict LLM prompt template for audit logging
8. [ ] Test with Italy research pilot

---

### Phase 2: Validation & Replay (Week 2)
**Goal**: Verify audit trails are complete and reproducible.

**Tasks**:
1. [ ] Build `cli/audit_replay.py` to generate replay scripts
2. [ ] Build `cli/audit_validate.py` to check for gaps
3. [ ] Create audit trail visualization tool
4. [ ] Test reproducibility by replaying job runs

---

### Phase 3: Semi-Automatic Logging (Week 3-4)
**Goal**: Reduce LLM burden with helper scripts.

**Tasks**:
1. [ ] Build wrapper scripts around common workflows
2. [ ] Create logging decorators for Python scrapers
3. [ ] Build session management helpers

---

### Phase 4: Automatic Logging via MCP Wrapper (BACKLOG)
**Goal**: Zero-effort logging via infrastructure.

**Tasks**:
1. [ ] Research MCP proxy architecture
2. [ ] Build prototype proxy MCP server
3. [ ] Add logging middleware to proxy
4. [ ] Test with Brave and Playwright MCPs
5. [ ] Deploy and configure Claude Code to use proxy
6. [ ] Migrate from manual logging to automatic

**Priority**: LOW - Deprioritized per user request

---

## Relationship Between Tables

```
job_run (1) ──── (many) tool_call
   │
   └── (many) scraper_audit_trail
                 │
                 ├── (0..1) sources (if is_source=1)
                 └── (0..1) parent trail entry (for navigation chains)
```

**Example Flow**:
1. LLM starts job: "Research Italy digital nomad visa" → `job_run` id=42
2. LLM searches Brave: "Italy digital nomad visa 2025" → `tool_call` id=100, `scraper_audit_trail` id=200
3. LLM finds 10 results, visits 3 official sites:
   - Visit 1: `scraper_audit_trail` id=201, parent=200
   - Visit 2: `scraper_audit_trail` id=202, parent=200
   - Visit 3: `scraper_audit_trail` id=203, parent=200
4. LLM marks Visit 1 as source: `sources` id=50, `scraper_audit_trail.is_source=1`, `source_id=50`
5. LLM clicks link on Visit 1 to requirements page: `scraper_audit_trail` id=204, parent=201
6. LLM finishes job: Updates `job_run` with totals

---

## Benefits

### Reproducibility
```bash
# Generate replay script
python cli/audit_replay.py --job-id 42 --output replay.sh

# Another LLM or human can re-run exact same steps
bash replay.sh
```

### Provenance
"Where did this Italy digital nomad income requirement come from?"
```bash
python cli/audit_query.py chain --trail-id 201
# Shows: Search → Google result → Official site → Requirements page → Specific section
```

### Quality Assurance
```bash
# Check if all pages were saved as artifacts
python cli/audit_validate.py --job-id 42

# Output:
# ✓ All 15 pages have artifacts
# ✗ Warning: 2 pages missing credibility ratings
```

### Statistics
```bash
python cli/audit_query.py stats

# Output:
# Total jobs: 15
# Total pages visited: 432
# Total sources found: 89
# Average sources per job: 5.9
# Most visited domain: vistoperitalia.esteri.it (23 visits)
```

---

## LLM Agent Workflow with Audit Logging

**Before starting research**:
```bash
job_id=$(python cli/audit_start_job.py --task "Research Italy DN visa" --country Italy)
echo "Job ID: $job_id"
```

**After each web action**:
```bash
# Search with Brave
brave_search "Italy digital nomad visa"

# Log it
python cli/audit_log_page.py \
  --job-id $job_id \
  --action search \
  --tool brave_web_search \
  --search-query "Italy digital nomad visa" \
  --session-id italy-dn-001

# Visit result
playwright navigate "https://example.com"

# Log it
python cli/audit_log_page.py \
  --job-id $job_id \
  --action navigate \
  --tool playwright_navigate \
  --url "https://example.com" \
  --artifact-path "data/raw/example_page.html" \
  --session-id italy-dn-001

# If this is a source
python cli/audit_mark_source.py \
  --trail-id <last_trail_id> \
  --source-type official \
  --credibility 5
```

**When finished**:
```bash
python cli/audit_finish_job.py --job-id $job_id --status completed
```

---

## Next Steps

1. **Review and approve** this audit logging plan
2. **Add tables** to database schema
3. **Build Phase 1 CLI tools** (manual logging)
4. **Create LLM prompt template** with strict logging requirements
5. **Test with pilot** (Italy digital nomad research)
6. **Iterate** based on findings
7. **Phase 4 (MCP wrapper)** → BACKLOG for future

---

**Last Updated**: 2025-10-25
**Status**: Proposed
**Priority Phase 1**: HIGH (immediate need)
**Priority Phase 4**: LOW (backlog, deprioritized)
