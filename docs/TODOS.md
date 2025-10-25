---

kanban-plugin: basic

---

## 📋 Backlog - Future Work

- [ ] Research Ireland citizenship by descent rules #research
- [ ] Research Italian Innovative Startup visa details #research
- [ ] Research freelancer visas for all countries #research
- [ ] Set up automated re-scraping schedule #automation
- [ ] Create change detection notifications #automation
- [ ] Create automated backup schedule #automation
- [ ] Extend database schema for companies #future
- [ ] Create company scraping tools #future
- [ ] Build MCP proxy wrapper for automatic audit logging #backlog #deprioritized
- [ ] Research MCP proxy architecture patterns #backlog #deprioritized
- [ ] Add OpenTelemetry observability #backlog #deprioritized


## 📝 Todo - Ready to Start

### Phase 1: Foundation (PRIORITY)
- [ ] Create directory structure (src/, cli/, scripts/, data/, config/, tests/, docs/vault/) #foundation #critical
- [ ] Create subdirectories (data/raw/, data/extracted/, data/database/, docs/vault/Countries/) #foundation #critical
- [ ] Create .gitignore file #foundation #critical
- [ ] Create requirements.txt with all dependencies #foundation #critical
- [ ] Design final database schema SQL file (11 tables + 2 new artifact tables) #database #critical
- [ ] Add audit logging tables (`job_run`, `tool_call`, `scraper_audit_trail`) #database #audit
- [ ] Add artifact tables (`artifacts`, `knowledge_artifacts`) #database #artifacts #critical
- [ ] Create database initialization script (`scripts/db_init.py`) #database #critical
- [ ] Create `cli/db_query.py` - Query database #cli #critical
- [ ] Create `cli/db_insert.py` - Insert records #cli #critical
- [ ] Create `cli/db_update.py` - Update records #cli
- [ ] Initialize process log (`docs/logs/process_log.md`) #logging #critical
- [ ] Initialize domain knowledge log (`docs/logs/domain_knowledge.md`) #logging #critical
- [ ] Create country task log template (`docs/countries/TEMPLATE/tasks.md`) #logging
- [ ] Create `cli/log_append.py` - Append to process log #cli #logging
- [ ] Create `cli/domain_log.py` - Add domain knowledge #cli #logging
- [ ] Create `cli/country_task.py` - Manage country tasks #cli #logging

### Audit Logging Tools (HIGH PRIORITY)
- [ ] Create `cli/audit_start_job.py` - Start scraping job #cli #audit #critical
- [ ] Create `cli/audit_log_page.py` - Log every page visited #cli #audit #critical
- [ ] Create `cli/audit_mark_source.py` - Mark knowledge sources #cli #audit #critical
- [ ] Create `cli/audit_finish_job.py` - Finish job #cli #audit #critical
- [ ] Create `cli/audit_query.py` - Query audit trail #cli #audit
- [ ] Create `cli/audit_replay.py` - Generate replay scripts #cli #audit
- [ ] Create `cli/audit_validate.py` - Validate completeness #cli #audit
- [ ] Create LLM prompt template for strict audit logging #documentation #audit

### Artifact Management Tools (HIGH PRIORITY)
- [ ] Create `cli/artifact_register.py` - Register downloaded artifacts (PDFs, HTML, etc.) #cli #artifacts #critical
- [ ] Create `cli/artifact_extract.py` - Extract text from PDFs/HTML to markdown #cli #artifacts #critical
- [ ] Create `cli/artifact_list.py` - List artifacts with filters #cli #artifacts
- [ ] Create `cli/knowledge_register.py` - Register Obsidian vault documents #cli #artifacts #critical
- [ ] Create `cli/knowledge_update.py` - Update knowledge artifact metadata #cli #artifacts
- [ ] Create `cli/knowledge_list.py` - List knowledge artifacts #cli #artifacts

### Phase 2: Research Tools
- [ ] Create `cli/source_manager.py` - Manage sources #cli
- [ ] Create `cli/pathway_crud.py` - CRUD for pathways #cli
- [ ] Create `cli/country_status.py` - Show country progress #cli
- [ ] Create `cli/stats.py` - Project statistics #cli
- [ ] Create `cli/export.py` - Export data #cli
- [ ] Create `scripts/db_migrate.py` - Schema migrations #database
- [ ] Compile official Italy immigration sources #research #italy
- [ ] Compile official Denmark immigration sources #research #denmark
- [ ] Compile official Netherlands immigration sources #research #netherlands


## 🔄 In Progress - Currently Working On



## ✅ Done - Completed

- [x] Create initial project plan (PROJECT_PLAN.md) #planning
- [x] Validate concepts with web research (Brave Search) #planning
- [x] Identify major 2025 policy changes #research
- [x] Create master todos reference (MASTER_TODOS.md) #planning
- [x] Create CLI tools specification (CLI_TOOLS_SPEC.md) #planning
- [x] Create audit logging plan (AUDIT_LOGGING_PLAN.md) #planning
- [x] Create unified kanban board (TODOS.md) #planning


## 🚫 Blocked - Waiting On Something

- [ ] Test audit logging with Italy pilot (blocked: needs audit + artifact CLI tools) #blocked #audit
- [ ] Begin Italy research (blocked: needs database + CLI tools) #blocked #research


## 🎯 Next Immediate Actions

**Start here:**
1. Move "Create directory structure" to In Progress
2. Create the folders
3. Move to Done
4. Move "Create .gitignore" to In Progress
5. Continue...


## 📊 Research Tracking

### Priority Tier 1 (Start After Foundation)
- [ ] Italy: Digital nomad visa #research #italy #tier1
- [ ] Italy: Innovative startup visa #research #italy #tier1
- [ ] Italy: Elective residency visa #research #italy #tier1
- [ ] Italy: Citizenship by descent (post-Tajani) #research #italy #tier1
- [ ] Italy: EU Blue Card #research #italy #tier1
- [ ] Italy: Self-employment visa #research #italy #tier1
- [ ] Denmark: Digital nomad visa #research #denmark #tier1
- [ ] Denmark: Work permits (no EU Blue Card) #research #denmark #tier1
- [ ] Denmark: Startup visa #research #denmark #tier1
- [ ] Netherlands: Digital nomad visa (3-year) #research #netherlands #tier1
- [ ] Netherlands: Highly skilled migrant #research #netherlands #tier1
- [ ] Netherlands: Startup visa #research #netherlands #tier1
- [ ] Greece: Digital nomad visa #research #greece #tier1
- [ ] Greece: Golden visa (real estate) #research #greece #tier1

### Priority Tier 2
- [ ] Norway: Digital nomad visa #research #norway #tier2
- [ ] Norway: Skilled worker permits #research #norway #tier2
- [ ] Sweden: Work permits #research #sweden #tier2
- [ ] Sweden: EU Blue Card #research #sweden #tier2
- [ ] Switzerland: Work permits #research #switzerland #tier2
- [ ] France: Digital nomad visa #research #france #tier2
- [ ] France: Talent passport (€59,373) #research #france #tier2

### Priority Tier 3
- [ ] Spain: Digital nomad visa #research #spain #tier3
- [ ] Spain: Golden visa (no real estate) #research #spain #tier3
- [ ] Portugal: Digital nomad visa (D7/D8) #research #portugal #tier3
- [ ] Portugal: Golden visa (no real estate) #research #portugal #tier3
- [ ] Germany: EU Blue Card (€48,300) #research #germany #tier3
- [ ] Germany: Freelance visa #research #germany #tier3
- [ ] Belgium: EU Blue Card #research #belgium #tier3

### Priority Tier 4
- [ ] Ireland: Work permits #research #ireland #tier4
- [ ] Ireland: Citizenship by descent #research #ireland #tier4
- [ ] Austria: Red-White-Red Card #research #austria #tier4
- [ ] Czech Republic: Digital nomad visa #research #czech #tier4


## 📝 Notes

### Tags Used
- `#foundation` - Core infrastructure
- `#critical` - Must do ASAP
- `#database` - Database related
- `#cli` - CLI tool
- `#audit` - Audit logging
- `#artifacts` - Artifact management (NEW)
- `#logging` - General logging
- `#research` - Country/pathway research
- `#automation` - Automated systems
- `#future` - Low priority future work
- `#backlog` - Explicitly deprioritized
- `#deprioritized` - User requested to backlog
- `#blocked` - Blocked by dependencies
- `#tier1` / `#tier2` / `#tier3` / `#tier4` - Research priority
- Country tags: `#italy`, `#denmark`, `#netherlands`, etc.

### How to Use This Board
1. **Move tasks** from Todo → In Progress → Done as you work
2. **Update** task descriptions if needed
3. **Add new tasks** to Backlog first, then promote to Todo when ready
4. **Use tags** to filter and organize
5. **Check "Next Immediate Actions"** to know where to start
6. **This is the SINGLE SOURCE OF TRUTH** for todos

### Other Documents
- **MASTER_TODOS.md**: Reference showing all tasks organized by 11 phases (read-only, for context)
- **PROJECT_PLAN.md**: Overall strategy and architecture (reference, not todos)
- **AUDIT_LOGGING_PLAN.md**: Detailed audit logging design (2-table strategy)
- **ARTIFACTS_STRATEGY.md**: Artifact & knowledge management design (hybrid SQLite + filesystem) (NEW)
- **CLI_TOOLS_SPEC.md**: Specifications for all CLI tools
- **QUICK_START.md**: Quick reference for LLM agents


%% kanban:settings
```
{"kanban-plugin":"basic","hide-tags-in-title":false,"link-date-to-daily-note":false,"show-checkboxes":true,"tag-colors":[{"tagKey":"#critical","color":"red","backgroundColor":"rgba(255,0,0,0.1)"},{"tagKey":"#audit","color":"orange","backgroundColor":"rgba(255,165,0,0.1)"},{"tagKey":"#blocked","color":"gray","backgroundColor":"rgba(128,128,128,0.1)"},{"tagKey":"#deprioritized","color":"lightgray","backgroundColor":"rgba(211,211,211,0.1)"}]}
```
%%
