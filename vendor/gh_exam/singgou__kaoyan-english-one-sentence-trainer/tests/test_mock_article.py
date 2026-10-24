from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_mock_article import validate, words  # noqa: E402


def make_article(word_count: int, paragraph_count: int = 7) -> str:
    sentence = (
        "Careful institutions examine ordinary change because public habits often reveal "
        "how incentives shape choices while leaving room for disagreement."
    )
    tokens = words(sentence)
    repeated = (tokens * ((word_count // len(tokens)) + 1))[:word_count]
    sizes = [word_count // paragraph_count] * paragraph_count
    for index in range(word_count % paragraph_count):
        sizes[index] += 1
    output: list[str] = []
    cursor = 0
    for size in sizes:
        paragraph_tokens = repeated[cursor : cursor + size]
        cursor += size
        chunks = [paragraph_tokens[index : index + 20] for index in range(0, len(paragraph_tokens), 20)]
        output.append(" ".join(" ".join(chunk).capitalize() + "." for chunk in chunks))
    return "\n\n".join(output)


class MockArticleValidationTests(unittest.TestCase):
    def test_valid_article_respects_requested_word_range(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "corpus.jsonl"
            corpus.write_text("", encoding="utf-8")
            report = validate(make_article(420), corpus_path=corpus)
        self.assertTrue(report["valid"], report)
        self.assertEqual(report["metrics"]["word_count"], 420)
        self.assertEqual(report["metrics"]["paragraph_count"], 7)

    def test_word_count_boundaries_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "corpus.jsonl"
            corpus.write_text("", encoding="utf-8")
            below = validate(make_article(387), corpus_path=corpus)
            above = validate(make_article(453), corpus_path=corpus)
        self.assertFalse(below["valid"])
        self.assertFalse(above["valid"])
        self.assertIn("word count 387", below["errors"][0])
        self.assertIn("word count 453", above["errors"][0])

    def test_long_copy_from_true_corpus_is_rejected(self) -> None:
        copied = "one two three four five six seven eight nine ten eleven twelve"
        article = copied.capitalize() + ".\n\n" + make_article(396, paragraph_count=6)
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "corpus.jsonl"
            corpus.write_text(
                json.dumps({"id": "true-passage", "text": copied + "."}) + "\n",
                encoding="utf-8",
            )
            report = validate(article, corpus_path=corpus)
        self.assertFalse(report["valid"])
        self.assertEqual(report["metrics"]["shared_corpus_ngram"]["source_id"], "true-passage")

    def test_chinese_and_markdown_are_not_article_body(self) -> None:
        article = "# Heading\n\n" + make_article(400) + "\n\n这是说明"
        with tempfile.TemporaryDirectory() as directory:
            corpus = Path(directory) / "corpus.jsonl"
            corpus.write_text("", encoding="utf-8")
            report = validate(article, corpus_path=corpus)
        self.assertFalse(report["valid"])
        self.assertIn("article body contains Chinese characters", report["errors"])
        self.assertIn(
            "article body contains a Markdown heading, list, quote, or code fence",
            report["errors"],
        )


if __name__ == "__main__":
    unittest.main()
