#!/usr/bin/env python3
"""
Database Initialization Script

Creates the SQLite database and initializes it with the schema.
Also populates initial data for the 15 priority countries.

Usage:
    python scripts/db_init.py [--db-path PATH] [--force]

Options:
    --db-path PATH    Path to database file (default: data/database/residency.db)
    --force           Overwrite existing database
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
SCHEMA_PATH = PROJECT_ROOT / "config" / "schema.sql"
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "database" / "residency.db"


def init_database(db_path: Path, force: bool = False) -> bool:
    """
    Initialize the database with schema and seed data.

    Args:
        db_path: Path to the database file
        force: If True, overwrite existing database

    Returns:
        True if successful, False otherwise
    """
    # Check if database already exists
    if db_path.exists() and not force:
        print(f"❌ Database already exists at {db_path}")
        print("   Use --force to overwrite")
        return False

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Delete existing database if force=True
    if db_path.exists() and force:
        print(f"⚠️  Deleting existing database at {db_path}")
        db_path.unlink()

    # Read schema
    if not SCHEMA_PATH.exists():
        print(f"❌ Schema file not found at {SCHEMA_PATH}")
        return False

    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()

    # Create database and execute schema
    print(f"📦 Creating database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        print("📝 Executing schema...")
        cursor.executescript(schema_sql)
        conn.commit()
        print("✅ Schema created successfully")

        # Insert seed data
        print("🌱 Inserting seed data...")
        insert_seed_data(cursor)
        conn.commit()
        print("✅ Seed data inserted successfully")

        # Verify
        verify_database(cursor)

        print(f"\n✅ Database initialized successfully at {db_path}")
        return True

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def insert_seed_data(cursor: sqlite3.Cursor):
    """Insert initial data for 15 priority countries"""

    countries_data = [
        # (name, code, is_eu, is_schengen, capital, language, currency, immigration_website)
        ('Italy', 'IT', 1, 1, 'Rome', 'Italian', 'EUR', 'https://vistoperitalia.esteri.it'),
        ('Denmark', 'DK', 1, 1, 'Copenhagen', 'Danish', 'DKK', 'https://www.nyidanmark.dk'),
        ('Netherlands', 'NL', 1, 1, 'Amsterdam', 'Dutch', 'EUR', 'https://ind.nl'),
        ('Greece', 'GR', 1, 1, 'Athens', 'Greek', 'EUR', 'https://www.migrationsystem.gr'),
        ('Norway', 'NO', 0, 1, 'Oslo', 'Norwegian', 'NOK', 'https://www.udi.no'),  # NOT EU
        ('Sweden', 'SE', 1, 1, 'Stockholm', 'Swedish', 'SEK', 'https://www.migrationsverket.se'),
        ('Switzerland', 'CH', 0, 1, 'Bern', 'German/French/Italian', 'CHF', 'https://www.sem.admin.ch'),  # NOT EU
        ('France', 'FR', 1, 1, 'Paris', 'French', 'EUR', 'https://www.service-public.fr'),
        ('Spain', 'ES', 1, 1, 'Madrid', 'Spanish', 'EUR', 'https://www.inclusion.gob.es'),
        ('Portugal', 'PT', 1, 1, 'Lisbon', 'Portuguese', 'EUR', 'https://www.sef.pt'),
        ('Germany', 'DE', 1, 1, 'Berlin', 'German', 'EUR', 'https://www.bamf.de'),
        ('Belgium', 'BE', 1, 1, 'Brussels', 'Dutch/French/German', 'EUR', 'https://dofi.ibz.be'),
        ('Ireland', 'IE', 1, 0, 'Dublin', 'English/Irish', 'EUR', 'https://www.irishimmigration.ie'),  # NOT Schengen
        ('Austria', 'AT', 1, 1, 'Vienna', 'German', 'EUR', 'https://www.migration.gv.at'),
        ('Czech Republic', 'CZ', 1, 1, 'Prague', 'Czech', 'CZK', 'https://www.mvcr.cz'),
    ]

    cursor.executemany("""
        INSERT INTO countries (name, code, is_eu_member, is_schengen, capital,
                             official_language, currency, immigration_website)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, countries_data)

    print(f"   ✓ Inserted {len(countries_data)} countries")


def verify_database(cursor: sqlite3.Cursor):
    """Verify database was created correctly"""

    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    expected_tables = [
        'countries', 'residency_pathways', 'sources', 'documents', 'pathway_sources',
        'legal_references', 'scraping_jobs', 'companies',
        'job_run', 'tool_call', 'scraper_audit_trail',
        'artifacts', 'knowledge_artifacts',
        'schema_version'
    ]

    print(f"\n📊 Verification:")
    print(f"   Tables created: {len(tables)}")

    for table in expected_tables:
        if table in tables:
            print(f"   ✓ {table}")
        else:
            print(f"   ✗ {table} (MISSING)")

    # Check countries
    cursor.execute("SELECT COUNT(*) FROM countries")
    count = cursor.fetchone()[0]
    print(f"\n   Countries: {count} / 15")

    # Check schema version
    cursor.execute("SELECT version, description FROM schema_version")
    version, desc = cursor.fetchone()
    print(f"   Schema version: {version}")
    print(f"   Description: {desc}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Initialize EU Residency Research Database')
    parser.add_argument(
        '--db-path',
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f'Path to database file (default: {DEFAULT_DB_PATH})'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing database'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("EU Residency Research - Database Initialization")
    print("=" * 60)
    print()

    success = init_database(args.db_path, args.force)

    if success:
        print("\n🎉 Database is ready to use!")
        print(f"\nLocation: {args.db_path}")
        print("\nNext steps:")
        print("  1. Use CLI tools to query: python cli/db_query.py")
        print("  2. Insert pathways: python cli/db_insert.py")
        print("  3. Start research: python cli/audit_start_job.py --task '...'")
        sys.exit(0)
    else:
        print("\n❌ Database initialization failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
