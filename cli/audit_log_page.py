#!/usr/bin/env python3
"""
Audit Log Page CLI Tool

Log every page visited, search performed, or web action taken during research.
This creates a complete audit trail for reproducibility.

Usage:
    python cli/audit_log_page.py --job-id 42 --action search --search-query "Italy visa"
    python cli/audit_log_page.py --job-id 42 --action navigate --url "https://..." --title "..."

Returns:
    Trail ID (integer) for referencing this specific action
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


def compute_hash(file_path: str) -> str:
    """Compute SHA256 hash of a file"""
    if not Path(file_path).exists():
        return None

    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def log_page(
    job_id: int,
    action_type: str,
    tool_name: str = None,
    url: str = None,
    search_query: str = None,
    http_status: int = None,
    page_title: str = None,
    page_language: str = None,
    artifact_path: str = None,
    parent_trail_id: int = None,
    session_id: str = None,
    status: str = "success",
    error_message: str = None,
    duration_ms: int = None,
    notes: str = None
) -> int:
    """
    Log a page visit or web action.

    Returns:
        trail_id (int): The ID of the created audit trail entry
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verify job exists
        cursor.execute("SELECT id FROM job_run WHERE id = ?", (job_id,))
        if not cursor.fetchone():
            print(f"❌ Job {job_id} not found", file=sys.stderr)
            print("   Run: python cli/audit_start_job.py --task '...'", file=sys.stderr)
            sys.exit(1)

        # Compute artifact hash if path provided
        artifact_hash = None
        if artifact_path:
            artifact_hash = compute_hash(artifact_path)

        # Insert audit trail entry
        cursor.execute("""
            INSERT INTO scraper_audit_trail (
                job_run_id,
                action_type,
                tool_name,
                url,
                search_query,
                http_status,
                page_title,
                page_language,
                artifact_path,
                artifact_hash,
                parent_trail_id,
                session_id,
                timestamp,
                status,
                error_message,
                duration_ms,
                notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            action_type,
            tool_name,
            url,
            search_query,
            http_status,
            page_title,
            page_language,
            artifact_path,
            artifact_hash,
            parent_trail_id,
            session_id,
            datetime.now().isoformat(),
            status,
            error_message,
            duration_ms,
            notes
        ))

        # Update job statistics
        cursor.execute("""
            UPDATE job_run
            SET pages_visited = pages_visited + 1
            WHERE id = ?
        """, (job_id,))

        conn.commit()
        trail_id = cursor.lastrowid

        # Print to stderr for logging, stdout for scripting
        print(f"✅ Action logged", file=sys.stderr)
        print(f"   Trail ID: {trail_id}", file=sys.stderr)
        print(f"   Job ID: {job_id}", file=sys.stderr)
        print(f"   Action: {action_type}", file=sys.stderr)
        if url:
            print(f"   URL: {url}", file=sys.stderr)
        if search_query:
            print(f"   Search: {search_query}", file=sys.stderr)
        if page_title:
            print(f"   Title: {page_title}", file=sys.stderr)
        print(file=sys.stderr)

        # Output trail ID to stdout for scripting
        print(trail_id)

        return trail_id

    except Exception as e:
        print(f"❌ Error logging page: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Log a page visit or web action for audit trail',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Log a search action
    python cli/audit_log_page.py \\
        --job-id 42 \\
        --action search \\
        --tool brave_web_search \\
        --search-query "Italy digital nomad visa 2025"

    # Log a page navigation
    python cli/audit_log_page.py \\
        --job-id 42 \\
        --action navigate \\
        --tool playwright_navigate \\
        --url "https://vistoperitalia.esteri.it/home/en" \\
        --title "Italy Visa Portal" \\
        --http-status 200 \\
        --artifact-path "data/raw/italy/2025-10-25_vistoperitalia.html"

    # Log with session tracking
    python cli/audit_log_page.py \\
        --job-id 42 \\
        --action fetch \\
        --url "https://example.com" \\
        --session-id "italy-dn-research-001"

    # Capture trail ID for later reference
    trail_id=$(python cli/audit_log_page.py --job-id 42 --action navigate --url "...")
    echo "Trail ID: $trail_id"
        """
    )

    parser.add_argument('--job-id', required=True, type=int, help='Job ID from audit_start_job.py')
    parser.add_argument('--action', required=True,
                       choices=['search', 'fetch', 'navigate', 'click', 'extract', 'screenshot', 'download'],
                       help='Action type')
    parser.add_argument('--tool', help='Tool name (e.g., brave_web_search, playwright_navigate)')
    parser.add_argument('--url', help='URL visited')
    parser.add_argument('--search-query', help='Search query (for search actions)')
    parser.add_argument('--http-status', type=int, help='HTTP status code')
    parser.add_argument('--title', help='Page title')
    parser.add_argument('--language', help='Page language code')
    parser.add_argument('--artifact-path', help='Path to saved artifact (HTML/PDF/screenshot)')
    parser.add_argument('--parent-trail-id', type=int, help='Parent trail ID (for linked actions)')
    parser.add_argument('--session-id', help='Session ID (for grouping related actions)')
    parser.add_argument('--status', default='success', choices=['success', 'error', 'timeout', 'skipped'],
                       help='Action status')
    parser.add_argument('--error', help='Error message (if status=error)')
    parser.add_argument('--duration', type=int, help='Duration in milliseconds')
    parser.add_argument('--notes', help='Additional notes')

    args = parser.parse_args()

    log_page(
        job_id=args.job_id,
        action_type=args.action,
        tool_name=args.tool,
        url=args.url,
        search_query=args.search_query,
        http_status=args.http_status,
        page_title=args.title,
        page_language=args.language,
        artifact_path=args.artifact_path,
        parent_trail_id=args.parent_trail_id,
        session_id=args.session_id,
        status=args.status,
        error_message=args.error,
        duration_ms=args.duration,
        notes=args.notes
    )


if __name__ == '__main__':
    main()
