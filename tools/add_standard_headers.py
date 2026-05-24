"""
Add standard Jalali-date headers to Python source files.

Standard header format:
    # wordpipe/<module_path>.py
    # Created/Modified: YYYY-MM-DD (Jalali: YYYY/MM/DD)
    # Purpose: <one-line description>

Usage:
    python tools/add_standard_headers.py [--dry-run] [--path <path>]

Dependencies: stdlib only.
"""
# tools/add_standard_headers.py
# Created: 2026-05-18 (Jalali: 1405/02/28)
# Modified: 2026-05-18 (Jalali: 1405/02/28)
# Purpose: Add standard Jalali-date headers to Python source files.


from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
import sys
from pathlib import Path


# Jalali date conversion (algorithm from tools/jalali.py)
def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    """Convert Gregorian year/month/day to Jalali (Shamsi) date.

    Uses the algorithm from tools/jalali.py (Birashk method).
    Tested: 2026-02-14 -> 1404-11-25
    """
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621

    gy2 = gy + 1 if gm > 2 else gy
    days = (
        365 * gy
        + (gy2 + 3) // 4
        - (gy2 + 99) // 100
        + (gy2 + 399) // 400
        - 80
        + gd
        + g_d_m[gm - 1]
    )

    jy += 33 * (days // 12053)
    days %= 12053

    jy += 4 * (days // 1461)
    days %= 1461

    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365

    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)

    return jy, jm, jd


def get_git_first_commit_date(filepath: str | Path) -> tuple[int, int, int] | None:
    """Get the first commit date for a file via git log."""
    try:
        result = subprocess.run(
            ["git", "log", "--follow", "--format=%ai", "--diff-filter=A", str(filepath)],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            date_str = result.stdout.strip().split("\n")[-1].split()[0]
            parts = date_str.split("-")
            return (int(parts[0]), int(parts[1]), int(parts[2]))
    except Exception:
        pass
    return None


def get_git_last_modified_date(filepath: str | Path) -> tuple[int, int, int] | None:
    """Get the last commit date for a file via git log."""
    try:
        result = subprocess.run(
            ["git", "log", "--follow", "--format=%ai", "-1", str(filepath)],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            date_str = result.stdout.strip().split()[0]
            parts = date_str.split("-")
            return (int(parts[0]), int(parts[1]), int(parts[2]))
    except Exception:
        pass
    return None


def format_jalali(gy: int, gm: int, gd: int) -> str:
    """Format a Gregorian date as Jalali string."""
    jy, jm, jd = gregorian_to_jalali(gy, gm, gd)
    return f"{jy:04d}/{jm:02d}/{jd:02d}"


def format_gregorian(gy: int, gm: int, gd: int) -> str:
    """Format as YYYY-MM-DD."""
    return f"{gy:04d}-{gm:02d}-{gd:02d}"


STANDARD_HEADER_TEMPLATE = """# {rel_path}
# Created: {created_greg} (Jalali: {created_jalali})
# Modified: {modified_greg} (Jalali: {modified_jalali})
# Purpose: {purpose}
"""


HEADER_REGEX = re.compile(
    r'^(""".*?"""\s*\n)?'  # Optional docstring
    r'(#.*?\n)*',  # Any number of existing comment headers
    re.DOTALL,
)


def detect_purpose(filepath: str | Path) -> str:
    """Detect file purpose from its content."""
    content = Path(filepath).read_text(encoding="utf-8")
    rel = str(filepath).replace("\\", "/")

    # Try docstring
    docstring_match = re.match(r'^\s*"""(.+?)"""', content, re.DOTALL)
    if docstring_match:
        first_line = docstring_match.group(1).strip().split("\n")[0]
        if len(first_line) < 80:
            return first_line

    # Try existing # comments
    for line in content.split("\n")[:5]:
        line = line.strip()
        if line.startswith("# ") and "file:" not in line and "Created" not in line and "Modified" not in line and "Purpose" not in line:
            return line[2:].strip()

    # Use filename
    return f"{Path(filepath).name} — see docstring for details"


def add_header(filepath: str | Path, repo_root: Path | None = None, dry_run: bool = False) -> bool:
    """Add or update standard header in a Python file. Returns True if changed."""
    filepath = Path(filepath)
    # Compute relative path
    if repo_root:
        try:
            rel = filepath.relative_to(repo_root).as_posix()
        except ValueError:
            rel = filepath.name
    else:
        try:
            rel = filepath.relative_to(Path.cwd()).as_posix()
        except ValueError:
            rel = filepath.name
    content = filepath.read_text(encoding="utf-8")

    # Get dates
    created_git = get_git_first_commit_date(filepath)
    modified_git = get_git_last_modified_date(filepath)

    fs_mtime = datetime.datetime.fromtimestamp(filepath.stat().st_mtime)
    fs_mtime_g = (fs_mtime.year, fs_mtime.month, fs_mtime.day)

    created_g = created_git or fs_mtime_g
    modified_g = modified_git or fs_mtime_g

    purpose = detect_purpose(filepath)

    header = STANDARD_HEADER_TEMPLATE.format(
        rel_path=rel,
        created_greg=format_gregorian(*created_g),
        created_jalali=format_jalali(*created_g),
        modified_greg=format_gregorian(*modified_g),
        modified_jalali=format_jalali(*modified_g),
        purpose=purpose,
    )

    # Strategy: find and replace ALL occurrences of our header pattern.
    # Some files may have duplicate headers from previous runs.
    header_pattern = re.compile(
        r'^# .+?\n# Created: .+?\n# Modified: .+?\n# Purpose: .+?\n',
        re.MULTILINE,
    )

    new_content, count = header_pattern.subn(header, content)
    if count > 0:
        if new_content != content:
            if not dry_run:
                filepath.write_text(new_content, encoding="utf-8")
                print(f"  UPDATED header: {rel}")
            else:
                print(f"  WOULD UPDATE header: {rel}")
            return True
        return False

    # No existing header — insert after docstring or at top
    docstring_match = re.match(r'^(""".*?""")\s*\n?', content, re.DOTALL)
    if docstring_match:
        docstring = docstring_match.group(1)
        rest = content[docstring_match.end():]
        new_content = docstring + "\n" + header + "\n" + rest.lstrip()
    else:
        new_content = header + "\n" + content

    if new_content != content:
        if not dry_run:
            filepath.write_text(new_content, encoding="utf-8")
            print(f"  ADDED header: {rel}")
        else:
            print(f"  WOULD ADD header: {rel}")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Add standard Jalali-date headers to Python files.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be changed without modifying.")
    parser.add_argument("--path", default=".", help="Root path to scan (default: current directory).")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    print(f"Scanning {root} for Python files...")

    changed = 0
    skipped = 0
    for pyfile in sorted(root.rglob("*.py")):
        rel = pyfile.relative_to(root)
        # Skip __pycache__, .git, _WORK, legacy snapshot copies
        if any(
            part in pyfile.parts
            for part in ("__pycache__", ".git", "_WORK", "save ", "save")
        ):
            continue
        # Skip legacy archive copies
        if "legacy" in pyfile.parts and "1404" in str(pyfile):
            continue

        try:
            if add_header(str(pyfile), repo_root=root, dry_run=args.dry_run):
                changed += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  ERROR {rel}: {e}")

    print(f"\nDone. {changed} files changed, {skipped} files skipped.")


if __name__ == "__main__":
    main()
