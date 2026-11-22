#!/usr/bin/env python3
"""Check that every shelf entry in README.md follows the format in the Legend.

Full entries (Start here, Books, Courses, Certifications, Skills & prompts,
Talks, People):

    - **[Title](url)** — Author · Type · Price · Time · Level · **Verdict** — Why, and the caveat.

Short entries (Currently, Backlog) have no price, time, level or verdict:

    - **[Title](url)** — Author · Type — Note.

Placeholders like ``- *(to add)*`` are allowed. Exit code 1 on any problem.
Standard library only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TYPES = {"Book", "Course", "Cert", "Skill", "Talk", "Person"}
LEVELS = {"Starter", "Working", "Deep"}
VERDICTS = {"Must", "Worth it", "Skim", "Skip"}
PRICE_RE = re.compile(r"^(Free|\${1,3})(\s|$)")

FULL_SECTIONS = {
    "Start here",
    "Books",
    "Courses",
    "Certifications",
    "Skills & prompts",
    "Talks",
    "People",
}
SHORT_SECTIONS = {"Currently", "Backlog"}

SEP = " — "
LIST_ITEM_RE = re.compile(r"^(?:-|\d+\.)\s+(.*)$")
PLACEHOLDER_RE = re.compile(r"^\*\(to add\)\*$")
TITLE_RE = re.compile(r"^\*\*\[[^\]]+\]\((https?://[^)\s]+)\)\*\*$")
VERDICT_RE = re.compile(r"^\*\*([^*]+)\*\*")


def check_entry(text: str, full: bool) -> list[str]:
    """Return a list of problems for one list item (without the bullet)."""
    if PLACEHOLDER_RE.match(text):
        return []
    parts = text.split(SEP)
    if len(parts) < 3:
        return [f"expected 'Title — meta — note' separated by '{SEP.strip()}'"]
    problems: list[str] = []
    if not TITLE_RE.match(parts[0]):
        problems.append("title must be **[Title](https://…)**")
    meta = [m.strip() for m in parts[1].split(" · ")]
    if not parts[2].strip():
        problems.append("the note after the meta is empty")

    if not full:
        if len(meta) != 2:
            return problems + [f"meta must be 'Author · Type', got {len(meta)} fields"]
        if meta[1] not in TYPES:
            problems.append(f"unknown Type '{meta[1]}'")
        return problems

    if len(meta) != 6:
        return problems + [
            f"meta must be 'Author · Type · Price · Time · Level · **Verdict**', got {len(meta)} fields"
        ]
    author, type_, price, time, level, verdict = meta
    if not author:
        problems.append("Author is empty")
    if type_ not in TYPES:
        problems.append(f"unknown Type '{type_}'")
    if not PRICE_RE.match(price):
        problems.append(f"Price must start with Free, $, $$ or $$$, got '{price}'")
    if not time:
        problems.append("Time is empty")
    if level not in LEVELS:
        problems.append(f"unknown Level '{level}'")
    m = VERDICT_RE.match(verdict)
    if not m or m.group(1) not in VERDICTS:
        problems.append(f"Verdict must be bold Must / Worth it / Skim / Skip, got '{verdict}'")
    return problems


def check_readme(text: str) -> list[str]:
    """Return 'line N: problem' strings for the whole README."""
    errors: list[str] = []
    section: str | None = None
    for n, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## "):
            section = line[3:].strip()
            continue
        if section not in FULL_SECTIONS and section not in SHORT_SECTIONS:
            continue
        m = LIST_ITEM_RE.match(line)
        if not m:
            continue
        for problem in check_entry(m.group(1).strip(), full=section in FULL_SECTIONS):
            errors.append(f"line {n} ({section}): {problem}")
    return errors


def main(argv: list[str]) -> int:
    path = Path(argv[1] if len(argv) > 1 else "README.md")
    errors = check_readme(path.read_text(encoding="utf-8"))
    for e in errors:
        print(f"{path}: {e}")
    if errors:
        print(f"\n{len(errors)} problem(s). See the Legend in README.md for the format.")
        return 1
    print(f"{path}: all entries follow the format.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
