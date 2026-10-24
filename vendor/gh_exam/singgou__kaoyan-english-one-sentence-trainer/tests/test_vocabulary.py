from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_vocabulary import (  # noqa: E402
    build_lexicon,
    is_safe,
    occurrences,
    tokenization_input_errors,
)


class VocabularyTests(unittest.TestCase):
    def test_corrupt_source_text_is_rejected_before_tokenization(self) -> None:
        passage = {
            "id": "2021-reading-text1-passage",
            "text": "Genuine prose. �i½( - ) page footer",
            "source_completeness_status": "no_known_gap",
            "safe_for_training": True,
            "known_source_gap": None,
        }
        question = {
            "id": "2021-reading-q21",
            "stem": "What follows?",
            "options": {"A": "One", "B": "Two", "C": "Three", "D": "Four"},
        }
        errors = tokenization_input_errors([passage], [question])
        self.assertEqual(errors, ["2021-reading-text1-passage: corrupt passage text"])

    def test_occurrence_spans_and_scope_coverage_are_exact(self) -> None:
        passage = {
            "id": "2018-reading-text1-passage",
            "year": 2018,
            "article": "Text 1",
            "text": "Evidence supports reading.",
            "source_file": "exam.pdf",
            "source_page_start": 4,
            "text_status": "cross_checked",
            "needs_manual_review": False,
            "source_completeness_status": "no_known_gap",
            "safe_for_training": True,
            "known_source_gap": None,
        }
        question = {
            "id": "2018-reading-q21",
            "year": 2018,
            "article": "Text 1",
            "question_number": 21,
            "stem": "What works?",
            "options": {"A": "Evidence.", "B": "Noise.", "C": "Guessing.", "D": "Nothing."},
            "source_file": "exam.pdf",
            "source_page": 5,
            "text_status": "auto_extracted",
            "needs_manual_review": True,
        }

        rows, coverage = occurrences([passage], [question])
        original = passage["text"]
        passage_rows = [row for row in rows if row["scope"] == "passage_article"]

        self.assertEqual(coverage["passage_article_records_tokenized"], 1)
        self.assertEqual(coverage["question_records_tokenized"], 1)
        self.assertTrue(
            all(original[row["char_start"] : row["char_end"]] == row["surface"] for row in passage_rows)
        )
        evidence = next(item for item in build_lexicon(rows) if item["normalized"] == "evidence")
        self.assertEqual(evidence["occurrence_count"], 2)
        self.assertEqual(evidence["safe_occurrence_count"], 1)
        self.assertEqual(evidence["lemma_status"], "not_computed")

    def test_known_incomplete_passage_is_not_safe_vocabulary_evidence(self) -> None:
        candidate = {
            "text_status": "cross_checked",
            "needs_manual_review": False,
            "safe_for_training": False,
        }
        self.assertFalse(is_safe(candidate))


if __name__ == "__main__":
    unittest.main()
