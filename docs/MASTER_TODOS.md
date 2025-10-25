# Master TODO List - EU Residency Research Project

## Legend
- [ ] Todo
- [x] Done
- [~] In Progress
- [!] Blocked

---

## Phase 1: Foundation & Tooling (Priority: CRITICAL)

### Database Infrastructure
- [ ] Design final database schema (review and refine from PROJECT_PLAN.md)
- [ ] Add audit logging tables to schema (`job_run`, `tool_call`, `scraper_audit_trail`)
- [ ] Create database initialization script (`scripts/db_init.py`)
- [ ] Create database migration CLI tool (`scripts/db_migrate.py`)
- [ ] Create database backup/restore utilities
- [ ] Add database version tracking table

### CLI Tools for LLM Interaction
- [ ] Create `cli/db_query.py` - Query database with natural language friendly output
- [ ] Create `cli/db_insert.py` - Insert records into database tables
- [ ] Create `cli/db_update.py` - Update existing records
- [ ] Create `cli/country_status.py` - Show research status for a country
- [ ] Create `cli/pathway_crud.py` - CRUD operations for residency pathways
- [ ] Create `cli/source_manager.py` - Manage sources and their credibility
- [ ] Create `cli/stats.py` - Show project statistics and coverage
- [ ] Create `cli/export.py` - Export data to various formats (JSON, CSV, Markdown)

### Scraping & Automation Tools
- [ ] Create `cli/scrape_url.py` - Scrape single URL and store in database
- [ ] Create `cli/scrape_batch.py` - Batch scrape from URL list
- [ ] Create `cli/scrape_scheduler.py` - Schedule periodic re-scraping
- [ ] Create `cli/content_extractor.py` - Extract structured data from HTML/PDF
- [ ] Create `cli/change_detector.py` - Detect changes in previously scraped content
- [ ] Create `cli/validate_sources.py` - Check if sources are still accessible

### Logging System
- [ ] Create append-only process log (`docs/logs/process_log.md`)
- [ ] Create domain knowledge log (`docs/logs/domain_knowledge.md`)
- [ ] Create per-country task logs (template: `docs/countries/{country}/tasks.md`)
- [ ] Create CLI tool `cli/log_append.py` - Append to process log
- [ ] Create CLI tool `cli/domain_log.py` - Add domain knowledge entries
- [ ] Create CLI tool `cli/country_task.py` - Manage country-specific tasks

### Audit Logging System (NEW - See AUDIT_LOGGING_PLAN.md)
- [ ] Create `cli/audit_start_job.py` - Start a new scraping job run
- [ ] Create `cli/audit_log_page.py` - Log every page visited to audit trail
- [ ] Create `cli/audit_mark_source.py` - Mark audit entries as knowledge sources
- [ ] Create `cli/audit_log_tool_call.py` - Log LLM tool calls
- [ ] Create `cli/audit_finish_job.py` - Finish job and compute statistics
- [ ] Create `cli/audit_query.py` - Query audit trail (chains, stats, sources)
- [ ] Create `cli/audit_replay.py` - Generate reproducible replay scripts
- [ ] Create `cli/audit_validate.py` - Validate audit trail completeness
- [ ] Create strict LLM prompt template requiring audit logging after EVERY web action
- [ ] Test audit logging with Italy research pilot

### Project Structure Setup
- [ ] Create all necessary directories
- [ ] Create `.gitignore` with appropriate exclusions
- [ ] Create `requirements.txt` with all dependencies
- [ ] Create `README.md` with setup instructions
- [ ] Create `CONTRIBUTING.md` for LLM agent guidelines
- [ ] Create configuration files (`config/settings.yaml`, `config/scraping_targets.yaml`)

---

## Phase 2: Data Collection Infrastructure (Priority: HIGH)

### Source Discovery
- [ ] Compile list of official government immigration websites (all 15 countries)
- [ ] Compile list of embassy/consulate websites
- [ ] Find official legal databases for each country
- [ ] Identify reputable immigration lawyer/consultant sites
- [ ] Identify expat community forums and subreddits
- [ ] Document source credibility ratings in database

### Content Extraction & Parsing
- [ ] Build HTML parser for common government site structures
- [ ] Build PDF text extractor for legal documents
- [ ] Build table extractor for requirements/fee schedules
- [ ] Create named entity recognition for visa/permit names
- [ ] Create financial amount extractor (with currency conversion)
- [ ] Create date/deadline extractor

### Validation & Quality Control
- [ ] Create data validation rules for each table
- [ ] Create cross-reference checker (flag conflicting info)
- [ ] Create completeness checker (ensure all fields populated)
- [ ] Create freshness tracker (flag outdated information)
- [ ] Create duplicate detector

---

## Phase 3: Country Research - Priority Tier 1 (Priority: HIGH)

### Italy
- [ ] Research digital nomad visa requirements
- [ ] Research innovative startup visa (complete details)
- [ ] Research elective residency visa (financial independence)
- [ ] Research citizenship by descent (post-Tajani Decree)
- [ ] Research EU Blue Card implementation in Italy
- [ ] Research self-employment visa options
- [ ] Compile all sources in database
- [ ] Create country summary document
- [ ] Create pathway comparison table

### Denmark
- [ ] Research digital nomad visa (if available)
- [ ] Research work permit requirements (note: NO EU Blue Card)
- [ ] Research self-employment/freelancer options
- [ ] Research startup visa programs
- [ ] Research residence permit pathways
- [ ] Compile all sources in database
- [ ] Create country summary document
- [ ] Create pathway comparison table

### Netherlands
- [ ] Research digital nomad visa (3-year with business plan)
- [ ] Research highly skilled migrant visa
- [ ] Research startup visa (1-year residence permit)
- [ ] Research self-employment visa
- [ ] Research orientation year visa (for graduates)
- [ ] Research DAFT treaty (if US citizen)
- [ ] Compile all sources in database
- [ ] Create country summary document
- [ ] Create pathway comparison table

### Greece
- [ ] Research digital nomad visa requirements
- [ ] Research golden visa (real estate still available)
- [ ] Research financially independent person visa
- [ ] Research EU Blue Card implementation
- [ ] Research startup/entrepreneur visa
- [ ] Compile all sources in database
- [ ] Create country summary document
- [ ] Create pathway comparison table

---

## Phase 4: Country Research - Priority Tier 2 (Priority: MEDIUM)

### Norway (Schengen, NOT EU)
- [ ] Research digital nomad visa options
- [ ] Research skilled worker permits
- [ ] Research self-employment permits
- [ ] Research startup visa programs
- [ ] Note differences from EU programs
- [ ] Compile all sources in database
- [ ] Create country summary document

### Sweden
- [ ] Research work permit requirements
- [ ] Research EU Blue Card implementation
- [ ] Research self-employment permits
- [ ] Research startup visa options
- [ ] Compile all sources in database
- [ ] Create country summary document

### Switzerland (Schengen, NOT EU)
- [ ] Research work permit requirements (note: highly restrictive)
- [ ] Research self-employment permits
- [ ] Research startup/business permits
- [ ] Research cantonal variations in requirements
- [ ] Note differences from EU programs
- [ ] Compile all sources in database
- [ ] Create country summary document

### France
- [ ] Research digital nomad visa options
- [ ] Research talent passport (EU Blue Card equivalent, €59,373 min)
- [ ] Research entrepreneur/business creation visa
- [ ] Research freelance/self-employment options
- [ ] Research tech visa program
- [ ] Compile all sources in database
- [ ] Create country summary document

---

## Phase 5: Country Research - Priority Tier 3 (Priority: MEDIUM)

### Spain
- [ ] Research digital nomad visa requirements
- [ ] Research golden visa (post-April 2025, NO real estate)
- [ ] Research entrepreneur/startup visa
- [ ] Research EU Blue Card implementation
- [ ] Research non-lucrative visa (financial independence)
- [ ] Compile all sources in database
- [ ] Create country summary document

### Portugal
- [ ] Research digital nomad visa (D7 or D8 visa)
- [ ] Research golden visa (post-2023, NO real estate)
- [ ] Research D2 entrepreneur visa
- [ ] Research tech visa program
- [ ] Research passive income visa
- [ ] Compile all sources in database
- [ ] Create country summary document

### Germany
- [ ] Research digital nomad visa options
- [ ] Research EU Blue Card (€48,300 or €43,759.80 for shortage occupations)
- [ ] Research freelance visa (Freiberufler)
- [ ] Research startup visa
- [ ] Research job seeker visa
- [ ] Compile all sources in database
- [ ] Create country summary document

### Belgium
- [ ] Research digital nomad visa options
- [ ] Research EU Blue Card implementation
- [ ] Research self-employment visa (professional card)
- [ ] Research startup visa programs
- [ ] Compile all sources in database
- [ ] Create country summary document

---

## Phase 6: Country Research - Priority Tier 4 (Priority: LOW)

### Ireland (NO EU Blue Card)
- [ ] Research work permit types (Critical Skills, General)
- [ ] Research startup visa (STEP program)
- [ ] Research citizenship by descent (grandparent eligibility)
- [ ] Research self-employment permits
- [ ] Compile all sources in database
- [ ] Create country summary document

### Austria
- [ ] Research Red-White-Red Card (skilled workers)
- [ ] Research EU Blue Card implementation
- [ ] Research startup visa options
- [ ] Research self-employment permits
- [ ] Compile all sources in database
- [ ] Create country summary document

### Czech Republic
- [ ] Research digital nomad visa (Zivno)
- [ ] Research employee card (work permit)
- [ ] Research EU Blue Card implementation
- [ ] Research business visa (trade license)
- [ ] Compile all sources in database
- [ ] Create country summary document

---

## Phase 7: Knowledge Organization & Documentation (Priority: MEDIUM)

### Documentation Creation
- [ ] Create master comparison table (all countries, all pathways)
- [ ] Create decision tree flowchart (which pathway for your situation)
- [ ] Create financial requirements comparison
- [ ] Create processing time comparison
- [ ] Create path-to-citizenship timeline for each pathway
- [ ] Create tax implications summary by country
- [ ] Create family inclusion summary by pathway

### Obsidian Vault Setup
- [ ] Create Obsidian vault structure
- [ ] Create country note templates
- [ ] Create pathway note templates
- [ ] Create MOC (Map of Content) for navigation
- [ ] Set up tags taxonomy
- [ ] Create dataview queries for dynamic tables
- [ ] Create graph view optimization
- [ ] Link all markdown files with bidirectional links

### Evidence & Source Management
- [ ] Ensure all pathway claims link to sources
- [ ] Store PDFs of official documents
- [ ] Screenshot relevant web pages
- [ ] Archive official legal texts
- [ ] Create source verification checklist
- [ ] Tag sources with last-verified date

---

## Phase 8: Automation & Maintenance (Priority: LOW)

### Automated Monitoring
- [ ] Set up automated re-scraping schedule (monthly)
- [ ] Create change detection notifications
- [ ] Create broken link detector
- [ ] Create policy change monitor (RSS feeds, Google Alerts)
- [ ] Set up automated backup schedule

### Data Refresh Pipeline
- [ ] Create automated refresh workflow
- [ ] Create LLM prompt templates for consistency
- [ ] Create validation pipeline for refreshed data
- [ ] Create diff reports (what changed from last scrape)
- [ ] Create notification system for critical changes

---

## Phase 9: Company Research Extension (Priority: FUTURE)

### Company Database
- [ ] Extend database schema for companies table
- [ ] Create company scraping tools
- [ ] Identify tech job boards by country
- [ ] Scrape company career pages
- [ ] Link companies to visa sponsorship likelihood
- [ ] Create company-to-pathway recommendations

### Company Research by Country
- [ ] Research tech companies in each priority country
- [ ] Identify companies known for visa sponsorship
- [ ] Document company size and tech stack requirements
- [ ] Create company comparison tables
- [ ] Link to job posting aggregators

---

## Phase 10: MCP Wrapper for Automatic Audit Logging (Priority: BACKLOG)

### Long-Term Strategy - Deprioritized
**Goal**: Eliminate need for LLMs to manually log by wrapping Brave/Playwright MCPs with automatic logging middleware.

**Options**:
1. Fork Brave/Playwright MCP servers and add logging
2. Build proxy MCP server that wraps existing MCPs
3. Build custom MCP server that combines search + scraping + logging

**Tasks** (DEPRIORITIZED):
- [ ] Research MCP proxy architecture patterns
- [ ] Design logging middleware for MCP tool calls
- [ ] Build prototype proxy MCP server
- [ ] Test with Brave Search MCP
- [ ] Test with Playwright MCP
- [ ] Add OpenTelemetry observability spans
- [ ] Deploy and configure Claude Code to use logging MCPs
- [ ] Migrate from manual logging to automatic
- [ ] Document MCP wrapper architecture

**Status**: BACKLOG - Start with Phase 1 manual logging first, revisit after proving value

---

## Phase 11: Advanced Features (Priority: FUTURE)

### Interactive Tools
- [ ] Create eligibility quiz/calculator
- [ ] Create cost calculator (total pathway cost)
- [ ] Create timeline estimator (how long to residency/citizenship)
- [ ] Create document checklist generator per pathway
- [ ] Create application tracker template

### Web Interface (Optional)
- [ ] Design simple web UI for navigation
- [ ] Create search functionality
- [ ] Create filtering by criteria (budget, timeline, skill level)
- [ ] Create comparison tool (side-by-side pathways)
- [ ] Deploy static site (GitHub Pages or similar)

---

## Continuous Tasks

### Process Logging
- [ ] Log all major decisions in process_log.md
- [ ] Log all blockers and solutions in process_log.md
- [ ] Document all scraping errors and resolutions
- [ ] Document API/rate limiting issues
- [ ] Document parsing challenges and solutions

### Domain Knowledge Logging
- [ ] Log all major policy changes discovered
- [ ] Log all legal terms and definitions
- [ ] Log all visa/permit types discovered
- [ ] Log all financial thresholds by pathway
- [ ] Log all processing times discovered
- [ ] Log all unexpected requirements/restrictions

### Quality Assurance
- [ ] Weekly review of data completeness
- [ ] Monthly source verification check
- [ ] Quarterly full data refresh
- [ ] Regular conflict resolution (contradictory sources)
- [ ] Regular freshness check (flag outdated info)

---

## LLM Agent Guidelines

When working on this project, LLM agents should:

1. **Always log actions** in the process log
2. **Always log web actions** to audit trail (CRITICAL - see AUDIT_LOGGING_PLAN.md):
   - Start job with `cli/audit_start_job.py`
   - Log EVERY page visited with `cli/audit_log_page.py`
   - Mark knowledge sources with `cli/audit_mark_source.py`
   - Finish job with `cli/audit_finish_job.py`
3. **Always validate information** with multiple sources
4. **Always link to evidence** when documenting pathways
5. **Always use CLI tools** for database interactions (never raw SQL)
6. **Always update country task lists** when completing work
7. **Always tag domain knowledge** when learned
8. **Always use Brave Search MCP** for initial research
9. **Always use Playwright MCP** for dynamic content
10. **Always be respectful** of scraping rate limits
11. **Always prefer official sources** over third-party sites
12. **Always save artifacts** (HTML, PDF) to data/raw/ with audit trail references

---

## Next Immediate Actions

1. [ ] Review and approve this master todos list
2. [ ] Create directory structure
3. [ ] Initialize git repository with proper .gitignore
4. [ ] Create requirements.txt
5. [ ] Create database schema SQL file
6. [ ] Create first CLI tool (db_init.py)
7. [ ] Create logging system documents
8. [ ] Begin Italy research (highest priority)

---

**Last Updated**: 2025-10-25
**Status**: Planning Phase
**Next Milestone**: Complete Phase 1 Foundation
