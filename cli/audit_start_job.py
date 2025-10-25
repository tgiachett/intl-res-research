#!/usr/bin/env python3
"""
Audit Start Job CLI Tool

Start a new scraping/research job and return the job ID for tracking.

Usage:
    python cli/audit_start_job.py --task "Research Italy Digital Nomad Visa" --country Italy

Returns:
    Job ID (integer) that should be used for all subsequent audit logging
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


def start_job(task: str, country: str = None, pathway_type: str = None, llm_model: str = None) -> int:
    """
    Start a new research job.

    Returns:
        job_id (int): The ID of the created job
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO job_run (
                task_description,
                country,
                pathway_type,
                status,
                started_at,
                llm_model
            ) VALUES (?, ?, ?, 'running', ?, ?)
        """, (
            task,
            country,
            pathway_type,
            datetime.now().isoformat(),
            llm_model or "unknown"
        ))

        conn.commit()
        job_id = cursor.lastrowid

        print(f"✅ Job started successfully", file=sys.stderr)
        print(f"   Job ID: {job_id}", file=sys.stderr)
        print(f"   Task: {task}", file=sys.stderr)
        if country:
            print(f"   Country: {country}", file=sys.stderr)
        if pathway_type:
            print(f"   Pathway: {pathway_type}", file=sys.stderr)
        print(file=sys.stderr)
        print(f"   Use this job ID for all audit logging:", file=sys.stderr)
        print(f"   cli/audit_log_page.py --job-id {job_id} ...", file=sys.stderr)
        print(file=sys.stderr)

        # Output just the job ID to stdout for scripting
        print(job_id)

        return job_id

    except Exception as e:
        print(f"❌ Error starting job: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Start a new research job for audit tracking',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Start Italy research job
    python cli/audit_start_job.py --task "Research Italy Digital Nomad Visa" --country Italy

    # Start job and capture ID
    job_id=$(python cli/audit_start_job.py --task "Research Denmark work permits" --country Denmark)
    echo "Job ID: $job_id"

    # Start job with pathway type
    python cli/audit_start_job.py \\
        --task "Research Netherlands highly skilled migrant visa" \\
        --country Netherlands \\
        --pathway digital_nomad
        """
    )

    parser.add_argument('--task', required=True, help='Task description')
    parser.add_argument('--country', help='Country name')
    parser.add_argument('--pathway', help='Pathway type')
    parser.add_argument('--llm-model', help='LLM model name')

    args = parser.parse_args()

    start_job(args.task, args.country, args.pathway, args.llm_model)


if __name__ == '__main__':
    main()
