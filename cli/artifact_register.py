#!/usr/bin/env python3
"""
Artifact Register CLI Tool

Register a downloaded artifact (PDF, HTML, screenshot, etc.) in the database.
Computes SHA256 hash for deduplication and links to audit trail.

Usage:
    python cli/artifact_register.py --type pdf --path "data/raw/italy/visa.pdf" --title "..."
"""

import sqlite3
import sys
import hashlib
import os
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


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of a file"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_mime_type(file_path: Path) -> str:
    """Guess MIME type from file extension"""
    ext = file_path.suffix.lower()
    mime_types = {
        '.pdf': 'application/pdf',
        '.html': 'text/html',
        '.htm': 'text/html',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.zip': 'application/zip',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.txt': 'text/plain',
        '.md': 'text/markdown'
    }
    return mime_types.get(ext, 'application/octet-stream')


def register_artifact(
    artifact_type: str,
    file_path: str,
    title: str,
    trail_id: int = None,
    source_id: int = None,
    source_url: str = None,
    description: str = None,
    country: str = None,
    pathway_type: str = None,
    language: str = 'en'
) -> int:
    """
    Register an artifact in the database.

    Returns:
        artifact_id (int): The ID of the registered artifact
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Resolve file path
        full_path = Path(file_path)
        if not full_path.is_absolute():
            full_path = PROJECT_ROOT / file_path

        if not full_path.exists():
            print(f"❌ File not found: {full_path}", file=sys.stderr)
            sys.exit(1)

        # Get file info
        file_size = full_path.stat().st_size
        file_name = full_path.name
        mime_type = get_mime_type(full_path)

        # Compute hash
        print(f"🔍 Computing SHA256 hash...", file=sys.stderr)
        sha256_hash = compute_sha256(full_path)

        # Check for duplicates
        cursor.execute("SELECT id, file_path FROM artifacts WHERE sha256 = ?", (sha256_hash,))
        existing = cursor.fetchone()

        if existing:
            print(f"⚠️  Artifact already registered (ID: {existing['id']})", file=sys.stderr)
            print(f"   Existing path: {existing['file_path']}", file=sys.stderr)
            print(f"   Duplicate detected via SHA256: {sha256_hash[:16]}...", file=sys.stderr)
            print(existing['id'])  # Output to stdout for scripting
            return existing['id']

        # Make path relative to project root
        try:
            relative_path = full_path.relative_to(PROJECT_ROOT)
        except ValueError:
            relative_path = full_path

        # Insert artifact
        cursor.execute("""
            INSERT INTO artifacts (
                trail_id,
                source_id,
                artifact_type,
                file_path,
                file_name,
                file_size_bytes,
                mime_type,
                sha256,
                title,
                description,
                source_url,
                language,
                downloaded_at,
                extraction_status,
                country,
                pathway_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trail_id,
            source_id,
            artifact_type,
            str(relative_path),
            file_name,
            file_size,
            mime_type,
            sha256_hash,
            title,
            description,
            source_url,
            language,
            datetime.now().isoformat(),
            'pending',
            country,
            pathway_type
        ))

        # Update job statistics if trail_id provided
        if trail_id:
            cursor.execute("""
                SELECT job_run_id FROM scraper_audit_trail WHERE id = ?
            """, (trail_id,))
            result = cursor.fetchone()
            if result:
                job_run_id = result['job_run_id']
                cursor.execute("""
                    UPDATE job_run
                    SET artifacts_downloaded = artifacts_downloaded + 1
                    WHERE id = ?
                """, (job_run_id,))

        conn.commit()
        artifact_id = cursor.lastrowid

        # Print summary
        print(f"✅ Artifact registered successfully", file=sys.stderr)
        print(f"   ID: {artifact_id}", file=sys.stderr)
        print(f"   Type: {artifact_type}", file=sys.stderr)
        print(f"   Title: {title}", file=sys.stderr)
        print(f"   Path: {relative_path}", file=sys.stderr)
        print(f"   Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)", file=sys.stderr)
        print(f"   Hash: {sha256_hash[:16]}...", file=sys.stderr)
        if country:
            print(f"   Country: {country}", file=sys.stderr)

        # Output artifact ID to stdout for scripting
        print(artifact_id)

        return artifact_id

    except Exception as e:
        print(f"❌ Error registering artifact: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Register a downloaded artifact in the database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Register a PDF
    python cli/artifact_register.py \\
        --type pdf \\
        --path "data/raw/italy/2025-10-25_visa_requirements.pdf" \\
        --title "Italy Visa Requirements PDF" \\
        --source-url "https://vistoperitalia.esteri.it/docs/requirements.pdf" \\
        --country Italy

    # Register HTML with trail linking
    python cli/artifact_register.py \\
        --type html \\
        --path "data/raw/denmark/2025-10-25_nyidanmark.html" \\
        --title "Denmark Work Permits" \\
        --trail-id 45 \\
        --country Denmark \\
        --pathway digital_nomad

    # Capture artifact ID
    artifact_id=$(python cli/artifact_register.py \\
        --type pdf \\
        --path "data/raw/italy/visa.pdf" \\
        --title "Italy Visa Info")
    echo "Registered artifact ID: $artifact_id"
        """
    )

    parser.add_argument('--type', required=True,
                       choices=['pdf', 'html', 'screenshot', 'zip', 'doc', 'docx',
                               'extracted_text', 'extracted_table', 'extracted_list'],
                       help='Artifact type')
    parser.add_argument('--path', required=True, help='File path (relative or absolute)')
    parser.add_argument('--title', required=True, help='Artifact title')
    parser.add_argument('--trail-id', type=int, help='Audit trail ID (for linking)')
    parser.add_argument('--source-id', type=int, help='Source ID (for linking)')
    parser.add_argument('--source-url', help='Source URL')
    parser.add_argument('--description', help='Description')
    parser.add_argument('--country', help='Country name')
    parser.add_argument('--pathway', help='Pathway type')
    parser.add_argument('--language', default='en', help='Language code (default: en)')

    args = parser.parse_args()

    register_artifact(
        artifact_type=args.type,
        file_path=args.path,
        title=args.title,
        trail_id=args.trail_id,
        source_id=args.source_id,
        source_url=args.source_url,
        description=args.description,
        country=args.country,
        pathway_type=args.pathway,
        language=args.language
    )


if __name__ == '__main__':
    main()
