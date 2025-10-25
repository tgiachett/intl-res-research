#!/usr/bin/env python3
"""
Database Query CLI Tool

Query the residency research database with various filters and output formats.

Usage:
    python cli/db_query.py countries
    python cli/db_query.py pathways --country Italy
    python cli/db_query.py sources --credibility 5
    python cli/db_query.py audit-trail --job-id 42

Examples:
    # List all countries
    python cli/db_query.py countries

    # List all pathways for Italy
    python cli/db_query.py pathways --country Italy

    # List digital nomad visas across all countries
    python cli/db_query.py pathways --type digital_nomad

    # List official sources (5-star credibility)
    python cli/db_query.py sources --credibility 5

    # Show audit trail for a specific job
    python cli/db_query.py audit-trail --job-id 42

    # Show all artifacts for Italy
    python cli/db_query.py artifacts --country Italy
"""

import sqlite3
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "database" / "residency.db"


def get_db_connection() -> sqlite3.Connection:
    """Get database connection"""
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        print("   Run: python scripts/db_init.py")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def format_table(rows: List[sqlite3.Row], columns: Optional[List[str]] = None) -> str:
    """Format rows as a table"""
    if not rows:
        return "No results found."

    # Get column names
    if columns is None:
        columns = rows[0].keys()

    # Calculate column widths
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            val = str(row[col]) if row[col] is not None else ""
            widths[col] = max(widths[col], len(val))

    # Build table
    header = " | ".join(col.ljust(widths[col]) for col in columns)
    separator = "-+-".join("-" * widths[col] for col in columns)

    lines = [header, separator]
    for row in rows:
        line = " | ".join(
            str(row[col]).ljust(widths[col]) if row[col] is not None else "".ljust(widths[col])
            for col in columns
        )
        lines.append(line)

    return "\n".join(lines)


def query_countries(args) -> None:
    """List all countries"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            name,
            code,
            CASE WHEN is_eu_member THEN '✓' ELSE '✗' END as EU,
            CASE WHEN is_schengen THEN '✓' ELSE '✗' END as Schengen,
            capital,
            official_language as language,
            currency
        FROM countries
        ORDER BY name
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    print(f"\n📍 Countries ({len(rows)} total)\n")
    print(format_table(rows))
    print()

    conn.close()


def query_pathways(args) -> None:
    """List residency pathways with filters"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Build query
    query = """
        SELECT
            c.name as country,
            p.pathway_type as type,
            p.name,
            p.min_income_eur as income,
            p.initial_duration_months as duration,
            CASE WHEN p.renewable THEN '✓' ELSE '✗' END as renewable,
            p.application_fee_eur as fee,
            CASE WHEN p.is_active THEN '✓' ELSE '✗' END as active
        FROM residency_pathways p
        JOIN countries c ON p.country_id = c.id
    """

    conditions = []
    params = []

    if args.country:
        conditions.append("c.name = ?")
        params.append(args.country)

    if args.type:
        conditions.append("p.pathway_type = ?")
        params.append(args.type)

    if args.active_only:
        conditions.append("p.is_active = 1")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY c.name, p.pathway_type"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    filter_info = []
    if args.country:
        filter_info.append(f"country={args.country}")
    if args.type:
        filter_info.append(f"type={args.type}")

    filter_str = f" ({', '.join(filter_info)})" if filter_info else ""

    print(f"\n🛂 Residency Pathways{filter_str} ({len(rows)} found)\n")
    print(format_table(rows))
    print()

    conn.close()


def query_sources(args) -> None:
    """List sources with filters"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            s.title,
            s.source_type as type,
            s.credibility,
            c.name as country,
            s.url,
            s.last_verified_date as verified
        FROM sources s
        LEFT JOIN countries c ON s.country_id = c.id
    """

    conditions = []
    params = []

    if args.country:
        conditions.append("c.name = ?")
        params.append(args.country)

    if args.credibility:
        conditions.append("s.credibility = ?")
        params.append(args.credibility)

    if args.source_type:
        conditions.append("s.source_type = ?")
        params.append(args.source_type)

    if args.active_only:
        conditions.append("s.is_active = 1")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY s.credibility DESC, c.name"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    filter_info = []
    if args.country:
        filter_info.append(f"country={args.country}")
    if args.credibility:
        filter_info.append(f"credibility={args.credibility}")

    filter_str = f" ({', '.join(filter_info)})" if filter_info else ""

    print(f"\n📚 Sources{filter_str} ({len(rows)} found)\n")
    print(format_table(rows, columns=['title', 'type', 'credibility', 'country', 'verified']))
    print()

    conn.close()


def query_audit_trail(args) -> None:
    """Show audit trail for a job"""
    conn = get_db_connection()
    cursor = conn.cursor()

    if not args.job_id:
        # List recent jobs
        cursor.execute("""
            SELECT
                id,
                task_description as task,
                country,
                status,
                started_at,
                pages_visited,
                sources_found
            FROM job_run
            ORDER BY started_at DESC
            LIMIT 20
        """)
        rows = cursor.fetchall()
        print(f"\n📋 Recent Jobs ({len(rows)} shown)\n")
        print(format_table(rows))
        print("\nUse --job-id N to see detailed audit trail")
    else:
        # Show job details
        cursor.execute("""
            SELECT *
            FROM job_run
            WHERE id = ?
        """, (args.job_id,))
        job = cursor.fetchone()

        if not job:
            print(f"❌ Job {args.job_id} not found")
            conn.close()
            return

        print(f"\n📋 Job #{job['id']}: {job['task_description']}\n")
        print(f"Country: {job['country']}")
        print(f"Status: {job['status']}")
        print(f"Started: {job['started_at']}")
        print(f"Completed: {job['completed_at']}")
        print(f"Pages visited: {job['pages_visited']}")
        print(f"Sources found: {job['sources_found']}")
        print(f"Artifacts: {job['artifacts_downloaded']}")

        # Show trail
        cursor.execute("""
            SELECT
                id,
                action_type,
                tool_name,
                url,
                page_title,
                CASE WHEN is_source THEN '★' ELSE '' END as source,
                status,
                timestamp
            FROM scraper_audit_trail
            WHERE job_run_id = ?
            ORDER BY timestamp
        """, (args.job_id,))
        trail_rows = cursor.fetchall()

        if trail_rows:
            print(f"\n📜 Audit Trail ({len(trail_rows)} actions)\n")
            print(format_table(trail_rows, columns=['id', 'action_type', 'tool_name', 'page_title', 'source', 'status']))
        else:
            print("\nNo audit trail entries found.")

    print()
    conn.close()


def query_artifacts(args) -> None:
    """List artifacts with filters"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            id,
            artifact_type as type,
            title,
            country,
            file_name,
            file_size_bytes / 1024 as size_kb,
            extraction_status as extracted,
            downloaded_at
        FROM artifacts
    """

    conditions = []
    params = []

    if args.country:
        conditions.append("country = ?")
        params.append(args.country)

    if args.artifact_type:
        conditions.append("artifact_type = ?")
        params.append(args.artifact_type)

    if args.extraction_status:
        conditions.append("extraction_status = ?")
        params.append(args.extraction_status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY downloaded_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    filter_info = []
    if args.country:
        filter_info.append(f"country={args.country}")
    if args.artifact_type:
        filter_info.append(f"type={args.artifact_type}")

    filter_str = f" ({', '.join(filter_info)})" if filter_info else ""

    print(f"\n📦 Artifacts{filter_str} ({len(rows)} found)\n")
    print(format_table(rows, columns=['id', 'type', 'title', 'country', 'size_kb', 'extracted']))
    print()

    conn.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Query EU Residency Research Database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', help='Query command')

    # Countries command
    parser_countries = subparsers.add_parser('countries', help='List countries')

    # Pathways command
    parser_pathways = subparsers.add_parser('pathways', help='List residency pathways')
    parser_pathways.add_argument('--country', help='Filter by country name')
    parser_pathways.add_argument('--type', help='Filter by pathway type')
    parser_pathways.add_argument('--active-only', action='store_true', help='Show only active pathways')

    # Sources command
    parser_sources = subparsers.add_parser('sources', help='List sources')
    parser_sources.add_argument('--country', help='Filter by country name')
    parser_sources.add_argument('--credibility', type=int, choices=[1, 2, 3, 4, 5], help='Filter by credibility')
    parser_sources.add_argument('--source-type', help='Filter by source type')
    parser_sources.add_argument('--active-only', action='store_true', help='Show only active sources')

    # Audit trail command
    parser_audit = subparsers.add_parser('audit-trail', help='Show audit trail')
    parser_audit.add_argument('--job-id', type=int, help='Job ID to query')

    # Artifacts command
    parser_artifacts = subparsers.add_parser('artifacts', help='List artifacts')
    parser_artifacts.add_argument('--country', help='Filter by country')
    parser_artifacts.add_argument('--artifact-type', help='Filter by artifact type')
    parser_artifacts.add_argument('--extraction-status', help='Filter by extraction status')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to handler
    handlers = {
        'countries': query_countries,
        'pathways': query_pathways,
        'sources': query_sources,
        'audit-trail': query_audit_trail,
        'artifacts': query_artifacts,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
