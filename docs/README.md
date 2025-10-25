# EU Residency Research Project - Documentation

## 📋 Document Index

### ⭐ SINGLE SOURCE OF TRUTH FOR TODOS
**[TODOS.md](TODOS.md)** - Obsidian kanban board with ALL active tasks (Backlog → Todo → In Progress → Done → Blocked)

### Core Planning Documents (Reference - NOT Todos)
1. **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Overall project strategy, architecture, and validated 2025 updates
2. **[MASTER_TODOS.md](MASTER_TODOS.md)** - All tasks organized by 11 phases (reference for scope, active work tracked in TODOS.md)
3. **[CLI_TOOLS_SPEC.md](CLI_TOOLS_SPEC.md)** - Detailed specification for all 20+ CLI tools with usage examples
4. **[AUDIT_LOGGING_PLAN.md](AUDIT_LOGGING_PLAN.md)** - Complete audit logging design (2-table strategy, CLI tools, MCP wrapper plan)
5. **[ARTIFACTS_STRATEGY.md](ARTIFACTS_STRATEGY.md)** - Artifact & knowledge management (hybrid SQLite + filesystem, Obsidian vault)
6. **[QUICK_START.md](QUICK_START.md)** - Quick reference guide for LLM agents
7. **[KANBAN.md](KANBAN.md)** - DEPRECATED, replaced by TODOS.md

### Project Prompts
- **[prompts/initial.md](prompts/initial.md)** - Original project requirements
- **[prompts/02.md](prompts/02.md)** - LLM agent workflow and tooling requirements
- **[prompts/03.md](prompts/03.md)** - Audit logging requirements and MCP wrapper strategy
- **[prompts/04.md](prompts/04.md)** - Artifact management strategy and knowledge storage

## 🎯 Project Goal
Research and catalogue **all possible pathways** to gain residency (and potentially dual citizenship) in EU countries, with focus on living and working in the EU for extended periods.

## 🌍 Priority Countries (15)
1. Italy
2. Denmark
3. Netherlands
4. Greece
5. Norway *(Schengen, NOT EU)*
6. Sweden
7. Switzerland *(Schengen, NOT EU)*
8. France
9. Spain
10. Portugal
11. Germany
12. Belgium
13. Ireland
14. Austria
15. Czech Republic

## 🛂 Residency Pathways Being Researched
1. **Digital Nomad Visas** - 13+ countries offering programs
2. **Investment/Golden Visas** - Major changes in 2025 (Portugal/Spain removed real estate)
3. **Employment Visas** - EU Blue Card (25 countries), company sponsorship
4. **Startup/Entrepreneur Visas** - Italian Innovative Startup, etc.
5. **Citizenship by Descent** - Italy (restricted 2025), Ireland
6. **Freelancer/Self-Employment Visas**
7. **Other Pathways** - Student, retirement, etc.

## ⚠️ Critical 2025 Policy Updates
- **Italy**: Citizenship by descent NOW LIMITED to parent/grandparent only (May 24, 2025 - "Tajani Decree")
- **Portugal**: Golden Visa NO LONGER accepts real estate (removed Oct 2023)
- **Spain**: Golden Visa real estate option ENDED April 3, 2025
- **EU Blue Card**: NOT available in Denmark and Ireland
- **Geography**: Norway & Switzerland are Schengen but NOT EU members

## 🏗️ Project Architecture

### Technology Stack
- **Language**: Python 3.10+
- **Database**: SQLite
- **Web Scraping**: Brave Search MCP, Playwright MCP, custom tools
- **Documentation**: Markdown (Obsidian-compatible)

### Directory Structure
```
intl-res-research/
├── docs/                      # All documentation
│   ├── PROJECT_PLAN.md        # Overall strategy
│   ├── MASTER_TODOS.md        # Complete task list
│   ├── CLI_TOOLS_SPEC.md      # Tool specifications
│   ├── KANBAN.md              # Task board
│   ├── QUICK_START.md         # LLM agent guide
│   ├── prompts/               # Project requirements
│   ├── logs/                  # Process and domain logs
│   ├── countries/             # Per-country research
│   │   └── {country}/
│   │       ├── tasks.md       # Country task tracking
│   │       └── *.md           # Research findings
│   ├── research/              # Organized findings
│   └── sources/               # Source documentation
├── src/
│   ├── scrapers/              # Web scraping modules
│   ├── database/              # Database models
│   ├── parsers/               # Content parsing
│   ├── validators/            # Data validation
│   └── utils/                 # Helper functions
├── cli/                       # CLI tools for LLM agents
│   ├── db_query.py            # Query database
│   ├── db_insert.py           # Insert records
│   ├── log_append.py          # Process logging
│   ├── domain_log.py          # Domain knowledge
│   └── ... (see CLI_TOOLS_SPEC.md)
├── scripts/                   # Setup and maintenance
│   ├── db_init.py             # Initialize database
│   ├── db_migrate.py          # Schema migrations
│   └── ...
├── data/
│   ├── raw/                   # Downloaded HTML/PDFs
│   ├── processed/             # Extracted data
│   └── database/              # SQLite database
├── config/
│   ├── settings.yaml          # Application settings
│   └── scraping_targets.yaml # Scraping configurations
└── tests/                     # Tests
```

## 📊 Database Schema
13 core tables (8 original + 3 audit logging + 2 artifact management):

**Core Data:**
1. **countries** - 15 priority countries with EU/Schengen status
2. **residency_pathways** - All visa/permit types with requirements
3. **sources** - URLs with credibility ratings (1-5), knowledge sources
4. **documents** - DEPRECATED (replaced by artifacts table)
5. **pathway_sources** - Junction table linking pathways to sources
6. **legal_references** - Official laws and regulations
7. **scraping_jobs** - DEPRECATED (replaced by audit logging tables)
8. **companies** - *(future)* Tech companies for job research

**Audit Logging:**
9. **job_run** - Top-level scraping tasks with statistics
10. **tool_call** - Individual LLM tool invocations
11. **scraper_audit_trail** - Every page visited, complete reproducibility

**Artifact Management (NEW):**
12. **artifacts** - Downloaded files (PDFs, HTML, screenshots) with metadata, deduplication
13. **knowledge_artifacts** - Obsidian vault documents with metadata, completeness tracking

**Storage Strategy:** Content in filesystem (`data/raw/`, `data/extracted/`, `docs/vault/`), metadata in SQLite

See [AUDIT_LOGGING_PLAN.md](AUDIT_LOGGING_PLAN.md) and [ARTIFACTS_STRATEGY.md](ARTIFACTS_STRATEGY.md) for complete schemas.

## 🔧 CLI Tools
**25+ tools being built** for LLM agents:
- Database operations (query, insert, update)
- Research status tracking
- Scraping and automation
- Content extraction
- Logging (process + domain knowledge + audit trail)
- Artifact management (register, extract, list)
- Knowledge management (Obsidian vault tracking)
- Data validation and export

See [CLI_TOOLS_SPEC.md](CLI_TOOLS_SPEC.md) for complete details.

## 📝 Logging System

### Three Log Types:
1. **Process Log** (`logs/process_log.md`)
   - Append-only log of decisions, blockers, solutions, errors
   - Documents the journey of solving this problem

2. **Domain Knowledge Log** (`logs/domain_knowledge.md`)
   - Terms, policies, requirements, thresholds discovered
   - Building a knowledge base about EU residency/citizenship

3. **Country Task Logs** (`countries/{country}/tasks.md`)
   - Per-country TODO and DONE tracking
   - Done tasks must link to evidence/documentation

## 🎯 Current Status
- **Phase**: Planning complete, starting Foundation (Phase 1)
- **Priority**: Build CLI tools and database infrastructure
- **Next Up**:
  1. Create directory structure
  2. Initialize database with schema
  3. Build first CLI tools (db_init, db_query, db_insert)
  4. Start Italy research

## 🚀 Quick Start for LLM Agents

1. **Read** [QUICK_START.md](QUICK_START.md) first
2. **Check** [TODOS.md](TODOS.md) for current tasks (SINGLE SOURCE OF TRUTH)
3. **Move tasks** on [TODOS.md](TODOS.md) as you work (Todo → In Progress → Done)
4. **Log everything**:
   - Decisions/blockers → `logs/process_log.md` (use `cli/log_append.py`)
   - Domain learning → `logs/domain_knowledge.md` (use `cli/domain_log.py`)
   - Web actions → audit trail (use `cli/audit_log_page.py` AFTER EVERY web action)
   - Country work → `countries/{country}/tasks.md` (use `cli/country_task.py`)
5. **Use CLI tools** for all database operations (never raw SQL)
6. **Link to sources** for all claims
7. **Follow quality standards** (minimum 2 official sources per pathway)

## 📚 Implementation Phases

### Phase 1: Foundation (Week 1-2) - CURRENT
- Set up project structure
- Initialize database
- Build core CLI tools
- Create logging system

### Phase 2: Research Infrastructure (Week 2-3)
- Build scraping tools
- Create content extractors
- Set up validation pipeline

### Phase 3-4: Country Research (Week 3-8)
- Research all 15 countries
- Document all pathways
- Build source library

### Phase 5: Knowledge Organization (Week 8-9)
- Create comparison tables
- Build Obsidian vault
- Generate decision trees

### Phase 6: Company Research (Week 10+)
- Extend for job research
- Catalogue tech companies

See [MASTER_TODOS.md](MASTER_TODOS.md) for complete breakdown.

## 📖 Documentation Guidelines

### For Each Pathway Document:
- Official program name
- Legal basis (law/regulation numbers)
- Eligibility requirements
- Financial requirements (amounts + currency)
- Required documentation
- Application process and timeline
- Costs (all fees)
- Duration and renewal terms
- Path to permanent residency
- Path to citizenship (if any)
- Restrictions and obligations
- Tax implications
- **Minimum 2 official sources**

### Source Credibility Ratings:
- **5 stars**: Official government (immigration ministry, embassy)
- **4 stars**: Legal databases (official legal texts)
- **3 stars**: Verified professionals (licensed lawyers)
- **2 stars**: News/media (reputable outlets)
- **1 star**: Community (Reddit, forums - requires cross-reference)

## 🔄 Workflow for LLM Agents

1. Check [TODOS.md](TODOS.md) for priorities (SINGLE SOURCE)
2. Move task to "In Progress" on [TODOS.md](TODOS.md)
3. **Start job**: `cli/audit_start_job.py --task "..." --country X`
4. Use Brave Search MCP for research
5. **Log search**: `cli/audit_log_page.py --action search ...`
6. Use Playwright MCP for scraping
7. **Log every page**: `cli/audit_log_page.py --action navigate ...`
8. **Mark sources**: `cli/audit_mark_source.py` for knowledge sources
9. Use CLI tools to store data in database
10. Log decisions with `cli/log_append.py`
11. Log domain knowledge with `cli/domain_log.py`
12. Create markdown documentation with evidence
13. **Finish job**: `cli/audit_finish_job.py --job-id X`
14. Update country task log with `cli/country_task.py`
15. Move task to "Done" on [TODOS.md](TODOS.md)

## 🛠️ Tools Available

### MCP Servers (Already Available)
- **Brave Search MCP** - Web search for sources
- **Playwright MCP** - Browser automation for scraping

### Custom CLI Tools (To Be Built)
See [CLI_TOOLS_SPEC.md](CLI_TOOLS_SPEC.md) for:
- 20+ CLI tools for database, scraping, logging, validation
- Usage examples for each tool
- Development priorities

## 📈 Success Metrics
- **Coverage**: All 15 countries researched
- **Depth**: Minimum 5 pathways per country
- **Quality**: 2+ official sources per pathway
- **Usability**: Easy navigation and comparison
- **Freshness**: All data from 2025
- **Extensibility**: Clean architecture for future additions

## 🤝 Contributing (LLM Agent Guidelines)

When working on this project:
1. Always log actions in process log
2. Always validate with multiple sources
3. Always link to evidence
4. Always use CLI tools (never raw SQL)
5. Always update task lists
6. Always tag domain knowledge
7. Be respectful of rate limits
8. Save raw HTML/PDF for re-parsing
9. Prefer official sources
10. Flag conflicting information

## 📞 Getting Help
- **What to do next** → [TODOS.md](TODOS.md) ⭐ SINGLE SOURCE OF TRUTH
- Overall strategy → [PROJECT_PLAN.md](PROJECT_PLAN.md)
- Full scope (all phases) → [MASTER_TODOS.md](MASTER_TODOS.md) (reference only)
- How to use tools → [CLI_TOOLS_SPEC.md](CLI_TOOLS_SPEC.md)
- Audit logging → [AUDIT_LOGGING_PLAN.md](AUDIT_LOGGING_PLAN.md)
- Artifact management → [ARTIFACTS_STRATEGY.md](ARTIFACTS_STRATEGY.md)
- Quick reference → [QUICK_START.md](QUICK_START.md)

---

**Project Status**: Planning Complete ✓
**Current Phase**: Foundation (Phase 1)
**Last Updated**: 2025-10-25
**Next Milestone**: Complete database and CLI tool infrastructure
