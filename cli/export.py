#!/usr/bin/env python3
"""
Export CLI Tool

Export data from database to various formats, including generating
human-readable markdown files for the Obsidian knowledge base.

DATABASE IS SOURCE OF TRUTH - This tool generates markdown from DB.

Usage:
    python cli/export.py pathway Italy digital_nomad --format obsidian
    python cli/export.py country Italy --format obsidian
    python cli/export.py all-pathways --format obsidian --overwrite

Examples:
    # Export single pathway to markdown
    python cli/export.py pathway Italy digital_nomad --format obsidian

    # Export all Italy pathways
    python cli/export.py country Italy --format obsidian --overwrite

    # Export all pathways for all countries
    python cli/export.py all-pathways --format obsidian --overwrite
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "data" / "database" / "residency.db"
VAULT_PATH = PROJECT_ROOT / "docs" / "vault"


def get_db_connection() -> sqlite3.Connection:
    """Get database connection"""
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}", file=sys.stderr)
        print("   Run: python scripts/db_init.py", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_pathway_sources(conn: sqlite3.Connection, pathway_id: int) -> list:
    """Get all sources linked to a pathway"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            s.id,
            s.url,
            s.title,
            s.source_type,
            s.credibility,
            ps.excerpt,
            ps.relevance_score
        FROM pathway_sources ps
        JOIN sources s ON ps.source_id = s.id
        WHERE ps.pathway_id = ?
        ORDER BY s.credibility DESC, ps.relevance_score DESC
    """, (pathway_id,))
    return cursor.fetchall()


def generate_pathway_markdown(pathway: sqlite3.Row, sources: list) -> str:
    """
    Generate Obsidian-compatible markdown for a pathway.

    DATABASE IS SOURCE OF TRUTH - this is generated from DB data.
    """

    # Build markdown
    md = []

    # Header
    md.append(f"# {pathway['name']}")
    md.append("")
    md.append(f"**Country**: 🇮🇹 {pathway['country_name']}")
    md.append(f"**Type**: {pathway['pathway_type']}")
    md.append(f"**Status**: {'✅ Active' if pathway['is_active'] else '❌ Inactive'}")
    if pathway['official_name']:
        md.append(f"**Official Name**: {pathway['official_name']}")
    md.append(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}")
    md.append(f"**Generated from Database**: Pathway ID {pathway['id']}")
    md.append("")
    md.append("---")
    md.append("")

    # Overview
    md.append("## Overview")
    md.append("")
    if pathway['description']:
        md.append(pathway['description'])
    md.append("")

    if pathway['legal_basis']:
        md.append(f"**Legal Basis**: {pathway['legal_basis']}")
        md.append("")

    md.append("---")
    md.append("")

    # Requirements
    md.append("## Requirements")
    md.append("")

    if pathway['min_income_eur']:
        md.append(f"### Financial")
        md.append(f"- **Minimum Income**: €{pathway['min_income_eur']:,}/year")
        md.append("")

    if pathway['min_investment_eur']:
        md.append(f"### Investment")
        md.append(f"- **Minimum Investment**: €{pathway['min_investment_eur']:,}")
        md.append("")

    if pathway['education_requirement']:
        md.append(f"### Education")
        md.append(f"- {pathway['education_requirement']}")
        md.append("")

    if pathway['language_requirement']:
        md.append(f"### Language")
        md.append(f"- {pathway['language_requirement']}")
        md.append("")

    if pathway['age_restrictions']:
        md.append(f"### Age")
        md.append(f"- {pathway['age_restrictions']}")
        md.append("")

    if pathway['required_documents']:
        md.append(f"### Required Documents")
        md.append(f"{pathway['required_documents']}")
        md.append("")

    md.append("---")
    md.append("")

    # Application Process
    if pathway['application_process']:
        md.append("## Application Process")
        md.append("")
        md.append(pathway['application_process'])
        md.append("")

        if pathway['processing_time_days']:
            md.append(f"**Processing Time**: {pathway['processing_time_days']} days")
            md.append("")

        if pathway['application_fee_eur']:
            md.append(f"**Application Fee**: €{pathway['application_fee_eur']}")
            md.append("")

        md.append("---")
        md.append("")

    # Duration & Renewal
    md.append("## Duration & Renewal")
    md.append("")

    if pathway['initial_duration_months']:
        md.append(f"- **Initial Duration**: {pathway['initial_duration_months']} months ({pathway['initial_duration_months']//12} year{'s' if pathway['initial_duration_months']//12 != 1 else ''})")

    if pathway['renewable']:
        md.append(f"- **Renewable**: Yes")
        if pathway['max_renewals']:
            md.append(f"- **Max Renewals**: {pathway['max_renewals']}")
        if pathway['total_max_duration_months']:
            md.append(f"- **Total Max Duration**: {pathway['total_max_duration_months']} months")
    else:
        md.append(f"- **Renewable**: No")

    md.append("")

    if pathway['path_to_permanent_residency']:
        md.append(f"**Path to Permanent Residency**: {pathway['path_to_permanent_residency']}")
        md.append("")

    if pathway['path_to_citizenship']:
        md.append(f"**Path to Citizenship**: {pathway['path_to_citizenship']}")
        if pathway['min_years_to_citizenship']:
            md.append(f"- Typically {pathway['min_years_to_citizenship']} years")
        md.append("")

    md.append("---")
    md.append("")

    # Rights & Restrictions
    md.append("## Rights & Restrictions")
    md.append("")

    if pathway['work_rights']:
        md.append(f"### Work Rights")
        md.append(f"{pathway['work_rights']}")
        md.append("")

    if pathway['family_inclusion']:
        md.append(f"### Family")
        md.append(f"{pathway['family_inclusion']}")
        md.append("")

    if pathway['travel_rights']:
        md.append(f"### Travel")
        md.append(f"{pathway['travel_rights']}")
        md.append("")

    if pathway['restrictions']:
        md.append(f"### Restrictions")
        md.append(f"{pathway['restrictions']}")
        md.append("")

    md.append("---")
    md.append("")

    # Tax Implications
    if pathway['tax_implications']:
        md.append("## Tax Implications")
        md.append("")
        md.append(pathway['tax_implications'])
        md.append("")
        md.append("---")
        md.append("")

    # Policy Changes
    if pathway['policy_changes_2025']:
        md.append("## 2025 Policy Changes")
        md.append("")
        md.append(pathway['policy_changes_2025'])
        md.append("")
        md.append("---")
        md.append("")

    # Sources
    if sources:
        md.append("## Sources")
        md.append("")
        for idx, source in enumerate(sources, 1):
            md.append(f"{idx}. **{source['title']}**")
            md.append(f"   - URL: {source['url']}")
            md.append(f"   - Type: {source['source_type']}")
            md.append(f"   - Credibility: {'⭐' * source['credibility']} ({source['credibility']}/5)")
            if source['relevance_score']:
                md.append(f"   - Relevance: {source['relevance_score']}/5")
            if source['excerpt']:
                md.append(f"   - Excerpt: \"{source['excerpt']}\"")
            md.append("")

        md.append("---")
        md.append("")

    # Metadata
    md.append("## Metadata")
    md.append("")
    md.append(f"- **Database ID**: {pathway['id']}")
    md.append(f"- **Last Verified**: {pathway['last_verified_date'] or 'N/A'}")
    md.append(f"- **Created**: {pathway['created_at']}")
    md.append(f"- **Updated**: {pathway['updated_at']}")
    md.append("")

    # Tags
    md.append("---")
    md.append("")
    md.append(f"**Tags**: #{pathway['country_name'].lower().replace(' ', '-')} #{pathway['pathway_type'].replace('_', '-')} #residency #visa")

    return "\n".join(md)


def export_pathway(country: str, pathway_type: str, output_path: str = None, overwrite: bool = False) -> None:
    """Export a single pathway to markdown"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get pathway with country name
        cursor.execute("""
            SELECT p.*, c.name as country_name
            FROM residency_pathways p
            JOIN countries c ON p.country_id = c.id
            WHERE c.name = ? AND p.pathway_type = ?
        """, (country, pathway_type))

        pathway = cursor.fetchone()

        if not pathway:
            print(f"❌ Pathway not found: {country} / {pathway_type}", file=sys.stderr)
            sys.exit(1)

        # Get sources
        sources = get_pathway_sources(conn, pathway['id'])

        # Generate markdown
        markdown = generate_pathway_markdown(pathway, sources)

        # Determine output path
        if not output_path:
            filename = f"{pathway['name'].replace('/', '_').replace(' ', '_')}.md"
            output_path = VAULT_PATH / "Countries" / country / filename
        else:
            output_path = Path(output_path)

        # Check if exists
        if output_path.exists() and not overwrite:
            print(f"⚠️  File exists: {output_path}", file=sys.stderr)
            print(f"   Use --overwrite to replace", file=sys.stderr)
            sys.exit(1)

        # Write file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown)

        print(f"✅ Exported pathway to {output_path}", file=sys.stderr)
        print(f"   Country: {country}", file=sys.stderr)
        print(f"   Type: {pathway_type}", file=sys.stderr)
        print(f"   Name: {pathway['name']}", file=sys.stderr)
        print(f"   Size: {len(markdown)} bytes", file=sys.stderr)
        print(f"   Sources: {len(sources)}", file=sys.stderr)

        # Output path for scripting
        print(output_path)

    finally:
        conn.close()


def generate_country_index(country: str, pathways: list, country_info: sqlite3.Row) -> str:
    """Generate country index/README from database"""
    md = []

    # Header
    md.append(f"# {country} - Residency & Citizenship Pathways")
    md.append("")
    md.append(f"**EU Member**: {'✅ Yes' if country_info['is_eu_member'] else '❌ No'}")
    md.append(f"**Schengen**: {'✅ Yes' if country_info['is_schengen'] else '❌ No'}")
    md.append(f"**Capital**: {country_info['capital']}")
    md.append(f"**Language**: {country_info['official_language']}")
    md.append(f"**Currency**: {country_info['currency']}")
    md.append(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}")
    md.append(f"**Generated from Database**")
    md.append("")
    md.append("---")
    md.append("")

    # Pathways overview
    md.append(f"## Residency Pathways ({len(pathways)} documented)")
    md.append("")

    for pathway in pathways:
        filename = f"{pathway['name'].replace('/', '_').replace(' ', '_')}.md"
        md.append(f"### [{pathway['name']}]({filename})")
        md.append(f"- **Type**: {pathway['pathway_type']}")
        md.append(f"- **Status**: {'✅ Active' if pathway['is_active'] else '❌ Inactive'}")
        if pathway['min_income_eur']:
            md.append(f"- **Min Income**: €{pathway['min_income_eur']:,}/year")
        if pathway['min_investment_eur']:
            md.append(f"- **Min Investment**: €{pathway['min_investment_eur']:,}")
        if pathway['initial_duration_months']:
            md.append(f"- **Duration**: {pathway['initial_duration_months']} months")
        md.append("")

    md.append("---")
    md.append("")

    # Quick comparison table
    md.append("## Quick Comparison")
    md.append("")
    md.append("| Pathway | Min Income/Investment | Duration | Renewable |")
    md.append("|---------|----------------------|----------|-----------|")

    for pathway in pathways:
        amount = ""
        if pathway['min_income_eur']:
            amount = f"€{pathway['min_income_eur']:,}/yr"
        elif pathway['min_investment_eur']:
            amount = f"€{pathway['min_investment_eur']:,}"

        duration = f"{pathway['initial_duration_months']} mo" if pathway['initial_duration_months'] else "N/A"
        renewable = "✅" if pathway['renewable'] else "❌"

        md.append(f"| {pathway['name']} | {amount} | {duration} | {renewable} |")

    md.append("")
    md.append("---")
    md.append("")

    # Add sources summary
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT s.*
        FROM sources s
        WHERE s.country_id = ?
        ORDER BY s.credibility DESC, s.title
    """, (country_info['id'],))

    country_sources = cursor.fetchall()
    conn.close()

    if country_sources:
        md.append("## All Sources")
        md.append("")

        # Group by credibility
        by_credibility = {}
        for source in country_sources:
            cred = source['credibility']
            if cred not in by_credibility:
                by_credibility[cred] = []
            by_credibility[cred].append(source)

        for cred in sorted(by_credibility.keys(), reverse=True):
            md.append(f"### {'⭐' * cred} ({cred}/5) - {len(by_credibility[cred])} source(s)")
            md.append("")
            for source in by_credibility[cred]:
                md.append(f"- **{source['title']}**")
                md.append(f"  - URL: {source['url']}")
                md.append(f"  - Type: {source['source_type']}")
                if source['last_verified_date']:
                    md.append(f"  - Last Verified: {source['last_verified_date']}")
                md.append("")

        md.append("---")
        md.append("")

    md.append(f"**Generated from Database** - Country ID: {country_info['id']}")
    md.append(f"**Tags**: #{country.lower().replace(' ', '-')} #overview #index")

    return "\n".join(md)


def export_country(country: str, overwrite: bool = False) -> None:
    """Export all pathways for a country AND generate index"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get country info
        cursor.execute("SELECT * FROM countries WHERE name = ?", (country,))
        country_info = cursor.fetchone()

        if not country_info:
            print(f"❌ Country not found: {country}", file=sys.stderr)
            sys.exit(1)

        # Get all pathways for country
        cursor.execute("""
            SELECT p.*, c.name as country_name
            FROM residency_pathways p
            JOIN countries c ON p.country_id = c.id
            WHERE c.name = ?
            ORDER BY p.pathway_type
        """, (country,))

        pathways = cursor.fetchall()

        if not pathways:
            print(f"❌ No pathways found for {country}", file=sys.stderr)
            sys.exit(1)

        print(f"📤 Exporting {len(pathways)} pathways for {country}...\n", file=sys.stderr)

        # Export individual pathways
        exported = []
        for pathway in pathways:
            try:
                export_pathway(country, pathway['pathway_type'], overwrite=overwrite)
                exported.append(pathway['pathway_type'])
            except Exception as e:
                print(f"❌ Error exporting {pathway['pathway_type']}: {e}", file=sys.stderr)

        # Generate country index
        print(f"\n📋 Generating country index...", file=sys.stderr)
        index_md = generate_country_index(country, pathways, country_info)
        index_path = VAULT_PATH / "Countries" / country / "README.md"

        if index_path.exists() and not overwrite:
            print(f"⚠️  Index exists: {index_path}", file=sys.stderr)
            print(f"   Use --overwrite to replace", file=sys.stderr)
        else:
            index_path.write_text(index_md)
            print(f"✅ Generated country index: {index_path}", file=sys.stderr)

        print(f"\n✅ Exported {len(exported)} pathways + index for {country}", file=sys.stderr)

    finally:
        conn.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Export data from database to various formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', help='Export command')

    # Pathway command
    parser_pathway = subparsers.add_parser('pathway', help='Export single pathway')
    parser_pathway.add_argument('country', help='Country name')
    parser_pathway.add_argument('pathway_type', help='Pathway type')
    parser_pathway.add_argument('--format', default='obsidian', choices=['obsidian', 'json', 'csv'],
                                help='Output format')
    parser_pathway.add_argument('--output', help='Output path (default: auto-generate)')
    parser_pathway.add_argument('--overwrite', action='store_true', help='Overwrite existing files')

    # Country command
    parser_country = subparsers.add_parser('country', help='Export all pathways for a country')
    parser_country.add_argument('country', help='Country name')
    parser_country.add_argument('--format', default='obsidian', choices=['obsidian', 'json', 'csv'],
                                help='Output format')
    parser_country.add_argument('--overwrite', action='store_true', help='Overwrite existing files')

    # All pathways command
    parser_all = subparsers.add_parser('all-pathways', help='Export all pathways for all countries')
    parser_all.add_argument('--format', default='obsidian', choices=['obsidian', 'json', 'csv'],
                           help='Output format')
    parser_all.add_argument('--overwrite', action='store_true', help='Overwrite existing files')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to handler
    if args.command == 'pathway':
        export_pathway(args.country, args.pathway_type, args.output, args.overwrite)
    elif args.command == 'country':
        export_country(args.country, args.overwrite)
    elif args.command == 'all-pathways':
        # Get all countries
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM countries ORDER BY name")
        countries = cursor.fetchall()
        conn.close()

        print(f"📤 Exporting pathways for {len(countries)} countries...\n", file=sys.stderr)

        for country_row in countries:
            try:
                export_country(country_row['name'], args.overwrite)
            except SystemExit:
                # No pathways for this country, skip
                pass

        print(f"\n✅ Export complete", file=sys.stderr)
    else:
        print(f"❌ Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
