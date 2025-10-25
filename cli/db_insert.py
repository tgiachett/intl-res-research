#!/usr/bin/env python3
"""
Database Insert CLI Tool

Insert records into the residency research database.

Usage:
    python cli/db_insert.py pathway --country Italy --type digital_nomad --name "Digital Nomad Visa" ...
    python cli/db_insert.py source --url "https://..." --title "..." --credibility 5
    python cli/db_insert.py legal-ref --country Italy --ref-number "Law 123/2025" --title "..."

Examples:
    # Insert a pathway
    python cli/db_insert.py pathway \
        --country Italy \
        --type digital_nomad \
        --name "Digital Nomad Visa" \
        --min-income 28000 \
        --duration 12 \
        --renewable \
        --fee 50

    # Insert a source
    python cli/db_insert.py source \
        --url "https://vistoperitalia.esteri.it" \
        --title "Italy Official Visa Portal" \
        --type official_government \
        --credibility 5 \
        --country Italy

    # Insert a legal reference
    python cli/db_insert.py legal-ref \
        --country Italy \
        --ref-number "Decree 123/2025" \
        --title "Digital Nomad Visa Decree" \
        --type decree \
        --effective-date "2025-01-15"
"""

import sqlite3
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

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
    conn.row_factory = sqlite3.Row
    return conn


def get_country_id(conn: sqlite3.Connection, country_name: str) -> Optional[int]:
    """Get country ID by name"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM countries WHERE name = ?", (country_name,))
    row = cursor.fetchone()
    return row['id'] if row else None


def insert_pathway(args) -> None:
    """Insert a residency pathway"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get country ID
        country_id = get_country_id(conn, args.country)
        if not country_id:
            print(f"❌ Country '{args.country}' not found")
            print("   Available countries: Italy, Denmark, Netherlands, etc.")
            sys.exit(1)

        # Prepare data
        data = {
            'country_id': country_id,
            'pathway_type': args.type,
            'name': args.name,
            'official_name': args.official_name,
            'description': args.description,
            'legal_basis': args.legal_basis,
            'min_income_eur': args.min_income,
            'min_investment_eur': args.min_investment,
            'education_requirement': args.education_req,
            'language_requirement': args.language_req,
            'age_restrictions': args.age_restrictions,
            'required_documents': args.documents,
            'application_process': args.process,
            'processing_time_days': args.processing_time,
            'application_fee_eur': args.fee,
            'initial_duration_months': args.duration,
            'renewable': 1 if args.renewable else 0,
            'max_renewals': args.max_renewals,
            'total_max_duration_months': args.max_duration,
            'path_to_permanent_residency': args.path_pr,
            'path_to_citizenship': args.path_citizenship,
            'min_years_to_citizenship': args.years_to_citizenship,
            'work_rights': args.work_rights,
            'family_inclusion': args.family,
            'travel_rights': args.travel_rights,
            'restrictions': args.restrictions,
            'tax_implications': args.tax,
            'is_active': 1 if not args.inactive else 0,
            'last_verified_date': args.verified_date or datetime.now().strftime('%Y-%m-%d'),
            'policy_changes_2025': args.policy_changes
        }

        # Build query
        columns = [k for k, v in data.items() if v is not None]
        placeholders = ['?' for _ in columns]
        values = [data[k] for k in columns]

        query = f"""
            INSERT INTO residency_pathways ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        cursor.execute(query, values)
        conn.commit()

        pathway_id = cursor.lastrowid
        print(f"✅ Pathway inserted successfully")
        print(f"   ID: {pathway_id}")
        print(f"   Country: {args.country}")
        print(f"   Type: {args.type}")
        print(f"   Name: {args.name}")

    except sqlite3.IntegrityError as e:
        print(f"❌ Error: Pathway already exists or constraint violation")
        print(f"   {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inserting pathway: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def insert_source(args) -> None:
    """Insert a source"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get country ID if specified
        country_id = None
        if args.country:
            country_id = get_country_id(conn, args.country)
            if not country_id:
                print(f"❌ Country '{args.country}' not found")
                sys.exit(1)

        # Prepare data
        data = {
            'url': args.url,
            'title': args.title,
            'source_type': args.source_type,
            'credibility': args.credibility,
            'description': args.description,
            'language': args.language or 'en',
            'country_id': country_id,
            'pathway_type': args.pathway_type,
            'is_active': 1 if not args.inactive else 0,
            'last_accessed_date': datetime.now().strftime('%Y-%m-%d'),
            'last_verified_date': args.verified_date or datetime.now().strftime('%Y-%m-%d'),
            'notes': args.notes
        }

        # Build query
        columns = [k for k, v in data.items() if v is not None]
        placeholders = ['?' for _ in columns]
        values = [data[k] for k in columns]

        query = f"""
            INSERT INTO sources ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        cursor.execute(query, values)
        conn.commit()

        source_id = cursor.lastrowid
        print(f"✅ Source inserted successfully")
        print(f"   ID: {source_id}")
        print(f"   Title: {args.title}")
        print(f"   Type: {args.source_type}")
        print(f"   Credibility: {args.credibility} ⭐")
        print(f"   URL: {args.url}")

    except sqlite3.IntegrityError as e:
        print(f"❌ Error: Source already exists (duplicate URL)")
        print(f"   {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inserting source: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def insert_legal_ref(args) -> None:
    """Insert a legal reference"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get country ID
        country_id = get_country_id(conn, args.country)
        if not country_id:
            print(f"❌ Country '{args.country}' not found")
            sys.exit(1)

        # Prepare data
        data = {
            'country_id': country_id,
            'reference_number': args.ref_number,
            'title': args.title,
            'official_url': args.url,
            'reference_type': args.ref_type,
            'enactment_date': args.enactment_date,
            'effective_date': args.effective_date,
            'expiry_date': args.expiry_date,
            'summary': args.summary,
            'full_text_path': args.full_text_path,
            'language': args.language or 'en'
        }

        # Build query
        columns = [k for k, v in data.items() if v is not None]
        placeholders = ['?' for _ in columns]
        values = [data[k] for k in columns]

        query = f"""
            INSERT INTO legal_references ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        cursor.execute(query, values)
        conn.commit()

        ref_id = cursor.lastrowid
        print(f"✅ Legal reference inserted successfully")
        print(f"   ID: {ref_id}")
        print(f"   Country: {args.country}")
        print(f"   Reference: {args.ref_number}")
        print(f"   Title: {args.title}")

    except sqlite3.IntegrityError as e:
        print(f"❌ Error: Legal reference already exists")
        print(f"   {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inserting legal reference: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def link_pathway_source(args) -> None:
    """Link a pathway to a source"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verify pathway exists
        cursor.execute("SELECT id FROM residency_pathways WHERE id = ?", (args.pathway_id,))
        if not cursor.fetchone():
            print(f"❌ Pathway {args.pathway_id} not found")
            sys.exit(1)

        # Verify source exists
        cursor.execute("SELECT id FROM sources WHERE id = ?", (args.source_id,))
        if not cursor.fetchone():
            print(f"❌ Source {args.source_id} not found")
            sys.exit(1)

        # Insert link
        cursor.execute("""
            INSERT INTO pathway_sources (pathway_id, source_id, relevance_score, excerpt, page_number, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (args.pathway_id, args.source_id, args.relevance or 5, args.excerpt, args.page, args.notes))

        conn.commit()

        print(f"✅ Pathway {args.pathway_id} linked to source {args.source_id}")

    except sqlite3.IntegrityError:
        print(f"❌ Error: Link already exists")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error linking pathway to source: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Insert records into EU Residency Research Database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest='command', help='Insert command')

    # Pathway command
    parser_pathway = subparsers.add_parser('pathway', help='Insert a residency pathway')
    parser_pathway.add_argument('--country', required=True, help='Country name')
    parser_pathway.add_argument('--type', required=True, help='Pathway type')
    parser_pathway.add_argument('--name', required=True, help='Pathway name')
    parser_pathway.add_argument('--official-name', help='Official name')
    parser_pathway.add_argument('--description', help='Description')
    parser_pathway.add_argument('--legal-basis', help='Legal basis (law/regulation)')
    parser_pathway.add_argument('--min-income', type=int, help='Minimum income (EUR)')
    parser_pathway.add_argument('--min-investment', type=int, help='Minimum investment (EUR)')
    parser_pathway.add_argument('--education-req', help='Education requirement')
    parser_pathway.add_argument('--language-req', help='Language requirement')
    parser_pathway.add_argument('--age-restrictions', help='Age restrictions')
    parser_pathway.add_argument('--documents', help='Required documents')
    parser_pathway.add_argument('--process', help='Application process')
    parser_pathway.add_argument('--processing-time', type=int, help='Processing time (days)')
    parser_pathway.add_argument('--fee', type=float, help='Application fee (EUR)')
    parser_pathway.add_argument('--duration', type=int, help='Initial duration (months)')
    parser_pathway.add_argument('--renewable', action='store_true', help='Is renewable')
    parser_pathway.add_argument('--max-renewals', type=int, help='Maximum renewals')
    parser_pathway.add_argument('--max-duration', type=int, help='Total max duration (months)')
    parser_pathway.add_argument('--path-pr', help='Path to permanent residency')
    parser_pathway.add_argument('--path-citizenship', help='Path to citizenship')
    parser_pathway.add_argument('--years-to-citizenship', type=int, help='Years to citizenship')
    parser_pathway.add_argument('--work-rights', help='Work rights')
    parser_pathway.add_argument('--family', help='Family inclusion')
    parser_pathway.add_argument('--travel-rights', help='Travel rights')
    parser_pathway.add_argument('--restrictions', help='Restrictions')
    parser_pathway.add_argument('--tax', help='Tax implications')
    parser_pathway.add_argument('--inactive', action='store_true', help='Mark as inactive')
    parser_pathway.add_argument('--verified-date', help='Last verified date (YYYY-MM-DD)')
    parser_pathway.add_argument('--policy-changes', help='2025 policy changes')

    # Source command
    parser_source = subparsers.add_parser('source', help='Insert a source')
    parser_source.add_argument('--url', required=True, help='Source URL')
    parser_source.add_argument('--title', required=True, help='Source title')
    parser_source.add_argument('--source-type', required=True, help='Source type')
    parser_source.add_argument('--credibility', required=True, type=int, choices=[1, 2, 3, 4, 5], help='Credibility (1-5)')
    parser_source.add_argument('--description', help='Description')
    parser_source.add_argument('--language', help='Language code (default: en)')
    parser_source.add_argument('--country', help='Country name')
    parser_source.add_argument('--pathway-type', help='Pathway type')
    parser_source.add_argument('--inactive', action='store_true', help='Mark as inactive')
    parser_source.add_argument('--verified-date', help='Last verified date (YYYY-MM-DD)')
    parser_source.add_argument('--notes', help='Notes')

    # Legal reference command
    parser_legal = subparsers.add_parser('legal-ref', help='Insert a legal reference')
    parser_legal.add_argument('--country', required=True, help='Country name')
    parser_legal.add_argument('--ref-number', required=True, help='Reference number (e.g., Law 123/2025)')
    parser_legal.add_argument('--title', required=True, help='Title')
    parser_legal.add_argument('--url', help='Official URL')
    parser_legal.add_argument('--ref-type', help='Reference type')
    parser_legal.add_argument('--enactment-date', help='Enactment date (YYYY-MM-DD)')
    parser_legal.add_argument('--effective-date', help='Effective date (YYYY-MM-DD)')
    parser_legal.add_argument('--expiry-date', help='Expiry date (YYYY-MM-DD)')
    parser_legal.add_argument('--summary', help='Summary')
    parser_legal.add_argument('--full-text-path', help='Path to full text PDF/HTML')
    parser_legal.add_argument('--language', help='Language code')

    # Link pathway to source
    parser_link = subparsers.add_parser('link', help='Link a pathway to a source')
    parser_link.add_argument('--pathway-id', required=True, type=int, help='Pathway ID')
    parser_link.add_argument('--source-id', required=True, type=int, help='Source ID')
    parser_link.add_argument('--relevance', type=int, choices=[1, 2, 3, 4, 5], help='Relevance score (1-5)')
    parser_link.add_argument('--excerpt', help='Key excerpt from source')
    parser_link.add_argument('--page', type=int, help='Page number (for PDFs)')
    parser_link.add_argument('--notes', help='Notes')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to handler
    handlers = {
        'pathway': insert_pathway,
        'source': insert_source,
        'legal-ref': insert_legal_ref,
        'link': link_pathway_source,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
