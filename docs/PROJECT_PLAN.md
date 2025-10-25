# EU Residency Research Project - Overarching Plan

## Project Goal
Research and catalogue all possible pathways to gain residency (and potentially dual citizenship) in EU countries, with focus on living and working in the EU for extended periods.

## Priority Countries
1. Italy
2. Denmark
3. Netherlands
4. Greece
5. Norway (Schengen member, NOT EU member)
6. Sweden
7. Switzerland (Schengen member, NOT EU member)
8. France
9. Spain
10. Portugal
11. Germany
12. Belgium
13. Ireland
14. Austria (confirmed EU member)
15. Czech Republic

## Residency Pathways to Research

### Primary Pathways
1. **Digital Nomad Visas** ✅ Validated 2025
   - Income requirements (vary by country)
   - Duration and renewal terms (typically 1 year, renewable)
   - Tax implications
   - Available in: Italy, Portugal, Croatia, Czech Republic, Estonia, Germany, Hungary, Greece, Malta, Romania, Spain, Norway, Denmark
   - Note: Netherlands offers 3-year visa upfront but requires business plan

2. **Financial/Investment-Based Residency** ⚠️ MAJOR CHANGES IN 2025
   - **Portugal Golden Visa**: Real estate option REMOVED in 2023. Now requires €500,000+ in qualifying funds/capital transfer
   - **Spain Golden Visa**: Real estate option ENDED April 3, 2025
   - **Greece Golden Visa**: Still active with real estate options
   - Financial deposit requirements
   - Minimum investment thresholds

3. **Employment-Based Visas** ✅ Validated 2025
   - Company-sponsored work permits
   - **EU Blue Card**: Valid in 25 of 27 EU countries (all except Denmark and Ireland)
     - Requires: Valid work contract (6+ months), professional qualifications
     - Germany 2025: Minimum salary €48,300 (general) or €43,759.80 (shortage occupations)
     - France 2025: Minimum €59,373 gross annual
     - Provides path to permanent residency and family inclusion
   - Job seeker visas
   - Requirements and quotas

4. **Business/Entrepreneurship Visas**
   - Startup visa programs (e.g., Italian Innovative Startup)
   - Self-employment permits
   - Business investment requirements
   - Business plan requirements

5. **Citizenship by Descent** ⚠️ MAJOR RESTRICTIONS 2025
   - **Italian ancestry (jure sanguinis)**:
     - NEW as of May 24, 2025 ("Tajani Decree"): ONLY parent or grandparent qualifies (great-grandparents NO LONGER eligible)
     - Requires proof Italian ancestor didn't naturalize before child's adulthood
     - Ancestor must be born after March 17, 1861 (Italian unification)
     - Requires birth/marriage/death certificates for entire lineage
     - Virtual appointment system at consulates
   - **Irish ancestry**: Research needed
   - Documentation requirements
   - Application processes

6. **Other Pathways** (to be discovered)
   - Student visas with work rights
   - Freelancer visas
   - Artist/cultural visas
   - Family reunification
   - Long-term resident permits
   - Retirement visas

## Technical Architecture

### Technology Stack
- **Language**: Python 3.10+
- **Database**: SQLite
- **Web Scraping**: Beautiful Soup, Scrapy, or Playwright
- **Data Storage**: Local file system + database
- **Documentation**: Markdown files

### Project Structure
```
intl-res-research/
├── src/
│   ├── scrapers/           # Web scraping modules
│   ├── database/           # Database models and operations
│   ├── parsers/            # Content parsing utilities
│   ├── validators/         # Data validation
│   └── utils/              # Helper functions
├── data/
│   ├── raw/                # Downloaded HTML/PDF files
│   ├── processed/          # Extracted and structured data
│   └── database/           # SQLite database file
├── docs/
│   ├── research/           # Organized research by country
│   ├── sources/            # Source documentation
│   └── guides/             # How-to guides for each pathway
├── config/
│   ├── scraping_targets.yaml  # URLs and scraping configurations
│   └── settings.py         # Application settings
├── notebooks/              # Jupyter notebooks for exploration
├── tests/                  # Unit and integration tests
└── scripts/                # Utility scripts
```

## Database Schema

### Core Tables

1. **countries**
   - id, name, eu_member, schengen_member, notes

2. **residency_pathways**
   - id, country_id, pathway_type, name, description, requirements, duration, renewable, cost_estimate, processing_time, last_updated

3. **sources**
   - id, url, title, source_type (official/unofficial), language, credibility_rating, date_accessed, notes

4. **scraping_jobs**
   - id, url, target_type, status (pending/success/failed), start_time, end_time, error_message, retry_count

5. **documents**
   - id, source_id, file_path, file_type, download_date, file_size, checksum

6. **pathway_sources** (junction table)
   - pathway_id, source_id, relevance_score

7. **legal_references**
   - id, country_id, law_name, law_number, article, description, effective_date, url

8. **companies** (future extension)
   - id, name, country_id, industry, size, tech_stack, careers_url, notes

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Set up project structure
- [ ] Initialize SQLite database with schema
- [ ] Create base scraper framework
- [ ] Implement logging and error handling
- [ ] Create configuration management system

### Phase 2: Research Infrastructure (Week 2-3)
- [ ] Build URL catalogue for official government sources
- [ ] Implement scrapers for common website types
- [ ] Create document download and storage system
- [ ] Develop content extraction and parsing utilities
- [ ] Set up data validation pipeline

### Phase 3: Priority Country Research (Week 3-6)
- [ ] Research Italy (Digital Nomad, Innovative Startup, Ancestry)
- [ ] Research Denmark
- [ ] Research Netherlands
- [ ] Research Greece
- [ ] Research Norway
- [ ] Research Sweden
- [ ] Research Switzerland
- [ ] Document findings in structured format

### Phase 4: Remaining Countries (Week 6-8)
- [ ] Research France
- [ ] Research Spain
- [ ] Research Portugal
- [ ] Research Germany
- [ ] Research Belgium
- [ ] Research Ireland (including ancestry)
- [ ] Research Austria
- [ ] Research Czech Republic

### Phase 5: Knowledge Organization (Week 8-9)
- [ ] Create comprehensive documentation per country
- [ ] Build comparison matrices
- [ ] Develop navigation system (Obsidian integration)
- [ ] Create summary reports
- [ ] Generate pathway decision trees

### Phase 6: Company Research Extension (Week 10+)
- [ ] Extend database schema for companies
- [ ] Build company scrapers
- [ ] Catalogue tech companies by country
- [ ] Link job opportunities to visa pathways

## Key Information to Capture

### For Each Residency Pathway
- Official program name
- Legal basis (law/regulation numbers)
- Eligibility requirements
- Financial requirements
- Documentation needed
- Application process and timeline
- Costs (application fees, legal fees)
- Duration and renewal terms
- Path to permanent residency
- Path to citizenship (if any)
- Restrictions and obligations
- Tax implications
- Healthcare access
- Family members inclusion
- Success rates (if available)

### Source Credibility Levels
1. **Official Government** - Immigration ministry, embassy websites
2. **Legal Sources** - Official legal databases, government gazettes
3. **Verified Professional** - Immigration lawyers, consultants with credentials
4. **Community/Forum** - Reddit, expat forums (cross-reference required)
5. **News/Media** - Reputable news sources

## Tools and Automation

### Scraping Strategy
- **Respectful scraping**: Rate limiting, robots.txt compliance
- **Persistent storage**: Save raw HTML for re-parsing
- **Version tracking**: Track when information was last updated
- **Change detection**: Alert when official sources change

### Data Quality
- Cross-reference multiple sources
- Flag conflicting information
- Track information freshness
- Verify official sources

### Navigation and Access
- Obsidian vault integration
- Tag-based organization
- Search functionality
- Visual relationship maps
- Comparison tables

## Success Metrics
- Coverage: All priority countries researched (15 countries)
- Depth: Minimum 5 pathways per country documented
- Quality: 2+ official sources per pathway
- Usability: Easy navigation and comparison
- Extensibility: Clean architecture for adding companies

## Risk Mitigation
- **Outdated Information**: Include last-updated dates, implement periodic re-scraping
- **Language Barriers**: Use translation tools, note when translation is used
- **Complex Legal Text**: Link to original sources, consider professional review
- **Website Changes**: Store raw content, implement robust parsers
- **Scope Creep**: Focus on residency first, companies later

## Next Steps
1. Review and approve this plan
2. Create Obsidian kanban board with specific tasks
3. Set up development environment
4. Begin Phase 1 implementation

## Critical 2025 Updates (Validated via Web Search)

### ✅ Confirmed Active Programs
- **Digital Nomad Visas**: 13+ EU countries offering programs
- **EU Blue Card**: Active across 25 EU countries with updated 2025 salary thresholds
- **Italian Innovative Startup Visa**: Still active (needs deeper research)

### ⚠️ Major Policy Changes
1. **Portugal Golden Visa** (Oct 2023): Real estate investment pathway REMOVED
2. **Spain Golden Visa** (April 3, 2025): Real estate investment pathway ENDED
3. **Italian Citizenship by Descent** (May 24, 2025): "Tajani Decree" limits to parent/grandparent only
4. **Greece Golden Visa**: Still active with real estate options (possible changes coming)

### 🔍 Requires Further Research
- Ireland citizenship by descent rules
- Italian Innovative Startup visa current requirements
- Freelancer/self-employment visas by country
- Student visa work rights and transition pathways
- Country-specific digital nomad visa income requirements

### Key Findings
- **Norway & Switzerland**: Schengen members but NOT EU members (affects certain programs)
- **EU Blue Card**: NOT available in Denmark and Ireland
- **Golden Visas**: Rapidly changing landscape - must track 2025-2026 updates closely
- **Ancestry Citizenship**: Time-sensitive - Italian rules tightened significantly in 2025

## Notes
- Prioritize breadth over depth initially (survey all countries)
- Document as we go (don't wait until end)
- Keep raw data separate from processed data
- Make it easy to add new countries/pathways later
- Consider creating a simple web interface in future phases
- **CRITICAL**: Track policy changes - 2025 has seen major shifts in golden visa and citizenship programs
