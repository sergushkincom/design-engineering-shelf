import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check_entries import check_entry, check_readme  # noqa: E402

GOOD_FULL = (
    "**[Refactoring UI](https://example.com/book)** — Adam Wathan · Book · $ · 6 h · "
    "Starter · **Must** — Why it's here, and the caveat."
)
GOOD_SHORT = "**[Impeccable](https://example.com/skill)** — Paul Bakaus · Skill — Testing it next."


class CheckEntryTest(unittest.TestCase):
    def test_good_full_entry(self):
        self.assertEqual(check_entry(GOOD_FULL, full=True), [])

    def test_verdict_with_qualifier(self):
        text = GOOD_FULL.replace("**Must**", "**Skip** for designers")
        self.assertEqual(check_entry(text, full=True), [])

    def test_placeholder(self):
        self.assertEqual(check_entry("*(to add)*", full=True), [])

    def test_missing_field(self):
        text = GOOD_FULL.replace(" · Starter", "")
        self.assertTrue(check_entry(text, full=True))

    def test_bad_values(self):
        text = (
            GOOD_FULL.replace("Book", "Podcast")
            .replace(" $ ", " cheap ")
            .replace("Starter", "Easy")
            .replace("**Must**", "**Great**")
        )
        problems = " ".join(check_entry(text, full=True))
        for word in ("Type", "Price", "Level", "Verdict"):
            self.assertIn(word, problems)

    def test_title_needs_link(self):
        text = GOOD_FULL.replace("[Refactoring UI](https://example.com/book)", "Refactoring UI")
        self.assertTrue(check_entry(text, full=True))

    def test_missing_note(self):
        text = GOOD_FULL.split(" — Why")[0]
        self.assertTrue(check_entry(text, full=True))

    def test_good_short_entry(self):
        self.assertEqual(check_entry(GOOD_SHORT, full=False), [])

    def test_short_entry_with_verdict_fails(self):
        text = GOOD_SHORT.replace("Skill —", "Skill · **Must** —")
        self.assertTrue(check_entry(text, full=False))


class CheckReadmeTest(unittest.TestCase):
    def test_only_entry_sections_are_checked(self):
        readme = "\n".join(
            [
                "## How I pick",
                "- anything goes here",
                "## Books",
                "- " + GOOD_FULL,
                "## Backlog",
                "- " + GOOD_SHORT,
                "## Changelog",
                "- **2026-11** — free text",
            ]
        )
        self.assertEqual(check_readme(readme), [])

    def test_numbered_start_here(self):
        readme = "## Start here\n\n1. *(to add)*\n2. " + GOOD_FULL
        self.assertEqual(check_readme(readme), [])

    def test_reports_line_number(self):
        readme = "## Books\n- **[X](https://x.dev)** — broken"
        errors = check_readme(readme)
        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith("line 2 (Books)"))

    def test_real_readme_passes(self):
        readme = Path(__file__).resolve().parent.parent / "README.md"
        self.assertEqual(check_readme(readme.read_text(encoding="utf-8")), [])


if __name__ == "__main__":
    unittest.main()
