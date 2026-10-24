from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_passage_index import clean_passage_text, extract_passages  # noqa: E402


class PassageIndexTests(unittest.TestCase):
    def test_known_pdf_artifacts_are_narrowly_normalized(self) -> None:
        raw = (
            "A town's peculiarities一helping local people formed a “culture^^ for everyone. "
            "The genuine final sentence ends here. *-i½( - ) -i�fk! . 7 . (� 14 N)"
        )
        cleaned, warnings = clean_passage_text(raw)
        self.assertEqual(
            cleaned,
            "A town's peculiarities—helping local people formed a “culture” for everyone. "
            "The genuine final sentence ends here.",
        )
        self.assertIn("trimmed_garbled_page_footer", warnings)
        self.assertIn("normalized_pdf_double_caret_closing_quote:1", warnings)
        self.assertIn("normalized_cjk_dash_artifact:1", warnings)

    def test_unknown_replacement_character_is_not_silently_removed(self) -> None:
        cleaned, warnings = clean_passage_text(
            "First sentence! � is discussed as a symbol in the final sentence."
        )
        self.assertIn("�", cleaned)
        self.assertEqual(warnings, [])

    def test_full_passage_record_is_separate_from_questions(self) -> None:
        lines = ["Section II Reading Comprehension", "Part A"]
        for article in range(1, 5):
            start = 21 + (article - 1) * 5
            lines.extend(
                [
                    f"Text {article}",
                    "This is the first complete passage sentence.",
                    "Short ideas still remain inside the passage record.",
                    f"{start}. According to the text, which statement is supported?",
                    "[A] First option.",
                    "[B] Second option.",
                    "[C] Third option.",
                    "[D] Fourth option.",
                ]
            )
        lines.append("Part B")
        with tempfile.TemporaryDirectory(prefix="passage index ") as temp:
            root = Path(temp)
            source = root / "2018 exam.txt"
            source.write_text("\n".join(lines), encoding="utf-8")
            records, info = extract_passages(source, 2018, root)
        self.assertEqual(info["article_count"], 4)
        self.assertEqual(len(records), 4)
        self.assertTrue(all("According to" not in record["text"] for record in records))
        self.assertTrue(all("Short ideas" in record["text"] for record in records))


if __name__ == "__main__":
    unittest.main()
