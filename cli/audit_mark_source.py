#!/usr/bin/env python3
"""
Audit Mark Source CLI Tool

Mark a trail entry as a knowledge source and optionally create a source record.
This links audit trail entries to the sources table for provenance tracking.

Usage:
    python cli/audit_mark_source.py --trail-id 123 --source-type official --credibility 5
"""

import sqlite3
import sys
from pathlib import Path

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


def mark_source(
    trail_id: int,
    source_type: str = None,
    credibility: int = None,
    create_source_record: bool = False,
    notes: str = None
) -> None:
    """
    Mark a trail entry as a knowledge source.

    Args:
        trail_id: Trail ID to mark
        source_type: Type of source (for new source records)
        credibility: Credibility rating 1-5 (for new source records)
        create_source_record: If True, create a new source record
        notes: Additional notes
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verify trail exists
        cursor.execute("""
            SELECT id, job_run_id, url, page_title, is_source
            FROM scraper_audit_trail
            WHERE id = ?
        """, (trail_id,))
        trail = cursor.fetchone()

        if not trail:
            print(f"❌ Trail entry {trail_id} not found", file=sys.stderr)
            sys.exit(1)

        if trail['is_source']:
            print(f"⚠️  Trail entry {trail_id} is already marked as a source", file=sys.stderr)

        source_id = None

        # Create source record if requested
        if create_source_record:
            if not trail['url']:
                print(f"❌ Cannot create source record: trail has no URL", file=sys.stderr)
                sys.exit(1)

            if not source_type or not credibility:
                print(f"❌ Must provide --source-type and --credibility to create source record", file=sys.stderr)
                sys.exit(1)

            # Check if source already exists
            cursor.execute("SELECT id FROM sources WHERE url = ?", (trail['url'],))
            existing = cursor.fetchone()

            if existing:
                source_id = existing['id']
                print(f"ℹ️  Source already exists (ID: {source_id})", file=sys.stderr)
            else:
                # Create new source
                cursor.execute("""
                    INSERT INTO sources (
                        url,
                        title,
                        source_type,
                        credibility,
                        last_accessed_date
                    ) VALUES (?, ?, ?, ?, date('now'))
                """, (
                    trail['url'],
                    trail['page_title'] or trail['url'],
                    source_type,
                    credibility
                ))
                source_id = cursor.lastrowid
                print(f"✅ Created source record (ID: {source_id})", file=sys.stderr)

        # Mark trail as source
        cursor.execute("""
            UPDATE scraper_audit_trail
            SET is_source = 1,
                source_id = ?,
                notes = CASE
                    WHEN notes IS NULL THEN ?
                    WHEN ? IS NULL THEN notes
                    ELSE notes || '\n' || ?
                END
            WHERE id = ?
        """, (source_id, notes, notes, notes, trail_id))

        # Update job statistics
        cursor.execute("""
            UPDATE job_run
            SET sources_found = sources_found + 1
            WHERE id = ?
        """, (trail['job_run_id'],))

        conn.commit()

        print(f"✅ Trail entry {trail_id} marked as source", file=sys.stderr)
        if source_id:
            print(f"   Source ID: {source_id}", file=sys.stderr)
        print(f"   URL: {trail['url']}", file=sys.stderr)
        print(f"   Title: {trail['page_title']}", file=sys.stderr)

        # Output source ID to stdout for scripting
        if source_id:
            print(source_id)

    except Exception as e:
        print(f"❌ Error marking source: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Mark a trail entry as a knowledge source',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Simply mark a trail entry as a source
    python cli/audit_mark_source.py --trail-id 123

    # Mark and create a source record
    python cli/audit_mark_source.py \\
        --trail-id 123 \\
        --create-source \\
        --source-type official_government \\
        --credibility 5 \\
        --notes "Official Italy immigration portal"

    # Capture source ID
    source_id=$(python cli/audit_mark_source.py \\
        --trail-id 123 \\
        --create-source \\
        --source-type official_government \\
        --credibility 5)
    echo "Source ID: $source_id"
        """
    )

    parser.add_argument('--trail-id', required=True, type=int, help='Trail ID to mark as source')
    parser.add_argument('--create-source', action='store_true', help='Create a source record')
    parser.add_argument('--source-type', help='Source type (required if --create-source)')
    parser.add_argument('--credibility', type=int, choices=[1, 2, 3, 4, 5],
                       help='Credibility rating 1-5 (required if --create-source)')
    parser.add_argument('--notes', help='Additional notes')

    args = parser.parse_args()

    mark_source(
        trail_id=args.trail_id,
        source_type=args.source_type,
        credibility=args.credibility,
        create_source_record=args.create_source,
        notes=args.notes
    )


if __name__ == '__main__':
    main()
