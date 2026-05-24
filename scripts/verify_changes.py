#!/usr/bin/env python3
"""
verify_changes.py — Pre-commit verification gate for the WordPipe project.

Runs a battery of checks to ensure changes are safe to commit:
  1. ontology_mvp.py output vs baseline (byte-for-byte)
  2. check_rule_test_parity.py exit code
  3. pytest -q tests/
  4. YAML file validation (entities.yaml, relationships.yaml)
  5. Dangling doc link detection
  6. Rollback on failure

Usage:
  python scripts/verify_changes.py
  python scripts/verify_changes.py --skip-rollback   # exit with error instead of rolling back
  python scripts/verify_changes.py --verbose          # detailed logging

Exit codes:
  0 — All checks passed
  1 — One or more checks failed (and rollback was performed or --skip-rollback)
"""

import argparse
import csv
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCRIPTS_DIR = PROJECT_ROOT / "scripts"
ANALYTICS_DIR = PROJECT_ROOT / "analytics" / "ontology" / "mvp"
DOCS_ONTOLOGY_DIR = PROJECT_ROOT / "docs" / "ontology"
LABOR_LEDGER_PATH = PROJECT_ROOT / "docs" / "labor" / "LABOR_LEDGER.md"
ARCHIVE_DIR = PROJECT_ROOT / "archive" / "rollbacks"
GITIGNORE_PATH = PROJECT_ROOT / ".gitignore"

# Files that are known to have been moved/renamed — references to these are
# considered dangling links. Add files here as they are moved during refactoring.
KNOWN_MOVED_FILES: set = {
    # Example: "OLD_NAME.md",
}

# ------------------------------------------------------------------------------
# Logging
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
log = logging.getLogger("verify_changes")


# ------------------------------------------------------------------------------
# Check 1: ontology_mvp.py output vs baseline
# ------------------------------------------------------------------------------


def check_ontology_mvp() -> bool:
    """
    Run scripts/ontology_mvp.py and compare outputs byte-for-byte with
    analytics/ontology/mvp/ baseline files.

    Returns True if all outputs match or the script/baseline doesn't exist yet.
    """
    mvp_script = SCRIPTS_DIR / "ontology_mvp.py"
    if not mvp_script.exists():
        log.warning("SKIP: scripts/ontology_mvp.py not found (not yet implemented).")
        return True

    if not ANALYTICS_DIR.exists():
        log.warning("SKIP: analytics/ontology/mvp/ baseline directory not found.")
        return True

    # Run the script
    log.info("Running scripts/ontology_mvp.py...")
    result = subprocess.run(
        [sys.executable, str(mvp_script)],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        log.error("FAIL: ontology_mvp.py exited with code %d", result.returncode)
        log.error("stderr: %s", result.stderr.strip())
        return False

    # Expected output files
    expected_files = ["corpus.jsonl", "term_frequency.json", "cooccurrence_top100.csv"]
    all_match = True

    for fname in expected_files:
        generated = PROJECT_ROOT / fname
        baseline = ANALYTICS_DIR / fname

        if not generated.exists():
            log.error("FAIL: ontology_mvp.py did not produce %s", fname)
            all_match = False
            continue

        if not baseline.exists():
            log.warning("WARN: No baseline for %s — skipping byte comparison.", fname)
            generated.unlink(missing_ok=True)
            continue

        gen_bytes = generated.read_bytes()
        base_bytes = baseline.read_bytes()

        if gen_bytes == base_bytes:
            log.info("  PASS: %s matches baseline (%d bytes)", fname, len(gen_bytes))
        else:
            log.error(
                "FAIL: %s differs from baseline (%d vs %d bytes)",
                fname, len(gen_bytes), len(base_bytes),
            )
            all_match = False

        # Clean up generated file
        generated.unlink(missing_ok=True)

    return all_match


# ------------------------------------------------------------------------------
# Check 2: check_rule_test_parity.py exit code
# ------------------------------------------------------------------------------


def check_rule_test_parity() -> bool:
    """
    Run scripts/check_rule_test_parity.py and check exit code.

    Expected behaviour:
      - Exit code 0: All Must rules have tests (suspicious but not an error — OK)
      - Exit code 1: Some Must rules lack tests (expected for a project in progress)
      - Any other code or crash: FAIL

    Returns True if the script runs without crashing.
    """
    parity_script = SCRIPTS_DIR / "check_rule_test_parity.py"
    if not parity_script.exists():
        log.warning("SKIP: scripts/check_rule_test_parity.py not found (not yet implemented).")
        return True

    log.info("Running scripts/check_rule_test_parity.py...")
    result = subprocess.run(
        [sys.executable, str(parity_script)],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )

    if result.returncode in (0, 1):
        status = "all rules have tests" if result.returncode == 0 else "some rules lack tests"
        log.info("  PASS: check_rule_test_parity.py exited with code %d (%s)", result.returncode, status)
        return True
    else:
        log.error(
            "FAIL: check_rule_test_parity.py exited with code %d (expected 0 or 1)",
            result.returncode,
        )
        if result.stderr.strip():
            log.error("stderr: %s", result.stderr.strip()[:500])
        return False


# ------------------------------------------------------------------------------
# Check 3: pytest
# ------------------------------------------------------------------------------


def check_pytest() -> bool:
    """
    Run pytest -q tests/ and fail if any test fails.

    Returns True if all tests pass.
    """
    tests_dir = PROJECT_ROOT / "tests"
    if not tests_dir.exists():
        log.warning("SKIP: tests/ directory not found.")
        return True

    log.info("Running pytest -q tests/...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(tests_dir)],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )

    if result.returncode == 0:
        # Extract summary line like "1 passed in 0.12s"
        summary = [l for l in result.stdout.splitlines() if "passed" in l or "failed" in l]
        summary_str = summary[-1] if summary else "all passed"
        log.info("  PASS: %s", summary_str)
        return True
    else:
        log.error("FAIL: pytest exited with code %d", result.returncode)
        # Show last few lines of output
        lines = result.stdout.splitlines()
        for line in lines[-10:]:
            log.error("  %s", line)
        return False


# ------------------------------------------------------------------------------
# Check 4: YAML file validation
# ------------------------------------------------------------------------------


def check_yaml_files() -> bool:
    """
    Validate docs/ontology/entities.yaml and relationships.yaml.

    Returns True if both files are valid YAML (or don't exist yet).
    """
    yaml_files = [
        DOCS_ONTOLOGY_DIR / "entities.yaml",
        DOCS_ONTOLOGY_DIR / "relationships.yaml",
    ]

    all_valid = True
    for yaml_path in yaml_files:
        if not yaml_path.exists():
            log.warning("SKIP: %s not found (not yet created).", yaml_path)
            continue

        try:
            data = yaml_path.read_text(encoding="utf-8")
            parsed = yaml.safe_load(data)
            if parsed is None:
                log.warning("WARN: %s is empty or contains only null.", yaml_path)
            else:
                log.info("  PASS: %s is valid YAML (%s)", yaml_path.name, type(parsed).__name__)
        except yaml.YAMLError as e:
            log.error("FAIL: %s is not valid YAML: %s", yaml_path, e)
            all_valid = False

    return all_valid


# ------------------------------------------------------------------------------
# Check 5: Dangling doc links
# ------------------------------------------------------------------------------


def check_dangling_links() -> bool:
    """
    Scan all .md files for references to known moved files.

    Returns True if no dangling links are found.
    """
    md_files = list(PROJECT_ROOT.rglob("*.md"))

    # Exclude common non-project directories
    excluded_dirs = {
        ".git", "__pycache__", ".venv", "venv", "env", "node_modules",
        "_ARCHIVE", "_WORK", "_INBOX", "_META", "_SECURITY",
    }
    md_files = [
        f for f in md_files
        if not any(part in excluded_dirs for part in f.relative_to(PROJECT_ROOT).parts)
    ]

    found_any = False
    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for moved_file in KNOWN_MOVED_FILES:
            # Look for markdown links, plain references, or file paths
            if moved_file in text:
                rel_path = md_file.relative_to(PROJECT_ROOT)
                log.error("FAIL: %s references moved file '%s'", rel_path, moved_file)
                found_any = True

    if not found_any:
        log.info("  PASS: No dangling links to known moved files.")
        return True
    return False


# ------------------------------------------------------------------------------
# Rollback
# ------------------------------------------------------------------------------


def ensure_archive_in_gitignore() -> None:
    """Ensure archive/ is in .gitignore and any other ignore files."""
    gitignore_paths = [
        PROJECT_ROOT / ".gitignore",
        PROJECT_ROOT / ".gitignore.local",
    ]

    for gi_path in gitignore_paths:
        if not gi_path.exists():
            continue
        content = gi_path.read_text(encoding="utf-8")
        if "archive/" not in content:
            with open(gi_path, "a", encoding="utf-8") as f:
                f.write("\n# Rollback archives\narchive/\n")
            log.info("Added 'archive/' to %s", gi_path.name)


def get_recently_modified_files() -> List[Path]:
    """
    Get list of files modified in the last commit using git diff.

    Returns list of absolute Path objects.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
            timeout=30,
        )
        if result.returncode != 0:
            log.warning("Could not get git diff (no previous commit?). Using empty list.")
            return []

        files = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line:
                full_path = (PROJECT_ROOT / line).resolve()
                if full_path.exists():
                    files.append(full_path)
        return files
    except (subprocess.TimeoutExpired, FileNotFoundError):
        log.warning("git not available or timeout. Using empty file list.")
        return []


def perform_rollback(failed_step: str) -> None:
    """
    Roll back recent changes:
    1. Move modified files to archive/rollbacks/<date>/
    2. Restore from git checkout HEAD
    3. Update LABOR_LEDGER.md

    Args:
        failed_step: Name of the step that failed (for logging).
    """
    log.warning("=== ROLLBACK INITIATED ===")
    log.warning("Failure detected at step: %s", failed_step)

    # Ensure archive/ is in .gitignore
    ensure_archive_in_gitignore()

    # Create rollback directory
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rollback_dir = ARCHIVE_DIR / date_str
    rollback_dir.mkdir(parents=True, exist_ok=True)

    # Get recently modified files
    modified_files = get_recently_modified_files()
    if not modified_files:
        log.warning("No recently modified files found to roll back.")
        return

    # Move files to archive, preserving directory structure
    restored_count = 0
    for file_path in modified_files:
        try:
            rel_path = file_path.relative_to(PROJECT_ROOT)
        except ValueError:
            # File is outside project root — skip
            continue

        # Create target directory in archive
        target_dir = rollback_dir / rel_path.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / rel_path.name

        # Copy to archive first
        shutil.copy2(file_path, target_path)
        log.info("  Archived: %s -> %s", rel_path, target_path.relative_to(PROJECT_ROOT))

        # Restore from git
        try:
            subprocess.run(
                ["git", "checkout", "HEAD", "--", str(file_path)],
                capture_output=True, text=True, cwd=PROJECT_ROOT,
                timeout=30,
                check=True,
            )
            log.info("  Restored: %s", rel_path)
            restored_count += 1
        except subprocess.CalledProcessError as e:
            log.error("  Failed to restore %s: %s", rel_path, e.stderr.strip())
        except subprocess.TimeoutExpired:
            log.error("  Timeout restoring %s", rel_path)

    log.warning("Rollback complete: %d files archived, %d files restored.", len(modified_files), restored_count)

    # Update LABOR_LEDGER.md
    update_labor_ledger(failed_step, date_str, modified_files)


def update_labor_ledger(failed_step: str, date_str: str, files: List[Path]) -> None:
    """
    Append a rollback entry to docs/labor/LABOR_LEDGER.md.

    Creates the file and parent directory if they don't exist.
    """
    LABOR_LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)

    entry = (
        f"\n## Rollback: {date_str}\n\n"
        f"- **Failed step:** {failed_step}\n"
        f"- **Files rolled back:** {len(files)}\n"
        f"- **Archive:** `archive/rollbacks/{date_str}/`\n"
    )

    if not LABOR_LEDGER_PATH.exists():
        header = "# Labor Ledger\n\n_Auto-generated rollback log._\n"
        LABOR_LEDGER_PATH.write_text(header + entry, encoding="utf-8")
        log.info("Created LABOR_LEDGER.md with rollback entry.")
    else:
        with open(LABOR_LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
        log.info("Appended rollback entry to LABOR_LEDGER.md.")


# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pre-commit verification gate for the WordPipe project."
    )
    parser.add_argument(
        "--skip-rollback", action="store_true",
        help="Exit with error instead of rolling back on failure.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging.",
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    log.info("=" * 50)
    log.info("Verification Gate — %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    log.info("=" * 50)

    # Run all checks
    checks: List[Tuple[str, callable]] = [
        ("ontology_mvp.py output vs baseline", check_ontology_mvp),
        ("check_rule_test_parity.py exit code", check_rule_test_parity),
        ("pytest tests/", check_pytest),
        ("YAML file validation", check_yaml_files),
        ("Dangling doc links", check_dangling_links),
    ]

    failures: List[str] = []
    for name, check_fn in checks:
        log.info("")
        log.info("--- Check: %s ---", name)
        try:
            if check_fn():
                log.info("  Result: PASS")
            else:
                log.info("  Result: FAIL")
                failures.append(name)
        except Exception as e:
            log.error("  CRASH: %s — %s", name, e)
            failures.append(name)

    # Summary
    log.info("")
    log.info("=" * 50)
    if not failures:
        log.info("Verification passed — all %d checks OK.", len(checks))
        sys.exit(0)
    else:
        log.error("Verification FAILED — %d/%d checks failed:", len(failures), len(checks))
        for name in failures:
            log.error("  ✗ %s", name)

        if args.skip_rollback:
            log.error("Rollback skipped (--skip-rollback). Exiting with error.")
            sys.exit(1)
        else:
            # Roll back on the first failure
            perform_rollback(failures[0])
            log.error("Rollback complete. Exiting with error.")
            sys.exit(1)


if __name__ == "__main__":
    main()
