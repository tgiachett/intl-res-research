-- EU Residency Research Database Schema
-- Version: 1.0
-- Date: 2025-10-25
-- Total Tables: 13 (8 core + 3 audit + 2 artifacts)

-- ============================================================================
-- CORE DATA TABLES (8 tables)
-- ============================================================================

-- Table 1: countries
-- Stores information about the 15 priority countries
CREATE TABLE IF NOT EXISTS countries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  code TEXT NOT NULL UNIQUE,  -- ISO 3166-1 alpha-2 code (IT, DK, etc.)
  is_eu_member BOOLEAN NOT NULL DEFAULT 1,
  is_schengen BOOLEAN NOT NULL DEFAULT 1,
  capital TEXT,
  official_language TEXT,
  currency TEXT,
  immigration_website TEXT,
  notes TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_countries_code ON countries(code);
CREATE INDEX idx_countries_eu ON countries(is_eu_member);
CREATE INDEX idx_countries_schengen ON countries(is_schengen);

-- Table 2: residency_pathways
-- All visa and permit types with requirements
CREATE TABLE IF NOT EXISTS residency_pathways (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  country_id INTEGER NOT NULL REFERENCES countries(id),

  -- Classification
  pathway_type TEXT CHECK(pathway_type IN (
    'digital_nomad', 'employment', 'eu_blue_card', 'startup',
    'self_employment', 'investment', 'golden_visa', 'student',
    'retirement', 'family_reunification', 'citizenship_by_descent', 'other'
  )),

  -- Basic info
  name TEXT NOT NULL,
  official_name TEXT,
  description TEXT,
  legal_basis TEXT,  -- Law/regulation reference

  -- Requirements
  min_income_eur INTEGER,
  min_investment_eur INTEGER,
  education_requirement TEXT,
  language_requirement TEXT,
  age_restrictions TEXT,

  -- Documentation
  required_documents TEXT,  -- JSON array

  -- Process
  application_process TEXT,
  processing_time_days INTEGER,
  application_fee_eur REAL,

  -- Duration and renewal
  initial_duration_months INTEGER,
  renewable BOOLEAN DEFAULT 0,
  max_renewals INTEGER,
  total_max_duration_months INTEGER,

  -- Paths forward
  path_to_permanent_residency TEXT,
  path_to_citizenship TEXT,
  min_years_to_citizenship INTEGER,

  -- Rights and restrictions
  work_rights TEXT,
  family_inclusion TEXT,
  travel_rights TEXT,
  restrictions TEXT,

  -- Tax and financial
  tax_implications TEXT,

  -- Status
  is_active BOOLEAN DEFAULT 1,
  last_verified_date TEXT,
  policy_changes_2025 TEXT,

  -- Metadata
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

  UNIQUE(country_id, pathway_type, name)
);

CREATE INDEX idx_pathways_country ON residency_pathways(country_id);
CREATE INDEX idx_pathways_type ON residency_pathways(pathway_type);
CREATE INDEX idx_pathways_active ON residency_pathways(is_active);
CREATE INDEX idx_pathways_income ON residency_pathways(min_income_eur);

-- Table 3: sources
-- URLs and documents with credibility ratings
CREATE TABLE IF NOT EXISTS sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,

  -- Source info
  url TEXT UNIQUE,
  title TEXT NOT NULL,
  source_type TEXT CHECK(source_type IN (
    'official_government', 'embassy', 'legal_database',
    'licensed_lawyer', 'news', 'community', 'other'
  )),

  -- Credibility (1-5 stars)
  credibility INTEGER CHECK(credibility BETWEEN 1 AND 5),

  -- Content
  description TEXT,
  language TEXT DEFAULT 'en',

  -- Context
  country_id INTEGER REFERENCES countries(id),
  pathway_type TEXT,

  -- Status
  is_active BOOLEAN DEFAULT 1,
  last_accessed_date TEXT,
  last_verified_date TEXT,
  http_status INTEGER,

  -- Metadata
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  notes TEXT
);

CREATE INDEX idx_sources_country ON sources(country_id);
CREATE INDEX idx_sources_type ON sources(source_type);
CREATE INDEX idx_sources_credibility ON sources(credibility);
CREATE INDEX idx_sources_active ON sources(is_active);

-- Table 4: documents (DEPRECATED - use artifacts table instead)
-- Kept for backward compatibility, but new code should use artifacts
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_id INTEGER REFERENCES sources(id),
  file_path TEXT NOT NULL,
  file_type TEXT CHECK(file_type IN ('pdf', 'html', 'doc', 'txt', 'other')),
  file_size_bytes INTEGER,
  title TEXT,
  description TEXT,
  downloaded_at TEXT DEFAULT CURRENT_TIMESTAMP,
  hash_sha256 TEXT UNIQUE,
  notes TEXT,
  deprecated BOOLEAN DEFAULT 1  -- Marked as deprecated
);

-- Table 5: pathway_sources
-- Junction table linking pathways to sources (many-to-many)
CREATE TABLE IF NOT EXISTS pathway_sources (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pathway_id INTEGER NOT NULL REFERENCES residency_pathways(id),
  source_id INTEGER NOT NULL REFERENCES sources(id),
  relevance_score INTEGER CHECK(relevance_score BETWEEN 1 AND 5),
  excerpt TEXT,  -- Key quote or excerpt from source
  page_number INTEGER,  -- For PDF sources
  added_at TEXT DEFAULT CURRENT_TIMESTAMP,
  notes TEXT,

  UNIQUE(pathway_id, source_id)
);

CREATE INDEX idx_pathway_sources_pathway ON pathway_sources(pathway_id);
CREATE INDEX idx_pathway_sources_source ON pathway_sources(source_id);

-- Table 6: legal_references
-- Official laws and regulations
CREATE TABLE IF NOT EXISTS legal_references (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  country_id INTEGER NOT NULL REFERENCES countries(id),

  -- Legal reference
  reference_number TEXT NOT NULL,  -- e.g., "Law 123/2025"
  title TEXT NOT NULL,
  official_url TEXT,

  -- Classification
  reference_type TEXT CHECK(reference_type IN (
    'law', 'decree', 'regulation', 'directive', 'circular', 'other'
  )),

  -- Dates
  enactment_date TEXT,
  effective_date TEXT,
  expiry_date TEXT,

  -- Content
  summary TEXT,
  full_text_path TEXT,  -- Path to downloaded PDF/HTML

  -- Metadata
  language TEXT DEFAULT 'en',
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

  UNIQUE(country_id, reference_number)
);

CREATE INDEX idx_legal_country ON legal_references(country_id);
CREATE INDEX idx_legal_type ON legal_references(reference_type);

-- Table 7: scraping_jobs (DEPRECATED - use audit logging tables instead)
-- Kept for backward compatibility, but new code should use job_run
CREATE TABLE IF NOT EXISTS scraping_jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_name TEXT NOT NULL,
  target_url TEXT,
  country_id INTEGER REFERENCES countries(id),
  status TEXT CHECK(status IN ('pending', 'running', 'completed', 'failed')),
  started_at TEXT,
  completed_at TEXT,
  records_scraped INTEGER DEFAULT 0,
  error_message TEXT,
  notes TEXT,
  deprecated BOOLEAN DEFAULT 1  -- Marked as deprecated
);

-- Table 8: companies (FUTURE - Phase 9)
-- Tech companies for job research
CREATE TABLE IF NOT EXISTS companies (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  country_id INTEGER NOT NULL REFERENCES countries(id),

  -- Company info
  website TEXT,
  headquarters_city TEXT,
  industry TEXT,
  company_size TEXT CHECK(company_size IN (
    'startup', 'small', 'medium', 'large', 'enterprise'
  )),

  -- Tech stack
  tech_stack TEXT,  -- JSON array

  -- Visa sponsorship
  sponsors_visas BOOLEAN DEFAULT 0,
  sponsored_visa_types TEXT,  -- JSON array

  -- Job info
  careers_page_url TEXT,
  remote_work_policy TEXT,

  -- Metadata
  notes TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

  UNIQUE(name, country_id)
);

CREATE INDEX idx_companies_country ON companies(country_id);
CREATE INDEX idx_companies_sponsors ON companies(sponsors_visas);

-- ============================================================================
-- AUDIT LOGGING TABLES (3 tables)
-- ============================================================================

-- Table 9: job_run
-- Top-level scraping tasks with statistics
CREATE TABLE IF NOT EXISTS job_run (
  id INTEGER PRIMARY KEY AUTOINCREMENT,

  -- Job identification
  task_description TEXT NOT NULL,
  country TEXT,
  pathway_type TEXT,

  -- Status
  status TEXT CHECK(status IN ('running', 'completed', 'failed', 'aborted')) DEFAULT 'running',

  -- Timestamps
  started_at TEXT DEFAULT CURRENT_TIMESTAMP,
  completed_at TEXT,

  -- Statistics
  pages_visited INTEGER DEFAULT 0,
  sources_found INTEGER DEFAULT 0,
  artifacts_downloaded INTEGER DEFAULT 0,
  knowledge_created INTEGER DEFAULT 0,

  -- Error tracking
  error_count INTEGER DEFAULT 0,
  error_summary TEXT,

  -- Context
  llm_model TEXT,
  session_notes TEXT
);

CREATE INDEX idx_job_run_status ON job_run(status);
CREATE INDEX idx_job_run_country ON job_run(country);
CREATE INDEX idx_job_run_started ON job_run(started_at);

-- Table 10: tool_call
-- Individual LLM tool invocations
CREATE TABLE IF NOT EXISTS tool_call (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_run_id INTEGER NOT NULL REFERENCES job_run(id),

  -- Tool info
  tool_name TEXT NOT NULL,
  tool_parameters TEXT,  -- JSON

  -- Result
  status TEXT CHECK(status IN ('success', 'error', 'timeout')),
  result_summary TEXT,
  error_message TEXT,

  -- Timing
  called_at TEXT DEFAULT CURRENT_TIMESTAMP,
  duration_ms INTEGER
);

CREATE INDEX idx_tool_call_job ON tool_call(job_run_id);
CREATE INDEX idx_tool_call_tool ON tool_call(tool_name);
CREATE INDEX idx_tool_call_status ON tool_call(status);

-- Table 11: scraper_audit_trail
-- Every page visited, complete reproducibility
CREATE TABLE IF NOT EXISTS scraper_audit_trail (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_run_id INTEGER NOT NULL REFERENCES job_run(id),

  -- Action info
  action_type TEXT CHECK(action_type IN (
    'search', 'fetch', 'navigate', 'click', 'extract', 'screenshot', 'download'
  )),

  -- Tool used
  tool_name TEXT,  -- e.g., 'brave_web_search', 'playwright_navigate'

  -- Web action details
  url TEXT,
  search_query TEXT,
  http_method TEXT DEFAULT 'GET',
  http_status INTEGER,

  -- Content
  page_title TEXT,
  page_language TEXT,

  -- Artifact
  artifact_path TEXT,  -- Path to saved HTML/PDF/screenshot
  artifact_hash TEXT,  -- SHA256 for deduplication

  -- Source marking
  is_source BOOLEAN DEFAULT 0,  -- Mark if this is a knowledge source
  source_id INTEGER REFERENCES sources(id),

  -- Navigation context
  parent_trail_id INTEGER REFERENCES scraper_audit_trail(id),  -- Previous page
  session_id TEXT,  -- Group related actions

  -- Timing
  timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
  duration_ms INTEGER,

  -- Status
  status TEXT CHECK(status IN ('success', 'error', 'timeout', 'skipped')),
  error_message TEXT,

  -- Notes
  notes TEXT
);

CREATE INDEX idx_trail_job ON scraper_audit_trail(job_run_id);
CREATE INDEX idx_trail_action ON scraper_audit_trail(action_type);
CREATE INDEX idx_trail_url ON scraper_audit_trail(url);
CREATE INDEX idx_trail_source ON scraper_audit_trail(is_source);
CREATE INDEX idx_trail_session ON scraper_audit_trail(session_id);
CREATE INDEX idx_trail_timestamp ON scraper_audit_trail(timestamp);

-- ============================================================================
-- ARTIFACT MANAGEMENT TABLES (2 tables)
-- ============================================================================

-- Table 12: artifacts
-- Downloaded files (PDFs, HTML, screenshots) with metadata
CREATE TABLE IF NOT EXISTS artifacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trail_id INTEGER REFERENCES scraper_audit_trail(id),
  source_id INTEGER REFERENCES sources(id),

  -- Classification
  artifact_type TEXT CHECK(artifact_type IN (
    'pdf', 'html', 'screenshot', 'zip', 'doc', 'docx',
    'extracted_text', 'extracted_table', 'extracted_list'
  )),

  -- File info
  file_path TEXT NOT NULL UNIQUE,  -- Relative to project root
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

  -- Extraction status
  extraction_status TEXT CHECK(extraction_status IN (
    'pending', 'extracted', 'failed', 'skipped', 'not_applicable'
  )) DEFAULT 'pending',
  extracted_to_path TEXT,  -- Path to extracted markdown file
  extraction_error TEXT,

  -- Context
  country TEXT,
  pathway_type TEXT,

  -- Metadata
  page_count INTEGER,  -- For PDFs
  word_count INTEGER,

  notes TEXT
);

CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
CREATE INDEX idx_artifacts_country ON artifacts(country);
CREATE INDEX idx_artifacts_hash ON artifacts(sha256);
CREATE INDEX idx_artifacts_source ON artifacts(source_id);
CREATE INDEX idx_artifacts_trail ON artifacts(trail_id);
CREATE INDEX idx_artifacts_extraction ON artifacts(extraction_status);

-- Table 13: knowledge_artifacts
-- Obsidian vault documents with metadata
CREATE TABLE IF NOT EXISTS knowledge_artifacts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,

  -- File info
  file_path TEXT NOT NULL UNIQUE,  -- Relative path in vault
  file_type TEXT CHECK(file_type IN (
    'country_summary', 'pathway_guide', 'comparison',
    'legal_reference', 'source_list', 'moc', 'other'
  )),

  -- Classification
  country TEXT,
  pathway_type TEXT,

  -- Metadata
  title TEXT NOT NULL,
  description TEXT,
  tags TEXT,  -- JSON array

  -- Relationships (JSON arrays of IDs)
  based_on_artifacts TEXT,  -- Array of artifact IDs
  linked_pathways TEXT,     -- Array of pathway IDs
  linked_sources TEXT,      -- Array of source IDs

  -- Status
  status TEXT CHECK(status IN ('draft', 'review', 'complete', 'outdated')) DEFAULT 'draft',
  completeness_score INTEGER CHECK(completeness_score BETWEEN 0 AND 100),

  -- Timestamps
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
  reviewed_at TEXT,
  last_verified_date TEXT,

  -- Obsidian metadata
  word_count INTEGER,
  internal_links_count INTEGER,
  external_links_count INTEGER,

  notes TEXT
);

CREATE INDEX idx_knowledge_country ON knowledge_artifacts(country);
CREATE INDEX idx_knowledge_type ON knowledge_artifacts(file_type);
CREATE INDEX idx_knowledge_status ON knowledge_artifacts(status);
CREATE INDEX idx_knowledge_completeness ON knowledge_artifacts(completeness_score);

-- ============================================================================
-- SCHEMA VERSION TRACKING
-- ============================================================================

CREATE TABLE IF NOT EXISTS schema_version (
  version TEXT PRIMARY KEY,
  applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
  description TEXT
);

INSERT INTO schema_version (version, description)
VALUES ('1.0', 'Initial schema with 13 tables (8 core + 3 audit + 2 artifacts)');

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- ============================================================================

-- Countries
CREATE TRIGGER IF NOT EXISTS update_countries_timestamp
AFTER UPDATE ON countries
BEGIN
  UPDATE countries SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Residency Pathways
CREATE TRIGGER IF NOT EXISTS update_pathways_timestamp
AFTER UPDATE ON residency_pathways
BEGIN
  UPDATE residency_pathways SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Sources
CREATE TRIGGER IF NOT EXISTS update_sources_timestamp
AFTER UPDATE ON sources
BEGIN
  UPDATE sources SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Legal References
CREATE TRIGGER IF NOT EXISTS update_legal_timestamp
AFTER UPDATE ON legal_references
BEGIN
  UPDATE legal_references SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Companies
CREATE TRIGGER IF NOT EXISTS update_companies_timestamp
AFTER UPDATE ON companies
BEGIN
  UPDATE companies SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Knowledge Artifacts
CREATE TRIGGER IF NOT EXISTS update_knowledge_timestamp
AFTER UPDATE ON knowledge_artifacts
BEGIN
  UPDATE knowledge_artifacts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
