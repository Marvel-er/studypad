from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_question_index import (  # noqa: E402
    _parse_explicit,
    apply_reviewed_corrections,
    classify_question,
    extract_questions,
)
from extract_sentences import Block  # noqa: E402


class QuestionIndexTests(unittest.TestCase):
    def test_fullwidth_and_combined_option_markers_are_split(self) -> None:
        records = _parse_explicit(
            [
                Block("21. What is the text mainly about?", page=3),
                Block("［A］Alpha [ B] Beta [C] Gamma [ D] Delta", page=3),
            ],
            [21],
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["options"], {"A": "Alpha", "B": "Beta", "C": "Gamma", "D": "Delta"})

    def test_part_b_stops_the_last_question_and_corrupt_tail_is_truncated(self) -> None:
        records = _parse_explicit(
            [
                Block("40. What is the best title?", page=10),
                Block("[A] Alpha", page=10),
                Block("[B] Beta", page=10),
                Block("[C] Gamma", page=10),
                Block("[D] Delta � broken page footer", page=10),
                Block("Part .B Directions: Questions 41-45", page=11),
                Block("[A] This must not be appended.", page=11),
            ],
            [40],
        )
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["options"]["D"], "Delta")
        self.assertTrue(records[0]["extraction_warnings"])
        self.assertNotIn("Part", " ".join(records[0]["options"].values()))

    def test_garbled_footer_prefix_is_removed_before_replacement_marker(self) -> None:
        records = _parse_explicit(
            [
                Block("30. What is the text centered on?", page=7),
                Block("[A] Alpha", page=7),
                Block("[B] Beta", page=7),
                Block("[C] Gamma", page=7),
                Block("[D] Delta *i½(-)-ii\\:M . 6. (� 14 Jf)", page=7),
            ],
            [30],
        )
        self.assertEqual(records[0]["options"]["D"], "Delta")
        self.assertIn(
            "truncated_garbled_page_footer_tail",
            records[0]["extraction_warnings"],
        )

    def test_standalone_pdf_footer_blocks_are_discarded(self) -> None:
        for footer in (
            "*i½(-)-ii\\:M . 6. (� 14 Jf)",
            "�i¼(-)-i�� . 8. (� 14 Jf)",
            "�i¼( - ) -il\\M .10. (� 14 Jf)",
        ):
            with self.subTest(footer=footer):
                records = _parse_explicit(
                    [
                        Block("40. What is the best title?", page=10),
                        Block("[A] Alpha", page=10),
                        Block("[B] Beta", page=10),
                        Block("[C] Gamma", page=10),
                        Block("[D] Delta", page=10),
                        Block(footer, page=10),
                    ],
                    [40],
                )
                self.assertEqual(records[0]["options"]["D"], "Delta")
                self.assertIn(
                    "discarded_garbled_page_footer_block",
                    records[0]["extraction_warnings"],
                )

    def test_repeated_pronoun_before_markers_stays_with_each_option(self) -> None:
        records = _parse_explicit(
            [
                Block("38. What can be learned about ExampleCorp?", page=11),
                Block("It [A] protects against unfair competition.", page=11),
                Block("It [B] engages in anti-competitive practices.", page=11),
                Block("It [C] is under investigation.", page=11),
                Block("It [D] pursues quality service.", page=11),
            ],
            [38],
        )
        self.assertEqual(records[0]["stem"], "What can be learned about ExampleCorp?")
        self.assertEqual(
            records[0]["options"],
            {
                "A": "It protects against unfair competition.",
                "B": "It engages in anti-competitive practices.",
                "C": "It is under investigation.",
                "D": "It pursues quality service.",
            },
        )

    def test_known_pdf_quote_and_possessive_artifacts_are_normalized(self) -> None:
        records = _parse_explicit(
            [
                Block('21. A "festival town^^ award could', page=5),
                Block("[A] support Riverton5s districts.", page=5),
                Block("[B] Beta", page=5),
                Block("[C] Gamma", page=5),
                Block("[D] Delta", page=5),
            ],
            [21],
        )
        self.assertEqual(records[0]["stem"], 'A "festival town” award could')
        self.assertEqual(records[0]["options"]["A"], "support Riverton’s districts.")

    def test_plural_digit_apostrophe_artifacts_are_normalized(self) -> None:
        records = _parse_explicit(
            [
                Block("36. Which interests matter?", page=5),
                Block("[A] companies5 interests", page=5),
                Block("[B] tech giants5 revenue", page=5),
                Block("[C] managers9 decisions", page=5),
                Block("[D] ordinary workers", page=5),
            ],
            [36],
        )
        self.assertEqual(records[0]["options"]["A"], "companies’ interests")
        self.assertEqual(records[0]["options"]["B"], "tech giants’ revenue")
        self.assertEqual(records[0]["options"]["C"], "managers’ decisions")

    def test_reviewed_correction_requires_exact_original_text(self) -> None:
        record = {
            "id": "2020-reading-q27",
            "stem": "According to the text?",
            "options": {"A": "A", "B": "B", "C": "reviewed industry.", "D": "D"},
            "extraction_warnings": [],
        }
        correction = {
            "record_id": "2020-reading-q27",
            "field": "options.C",
            "expected": "reviewed industry.",
            "replacement": "revived industry.",
            "evidence_source": "alternate.docx",
        }
        applied = apply_reviewed_corrections([record], [correction])
        self.assertEqual(applied, {("2020-reading-q27", "options.C")})
        self.assertEqual(record["options"]["C"], "revived industry.")
        self.assertTrue(record["reviewed_text_corrections"])

    def test_question_type_rules_use_overt_stem_evidence(self) -> None:
        self.assertEqual(
            classify_question("Which of the following would be the best title for the text?")["question_type"],
            "main_idea_or_title",
        )
        self.assertEqual(
            classify_question("The word 'charge' most probably means")["question_type"],
            "word_or_phrase_meaning",
        )

    def test_complete_text_fixture_produces_twenty_questions(self) -> None:
        lines = ["Section II Reading Comprehension", "Part A"]
        for article in range(1, 5):
            lines.extend(
                [
                    f"Text {article}",
                    "A passage sentence supplies enough prose for locating the question boundary.",
                ]
            )
            start = 21 + (article - 1) * 5
            for number in range(start, start + 5):
                lines.extend(
                    [
                        f"{number}. According to the text, which statement is supported?",
                        "[A] First option.",
                        "[B] Second option.",
                        "[C] Third option.",
                        "[D] Fourth option.",
                    ]
                )
        lines.append("Part B")

        with tempfile.TemporaryDirectory(prefix="question index ") as temp:
            root = Path(temp)
            source = root / "2018 exam.txt"
            source.write_text("\n".join(lines), encoding="utf-8")
            records, info = extract_questions(source, 2018, root)

        self.assertEqual(info["question_count"], 20)
        self.assertEqual([record["question_number"] for record in records], list(range(21, 41)))
        self.assertTrue(all(sorted(record["options"]) == list("ABCD") for record in records))


if __name__ == "__main__":
    unittest.main()
