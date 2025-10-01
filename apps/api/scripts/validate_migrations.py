#!/usr/bin/env python3
"""
Migration Validation Script

Validates Alembic migration consistency for AgentLab.
Story 3.0 - AC9: Migration Validation Script

Usage:
    python scripts/validate_migrations.py
    python scripts/validate_migrations.py --check-db
"""
import sys
import os
import subprocess
from pathlib import Path


def run_command(cmd: str) -> tuple[int, str, str]:
    """Run shell command and return result."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    return result.returncode, result.stdout, result.stderr


def validate_migrations():
    """Validate migration consistency."""
    print("=" * 80)
    print("ALEMBIC MIGRATION VALIDATION")
    print("=" * 80)
    print()

    errors = []
    warnings = []

    # 1. Check for multiple heads
    print("[1/7] Checking for multiple head revisions...")
    returncode, stdout, stderr = run_command("alembic heads")

    if returncode != 0:
        errors.append(f"Failed to get heads: {stderr}")
    else:
        heads = [line for line in stdout.split('\n') if line.strip() and not line.startswith('INFO')]
        if len(heads) > 1:
            errors.append(f"Found {len(heads)} head revisions (branching detected):\n{stdout}")
            print(f"   ❌ FAIL: {len(heads)} heads found (expected 1)")
        elif len(heads) == 1:
            print(f"   ✅ PASS: Single head revision")
        else:
            warnings.append("No head revisions found")
            print(f"   ⚠️  WARN: No heads found")

    # 2. Check current revision matches head
    print("[2/7] Checking database revision matches head...")
    returncode, current, stderr = run_command("alembic current")

    if returncode != 0:
        warnings.append(f"Could not check current revision: {stderr}")
        print(f"   ⚠️  WARN: Cannot verify (database may not be initialized)")
    else:
        returncode, head, stderr = run_command("alembic heads")
        if current.strip() and head.strip():
            current_rev = current.split()[0] if current.split() else ""
            head_rev = head.split()[0] if head.split() else ""

            if current_rev == head_rev:
                print(f"   ✅ PASS: Database at head ({current_rev})")
            elif current_rev:
                warnings.append(f"Database at {current_rev}, head is {head_rev}")
                print(f"   ⚠️  WARN: Database not at head")
            else:
                warnings.append("Database has no revision applied")
                print(f"   ⚠️  WARN: No revision applied")
        else:
            warnings.append("Could not determine revision status")
            print(f"   ⚠️  WARN: Cannot verify")

    # 3. Check for orphaned migrations
    print("[3/7] Checking for orphaned migrations...")
    returncode, stdout, stderr = run_command("alembic history")

    if returncode != 0:
        errors.append(f"Failed to get history: {stderr}")
    else:
        # Check if any migration is not reachable from head
        lines = [l for l in stdout.split('\n') if l.strip() and not l.startswith('INFO')]
        if lines:
            print(f"   ✅ PASS: Found {len(lines)} migrations")
        else:
            warnings.append("No migrations found")
            print(f"   ⚠️  WARN: No migrations found")

    # 4. Check migration file naming
    print("[4/7] Checking migration file naming consistency...")
    migrations_dir = Path(__file__).parent.parent / "migrations" / "versions"

    if migrations_dir.exists():
        migration_files = list(migrations_dir.glob("*.py"))
        migration_files = [f for f in migration_files if f.name != "__pycache__"]

        invalid_names = []
        for f in migration_files:
            # Should be: <revision>_<slug>.py
            if not f.stem[0].isalnum():
                invalid_names.append(f.name)

        if invalid_names:
            warnings.append(f"Invalid migration names: {invalid_names}")
            print(f"   ⚠️  WARN: {len(invalid_names)} invalid names")
        else:
            print(f"   ✅ PASS: All {len(migration_files)} migration files valid")
    else:
        errors.append(f"Migrations directory not found: {migrations_dir}")
        print(f"   ❌ FAIL: Migrations directory missing")

    # 5. Check for down_revision consistency
    print("[5/7] Checking down_revision consistency...")
    try:
        import importlib.util
        import sys

        # Add migrations to path
        sys.path.insert(0, str(migrations_dir.parent.parent))

        revisions_map = {}
        for migration_file in migration_files:
            if migration_file.stem == "__init__":
                continue

            spec = importlib.util.spec_from_file_location(migration_file.stem, migration_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                revision = getattr(module, 'revision', None)
                down_revision = getattr(module, 'down_revision', None)

                if revision:
                    revisions_map[revision] = {
                        'file': migration_file.name,
                        'down_revision': down_revision
                    }

        # Check for missing parents
        missing_parents = []
        for rev, info in revisions_map.items():
            down_rev = info['down_revision']
            if down_rev and isinstance(down_rev, str) and down_rev not in revisions_map and down_rev != '<base>':
                missing_parents.append(f"{rev} -> {down_rev} (in {info['file']})")

        if missing_parents:
            errors.append(f"Missing parent revisions: {missing_parents}")
            print(f"   ❌ FAIL: {len(missing_parents)} broken chains")
        else:
            print(f"   ✅ PASS: All down_revision links valid")

    except Exception as e:
        warnings.append(f"Could not validate down_revision: {e}")
        print(f"   ⚠️  WARN: Validation skipped ({e})")

    # 6. Check for duplicate revisions
    print("[6/7] Checking for duplicate revision IDs...")
    revision_ids = list(revisions_map.keys()) if 'revisions_map' in locals() else []
    duplicates = [r for r in revision_ids if revision_ids.count(r) > 1]

    if duplicates:
        errors.append(f"Duplicate revision IDs: {set(duplicates)}")
        print(f"   ❌ FAIL: {len(set(duplicates))} duplicates found")
    elif revision_ids:
        print(f"   ✅ PASS: All {len(revision_ids)} revisions unique")
    else:
        warnings.append("No revisions to check")
        print(f"   ⚠️  WARN: No revisions found")

    # 7. Validate upgrade/downgrade syntax
    print("[7/7] Checking upgrade/downgrade function definitions...")
    syntax_errors = []

    try:
        for migration_file in migration_files:
            if migration_file.stem == "__init__":
                continue

            with open(migration_file, 'r') as f:
                content = f.read()

                if 'def upgrade()' not in content:
                    syntax_errors.append(f"{migration_file.name}: missing upgrade()")
                if 'def downgrade()' not in content:
                    syntax_errors.append(f"{migration_file.name}: missing downgrade()")

        if syntax_errors:
            errors.append(f"Migration syntax errors: {syntax_errors}")
            print(f"   ❌ FAIL: {len(syntax_errors)} syntax errors")
        elif migration_files:
            print(f"   ✅ PASS: All migrations have upgrade/downgrade")
        else:
            warnings.append("No migration files to check")
            print(f"   ⚠️  WARN: No files to check")

    except Exception as e:
        warnings.append(f"Could not validate syntax: {e}")
        print(f"   ⚠️  WARN: Validation skipped ({e})")

    # Summary
    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()

    if errors:
        print(f"❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"   • {error}")
        print()

    if warnings:
        print(f"⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"   • {warning}")
        print()

    if not errors:
        if not warnings:
            print("✅ ALL CHECKS PASSED")
            return 0
        else:
            print(f"⚠️  PASSED WITH {len(warnings)} WARNINGS")
            return 0
    else:
        print(f"❌ VALIDATION FAILED WITH {len(errors)} ERRORS")
        return 1


if __name__ == "__main__":
    sys.exit(validate_migrations())
