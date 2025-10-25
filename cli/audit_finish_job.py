#!/usr/bin/env python3
"""
Audit Finish Job CLI Tool

Mark a research job as completed and update final statistics.

Usage:
    python cli/audit_finish_job.py --job-id 42 --status completed
    python cli/audit_finish_job.py --job-id 42 --status failed --error "Network timeout"
"""

import sqlite3
import sys
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


def finish_job(job_id: int, status: str, error_summary: str = None, session_notes: str = None) -> None:
    """
    Mark a job as completed.

    Args:
        job_id: Job ID to finish
        status: Final status (completed, failed, aborted)
        error_summary: Error summary if failed
        session_notes: Final session notes
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verify job exists and is running
        cursor.execute("""
            SELECT id, task_description, status, started_at,
                   pages_visited, sources_found, artifacts_downloaded
            FROM job_run
            WHERE id = ?
        """, (job_id,))
        job = cursor.fetchone()

        if not job:
            print(f"❌ Job {job_id} not found", file=sys.stderr)
            sys.exit(1)

        if job['status'] != 'running':
            print(f"⚠️  Job {job_id} is already {job['status']}", file=sys.stderr)

        # Count errors in audit trail
        cursor.execute("""
            SELECT COUNT(*) as error_count
            FROM scraper_audit_trail
            WHERE job_run_id = ? AND status = 'error'
        """, (job_id,))
        error_count = cursor.fetchone()['error_count']

        # Update job
        cursor.execute("""
            UPDATE job_run
            SET status = ?,
                completed_at = ?,
                error_count = ?,
                error_summary = ?,
                session_notes = CASE
                    WHEN session_notes IS NULL THEN ?
                    WHEN ? IS NULL THEN session_notes
                    ELSE session_notes || '\n' || ?
                END
            WHERE id = ?
        """, (
            status,
            datetime.now().isoformat(),
            error_count,
            error_summary,
            session_notes,
            session_notes,
            session_notes,
            job_id
        ))

        conn.commit()

        # Get updated stats
        cursor.execute("""
            SELECT pages_visited, sources_found, artifacts_downloaded, error_count
            FROM job_run
            WHERE id = ?
        """, (job_id,))
        stats = cursor.fetchone()

        # Calculate duration
        started = datetime.fromisoformat(job['started_at'])
        completed = datetime.now()
        duration = completed - started

        print(f"✅ Job {job_id} marked as {status}", file=sys.stderr)
        print(f"   Task: {job['task_description']}", file=sys.stderr)
        print(f"   Duration: {duration}", file=sys.stderr)
        print(file=sys.stderr)
        print(f"   📊 Statistics:", file=sys.stderr)
        print(f"   Pages visited: {stats['pages_visited']}", file=sys.stderr)
        print(f"   Sources found: {stats['sources_found']}", file=sys.stderr)
        print(f"   Artifacts: {stats['artifacts_downloaded']}", file=sys.stderr)
        print(f"   Errors: {stats['error_count']}", file=sys.stderr)

        if error_summary:
            print(file=sys.stderr)
            print(f"   ❌ Error: {error_summary}", file=sys.stderr)

    except Exception as e:
        print(f"❌ Error finishing job: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Mark a research job as completed',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Mark job as completed
    python cli/audit_finish_job.py --job-id 42 --status completed

    # Mark job as failed with error
    python cli/audit_finish_job.py \\
        --job-id 42 \\
        --status failed \\
        --error "Network timeout after 5 retries"

    # Add session notes
    python cli/audit_finish_job.py \\
        --job-id 42 \\
        --status completed \\
        --notes "Found 3 official sources, downloaded 2 PDFs"
        """
    )

    parser.add_argument('--job-id', required=True, type=int, help='Job ID to finish')
    parser.add_argument('--status', required=True, choices=['completed', 'failed', 'aborted'],
                       help='Final job status')
    parser.add_argument('--error', help='Error summary (if status=failed)')
    parser.add_argument('--notes', help='Session notes')

    args = parser.parse_args()

    finish_job(
        job_id=args.job_id,
        status=args.status,
        error_summary=args.error,
        session_notes=args.notes
    )


if __name__ == '__main__':
    main()
