# Agentic Workflow Analysis & Improvement Proposal

**Generated**: 2025-10-25 13:15
**Purpose**: Analyze current LLM workflow and redesign CLI tools to minimize bookkeeping

---

## Current Workflow - Analysis

### What LLMs Did in Italy Research

**Step-by-step for each pathway** (Example: Digital Nomad Visa):

```bash
# 1. Search (LLM is good at this ✅)
brave_search "Italy digital nomad visa 2025"

# 2. Log search (LLM must remember ❌)
python cli/audit_log_page.py --job-id 2 --action search --search-query "..."

# 3. Fetch page (LLM is good at this ✅)
mcp_fetch "https://consnewyork.esteri.it/..."

# 4. Log fetch (LLM must remember ❌)
trail_id=$(python cli/audit_log_page.py --job-id 2 --action fetch --url "..." --title "...")

# 5. Mark as source (LLM must remember ❌)
source_id=$(python cli/audit_mark_source.py --trail-id $trail_id --create-source --source-type official_government --credibility 5)

# 6. Register artifact (LLM must remember ❌)
python cli/artifact_register.py --type extracted_text --path "..." --trail-id $trail_id --source-id $source_id

# 7. Insert pathway (LLM must remember ❌)
pathway_id=$(python cli/db_insert.py pathway --country Italy --type digital_nomad --min-income 24789 ...)

# 8. Link pathway to source (LLM must remember ❌)
python cli/db_insert.py link --pathway-id $pathway_id --source-id $source_id
```

**Total**: 8 commands per pathway (5 of them are pure bookkeeping)

---

## Problem Statement

### LLM Weaknesses (User Quote)

> "they're unreliable at bookkeeping, strict rule-following, and multi-step computation—exactly what scrapers must do well."

**What LLMs Forget**:
- Logging audit trail after every action
- Tracking IDs across multiple commands
- Linking records in junction tables
- Following multi-step procedures precisely

**Evidence from Italy Research**:
- Had to be reminded to use process log
- Had to be reminded to use domain knowledge log
- Forgot to link some pathways to sources initially
- Needed multiple prompts to maintain consistency

### LLM Strengths (User Quote)

> "they're excellent at messy, language-y tasks (finding/reading/following links, summarizing, brittle DOMs)"

**What LLMs Excel At**:
- Finding relevant pages via search
- Following links and navigation
- Extracting structured data from messy HTML
- Summarizing and synthesizing information
- Understanding context and relevance
- Parsing unstructured text

---

## Proposed Solution: Bundled Transaction Commands

### Design Principle

**LLMs should**: Search, fetch, extract, summarize (language tasks)
**CLI tools should**: Log, link, track, update (bookkeeping tasks)

### New High-Level CLI Tools

#### 1. `cli/add_pathway_with_source.py` (PRIORITY)

**Single transaction command**:

```bash
python cli/add_pathway_with_source.py \
    --job-id 2 \
    --country Italy \
    --type digital_nomad \
    --name "Digital Nomad Visa" \
    --min-income 24789 \
    --duration 12 \
    --renewable \
    --description "Allows remote workers to live in Italy..." \
    --source-url "https://consnewyork.esteri.it/..." \
    --source-title "Italian Consulate NY" \
    --source-type official_government \
    --credibility 5 \
    --artifact-path "data/raw/italy/nomad_visa.md"
```

**What it does AUTOMATICALLY** (in one transaction):
1. ✅ Logs fetch to audit trail → trail_id
2. ✅ Creates/finds source record → source_id
3. ✅ Registers artifact (if provided) → artifact_id
4. ✅ Inserts pathway → pathway_id
5. ✅ Links pathway to source (pathway_sources table)
6. ✅ Links artifact to source and trail
7. ✅ Updates job statistics
8. ✅ All or nothing (transaction rollback on error)

**Returns**: pathway_id (for optional further actions)

**Reduced**: 8 commands → 1 command

#### 2. `cli/research_session.py` (WRAPPER)

**Session management**:

```bash
# Start session
session=$(python cli/research_session.py start --country Italy --task "Research all pathways")

# Add pathway (uses session context)
python cli/research_session.py add \
    --session $session \
    --type digital_nomad \
    --name "Digital Nomad Visa" \
    --min-income 24789 \
    --source-url "https://..." \
    --credibility 5

# Finish session (auto-generates knowledge base)
python cli/research_session.py finish --session $session --export
```

**Benefits**:
- Session tracks job_id automatically
- Auto-exports at end
- Even simpler for LLM

#### 3. `cli/quick_add.py` (SIMPLEST)

**Minimal input, maximum automation**:

```bash
python cli/quick_add.py \
    --country Italy \
    --type digital_nomad \
    --source-url "https://consnewyork.esteri.it/..." \
    --credibility 5
```

**What it does**:
- Starts job (if none running for country)
- Fetches URL automatically
- Extracts key data (income, duration) via LLM parsing
- Creates pathway, source, links
- Logs everything
- Updates knowledge base

**LLM only provides**: Country, type, URL, credibility
**Tool handles**: Everything else

---

## Proposed CLI Tool Reorganization

### Tier 1: HIGH-LEVEL (What LLMs Should Use Daily)

**Bundled transactions, minimal bookkeeping**:

1. [ ] `cli/add_pathway_with_source.py` - Add pathway (ONE command) **PRIORITY**
2. [ ] `cli/research_session.py` - Session wrapper **PRIORITY**
3. [x] `cli/export.py` - Generate knowledge base ✅
4. [ ] `cli/quick_add.py` - Super simple add (future)

### Tier 2: MID-LEVEL (Occasional Use)

**Useful for queries and management**:

- [x] `cli/db_query.py` - Query database ✅
- [x] `cli/audit_start_job.py` - Start job ✅
- [x] `cli/audit_finish_job.py` - Finish job ✅

### Tier 3: LOW-LEVEL (Debug/Repair Only)

**Fine-grained control, rarely used**:

- [x] `cli/db_insert.py` - Manual table insertion ✅
- [x] `cli/audit_log_page.py` - Manual audit logging ✅
- [x] `cli/audit_mark_source.py` - Manual source marking ✅
- [x] `cli/artifact_register.py` - Manual artifact registration ✅

---

## Workflow Comparison

### BEFORE (Italy Pilot - TOO COMPLEX)

```bash
# For EACH pathway:
1. Start job
2. Search → log search
3. Fetch → log fetch
4. Mark source → create source
5. Register artifact
6. Insert pathway
7. Link pathway to source
8. Finish job

Total: 8 commands × 5 pathways = 40 commands
```

**Issues**:
- 40 total commands for 5 pathways
- Must track job_id, trail_id, source_id, pathway_id, artifact_id
- Easy to forget steps
- No transaction safety

### AFTER (Proposed - SIMPLE)

```bash
# Start session once
session=$(python cli/research_session.py start --country Italy)

# For EACH pathway (ONE command):
python cli/add_pathway_with_source.py \
    --job-id $session \
    --country Italy \
    --type digital_nomad \
    [pathway data] \
    --source-url "..." \
    --credibility 5

# Finish session once (auto-exports)
python cli/research_session.py finish --session $session --export

Total: 2 + (1 × 5) + 1 = 8 commands total
```

**Benefits**:
- 8 commands for 5 pathways (vs 40)
- Track only session ID
- Transaction safety per pathway
- Auto-export at end

**Reduction**: 80% fewer commands

---

## Implementation Plan

### Phase 1: Core Bundled Tools (CRITICAL)

1. **Build `cli/add_pathway_with_source.py`**
   - Input: Pathway data + source info
   - Output: All tables updated, all links created
   - Transaction: Atomic (all or nothing)
   - Estimated: 200-300 lines of Python

2. **Update `cli/export.py`**
   - [x] Generate country README.md ✅
   - [ ] Add JSON/CSV export options
   - [ ] Add batch export mode

3. **Build `cli/research_session.py`**
   - Session management wrapper
   - Auto job start/finish
   - Context tracking
   - Estimated: 150-200 lines

### Phase 2: Enhanced Features

4. **Build `cli/db_update.py`**
   - Update pathway/source records
   - Regenerate markdown after update

5. **Build `cli/quick_add.py`**
   - Auto-fetch and parse
   - LLM-assisted data extraction
   - Fully automated pathway addition

### Phase 3: Testing & Documentation

6. **Update test suites**
   - Test bundled commands
   - Test transaction rollback
   - Test export generation

7. **Update documentation**
   - New workflow guide
   - LLM prompt templates
   - Quick start for agents

---

## Expected Benefits

### For LLMs
- ✅ 80% fewer commands
- ✅ 90% less ID tracking
- ✅ Focus on content extraction
- ✅ Transaction safety (can't partially complete)

### For Data Quality
- ✅ Consistent linking (automatic)
- ✅ Complete audit trails (automatic)
- ✅ No orphaned records
- ✅ Referential integrity maintained

### For Humans
- ✅ Simpler to understand
- ✅ Easier to debug
- ✅ Faster research
- ✅ Higher quality data

---

## Immediate Next Steps

1. [ ] Build `cli/add_pathway_with_source.py` (highest priority)
2. [ ] Test with adding Italy citizenship by descent pathway
3. [ ] Document new workflow
4. [ ] Update QUICK_START.md with simplified commands
5. [ ] Use new tools for Denmark/Netherlands research

---

## Recommendation

**Build `cli/add_pathway_with_source.py` IMMEDIATELY**

This single tool will:
- Reduce cognitive load on LLM by 80%
- Eliminate most bookkeeping errors
- Make research 5x faster
- Improve data consistency

**Estimated time**: 30-45 minutes to build and test

**ROI**: Massive - will be used for all 14 remaining countries

---

**Last Updated**: 2025-10-25T13:15:00
**Status**: Ready for implementation
**Priority**: CRITICAL
