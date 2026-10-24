from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analyze_corpus import analyze as analyze_corpus  # noqa: E402
from analyze_corpus import default_output_paths  # noqa: E402
from analyze_corpus import markdown_report as corpus_markdown  # noqa: E402
from analyze_exam_points import analyze as analyze_exam_points  # noqa: E402
from analyze_exam_points import markdown_report as exam_markdown  # noqa: E402


def corpus_record(*, safe: bool = False) -> dict[str, object]:
    return {
        "id": "2026-reading-text2-example",
        "year": 2026,
        "article": "Text 2",
        "original": "The available source text is incomplete.",
        "word_count": 7,
        "difficulty": 1,
        "grammar_tags": [],
        "vocabulary_tags": [],
        "text_status": "auto_extracted",
        "needs_manual_review": True,
        "safe_for_training": safe,
        "source_completeness_status": "known_incomplete_source",
        "known_source_gap": {
            "description": "The supplied PDF omits a paragraph used by Question 28.",
            "evidence_source": "exam.pdf",
            "evidence_pages": [9],
        },
    }


class AnalysisBoundaryTests(unittest.TestCase):
    def test_reviewed_cli_uses_distinct_default_outputs(self) -> None:
        full_json, full_markdown = default_output_paths(False)
        reviewed_json, reviewed_markdown = default_output_paths(True)
        self.assertNotEqual(full_json, reviewed_json)
        self.assertNotEqual(full_markdown, reviewed_markdown)
        self.assertEqual(reviewed_json.name, "corpus_stats_reviewed.json")
        self.assertEqual(reviewed_markdown.name, "corpus-insights-reviewed.md")

    def test_reviewed_report_retains_full_source_gap_boundary(self) -> None:
        full = [corpus_record()]
        reviewed = [
            {
                **corpus_record(safe=True),
                "id": "2024-reading-text1-example",
                "year": 2024,
                "article": "Text 1",
                "source_completeness_status": "no_known_gap",
                "known_source_gap": None,
                "text_status": "cross_checked",
                "needs_manual_review": False,
            }
        ]
        stat = analyze_corpus(reviewed, source_records=full + reviewed)
        self.assertEqual(
            stat["source_completeness"]["known_incomplete_article_ids"],
            ["2026-reading-text2-passage"],
        )
        self.assertIn("2026-reading-text2-passage", corpus_markdown(stat))

    def test_exam_report_discloses_incomplete_article(self) -> None:
        question = {
            "id": "2026-reading-q28",
            "year": 2026,
            "question_number": 28,
            "question_type": "reason_or_cause",
            "anchor_type": "implicit_local",
            "logic_signals": ["cause"],
            "text_status": "cross_checked",
            "needs_manual_review": False,
            "stem": "Why did the change occur?",
        }
        answer = {"year": 2026, "question_number": 28, "answer": "A"}
        stat = analyze_exam_points([question], [corpus_record()], [answer])
        self.assertEqual(
            stat["coverage"]["known_incomplete_article_ids"],
            ["2026-reading-text2-passage"],
        )
        report = exam_markdown(stat)
        self.assertIn("2026-reading-text2-passage", report)
        self.assertIn("不会推断或补写真文", report)


if __name__ == "__main__":
    unittest.main()
