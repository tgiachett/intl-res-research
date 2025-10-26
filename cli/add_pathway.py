#!/usr/bin/env python3
"""
Add Pathway CLI Tool - BUNDLED TRANSACTION

Add a pathway with source, audit logging, and artifacts in ONE atomic transaction.

This tool updates 6 tables automatically:
1. residency_pathways - The pathway
2. sources - Source record (or finds existing)
3. pathway_sources - Links pathway to source
4. artifacts - Artifact file (if provided)
5. scraper_audit_trail - Logs the fetch action
6. job_run - Updates statistics

LLMs should use THIS instead of manual db_insert.py + audit_log_page.py + etc.

Usage:
    python cli/add_pathway.py \\
        --job-id 2 \\
        --country Italy \\
        --type digital_nomad \\
        --name "Digital Nomad Visa" \\
        --min-income 24789 \\
        --source-url "https://..." \\
        --source-title "Italian Consulate" \\
        --credibility 5

Example (Full):
    python cli/add_pathway.py \\
        --job-id 2 \\
        --country Italy \\
        --type digital_nomad \\
        --name "Digital Nomad Visa" \\
        --official-name "Visto per Nomadi Digitali" \\
        --description "Remote work visa for highly skilled workers" \\
        --legal-basis "Legislative Decree n. 286/1998, art. 27-quater" \\
        --min-income 24789 \\
        --duration 12 \\
        --renewable \\
        --fee 50 \\
        --processing-time 45 \\
        --source-url "https://consnewyork.esteri.it/..." \\
        --source-title "Italian Consulate NY - Digital Nomad Visa" \\
        --source-type official_government \\
        --credibility 5 \\
        --artifact-path "data/raw/italy/2025-10-25_consulate_nomad.md"
"""

import sqlite3
import sys
import hashlib
from pathlib import Path
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "database" / "residency.db"


def get_db_connection() -> sqlite3.Connection:
    """Get database connection"""
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}", file=sys.stderr)
        print("   Run: python scripts/db_init.py", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_country_id(conn: sqlite3.Connection, country_name: str) -> int:
    """Get country ID by name"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM countries WHERE name = ?", (country_name,))
    row = cursor.fetchone()
    if not row:
        print(f"❌ Country '{country_name}' not found", file=sys.stderr)
        sys.exit(1)
    return row['id']


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file"""
    if not file_path.exists():
        return None
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def add_pathway_transaction(
    job_id: int,
    country: str,
    pathway_type: str,
    name: str,
    source_url: str,
    source_title: str,
    source_type: str,
    credibility: int,
    # Optional pathway fields
    official_name: str = None,
    description: str = None,
    legal_basis: str = None,
    min_income: int = None,
    min_investment: int = None,
    education_req: str = None,
    language_req: str = None,
    age_restrictions: str = None,
    documents: str = None,
    process: str = None,
    processing_time: int = None,
    fee: float = None,
    duration: int = None,
    renewable: bool = False,
    max_renewals: int = None,
    max_duration: int = None,
    path_pr: str = None,
    path_citizenship: str = None,
    years_to_citizenship: int = None,
    work_rights: str = None,
    family: str = None,
    travel_rights: str = None,
    restrictions: str = None,
    tax: str = None,
    policy_changes: str = None,
    # Optional artifact
    artifact_path: str = None,
    # Optional source fields
    source_description: str = None,
    source_excerpt: str = None,
    source_relevance: int = 5
) -> dict:
    """
    Add pathway with full transaction (6 tables updated).

    Returns:
        dict with pathway_id, source_id, artifact_id, trail_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Begin transaction
        cursor.execute("BEGIN TRANSACTION")

        print(f"🔄 Starting transaction...", file=sys.stderr)

        # 1. Verify job exists
        cursor.execute("SELECT id FROM job_run WHERE id = ?", (job_id,))
        if not cursor.fetchone():
            raise ValueError(f"Job {job_id} not found")

        # Get country ID
        country_id = get_country_id(conn, country)

        # 2. Create or find source
        print(f"📚 Creating/finding source...", file=sys.stderr)

        cursor.execute("SELECT id FROM sources WHERE url = ?", (source_url,))
        existing_source = cursor.fetchone()

        if existing_source:
            source_id = existing_source['id']
            print(f"   ✓ Found existing source (ID: {source_id})", file=sys.stderr)
        else:
            cursor.execute("""
                INSERT INTO sources (
                    url, title, source_type, credibility, description,
                    country_id, pathway_type, is_active,
                    last_accessed_date, last_verified_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, date('now'), date('now'))
            """, (source_url, source_title, source_type, credibility,
                  source_description, country_id, pathway_type))

            source_id = cursor.lastrowid
            print(f"   ✓ Created new source (ID: {source_id})", file=sys.stderr)

            # Update job stats
            cursor.execute("UPDATE job_run SET sources_found = sources_found + 1 WHERE id = ?", (job_id,))

        # 3. Log to audit trail
        print(f"📝 Logging to audit trail...", file=sys.stderr)

        cursor.execute("""
            INSERT INTO scraper_audit_trail (
                job_run_id, action_type, tool_name, url, page_title,
                is_source, source_id, artifact_path, status, timestamp
            ) VALUES (?, 'fetch', 'add_pathway_bundled', ?, ?, 1, ?, ?, 'success', ?)
        """, (job_id, source_url, source_title, source_id,
              artifact_path, datetime.now().isoformat()))

        trail_id = cursor.lastrowid
        print(f"   ✓ Logged to audit trail (ID: {trail_id})", file=sys.stderr)

        # Update job stats
        cursor.execute("UPDATE job_run SET pages_visited = pages_visited + 1 WHERE id = ?", (job_id,))

        # 4. Register artifact (if provided)
        artifact_id = None
        if artifact_path:
            print(f"📦 Registering artifact...", file=sys.stderr)

            full_path = Path(artifact_path)
            if not full_path.is_absolute():
                full_path = PROJECT_ROOT / artifact_path

            if full_path.exists():
                file_size = full_path.stat().st_size
                file_hash = compute_file_hash(full_path)

                # Check for duplicate
                cursor.execute("SELECT id FROM artifacts WHERE sha256 = ?", (file_hash,))
                existing_artifact = cursor.fetchone()

                if existing_artifact:
                    artifact_id = existing_artifact['id']
                    print(f"   ✓ Found existing artifact (ID: {artifact_id})", file=sys.stderr)
                else:
                    try:
                        relative_path = full_path.relative_to(PROJECT_ROOT)
                    except ValueError:
                        relative_path = full_path

                    cursor.execute("""
                        INSERT INTO artifacts (
                            trail_id, source_id, artifact_type, file_path,
                            file_name, file_size_bytes, sha256, title,
                            source_url, country, pathway_type, downloaded_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (trail_id, source_id, 'extracted_text', str(relative_path),
                          full_path.name, file_size, file_hash, name,
                          source_url, country, pathway_type, datetime.now().isoformat()))

                    artifact_id = cursor.lastrowid
                    print(f"   ✓ Registered artifact (ID: {artifact_id})", file=sys.stderr)

                    # Update job stats
                    cursor.execute("UPDATE job_run SET artifacts_downloaded = artifacts_downloaded + 1 WHERE id = ?", (job_id,))
            else:
                print(f"   ⚠️  Artifact file not found: {artifact_path}", file=sys.stderr)

        # 5. Insert pathway
        print(f"🛂 Inserting pathway...", file=sys.stderr)

        cursor.execute("""
            INSERT INTO residency_pathways (
                country_id, pathway_type, name, official_name, description,
                legal_basis, min_income_eur, min_investment_eur,
                education_requirement, language_requirement, age_restrictions,
                required_documents, application_process, processing_time_days,
                application_fee_eur, initial_duration_months, renewable,
                max_renewals, total_max_duration_months,
                path_to_permanent_residency, path_to_citizenship,
                min_years_to_citizenship, work_rights, family_inclusion,
                travel_rights, restrictions, tax_implications,
                is_active, last_verified_date, policy_changes_2025
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, date('now'), ?)
        """, (country_id, pathway_type, name, official_name, description,
              legal_basis, min_income, min_investment, education_req,
              language_req, age_restrictions, documents, process,
              processing_time, fee, duration, 1 if renewable else 0,
              max_renewals, max_duration, path_pr, path_citizenship,
              years_to_citizenship, work_rights, family, travel_rights,
              restrictions, tax, policy_changes))

        pathway_id = cursor.lastrowid
        print(f"   ✓ Inserted pathway (ID: {pathway_id})", file=sys.stderr)

        # 6. Link pathway to source
        print(f"🔗 Linking pathway to source...", file=sys.stderr)

        cursor.execute("""
            INSERT INTO pathway_sources (
                pathway_id, source_id, relevance_score, excerpt
            ) VALUES (?, ?, ?, ?)
        """, (pathway_id, source_id, source_relevance, source_excerpt))

        print(f"   ✓ Linked pathway to source", file=sys.stderr)

        # Commit transaction
        conn.commit()

        print(f"\n✅ TRANSACTION COMPLETE", file=sys.stderr)
        print(f"   Pathway ID: {pathway_id}", file=sys.stderr)
        print(f"   Source ID: {source_id}", file=sys.stderr)
        if artifact_id:
            print(f"   Artifact ID: {artifact_id}", file=sys.stderr)
        print(f"   Trail ID: {trail_id}", file=sys.stderr)
        print(file=sys.stderr)
        print(f"   Tables updated: 6", file=sys.stderr)
        print(f"   - residency_pathways ✓", file=sys.stderr)
        print(f"   - sources ✓", file=sys.stderr)
        print(f"   - pathway_sources ✓", file=sys.stderr)
        if artifact_id:
            print(f"   - artifacts ✓", file=sys.stderr)
        print(f"   - scraper_audit_trail ✓", file=sys.stderr)
        print(f"   - job_run ✓", file=sys.stderr)

        # Output pathway ID for scripting
        print(pathway_id)

        return {
            'pathway_id': pathway_id,
            'source_id': source_id,
            'artifact_id': artifact_id,
            'trail_id': trail_id
        }

    except Exception as e:
        print(f"\n❌ TRANSACTION FAILED - Rolling back", file=sys.stderr)
        print(f"   Error: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Add pathway with source in ONE transaction (6 tables updated)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Required arguments
    parser.add_argument('--job-id', required=True, type=int, help='Job ID from audit_start_job.py')
    parser.add_argument('--country', required=True, help='Country name')
    parser.add_argument('--type', required=True, help='Pathway type')
    parser.add_argument('--name', required=True, help='Pathway name')

    # Source arguments (REQUIRED)
    parser.add_argument('--source-url', required=True, help='Source URL')
    parser.add_argument('--source-title', required=True, help='Source title')
    parser.add_argument('--source-type', required=True,
                       choices=['official_government', 'embassy', 'legal_database',
                               'licensed_lawyer', 'news', 'community', 'other'],
                       help='Source type')
    parser.add_argument('--credibility', required=True, type=int, choices=[1, 2, 3, 4, 5],
                       help='Source credibility (1-5)')

    # Optional source fields
    parser.add_argument('--source-description', help='Source description')
    parser.add_argument('--source-excerpt', help='Key excerpt from source')
    parser.add_argument('--source-relevance', type=int, choices=[1, 2, 3, 4, 5], default=5,
                       help='Relevance score (default: 5)')

    # Optional artifact
    parser.add_argument('--artifact-path', help='Path to artifact file (PDF, HTML, markdown)')

    # Optional pathway fields
    parser.add_argument('--official-name', help='Official name in local language')
    parser.add_argument('--description', help='Pathway description')
    parser.add_argument('--legal-basis', help='Legal basis (law/decree)')
    parser.add_argument('--min-income', type=int, help='Minimum income (EUR/year)')
    parser.add_argument('--min-investment', type=int, help='Minimum investment (EUR)')
    parser.add_argument('--education-req', help='Education requirement')
    parser.add_argument('--language-req', help='Language requirement')
    parser.add_argument('--age-restrictions', help='Age restrictions')
    parser.add_argument('--documents', help='Required documents')
    parser.add_argument('--process', help='Application process')
    parser.add_argument('--processing-time', type=int, help='Processing time (days)')
    parser.add_argument('--fee', type=float, help='Application fee (EUR)')
    parser.add_argument('--duration', type=int, help='Initial duration (months)')
    parser.add_argument('--renewable', action='store_true', help='Is renewable')
    parser.add_argument('--max-renewals', type=int, help='Maximum renewals')
    parser.add_argument('--max-duration', type=int, help='Total max duration (months)')
    parser.add_argument('--path-pr', help='Path to permanent residency')
    parser.add_argument('--path-citizenship', help='Path to citizenship')
    parser.add_argument('--years-to-citizenship', type=int, help='Years to citizenship')
    parser.add_argument('--work-rights', help='Work rights')
    parser.add_argument('--family', help='Family inclusion')
    parser.add_argument('--travel-rights', help='Travel rights')
    parser.add_argument('--restrictions', help='Restrictions')
    parser.add_argument('--tax', help='Tax implications')
    parser.add_argument('--policy-changes', help='2025 policy changes')

    args = parser.parse_args()

    result = add_pathway_transaction(
        job_id=args.job_id,
        country=args.country,
        pathway_type=args.type,
        name=args.name,
        source_url=args.source_url,
        source_title=args.source_title,
        source_type=args.source_type,
        credibility=args.credibility,
        official_name=args.official_name,
        description=args.description,
        legal_basis=args.legal_basis,
        min_income=args.min_income,
        min_investment=args.min_investment,
        education_req=args.education_req,
        language_req=args.language_req,
        age_restrictions=args.age_restrictions,
        documents=args.documents,
        process=args.process,
        processing_time=args.processing_time,
        fee=args.fee,
        duration=args.duration,
        renewable=args.renewable,
        max_renewals=args.max_renewals,
        max_duration=args.max_duration,
        path_pr=args.path_pr,
        path_citizenship=args.path_citizenship,
        years_to_citizenship=args.years_to_citizenship,
        work_rights=args.work_rights,
        family=args.family,
        travel_rights=args.travel_rights,
        restrictions=args.restrictions,
        tax=args.tax,
        policy_changes=args.policy_changes,
        artifact_path=args.artifact_path,
        source_description=args.source_description,
        source_excerpt=args.source_excerpt,
        source_relevance=args.source_relevance
    )


if __name__ == '__main__':
    main()
