from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from classify_sentences import classify  # noqa: E402
from extract_sentences import (  # noqa: E402
    Block,
    clean_common_extraction_artifacts,
    extract_reading_articles,
    split_sentences,
)


class ExtractionTests(unittest.TestCase):
    def test_abbreviations_do_not_split_a_sentence(self) -> None:
        text = "Dr. Smith argues that U.S. policy should change. The evidence remains limited."
        self.assertEqual(2, len(split_sentences(text)))
        self.assertTrue(split_sentences(text)[0].startswith("Dr. Smith"))

    def test_abbreviation_match_does_not_consume_word_suffix(self) -> None:
        text = "This happened in the past. Museums preserve objects. Another point follows."
        self.assertEqual(3, len(split_sentences(text)))

    def test_repeated_glyph_artifacts_are_normalized_narrowly(self) -> None:
        raw = "Riverton5s firms5 paid fbr access. Nature9 s policy protects equal rights55"
        cleaned, warnings = clean_common_extraction_artifacts(raw)
        self.assertEqual(
            cleaned,
            "Riverton’s firms’ paid for access. Nature’s policy protects equal rights”",
        )
        self.assertTrue(warnings)

    def test_modern_part_a_excludes_questions_and_options(self) -> None:
        blocks = [Block("Section II Reading Comprehension"), Block("Part A Directions:")]
        for number in range(1, 5):
            blocks.extend(
                [
                    Block(f"Text {number}"),
                    Block("Researchers have shown that careful reading requires attention to both structure and context."),
                    Block("This finding matters because a familiar word may carry an unfamiliar meaning in academic prose."),
                    Block(f"{20 + (number - 1) * 5 + 1}. According to the text, what should readers notice?"),
                    Block("[A] Only the length of each sentence."),
                    Block("[B] Both structure and context."),
                    Block("[C] The author's biography."),
                    Block("[D] An unrelated example."),
                ]
            )
        blocks.append(Block("Part B"))
        articles, warnings = extract_reading_articles(blocks, 4)
        self.assertFalse(warnings)
        self.assertEqual({1, 2, 3, 4}, set(articles))
        self.assertTrue(all(len(items) == 2 for items in articles.values()))
        joined = " ".join(block.text for items in articles.values() for block in items)
        self.assertNotIn("According to", joined)
        self.assertNotIn("[A]", joined)

    def test_unmarked_stem_and_four_options_are_trimmed_before_later_question(self) -> None:
        blocks = [Block("Section II Reading Comprehension"), Block("Part A Directions:")]
        for number in range(1, 5):
            blocks.extend(
                [
                    Block(f"Text {number}"),
                    Block("The discussion opens by explaining an institutional change and its historical setting."),
                    Block("Additional evidence then complicates the familiar account of the issue."),
                    Block("Competing explanations are compared before their practical limits are identified."),
                    Block("The final claim is qualified rather than presented as an absolute recommendation."),
                    Block("The author introduces the example mainly to"),
                    Block("describe a familiar historical event."),
                    Block("illustrate the mechanism discussed above."),
                    Block("reject every alternative explanation."),
                    Block("question whether institutions can change."),
                    Block("Which of the following best summarizes the passage?"),
                    Block("A later unmarked option."),
                ]
            )
        articles, _warnings = extract_reading_articles(blocks, 4)
        self.assertTrue(all(len(items) == 4 for items in articles.values()))
        joined = " ".join(block.text for items in articles.values() for block in items)
        self.assertNotIn("introduces the example", joined)
        self.assertNotIn("best summarizes", joined)

    def test_short_rhetorical_fragment_is_not_mistaken_for_question_section(self) -> None:
        blocks = [Block("Section II Reading Comprehension"), Block("Part A Directions:")]
        for number in range(1, 5):
            blocks.extend(
                [
                    Block(f"Text {number}"),
                    Block("A long opening discussion establishes the public issue and explains why the familiar account remains incomplete."),
                    Block("Suburb of culture?"),
                    Block("A substantial continuation develops the argument with evidence, qualifications, and a clearly stated causal mechanism."),
                    Block("The conclusion then returns to the original tension while avoiding an absolute claim about every community."),
                    Block(f"{20 + (number - 1) * 5 + 1}. Which claim follows from the passage?"),
                    Block("[A] The first option."),
                    Block("[B] The second option."),
                    Block("[C] The third option."),
                    Block("[D] The fourth option."),
                ]
            )
        articles, _warnings = extract_reading_articles(blocks, 4)
        self.assertTrue(all(len(items) == 4 for items in articles.values()))
        self.assertTrue(
            all(any(item.text == "Suburb of culture?" for item in items) for items in articles.values())
        )

    def test_legacy_year_supports_five_passages(self) -> None:
        blocks = [Block("Section II Reading Comprehension"), Block("Part A")]
        starts = [21, 25, 29, 33, 37]
        for number, question in zip(range(1, 6), starts):
            blocks.extend(
                [
                    Block(f"Passage {number}"),
                    Block("Scientific specialization changes how researchers communicate knowledge across professional communities."),
                    Block("The historical development of this practice also affects participation in modern institutions."),
                    Block(f"{question}. Which statement best summarizes the passage?"),
                    Block("[A] A short option."),
                ]
            )
        articles, _warnings = extract_reading_articles(blocks, 5)
        self.assertEqual(5, len(articles))
        self.assertTrue(all(len(items) == 2 for items in articles.values()))

    def test_short_cross_page_continuation_is_retained(self) -> None:
        blocks = [
            Block("Section II Reading Comprehension", page=4),
            Block("Text 1", page=5),
            Block(
                "The research team carried instruments through deserts and recorded the difficult conditions they",
                page=5,
            ),
            Block("encountered.”", page=6),
            Block("21. What does the passage suggest?", page=6),
        ]
        for number in range(2, 5):
            blocks.extend(
                [
                    Block(f"Text {number}", page=number + 5),
                    Block(
                        "Researchers have shown that careful reading requires attention to structure and context.",
                        page=number + 5,
                    ),
                    Block(f"{16 + number * 5}. What follows?", page=number + 5),
                ]
            )
        articles, warnings = extract_reading_articles(blocks, 4)
        self.assertEqual(
            articles[1][0].text,
            "The research team carried instruments through deserts and recorded the difficult conditions they encountered.”",
        )
        self.assertTrue(any("cross-page continuation" in item for item in warnings))

    def test_difficulty_is_not_length_only(self) -> None:
        long_simple = (
            "The report lists many facts about schools, teachers, students, books, classes, libraries, "
            "buildings, schedules, lessons, examinations, and ordinary administrative routines."
        )
        shorter_complex = "Although the policy that officials defended was revised, what it would achieve remained uncertain."
        simple_result = classify(long_simple)
        complex_result = classify(shorter_complex)
        self.assertLess(simple_result["difficulty"], 5)
        self.assertGreaterEqual(complex_result["difficulty"], 2)
        self.assertIn("relative_clause", complex_result["grammar_tags"])

    def test_reporting_that_clause_is_not_forced_into_relative_clause(self) -> None:
        result = classify("Researchers argue that these mergers may weaken competition.")
        self.assertIn("noun_clause", result["grammar_tags"])
        self.assertNotIn("relative_clause", result["grammar_tags"])
        self.assertIsNone(result["tag_confidence"])
        self.assertEqual(result["tag_review_status"], "heuristic_unreviewed")


if __name__ == "__main__":
    unittest.main()
