# Artifacts & Knowledge Management Strategy

## The Problem

We have different types of artifacts and knowledge:
1. **Binary artifacts**: PDFs, screenshots, HTML files
2. **Extracted text**: Scraped plain text from web pages
3. **Structured knowledge**: Organized markdown notes about pathways
4. **Database records**: Structured pathway data

**Question**: Where should each type live? SQLite database or filesystem (Obsidian vault)?

---

## The Solution: Hybrid Approach

### Best of Both Worlds
- **SQLite**: Metadata, relationships, queryability
- **Filesystem (Obsidian)**: Actual content, human-readable, version control friendly

### Principle
**"SQLite for metadata and pointers, filesystem for content"**

---

## Artifact Types & Storage

### Type 1: Raw Artifacts (Binary/Large Files)
**Examples**: PDF documents, HTML files, screenshots, ZIP files

**Storage**: Filesystem at `data/raw/`
**Database**: `artifacts` table with metadata

**Workflow**:
```bash
# Download PDF
curl -o data/raw/italy_visa_2025_01_15.pdf "https://..."

# Log to database
cli/artifact_register.py \
  --trail-id 123 \
  --type pdf \
  --path "data/raw/italy_visa_2025_01_15.pdf" \
  --title "Italy Digital Nomad Visa Requirements 2025" \
  --source-url "https://..."
```

**Path Convention**:
```
data/raw/{country}/{date}_{source}_{type}.{ext}

Examples:
data/raw/italy/2025-01-15_vistoperitalia_visa_requirements.pdf
data/raw/italy/2025-01-15_innovativestartup_application_form.pdf
data/raw/denmark/2025-01-20_nyidanmark_work_permit.html
```

---

### Type 2: Extracted Text/Content
**Examples**: Scraped text from web pages, extracted PDF text

**Storage**: Filesystem at `data/extracted/` as markdown
**Database**: `artifacts` table with metadata

**Workflow**:
```bash
# Scrape and extract
playwright navigate "https://..."
# Save raw HTML
# Extract text content

# Save as markdown
echo "# Italy Digital Nomad Visa\n\n[content]..." > data/extracted/italy/2025-01-15_digital_nomad_raw.md

# Log to database
cli/artifact_register.py \
  --trail-id 123 \
  --type extracted_text \
  --path "data/extracted/italy/2025-01-15_digital_nomad_raw.md" \
  --title "Italy DN Visa Raw Text" \
  --source-url "https://..."
```

**Path Convention**:
```
data/extracted/{country}/{date}_{topic}_raw.md
```

---

### Type 3: Structured Knowledge (Obsidian Vault)
**Examples**: Organized pathway guides, country summaries, comparison tables

**Storage**: Filesystem at `docs/vault/` (Obsidian vault)
**Database**: `knowledge_artifacts` table with metadata

**Structure**:
```
docs/vault/
├── Countries/
│   ├── Italy/
│   │   ├── Digital Nomad Visa.md
│   │   ├── Innovative Startup Visa.md
│   │   ├── Citizenship by Descent.md
│   │   └── _Country Summary.md
│   ├── Denmark/
│   └── ...
├── Pathways/
│   ├── Digital Nomad Visas.md (cross-country comparison)
│   ├── EU Blue Card.md
│   └── ...
├── Legal References/
│   ├── Italy Law 123-2025.md
│   └── ...
├── Sources/
│   ├── Official Websites.md
│   └── ...
└── Index.md (MOC - Map of Content)
```

**Workflow**:
```bash
# Create structured knowledge document
# (Compiled from extracted text + database + research)
cat > "docs/vault/Countries/Italy/Digital Nomad Visa.md" <<EOF
# Italy Digital Nomad Visa

## Overview
...

## Requirements
...

## Sources
- [[italy_visa_2025_01_15.pdf]]
- https://vistoperitalia.esteri.it/...

## Related Pathways
- [[Innovative Startup Visa]]
- [[EU Blue Card]]
EOF

# Register in database
cli/knowledge_register.py \
  --path "docs/vault/Countries/Italy/Digital Nomad Visa.md" \
  --country Italy \
  --pathway-type digital_nomad \
  --status complete
```

---

### Type 4: Structured Data
**Examples**: Pathway requirements (name, cost, duration), country metadata

**Storage**: SQLite `residency_pathways` table
**Also exported to**: `docs/vault/` as markdown for Obsidian

**Workflow**:
```bash
# Insert structured data
cli/pathway_crud.py create \
  --country Italy \
  --type digital_nomad \
  --name "Digital Nomad Visa" \
  --cost 50 \
  --duration 12 \
  --renewable true \
  --income-requirement 28000

# Export to Obsidian
cli/export.py pathway Italy digital_nomad \
  --format markdown \
  --output "docs/vault/Countries/Italy/Digital Nomad Visa.md" \
  --template obsidian
```

---

## Database Schema Updates

### Updated `artifacts` Table
```sql
CREATE TABLE artifacts (
  id INTEGER PRIMARY KEY,
  trail_id INTEGER REFERENCES scraper_audit_trail(id),
  source_id INTEGER REFERENCES sources(id),

  -- Classification
  artifact_type TEXT CHECK(artifact_type IN (
    'pdf', 'html', 'screenshot', 'zip',
    'extracted_text', 'extracted_table', 'extracted_list'
  )),

  -- File info
  file_path TEXT NOT NULL,  -- Relative to project root
  file_name TEXT,
  file_size_bytes INTEGER,
  mime_type TEXT,

  -- Content hash (for deduplication)
  sha256 TEXT UNIQUE,

  -- Metadata
  title TEXT,
  description TEXT,
  source_url TEXT,
  language TEXT DEFAULT 'en',

  -- Timestamps
  downloaded_at TEXT DEFAULT CURRENT_TIMESTAMP,

  -- Status
  extraction_status TEXT CHECK(extraction_status IN ('pending', 'extracted', 'failed', 'skipped')),
  extracted_to_path TEXT,  -- Path to extracted markdown file

  -- Context
  country TEXT,
  pathway_type TEXT,

  UNIQUE(file_path)
);

CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
CREATE INDEX idx_artifacts_country ON artifacts(country);
CREATE INDEX idx_artifacts_hash ON artifacts(sha256);
CREATE INDEX idx_artifacts_source ON artifacts(source_id);
```

---

### New `knowledge_artifacts` Table
```sql
CREATE TABLE knowledge_artifacts (
  id INTEGER PRIMARY KEY,

  -- File info
  file_path TEXT NOT NULL UNIQUE,  -- Relative path in vault
  file_type TEXT CHECK(file_type IN ('country_summary', 'pathway_guide', 'comparison', 'legal_reference', 'source_list')),

  -- Classification
  country TEXT,
  pathway_type TEXT,

  -- Metadata
  title TEXT NOT NULL,
  description TEXT,
  tags TEXT,  -- JSON array

  -- Relationships
  based_on_artifacts TEXT,  -- JSON array of artifact IDs used to create this
  linked_pathways TEXT,     -- JSON array of pathway IDs
  linked_sources TEXT,      -- JSON array of source IDs

  -- Status
  status TEXT CHECK(status IN ('draft', 'review', 'complete', 'outdated')) DEFAULT 'draft',
  completeness_score INTEGER CHECK(completeness_score BETWEEN 0 AND 100),

  -- Timestamps
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  reviewed_at TEXT,

  -- Obsidian metadata
  word_count INTEGER,
  internal_links_count INTEGER,
  external_links_count INTEGER
);

CREATE INDEX idx_knowledge_country ON knowledge_artifacts(country);
CREATE INDEX idx_knowledge_type ON knowledge_artifacts(file_type);
CREATE INDEX idx_knowledge_status ON knowledge_artifacts(status);
```

---

## CLI Tools for Artifacts

### `cli/artifact_register.py`
Register a downloaded artifact.

**Usage**:
```bash
cli/artifact_register.py \
  --trail-id 123 \
  --type pdf \
  --path "data/raw/italy/2025-01-15_visa_requirements.pdf" \
  --title "Italy Visa Requirements" \
  --source-url "https://..." \
  --country Italy \
  --pathway digital_nomad
```

---

### `cli/artifact_extract.py`
Extract text from artifact (PDF, HTML).

**Usage**:
```bash
cli/artifact_extract.py \
  --artifact-id 45 \
  --output "data/extracted/italy/2025-01-15_visa_requirements.md"
```

**Does**:
- Extracts text from PDF/HTML
- Saves as markdown
- Updates `artifacts.extraction_status = 'extracted'`
- Updates `artifacts.extracted_to_path`

---

### `cli/knowledge_register.py`
Register a structured knowledge document in Obsidian vault.

**Usage**:
```bash
cli/knowledge_register.py \
  --path "docs/vault/Countries/Italy/Digital Nomad Visa.md" \
  --type pathway_guide \
  --country Italy \
  --pathway digital_nomad \
  --based-on-artifacts 45,46,47 \
  --status complete
```

---

### `cli/knowledge_update.py`
Update knowledge artifact metadata after editing.

**Usage**:
```bash
cli/knowledge_update.py \
  --path "docs/vault/Countries/Italy/Digital Nomad Visa.md" \
  --status complete \
  --compute-metrics
```

**Does**:
- Updates `updated_at` timestamp
- Counts words, internal links, external links
- Updates completeness score

---

### `cli/artifact_list.py`
List artifacts with filters.

**Usage**:
```bash
# List all PDFs for Italy
cli/artifact_list.py --country Italy --type pdf

# List extracted text needing review
cli/artifact_list.py --extraction-status extracted

# List all artifacts for a specific trail
cli/artifact_list.py --trail-id 123
```

---

### `cli/knowledge_list.py`
List knowledge artifacts with filters.

**Usage**:
```bash
# List all pathway guides
cli/knowledge_list.py --type pathway_guide

# List drafts needing completion
cli/knowledge_list.py --status draft

# List Italy knowledge
cli/knowledge_list.py --country Italy
```

---

## Workflow Example: Italy Digital Nomad Research

### Step 1: Start Job
```bash
job_id=$(cli/audit_start_job.py --task "Research Italy Digital Nomad Visa" --country Italy)
echo $job_id
# Output: 42
```

### Step 2: Search and Navigate
```bash
# Search with Brave
brave_search "Italy digital nomad visa 2025"

# Log search
cli/audit_log_page.py --job-id 42 --action search --search-query "Italy digital nomad visa 2025"

# Navigate to official site
playwright navigate "https://vistoperitalia.esteri.it/..."

# Log navigation
trail_id=$(cli/audit_log_page.py \
  --job-id 42 \
  --action navigate \
  --url "https://vistoperitalia.esteri.it/..." \
  --title "Italy Visa Requirements" \
  --artifact-path "data/raw/italy/2025-01-15_vistoperitalia.html")
echo $trail_id
# Output: 201
```

### Step 3: Download and Register Artifacts
```bash
# Download PDF
curl -o data/raw/italy/2025-01-15_visa_requirements.pdf "https://.../requirements.pdf"

# Register artifact
artifact_id=$(cli/artifact_register.py \
  --trail-id 201 \
  --type pdf \
  --path "data/raw/italy/2025-01-15_visa_requirements.pdf" \
  --title "Italy Digital Nomad Visa Requirements PDF" \
  --source-url "https://.../requirements.pdf" \
  --country Italy \
  --pathway digital_nomad)
echo $artifact_id
# Output: 45
```

### Step 4: Extract Text
```bash
# Extract text from PDF
cli/artifact_extract.py \
  --artifact-id 45 \
  --output "data/extracted/italy/2025-01-15_visa_requirements.md"

# Now you have markdown with extracted text
```

### Step 5: Mark as Source
```bash
# Mark the trail entry as a knowledge source
cli/audit_mark_source.py \
  --trail-id 201 \
  --source-type official \
  --credibility 5 \
  --notes "Official Italy immigration ministry site"
```

### Step 6: Create Structured Knowledge
```bash
# Manually create or use LLM to create structured knowledge
# from extracted text + database + research

# File: docs/vault/Countries/Italy/Digital Nomad Visa.md
cat > "docs/vault/Countries/Italy/Digital Nomad Visa.md" <<'EOF'
# Italy Digital Nomad Visa

## Overview
Italy offers a digital nomad visa allowing remote workers to live in Italy for up to 12 months.

## Requirements
- Remote work for non-Italian company
- Minimum income: €28,000/year
- Health insurance
- Clean criminal record

## Application Process
1. Apply online at vistoperitalia.esteri.it
2. Submit documentation
3. Wait 30-60 days
4. Collect visa from embassy

## Costs
- Application fee: €50
- Health insurance: ~€500/year

## Sources
- [[italy_visa_2025_01_15_vistoperitalia.html|Official Italy Immigration Site]]
- [[italy_visa_2025_01_15_visa_requirements.pdf|Requirements PDF]]
- https://vistoperitalia.esteri.it/...

## Related Pathways
- [[Innovative Startup Visa]]
- [[Elective Residency Visa]]

---
Tags: #italy #digital-nomad #visa #remote-work
Created: 2025-01-15
Status: Complete
EOF

# Register knowledge artifact
cli/knowledge_register.py \
  --path "docs/vault/Countries/Italy/Digital Nomad Visa.md" \
  --type pathway_guide \
  --country Italy \
  --pathway digital_nomad \
  --based-on-artifacts 45,46,47 \
  --status complete
```

### Step 7: Store Structured Data
```bash
# Also store in database for queryability
cli/pathway_crud.py create \
  --country Italy \
  --type digital_nomad \
  --name "Digital Nomad Visa" \
  --cost 50 \
  --duration 12 \
  --renewable true \
  --income-requirement 28000 \
  --processing-time-days 45
```

### Step 8: Finish Job
```bash
cli/audit_finish_job.py --job-id 42 --status completed
```

---

## Benefits of This Approach

### For Humans
✅ Read knowledge in Obsidian (beautiful, linked, searchable)
✅ View artifacts directly in filesystem
✅ Git-friendly (text files, not binary database)
✅ Easy backups and version control

### For LLMs
✅ Query database for structured data (costs, durations, etc.)
✅ Find artifacts by country, type, date
✅ Trace knowledge back to original sources
✅ Validate completeness with metadata

### For Both
✅ Full audit trail from search → artifact → knowledge
✅ Deduplication (SHA256 hashes)
✅ Easy to refresh outdated info (dates tracked)
✅ Flexible (can mix SQLite queries with file reads)

---

## Summary

### What Goes Where?

| Content Type | Storage | Database Table | Purpose |
|--------------|---------|----------------|---------|
| PDFs, HTML, screenshots | `data/raw/` | `artifacts` | Archive original sources |
| Extracted text | `data/extracted/` | `artifacts` | Intermediate processing |
| Structured knowledge | `docs/vault/` | `knowledge_artifacts` | Human-readable, Obsidian |
| Structured data | N/A | `residency_pathways` | Queryable, comparable |
| Metadata for all | N/A | All tables | Relationships, provenance |

### The Rule
**"Content lives in files, metadata lives in SQLite"**

---

## Next Steps

1. Add `artifacts` and `knowledge_artifacts` tables to schema
2. Build artifact CLI tools
3. Build knowledge CLI tools
4. Test workflow with Italy research pilot
5. Refine based on actual usage

---

**Last Updated**: 2025-10-25
**Status**: Proposed Architecture
**Ready for Implementation**: Yes
