"""Check the learner-source exclusions independently of HTML generation."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = [ROOT / "README.md", *sorted((ROOT / "labs").glob("*.md"))]
MARKER = re.compile(
    r"^<!-- presentation-exclude-(start|end): ([A-Z0-9]+(?:-[A-Z0-9]+)*) -->$"
)
BLOCK = re.compile(
    r"^<!-- presentation-exclude-start: ([A-Z0-9]+(?:-[A-Z0-9]+)*) -->\n"
    r"(.*?)"
    r"^<!-- presentation-exclude-end: \1 -->$",
    re.MULTILINE | re.DOTALL,
)
SCREENSHOT = re.compile(r"!\[[^\]]*\]\(([^)]*assets/screenshots/[^)]+)\)")
UNCONFIRMED = re.compile(
    r"未確認|未検証|未実施|原因未特定|未実証|確認できていません|"
    r"検証していません|原因.{0,8}特定されていません"
)

def presentation_source(path):
    source = path.read_text(encoding="utf-8")
    if path.name == "README.md":
        source = source.split("## 配備とAIエージェント向けプロンプト", 1)[0]
    return source


class PresentationExclusionSourceTests(unittest.TestCase):
    def test_markers_are_unique_balanced_and_registered(self):
        ids = []
        for path in SOURCES:
            active = None
            for line in path.read_text(encoding="utf-8").splitlines():
                if "presentation-exclude-" not in line:
                    continue
                marker = MARKER.fullmatch(line)
                self.assertIsNotNone(marker, f"{path}: malformed marker {line}")
                kind, identifier = marker.groups()
                if kind == "start":
                    self.assertIsNone(active, f"{path}: nested marker")
                    self.assertNotIn(identifier, ids, f"duplicate ID: {identifier}")
                    ids.append(identifier)
                    active = identifier
                else:
                    self.assertEqual(active, identifier, f"{path}: mismatched end")
                    active = None
            self.assertIsNone(active, f"{path}: unclosed marker")
        registry = (ROOT / "docs" / "UNCONFIRMED-ITEMS-JA.md").read_text(
            encoding="utf-8"
        )
        headings = re.findall(r"^### ([A-Z0-9-]+)$", registry, re.MULTILINE)
        self.assertTrue(ids)
        self.assertCountEqual(ids, headings)

    def test_exclusions_leave_all_screenshots_and_no_unconfirmed_terms(self):
        original_images = []
        included_images = []
        for path in SOURCES:
            source = path.read_text(encoding="utf-8")
            for block in BLOCK.finditer(source):
                self.assertNotRegex(
                    block[2], SCREENSHOT, f"{path}: image inside {block[1]}"
                )
            included = BLOCK.sub("", source)
            self.assertNotRegex(
                BLOCK.sub("", presentation_source(path)), UNCONFIRMED, str(path)
            )
            original_images.extend(SCREENSHOT.findall(source))
            included_images.extend(SCREENSHOT.findall(included))
        self.assertEqual(len(original_images), 578)
        self.assertEqual(original_images, included_images)

    def test_real_plan_parts_are_excluded_as_complete_sections(self):
        path = ROOT / "labs" / "09-variance-analyst.md"
        source = path.read_text(encoding="utf-8")
        blocks = {match[1]: match[2] for match in BLOCK.finditer(source)}
        self.assertIn("## 4. Part 1", blocks["LAB09-PART1-PROCEDURE"])
        self.assertIn("4. 選択した全キー", blocks["LAB09-PART1-PROCEDURE"])
        self.assertIn("## 5. Part 2", blocks["LAB09-PART2-PROCEDURE"])
        self.assertIn("6. 列契約に合わせて15列", blocks["LAB09-PART2-PROCEDURE"])
        included = BLOCK.sub("", source)
        self.assertNotIn("## 4. Part 1", included)
        self.assertNotIn("## 5. Part 2", included)
        self.assertIn("SQLCandidatesFailedFilterError", included)
        self.assertIn("Q4cはPeriodKey別の3つの合計だけを尋ねて成功しました。", included)


if __name__ == "__main__":
    unittest.main()
