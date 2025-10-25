# CLI Tools Specification

## Overview
This document specifies all CLI tools that LLM agents will use to interact with the database and automate research tasks.

---

## Database Tools

### `scripts/db_init.py`
Initialize the database with the complete schema.

**Usage:**
```bash
python scripts/db_init.py [--db-path PATH] [--force]
```

**Options:**
- `--db-path`: Path to database file (default: `data/database/residency.db`)
- `--force`: Drop existing tables and recreate

**Output:**
- Creates all tables
- Inserts initial seed data (15 priority countries)
- Prints summary of created tables

---

### `scripts/db_migrate.py`
Manage database schema migrations.

**Usage:**
```bash
python scripts/db_migrate.py <command> [options]

Commands:
  create <name>           Create a new migration file
  up                      Run pending migrations
  down                    Rollback last migration
  status                  Show migration status
  history                 Show migration history
```

**Examples:**
```bash
# Create new migration
python scripts/db_migrate.py create add_pathway_status_column

# Run migrations
python scripts/db_migrate.py up

# Check status
python scripts/db_migrate.py status
```

---

### `cli/db_query.py`
Query database with LLM-friendly output.

**Usage:**
```bash
python cli/db_query.py <table> [--where CONDITION] [--format FORMAT] [--limit N]
```

**Options:**
- `table`: Table name to query
- `--where`: SQL WHERE condition (e.g., "country_id=1")
- `--format`: Output format (table, json, markdown, csv)
- `--limit`: Limit number of results

**Examples:**
```bash
# Get all countries
python cli/db_query.py countries --format table

# Get pathways for Italy
python cli/db_query.py residency_pathways --where "country_id=1" --format markdown

# Get recent sources
python cli/db_query.py sources --limit 10 --format json
```

---

### `cli/db_insert.py`
Insert records into database tables.

**Usage:**
```bash
python cli/db_insert.py <table> --data JSON_DATA
# OR
python cli/db_insert.py <table> --file JSON_FILE
```

**Examples:**
```bash
# Insert a source
python cli/db_insert.py sources --data '{"url": "https://...", "title": "...", "source_type": "official"}'

# Insert from file
python cli/db_insert.py residency_pathways --file italy_pathways.json
```

**Output:**
- Returns inserted record ID
- Prints confirmation

---

### `cli/db_update.py`
Update existing database records.

**Usage:**
```bash
python cli/db_update.py <table> <id> --set KEY=VALUE [--set KEY=VALUE ...]
```

**Examples:**
```bash
# Update pathway cost
python cli/db_update.py residency_pathways 5 --set cost_estimate=50000 --set last_updated="2025-10-25"

# Update source credibility
python cli/db_update.py sources 12 --set credibility_rating=5
```

---

## Research Status Tools

### `cli/country_status.py`
Show research status for a country.

**Usage:**
```bash
python cli/country_status.py <country_name> [--format FORMAT]
```

**Output:**
```
Country: Italy
EU Member: Yes
Schengen Member: Yes

Research Progress:
  Pathways Documented: 6/10 (60%)
  Sources Collected: 23
  Last Updated: 2025-10-20

Pathways:
  ✓ Digital Nomad Visa (complete)
  ✓ Innovative Startup Visa (complete)
  ✓ EU Blue Card (complete)
  ✓ Citizenship by Descent (complete)
  ○ Elective Residency Visa (incomplete)
  ○ Self-Employment Visa (not started)
  ...

Tasks:
  ✓ 12 completed
  → 3 in progress
  ○ 8 pending
```

---

### `cli/stats.py`
Show project statistics and coverage.

**Usage:**
```bash
python cli/stats.py [--detailed]
```

**Output:**
```
=== EU Residency Research Project Stats ===

Countries:
  Total: 15
  Completed: 4 (27%)
  In Progress: 3 (20%)
  Not Started: 8 (53%)

Pathways:
  Total Documented: 47
  Average per Country: 3.1

Sources:
  Total: 156
  Official Government: 89 (57%)
  Legal Sources: 23 (15%)
  Professional: 31 (20%)
  Community: 13 (8%)

Data Freshness:
  < 1 month old: 102 (65%)
  1-3 months old: 41 (26%)
  > 3 months old: 13 (8%) ⚠️

Scraping Jobs:
  Successful: 143
  Failed: 12
  Pending: 3
```

---

## Content Management Tools

### `cli/pathway_crud.py`
CRUD operations for residency pathways.

**Usage:**
```bash
python cli/pathway_crud.py <command> [options]

Commands:
  create        Create new pathway
  read          Read pathway details
  update        Update pathway
  delete        Delete pathway
  list          List all pathways
```

**Examples:**
```bash
# Create pathway
python cli/pathway_crud.py create --country Italy --type "digital_nomad" --name "Digital Nomad Visa" --interactive

# Read pathway
python cli/pathway_crud.py read 5 --format markdown

# List pathways for country
python cli/pathway_crud.py list --country Italy
```

---

### `cli/source_manager.py`
Manage sources and their credibility.

**Usage:**
```bash
python cli/source_manager.py <command> [options]

Commands:
  add           Add new source
  verify        Verify source is still accessible
  rate          Update credibility rating
  list          List sources
  check-dead    Check for dead links
```

**Examples:**
```bash
# Add source
python cli/source_manager.py add --url "https://..." --type official --rating 5

# Verify source
python cli/source_manager.py verify 23

# Check all sources for dead links
python cli/source_manager.py check-dead
```

---

## Scraping Tools

### `cli/scrape_url.py`
Scrape single URL and store in database.

**Usage:**
```bash
python cli/scrape_url.py <url> [--type TYPE] [--country COUNTRY] [--save-raw]
```

**Options:**
- `--type`: Content type (government_site, legal_doc, forum, news)
- `--country`: Associated country
- `--save-raw`: Save raw HTML to data/raw/

**Output:**
- Scrapes URL
- Extracts structured content
- Stores in database
- Saves raw HTML if requested
- Returns scraping job ID

---

### `cli/scrape_batch.py`
Batch scrape from URL list.

**Usage:**
```bash
python cli/scrape_batch.py --file urls.txt [--delay SECONDS] [--parallel N]
```

**Options:**
- `--file`: Text file with URLs (one per line)
- `--delay`: Delay between requests (default: 2 seconds)
- `--parallel`: Number of parallel scrapers (default: 1)

**Output:**
- Progress bar
- Summary of successful/failed scrapes
- Log of errors

---

### `cli/content_extractor.py`
Extract structured data from HTML/PDF.

**Usage:**
```bash
python cli/content_extractor.py <file_path> --type TYPE [--output JSON_FILE]
```

**Types:**
- `visa_requirements`: Extract visa requirement details
- `financial_table`: Extract financial requirements
- `legal_text`: Extract and parse legal text
- `application_process`: Extract application steps

**Examples:**
```bash
# Extract requirements from HTML
python cli/content_extractor.py data/raw/italy_startup.html --type visa_requirements

# Extract financial table from PDF
python cli/content_extractor.py data/raw/denmark_fees.pdf --type financial_table --output denmark_fees.json
```

---

### `cli/change_detector.py`
Detect changes in previously scraped content.

**Usage:**
```bash
python cli/change_detector.py <url> [--threshold PERCENT]
```

**Options:**
- `--threshold`: Minimum change percentage to report (default: 5%)

**Output:**
- Compares current content with last scraped version
- Reports percentage changed
- Highlights changed sections
- Updates database with change log

---

## Logging Tools

### `cli/log_append.py`
Append to process log.

**Usage:**
```bash
python cli/log_append.py <category> <message>

Categories:
  decision       Major decisions made
  blocker        Blockers encountered
  solution       Solutions to problems
  error          Scraping/parsing errors
  discovery      New findings
```

**Examples:**
```bash
# Log a decision
python cli/log_append.py decision "Using Playwright for JavaScript-heavy sites"

# Log a blocker
python cli/log_append.py blocker "Italy government site returns 403 with requests library"

# Log a solution
python cli/log_append.py solution "Used Playwright with browser automation to bypass 403"
```

**Output:**
- Appends timestamped entry to `docs/logs/process_log.md`
- Includes timestamp, category, and message

---

### `cli/domain_log.py`
Add domain knowledge entries.

**Usage:**
```bash
python cli/domain_log.py <category> <title> <content>

Categories:
  term           Legal/visa terminology
  policy         Policy change
  requirement    Specific requirement discovered
  threshold      Financial/time threshold
  restriction    Restriction or limitation
```

**Examples:**
```bash
# Log a term
python cli/domain_log.py term "Jure Sanguinis" "Latin term meaning 'right of blood'. Italian citizenship by descent."

# Log a policy change
python cli/domain_log.py policy "Tajani Decree" "May 2025: Italy restricts jure sanguinis to parent/grandparent only"
```

**Output:**
- Appends to `docs/logs/domain_knowledge.md`
- Organized by category
- Includes timestamp and links

---

### `cli/country_task.py`
Manage country-specific tasks.

**Usage:**
```bash
python cli/country_task.py <country> <command> [options]

Commands:
  add           Add new task
  complete      Mark task as complete
  list          List all tasks
  status        Show task status
```

**Examples:**
```bash
# Add task
python cli/country_task.py Italy add "Research elective residency visa requirements"

# Complete task
python cli/country_task.py Italy complete 5 --evidence "docs/countries/italy/elective_residency.md"

# List tasks
python cli/country_task.py Italy list
```

**Output:**
- Updates `docs/countries/{country}/tasks.md`
- Links completed tasks to evidence

---

## Export Tools

### `cli/export.py`
Export data to various formats.

**Usage:**
```bash
python cli/export.py <command> [options]

Commands:
  country       Export country data
  pathway       Export pathway data
  comparison    Export comparison table
  all           Export everything
```

**Examples:**
```bash
# Export Italy data to markdown
python cli/export.py country Italy --format markdown --output docs/countries/italy/summary.md

# Export comparison table
python cli/export.py comparison --countries Italy,Spain,Portugal --format csv --output comparison.csv

# Export all data
python cli/export.py all --format json --output data/export/full_export.json
```

---

## Validation Tools

### `cli/validate_sources.py`
Check if sources are still accessible.

**Usage:**
```bash
python cli/validate_sources.py [--country COUNTRY] [--fix-redirects]
```

**Options:**
- `--country`: Validate only sources for specific country
- `--fix-redirects`: Update URLs that redirect

**Output:**
- Checks all source URLs
- Reports dead links
- Reports redirects
- Updates database with status

---

### `cli/validate_data.py`
Validate data completeness and consistency.

**Usage:**
```bash
python cli/validate_data.py [--table TABLE] [--fix]
```

**Options:**
- `--table`: Validate specific table
- `--fix`: Attempt to fix validation errors

**Output:**
- Missing required fields
- Invalid foreign keys
- Inconsistent data
- Duplicate records
- Outdated information

---

## Utility Tools

### `cli/backup.py`
Backup database and important files.

**Usage:**
```bash
python cli/backup.py [--destination PATH]
```

**Output:**
- Creates timestamped backup
- Compresses database and docs
- Stores in backups/ directory

---

### `cli/search.py`
Search across all documentation and database.

**Usage:**
```bash
python cli/search.py <query> [--type TYPE]
```

**Types:**
- `all`: Search everything (default)
- `pathways`: Search only pathways
- `sources`: Search only sources
- `docs`: Search only markdown docs

---

## Tool Development Priority

### Phase 1 (Immediate)
1. `scripts/db_init.py` - CRITICAL
2. `cli/db_query.py` - CRITICAL
3. `cli/db_insert.py` - CRITICAL
4. `cli/log_append.py` - HIGH
5. `cli/domain_log.py` - HIGH

### Phase 2 (Week 1)
1. `cli/country_status.py` - HIGH
2. `cli/pathway_crud.py` - HIGH
3. `cli/scrape_url.py` - HIGH
4. `cli/content_extractor.py` - MEDIUM
5. `scripts/db_migrate.py` - MEDIUM

### Phase 3 (Week 2)
1. `cli/stats.py` - MEDIUM
2. `cli/source_manager.py` - MEDIUM
3. `cli/export.py` - MEDIUM
4. `cli/validate_sources.py` - LOW
5. `cli/scrape_batch.py` - LOW

### Phase 4 (Future)
1. `cli/change_detector.py`
2. `cli/validate_data.py`
3. `cli/backup.py`
4. `cli/search.py`

---

**Last Updated**: 2025-10-25
