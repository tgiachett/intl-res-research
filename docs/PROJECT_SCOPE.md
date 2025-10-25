# EU Residency Research Project - Full Project Scope

## Overview
This document outlines the complete scope of work across all 11 phases of the EU Residency Research Project. It serves as a **reference guide** showing what could be done in each phase.

**For active task tracking, see [TODOS.md](TODOS.md) - the SINGLE source of truth for current work.**

---

## Phase 1: Foundation & Tooling (Week 1-2)

### Database Infrastructure
The foundation requires setting up a comprehensive database schema including:
- Final database schema design based on PROJECT_PLAN.md specifications
- Audit logging tables (`job_run`, `tool_call`, `scraper_audit_trail`) for complete tracking
- Artifact management tables (`artifacts`, `knowledge_artifacts`) for hybrid storage
- Database initialization script (`scripts/db_init.py`) to create all 13 tables
- Database migration tool (`scripts/db_migrate.py`) for schema evolution
- Backup and restore utilities for data protection
- Version tracking table for schema changes

### CLI Tools for LLM Interaction
Essential command-line tools for database operations:
- `cli/db_query.py` for querying with natural language friendly output
- `cli/db_insert.py` for inserting records into tables
- `cli/db_update.py` for updating existing records
- `cli/country_status.py` for showing research progress by country
- `cli/pathway_crud.py` for managing residency pathways
- `cli/source_manager.py` for managing sources and credibility ratings
- `cli/stats.py` for project statistics and coverage metrics
- `cli/export.py` for exporting data to JSON, CSV, and Markdown formats

### Audit Logging System
Critical tools for tracking all web scraping activities:
- `cli/audit_start_job.py` to begin scraping sessions
- `cli/audit_log_page.py` to log every page visited
- `cli/audit_mark_source.py` to identify knowledge sources
- `cli/audit_log_tool_call.py` to track LLM tool invocations
- `cli/audit_finish_job.py` to complete jobs with statistics
- `cli/audit_query.py` for querying audit trails
- `cli/audit_replay.py` to generate reproducible scripts
- `cli/audit_validate.py` to check completeness
- LLM prompt templates enforcing strict audit logging

### Artifact Management Tools
Tools for managing downloaded content and knowledge:
- `cli/artifact_register.py` for registering PDFs, HTML, screenshots
- `cli/artifact_extract.py` for extracting text to markdown
- `cli/artifact_list.py` for listing with filters
- `cli/knowledge_register.py` for Obsidian vault documents
- `cli/knowledge_update.py` for updating metadata
- `cli/knowledge_list.py` for listing knowledge artifacts

### Logging System
Comprehensive logging infrastructure:
- Process log (`docs/logs/process_log.md`) for decisions and blockers
- Domain knowledge log (`docs/logs/domain_knowledge.md`) for discoveries
- Country task logs (`docs/countries/{country}/tasks.md`) for tracking
- `cli/log_append.py` for process logging
- `cli/domain_log.py` for domain knowledge entries
- `cli/country_task.py` for country-specific tasks

### Project Structure
Complete directory organization including:
- Core directories (src/, cli/, scripts/, data/, config/, tests/, docs/vault/)
- Data subdirectories (data/raw/, data/extracted/, data/database/)
- Vault structure (docs/vault/Countries/, docs/vault/Pathways/)
- Configuration files (settings.yaml, scraping_targets.yaml)
- `.gitignore` with appropriate exclusions
- `requirements.txt` with all Python dependencies
- `README.md` with setup instructions
- `CONTRIBUTING.md` for LLM agent guidelines

---

## Phase 2: Data Collection Infrastructure (Week 2-3)

### Source Discovery
Comprehensive source identification:
- Official government immigration websites for all 15 countries
- Embassy and consulate websites
- Official legal databases per country
- Reputable immigration lawyer and consultant sites
- Expat community forums and subreddits
- Source credibility ratings documentation

### Content Extraction & Parsing
Tools for processing scraped content:
- HTML parser for government site structures
- PDF text extractor for legal documents
- Table extractor for requirements and fee schedules
- Named entity recognition for visa/permit names
- Financial amount extractor with currency conversion
- Date and deadline extractor

### Scraping & Automation Tools
Advanced scraping capabilities:
- `cli/scrape_url.py` for single URL scraping
- `cli/scrape_batch.py` for batch operations
- `cli/scrape_scheduler.py` for periodic re-scraping
- `cli/content_extractor.py` for structured data extraction
- `cli/change_detector.py` for content change detection
- `cli/validate_sources.py` for accessibility checks

### Validation & Quality Control
Data quality assurance:
- Validation rules for each database table
- Cross-reference checker for conflicting information
- Completeness checker for required fields
- Freshness tracker for outdated information
- Duplicate detector for content deduplication

---

## Phase 3: Priority Country Research - Tier 1

### Italy
Complete research coverage:
- Digital nomad visa requirements and process
- Innovative startup visa complete details
- Elective residency visa for financial independence
- Citizenship by descent (post-Tajani Decree restrictions)
- EU Blue Card implementation specifics
- Self-employment visa options
- Comprehensive source compilation
- Country summary documentation
- Pathway comparison tables

### Denmark
Full pathway investigation:
- Digital nomad visa availability check
- Work permit requirements (noting NO EU Blue Card)
- Self-employment and freelancer options
- Startup visa programs
- Residence permit pathways
- Source compilation and verification
- Country summary creation
- Pathway comparison development

### Netherlands
Detailed program research:
- Digital nomad visa (3-year with business plan requirement)
- Highly skilled migrant visa program
- Startup visa (1-year residence permit)
- Self-employment visa options
- Orientation year visa for graduates
- DAFT treaty for US citizens
- Complete source documentation
- Country summary and comparisons

### Greece
Comprehensive pathway analysis:
- Digital nomad visa requirements
- Golden visa with real estate (still available)
- Financially independent person visa
- EU Blue Card implementation
- Startup and entrepreneur visa options
- Source compilation
- Summary documentation
- Comparison tables

---

## Phase 4: Priority Country Research - Tier 2

### Norway (Schengen, NOT EU)
Special non-EU member research:
- Digital nomad visa options investigation
- Skilled worker permit requirements
- Self-employment permit pathways
- Startup visa programs
- Differences from EU programs documentation
- Source compilation
- Country summary

### Sweden
EU member pathway research:
- Work permit requirements
- EU Blue Card implementation details
- Self-employment permits
- Startup visa options
- Source documentation
- Country summary

### Switzerland (Schengen, NOT EU)
Highly restrictive system analysis:
- Work permit requirements and quotas
- Self-employment permits
- Startup and business permits
- Cantonal variation documentation
- Non-EU program differences
- Source compilation
- Summary creation

### France
Comprehensive French system research:
- Digital nomad visa options
- Talent passport (EU Blue Card equivalent, €59,373 minimum)
- Entrepreneur and business creation visa
- Freelance and self-employment options
- Tech visa program
- Complete documentation

---

## Phase 5: Priority Country Research - Tier 3

### Spain
Post-golden-visa era research:
- Digital nomad visa requirements
- Golden visa (post-April 2025, NO real estate)
- Entrepreneur and startup visa
- EU Blue Card implementation
- Non-lucrative visa for financial independence
- Source compilation
- Country documentation

### Portugal
Post-reform pathway research:
- Digital nomad visa (D7 or D8)
- Golden visa (post-2023, NO real estate)
- D2 entrepreneur visa
- Tech visa program
- Passive income visa
- Complete documentation

### Germany
Detailed German system analysis:
- Digital nomad visa options
- EU Blue Card (€48,300 or €43,759.80 for shortage occupations)
- Freelance visa (Freiberufler)
- Startup visa
- Job seeker visa
- Comprehensive documentation

### Belgium
Belgian pathway research:
- Digital nomad visa options
- EU Blue Card implementation
- Self-employment visa (professional card)
- Startup visa programs
- Source compilation
- Summary creation

---

## Phase 6: Priority Country Research - Tier 4

### Ireland (NO EU Blue Card)
Non-Blue-Card system research:
- Work permit types (Critical Skills, General)
- Startup visa (STEP program)
- Citizenship by descent (grandparent eligibility)
- Self-employment permits
- Complete documentation

### Austria
Austrian system analysis:
- Red-White-Red Card for skilled workers
- EU Blue Card implementation
- Startup visa options
- Self-employment permits
- Source compilation

### Czech Republic
Czech pathway research:
- Digital nomad visa (Zivno)
- Employee card (work permit)
- EU Blue Card implementation
- Business visa (trade license)
- Complete documentation

---

## Phase 7: Knowledge Organization & Documentation

### Documentation Creation
Comprehensive comparison materials:
- Master comparison table across all countries and pathways
- Decision tree flowchart for pathway selection
- Financial requirements comparison
- Processing time comparison
- Path-to-citizenship timelines
- Tax implications summary by country
- Family inclusion summary by pathway

### Obsidian Vault Setup
Knowledge management system:
- Vault structure creation
- Country note templates
- Pathway note templates
- MOC (Map of Content) for navigation
- Tags taxonomy development
- Dataview queries for dynamic tables
- Graph view optimization
- Bidirectional linking implementation

### Evidence & Source Management
Documentation verification:
- Pathway claims linked to sources
- PDF storage of official documents
- Web page screenshots
- Legal text archives
- Source verification checklists
- Last-verified date tagging

---

## Phase 8: Automation & Maintenance

### Automated Monitoring
Continuous update systems:
- Monthly re-scraping schedules
- Change detection notifications
- Broken link detection
- Policy change monitoring (RSS feeds, Google Alerts)
- Automated backup schedules

### Data Refresh Pipeline
Update automation:
- Automated refresh workflows
- LLM prompt templates for consistency
- Validation pipeline for refreshed data
- Diff reports for changes
- Critical change notifications

---

## Phase 9: Company Research Extension (Future)

### Company Database
Employment opportunity tracking:
- Database schema extension for companies
- Company scraping tool development
- Tech job board identification by country
- Career page scraping
- Visa sponsorship likelihood linking
- Company-to-pathway recommendations

### Company Research by Country
Tech sector analysis:
- Tech company research per priority country
- Visa sponsorship company identification
- Company size and tech stack documentation
- Comparison table creation
- Job posting aggregator linking

---

## Phase 10: MCP Wrapper for Automatic Audit Logging (Backlog)

### Long-Term Automation Strategy
**Status: DEPRIORITIZED**

This phase explores wrapping Brave and Playwright MCP servers with automatic logging middleware to eliminate manual logging requirements. Options include:
- Forking existing MCP servers with logging additions
- Building proxy MCP servers with logging middleware
- Creating custom MCP servers combining search, scraping, and logging

Tasks would include MCP proxy architecture research, logging middleware design, prototype development, testing with both Brave and Playwright MCPs, OpenTelemetry observability integration, and migration from manual to automatic logging.

This remains in the backlog as Phase 1 manual logging tools must prove their value first.

---

## Phase 11: Advanced Features (Future)

### Interactive Tools
User-facing utilities:
- Eligibility quiz and calculator
- Total pathway cost calculator
- Timeline estimator for residency/citizenship
- Document checklist generator per pathway
- Application tracker template

### Web Interface
Optional public access:
- Simple web UI design
- Search functionality
- Filtering by criteria (budget, timeline, skill level)
- Side-by-side pathway comparison tool
- Static site deployment (GitHub Pages)

---

## Continuous Activities

Throughout all phases, maintain:

### Process Logging
- Major decisions in process_log.md
- Blockers and solutions documentation
- Scraping error resolution tracking
- API/rate limiting issue documentation
- Parsing challenge solutions

### Domain Knowledge Logging
- Major policy change discoveries
- Legal term definitions
- Visa/permit type discoveries
- Financial threshold documentation
- Processing time updates
- Unexpected requirement discoveries

### Quality Assurance
- Weekly data completeness reviews
- Monthly source verification checks
- Quarterly full data refreshes
- Regular conflict resolution
- Freshness checking for outdated information

---

## Success Metrics

The project will be considered successful when achieving:
- **Coverage**: All 15 priority countries fully researched
- **Depth**: Minimum 5 pathways documented per country
- **Quality**: At least 2 official sources per pathway
- **Usability**: Easy navigation and comparison capabilities
- **Freshness**: All data current from 2025
- **Extensibility**: Clean architecture supporting future additions
- **Reproducibility**: Complete audit trails for all research

---

## Notes

This document provides the complete scope of the EU Residency Research Project. It is not a todo list but rather a comprehensive reference showing what work exists across all phases.

**For active task tracking, always refer to [TODOS.md](TODOS.md) - the single source of truth for current work.**

---

**Document Type**: Reference Only (No Active Todos)
**Last Updated**: 2025-10-25
**Status**: Complete Project Scope
**Active Work**: See [TODOS.md](TODOS.md)