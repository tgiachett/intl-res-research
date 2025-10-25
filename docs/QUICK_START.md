# Quick Start Guide for LLM Agents

## Project Overview
This is an LLM-driven research project to comprehensively document all pathways to EU residency and citizenship across 15 priority countries.

## Key Documents
1. **PROJECT_PLAN.md** - Overall strategy and architecture
2. **MASTER_TODOS.md** - Complete task list organized by phase
3. **CLI_TOOLS_SPEC.md** - Specification for all CLI tools
4. **KANBAN.md** - Obsidian kanban board for task tracking

## Current Status
- **Phase**: Planning Complete, Foundation Starting
- **Priority**: Build CLI tools and database infrastructure
- **Next Actions**: See "Immediate Next Steps" below

## Tools Available to LLM Agents
- **Brave Search MCP**: For web research and source discovery
- **Playwright MCP**: For scraping JavaScript-heavy sites
- **Custom CLI Tools**: (to be built) For database interaction and automation

## Logging Requirements
All LLM agents MUST log:
1. **Process Log** (`docs/logs/process_log.md`): Decisions, blockers, solutions, errors
2. **Domain Knowledge** (`docs/logs/domain_knowledge.md`): Terms, policies, requirements discovered
3. **Country Tasks** (`docs/countries/{country}/tasks.md`): Per-country task tracking with evidence links

## Critical 2025 Policy Updates
⚠️ **Must be aware of:**
- Italian citizenship by descent NOW LIMITED to parent/grandparent (May 2025)
- Portugal Golden Visa NO LONGER accepts real estate (Oct 2023)
- Spain Golden Visa NO LONGER accepts real estate (April 2025)
- EU Blue Card NOT available in Denmark and Ireland
- Norway & Switzerland are Schengen but NOT EU

## Database Schema (Summary)
Core tables:
1. `countries` - 15 priority countries
2. `residency_pathways` - All visa/permit types
3. `sources` - URLs with credibility ratings
4. `scraping_jobs` - Track scraping attempts
5. `documents` - Downloaded files
6. `pathway_sources` - Link pathways to sources
7. `legal_references` - Official laws/regulations
8. `companies` - (future) Tech companies by country

## CLI Tools Priority
**Build these first:**
1. `scripts/db_init.py` - Initialize database
2. `cli/db_query.py` - Query database
3. `cli/db_insert.py` - Insert records
4. `cli/log_append.py` - Append to process log
5. `cli/domain_log.py` - Log domain knowledge

## Research Priority
**Countries in order:**
1. Italy (digital nomad, startup visa, ancestry citizenship)
2. Denmark
3. Netherlands (3-year digital nomad visa)
4. Greece (golden visa still has real estate option)
5. Norway (Schengen, NOT EU)
6. Sweden
7. Switzerland (Schengen, NOT EU)
8. France (€59,373 talent passport)
9. Spain (digital nomad, post-golden-visa)
10. Portugal (D7/D8 visa, post-golden-visa)
11. Germany (€48,300 Blue Card)
12. Belgium
13. Ireland (citizenship by descent)
14. Austria
15. Czech Republic

## Pathway Types to Research
For each country, document:
1. Digital Nomad Visas
2. Investment/Golden Visas (if still available)
3. Employment visas (including EU Blue Card)
4. Startup/Entrepreneur visas
5. Citizenship by descent (Italy, Ireland)
6. Freelancer/Self-employment visas
7. Other pathways discovered

## Quality Standards
Each pathway MUST include:
- Official program name
- Legal basis (law/regulation numbers)
- Eligibility requirements
- Financial requirements (with amounts and currency)
- Required documentation
- Application process and timeline
- Costs (fees)
- Duration and renewal terms
- Path to permanent residency
- Path to citizenship (if any)
- At least 2 official sources

## Source Credibility Ratings
1. **Rating 5**: Official government (immigration ministry, embassy)
2. **Rating 4**: Legal databases (official legal texts)
3. **Rating 3**: Verified professionals (licensed immigration lawyers)
4. **Rating 2**: News/media (reputable outlets)
5. **Rating 1**: Community (Reddit, forums - cross-reference required)

## Immediate Next Steps
1. Create directory structure
2. Initialize Git with .gitignore
3. Create requirements.txt
4. Build db_init.py script
5. Initialize logging documents
6. Begin Italy research

## Working with This Project
1. Always check MASTER_TODOS.md for current priorities
2. Update KANBAN.md as you work
3. Log everything in process_log.md
4. Document domain knowledge in domain_knowledge.md
5. Link all claims to sources
6. Use CLI tools (once built) for all database operations
7. Be respectful of rate limits when scraping
8. Save raw HTML/PDF files for re-parsing
9. Update country task logs with evidence links

## Getting Help
- Check PROJECT_PLAN.md for overall strategy
- Check CLI_TOOLS_SPEC.md for tool usage
- Check MASTER_TODOS.md for what needs doing
- Check logs for past decisions and learnings

---

**Last Updated**: 2025-10-25
**Status**: Foundation phase starting
**Current Focus**: Build CLI tools and database infrastructure
