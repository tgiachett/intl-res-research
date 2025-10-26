#!/usr/bin/env python3
"""
Tests for Audit Logging CLI Tools

Tests the complete audit workflow:
1. Start job
2. Log pages
3. Mark sources
4. Finish job

Uses a separate test database to avoid polluting production data.
"""

import subprocess
import sqlite3
import tempfile
import shutil
import os
from pathlib import Path
import sys

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
TEST_DB_PATH = PROJECT_ROOT / "data" / "database" / "test_residency.db"
PROD_DB_PATH = PROJECT_ROOT / "data" / "database" / "residency.db"


def run_cli(command: list) -> tuple:
    """
    Run a CLI command and return (stdout, stderr, returncode)
    """
    # Set environment to use test database
    env = os.environ.copy()
    env['TEST_MODE'] = '1'

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        env=env
    )
    return result.stdout.strip(), result.stderr, result.returncode


def setup_test_database():
    """Create a fresh test database"""
    # Run db_init to create test database
    result = subprocess.run(
        ['python', 'scripts/db_init.py', '--db-path', str(TEST_DB_PATH), '--force'],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        print(f"   ❌ Failed to create test database", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    print(f"   ✓ Created fresh test database: {TEST_DB_PATH}")


def cleanup_test_database():
    """Remove test database"""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
        print(f"   ✓ Cleaned up test database")

    # Clean up test artifacts
    test_artifact = PROJECT_ROOT / "data" / "raw" / "test_page.html"
    if test_artifact.exists():
        test_artifact.unlink()
        print(f"   ✓ Cleaned up test artifact")


def test_audit_workflow():
    """Test complete audit workflow"""
    print("🧪 Testing Audit Workflow\n")
    print("=" * 60)

    # Setup test database
    setup_test_database()

    # Test 1: Start a job
    print("\n1️⃣  Testing audit_start_job.py...")
    stdout, stderr, code = run_cli([
        'python', 'cli/audit_start_job.py',
        '--task', 'Test Italy Research',
        '--country', 'Italy',
        '--pathway', 'digital_nomad'
    ])

    if code != 0:
        print(f"❌ FAILED: audit_start_job.py returned code {code}")
        print(f"stderr: {stderr}")
        return False

    job_id = int(stdout)
    print(f"✅ PASSED: Job created with ID {job_id}")
    print(f"   stderr output:\n{stderr}")

    # Test 2: Log a search action
    print("\n2️⃣  Testing audit_log_page.py (search)...")
    stdout, stderr, code = run_cli([
        'python', 'cli/audit_log_page.py',
        '--job-id', str(job_id),
        '--action', 'search',
        '--tool', 'brave_web_search',
        '--search-query', 'Italy digital nomad visa 2025'
    ])

    if code != 0:
        print(f"❌ FAILED: audit_log_page.py (search) returned code {code}")
        print(f"stderr: {stderr}")
        return False

    trail_id_1 = int(stdout)
    print(f"✅ PASSED: Search logged with trail ID {trail_id_1}")

    # Test 3: Log a navigation action
    print("\n3️⃣  Testing audit_log_page.py (navigate)...")

    # Create a test HTML artifact
    test_artifact_path = PROJECT_ROOT / "data" / "raw" / "test_page.html"
    test_artifact_path.parent.mkdir(parents=True, exist_ok=True)
    test_artifact_path.write_text("<html><body>Test</body></html>")

    stdout, stderr, code = run_cli([
        'python', 'cli/audit_log_page.py',
        '--job-id', str(job_id),
        '--action', 'navigate',
        '--tool', 'playwright_navigate',
        '--url', 'https://vistoperitalia.esteri.it',
        '--title', 'Italy Visa Portal',
        '--http-status', '200',
        '--artifact-path', str(test_artifact_path)
    ])

    if code != 0:
        print(f"❌ FAILED: audit_log_page.py (navigate) returned code {code}")
        print(f"stderr: {stderr}")
        return False

    trail_id_2 = int(stdout)
    print(f"✅ PASSED: Navigation logged with trail ID {trail_id_2}")

    # Test 4: Mark as source
    print("\n4️⃣  Testing audit_mark_source.py...")
    stdout, stderr, code = run_cli([
        'python', 'cli/audit_mark_source.py',
        '--trail-id', str(trail_id_2),
        '--create-source',
        '--source-type', 'official_government',
        '--credibility', '5',
        '--notes', 'Official Italy immigration portal'
    ])

    if code != 0:
        print(f"❌ FAILED: audit_mark_source.py returned code {code}")
        print(f"stderr: {stderr}")
        return False

    source_id = int(stdout) if stdout else None
    print(f"✅ PASSED: Trail marked as source (source ID: {source_id})")
    print(f"   stderr output:\n{stderr}")

    # Test 5: Finish job
    print("\n5️⃣  Testing audit_finish_job.py...")
    stdout, stderr, code = run_cli([
        'python', 'cli/audit_finish_job.py',
        '--job-id', str(job_id),
        '--status', 'completed',
        '--notes', 'Test job completed successfully'
    ])

    if code != 0:
        print(f"❌ FAILED: audit_finish_job.py returned code {code}")
        print(f"stderr: {stderr}")
        return False

    print(f"✅ PASSED: Job finished")
    print(f"   stderr output:\n{stderr}")

    # Test 6: Verify database state
    print("\n6️⃣  Verifying database state...")
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()

    # Check job_run
    cursor.execute("SELECT * FROM job_run WHERE id = ?", (job_id,))
    job = cursor.fetchone()
    if not job:
        print(f"❌ FAILED: Job {job_id} not found in database")
        return False

    print(f"   ✓ Job {job_id} found in database")
    print(f"   ✓ Status: {job[4]}")  # status column
    print(f"   ✓ Pages visited: {job[7]}")  # pages_visited column
    print(f"   ✓ Sources found: {job[8]}")  # sources_found column

    # Check audit trail
    cursor.execute("SELECT COUNT(*) FROM scraper_audit_trail WHERE job_run_id = ?", (job_id,))
    trail_count = cursor.fetchone()[0]
    print(f"   ✓ Audit trail entries: {trail_count}")

    if trail_count != 2:
        print(f"❌ FAILED: Expected 2 trail entries, found {trail_count}")
        return False

    # Check source was marked
    cursor.execute("""
        SELECT COUNT(*) FROM scraper_audit_trail
        WHERE job_run_id = ? AND is_source = 1
    """, (job_id,))
    source_count = cursor.fetchone()[0]
    print(f"   ✓ Marked sources: {source_count}")

    if source_count != 1:
        print(f"❌ FAILED: Expected 1 marked source, found {source_count}")
        return False

    # Check source record was created
    if source_id:
        cursor.execute("SELECT * FROM sources WHERE id = ?", (source_id,))
        source = cursor.fetchone()
        if not source:
            print(f"❌ FAILED: Source {source_id} not found in database")
            return False
        print(f"   ✓ Source record created (ID: {source_id})")

    conn.close()

    # Cleanup test database and files
    cleanup_test_database()

    print("\n✅ All audit workflow tests PASSED!")
    return True


def test_query_audit_trail():
    """Test querying the audit trail"""
    print("\n\n🧪 Testing Audit Trail Query\n")
    print("=" * 60)

    print("\n7️⃣  Testing db_query.py audit-trail...")
    stdout, stderr, code = run_cli([
        'python', 'cli/db_query.py',
        'audit-trail'
    ])

    if code != 0:
        print(f"❌ FAILED: db_query.py audit-trail returned code {code}")
        print(f"stderr: {stderr}")
        return False

    print("✅ PASSED: Audit trail query successful")
    print(f"\nOutput:\n{stdout}")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  AUDIT LOGGING TOOLS - TEST SUITE")
    print("=" * 60)

    all_passed = True

    # Test 1: Audit workflow
    if not test_audit_workflow():
        all_passed = False

    # Test 2: Query audit trail
    if not test_query_audit_trail():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
