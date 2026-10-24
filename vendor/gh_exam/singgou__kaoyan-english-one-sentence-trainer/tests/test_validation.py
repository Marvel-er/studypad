from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_artifacts import (  # noqa: E402
    passage_corruption_reasons,
    question_overlap_errors,
    sha256_path,
    vocabulary_input_hash_errors,
)
from validate_corpus import validate  # noqa: E402


class ValidationTests(unittest.TestCase):
    def test_passage_artifact_detector_rejects_noise(self) -> None:
        reasons = passage_corruption_reasons("Valid prose. �i½( - ) (� 14 Jf)^^")
        self.assertIn("replacement_character", reasons)
        self.assertIn("garbled_page_footer", reasons)
        self.assertIn("double_caret_quote_artifact", reasons)

    def test_passage_artifact_detector_rejects_quote_damage(self) -> None:
        self.assertIn(
            "unbalanced_curly_double_quotes",
            passage_corruption_reasons("She said “the evidence remained incomplete."),
        )
        self.assertIn(
            "unbalanced_straight_double_quotes",
            passage_corruption_reasons('She said "the evidence remained incomplete.'),
        )
        self.assertIn(
            "glued_double_quote_boundary",
            passage_corruption_reasons("Evidence“must be checked.”Again, the rule applies."),
        )

    def test_passage_artifact_detector_rejects_missing_layout_boundaries(self) -> None:
        reasons = passage_corruption_reasons(
            "The result.While workers'rights matter, plastics,designed badly fail."
        )
        self.assertIn("missing_space_after_sentence_punctuation", reasons)
        self.assertIn("missing_space_after_comma", reasons)
        self.assertIn("glued_plural_possessive_boundary", reasons)
    def test_passage_artifact_detector_accepts_normalized_punctuation(self) -> None:
        self.assertEqual(
            passage_corruption_reasons(
                "She called these “peculiarities—helping, with a closing quote.”"
            ),
            [],
        )

    def test_empty_corpus_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory(prefix="empty validation ") as temp:
            root = Path(temp)
            corpus = root / "corpus.jsonl"
            corpus.write_text("", encoding="utf-8")
            report = validate(corpus, root, 2018, 2018)
        self.assertFalse(report["valid"])
        self.assertIn("corpus contains no records", report["errors"])

    def test_vocabulary_lineage_hashes_reject_mutated_input(self) -> None:
        with tempfile.TemporaryDirectory(prefix="vocabulary lineage ") as temp:
            root = Path(temp)
            passages = root / "passages.jsonl"
            corpus = root / "corpus.jsonl"
            questions = root / "questions.jsonl"
            for path, text in (
                (passages, "passage\n"),
                (corpus, "sentence\n"),
                (questions, "question\n"),
            ):
                path.write_text(text, encoding="utf-8")
            stats = {
                "input_sha256": {
                    "passage_index_jsonl": sha256_path(passages),
                    "sentence_candidate_corpus_jsonl": sha256_path(corpus),
                    "question_index_jsonl": sha256_path(questions),
                }
            }
            self.assertEqual(
                vocabulary_input_hash_errors(stats, passages, corpus, questions),
                [],
            )
            questions.write_text("mutated\n", encoding="utf-8")
            self.assertEqual(
                vocabulary_input_hash_errors(stats, passages, corpus, questions),
                ["vocabulary_stats: input_sha256 mismatch for question_index_jsonl"],
            )

    def test_multiple_question_fragments_in_article_layers_are_rejected(self) -> None:
        question = {
            "year": 2014,
            "article": "Text 1",
            "question_number": 21,
            "stem": "The proposed policy was intended primarily to improve local participation",
            "options": {
                "A": "encourage residents to join public discussions more actively",
                "B": "reduce the cost of several unrelated national programmes",
                "C": "replace every existing institution with a private organisation",
                "D": "prevent local officials from collecting any public evidence",
            },
        }
        passages = [
            {
                "id": "2014-reading-text1-passage",
                "year": 2014,
                "article": "Text 1",
                "text": (
                    "Authentic prose ends here. The proposed policy was intended primarily to "
                    "improve local participation. Encourage residents to join public discussions "
                    "more actively."
                ),
            }
        ]
        corpus = [
            {
                "id": "2014-reading-text1-tail",
                "year": 2014,
                "article": "Text 1",
                "original": (
                    "The proposed policy was intended primarily to improve local participation, "
                    "and encourage residents to join public discussions more actively."
                ),
            }
        ]
        errors = question_overlap_errors(passages, corpus, [question])
        self.assertTrue(any(error.startswith("passage 2014-reading-text1") for error in errors))
        self.assertTrue(any(error.startswith("corpus 2014-reading-text1") for error in errors))

    def test_single_quoted_question_fragment_is_not_tail_contamination(self) -> None:
        question = {
            "year": 2018,
            "article": "Text 2",
            "question_number": 26,
            "stem": "What does the phrase careful institutional change most probably mean",
            "options": {"A": "One", "B": "Two", "C": "Three", "D": "Four"},
        }
        passages = [
            {
                "id": "2018-reading-text2-passage",
                "year": 2018,
                "article": "Text 2",
                "text": "The phrase careful institutional change most probably means gradual reform.",
            }
        ]
        self.assertEqual(question_overlap_errors(passages, [], [question]), [])


if __name__ == "__main__":
    unittest.main()
