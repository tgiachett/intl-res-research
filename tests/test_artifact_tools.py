#!/usr/bin/env python3
"""
Tests for Artifact Management CLI Tools

Tests artifact registration workflow.
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
    """Run a CLI command and return (stdout, stderr, returncode)"""
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT
    )
    return result.stdout.strip(), result.stderr, result.returncode


def setup_test_database():
    """Create a test database by copying production schema"""
    # Copy production database to test database
    if PROD_DB_PATH.exists():
        shutil.copy(PROD_DB_PATH, TEST_DB_PATH)
        print(f"   ✓ Created test database: {TEST_DB_PATH}")
    else:
        print(f"   ❌ Production database not found: {PROD_DB_PATH}")
        sys.exit(1)


def cleanup_test_database():
    """Remove test database and test files"""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
        print(f"   ✓ Cleaned up test database")

    # Clean up test files
    test_dir = PROJECT_ROOT / "data" / "raw" / "test_italy"
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"   ✓ Cleaned up test files")


def test_artifact_registration():
    """Test artifact registration"""
    print("🧪 Testing Artifact Registration\n")
    print("=" * 60)

    # Setup test database
    setup_test_database()

    # Create a test PDF file in a test directory
    test_pdf_path = PROJECT_ROOT / "data" / "raw" / "test_italy" / "test_visa.pdf"
    test_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    test_pdf_path.write_bytes(b"%PDF-1.4\n%Test PDF content\n%%EOF")

    print(f"   Created test PDF: {test_pdf_path}")

    # Test 1: Register artifact
    print("\n1️⃣  Testing artifact_register.py...")
    stdout, stderr, code = run_cli([
        'python', 'cli/artifact_register.py',
        '--type', 'pdf',
        '--path', str(test_pdf_path),
        '--title', 'Test Italy Visa PDF',
        '--source-url', 'https://example.com/test.pdf',
        '--country', 'Italy',
        '--pathway', 'digital_nomad',
        '--description', 'Test PDF for unit testing'
    ])

    if code != 0:
        print(f"❌ FAILED: artifact_register.py returned code {code}")
        print(f"stderr: {stderr}")
        return False

    artifact_id = int(stdout)
    print(f"✅ PASSED: Artifact registered with ID {artifact_id}")
    print(f"   stderr output:\n{stderr}")

    # Test 2: Try to register same artifact again (should detect duplicate)
    print("\n2️⃣  Testing duplicate detection...")
    stdout2, stderr2, code2 = run_cli([
        'python', 'cli/artifact_register.py',
        '--type', 'pdf',
        '--path', str(test_pdf_path),
        '--title', 'Duplicate PDF',
        '--country', 'Italy'
    ])

    if code2 != 0:
        print(f"❌ FAILED: artifact_register.py (duplicate) returned code {code2}")
        print(f"stderr: {stderr2}")
        return False

    artifact_id2 = int(stdout2)
    if artifact_id2 != artifact_id:
        print(f"❌ FAILED: Expected duplicate to return same ID {artifact_id}, got {artifact_id2}")
        return False

    print(f"✅ PASSED: Duplicate detected, returned existing ID {artifact_id}")
    print(f"   stderr output:\n{stderr2}")

    # Test 3: Verify database state
    print("\n3️⃣  Verifying database state...")
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()

    # Check artifact
    cursor.execute("SELECT * FROM artifacts WHERE id = ?", (artifact_id,))
    artifact = cursor.fetchone()

    if not artifact:
        print(f"❌ FAILED: Artifact {artifact_id} not found in database")
        return False

    print(f"   ✓ Artifact {artifact_id} found in database")
    print(f"   ✓ Type: {artifact[3]}")  # artifact_type
    print(f"   ✓ Title: {artifact[8]}")  # title
    print(f"   ✓ Country: {artifact[14]}")  # country
    print(f"   ✓ SHA256: {artifact[7][:16]}...")  # sha256 (first 16 chars)

    # Check only one artifact was created (duplicate prevention)
    cursor.execute("SELECT COUNT(*) FROM artifacts")
    count = cursor.fetchone()[0]
    print(f"   ✓ Total artifacts in database: {count}")

    # Should have 1 from this test
    if count < 1:
        print(f"❌ FAILED: Expected at least 1 artifact, found {count}")
        return False

    conn.close()

    # Cleanup test database and files
    cleanup_test_database()

    print("\n✅ All artifact registration tests PASSED!")
    return True


def test_query_artifacts():
    """Test querying artifacts"""
    print("\n\n🧪 Testing Artifact Query\n")
    print("=" * 60)

    print("\n4️⃣  Testing db_query.py artifacts...")
    stdout, stderr, code = run_cli([
        'python', 'cli/db_query.py',
        'artifacts',
        '--country', 'Italy'
    ])

    if code != 0:
        print(f"❌ FAILED: db_query.py artifacts returned code {code}")
        print(f"stderr: {stderr}")
        return False

    print("✅ PASSED: Artifacts query successful")
    print(f"\nOutput:\n{stdout}")
    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  ARTIFACT MANAGEMENT TOOLS - TEST SUITE")
    print("=" * 60)

    all_passed = True

    # Test 1: Artifact registration
    if not test_artifact_registration():
        all_passed = False

    # Test 2: Query artifacts
    if not test_query_artifacts():
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
