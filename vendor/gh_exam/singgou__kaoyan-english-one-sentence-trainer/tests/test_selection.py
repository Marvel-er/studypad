from __future__ import annotations

import json
import argparse
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import select_daily_sentence  # noqa: E402
from select_daily_sentence import (  # noqa: E402
    _is_selectable,
    choose_new,
    commit_selection,
    default_progress,
    prompt_for,
    recover_pending_selection,
    safe_pending,
)


def record(sentence_id: str, year: int, tags: list[str], difficulty: int = 3) -> dict:
    return {
        "id": sentence_id,
        "year": year,
        "section": "Reading Part A",
        "article": "Text 1",
        "original": "The policy that researchers examined may affect how students understand difficult academic arguments.",
        "word_count": 15,
        "difficulty": difficulty,
        "grammar_tags": tags,
        "text_status": "cross_checked",
        "needs_manual_review": False,
        "source_completeness_status": "no_known_gap",
        "safe_for_training": True,
        "known_source_gap": None,
        "provenance_status": "source_unverified",
        "source_status": "user_provided_question_file",
        "source_file": f"{year}年真题.docx",
        "extraction_method": "python-docx",
        "extraction_origin": "document_text",
    }


class SelectionTests(unittest.TestCase):
    def test_weakness_bucket_prefers_matching_structure(self) -> None:
        corpus = [
            record("a", 2018, ["relative_clause"]),
            record("b", 2019, ["comparison"]),
        ]
        progress = default_progress()
        grammar = {"relative_clause": {"attempts": 4, "wrong": 3, "level": "weak"}}
        selected, bucket, fallback = choose_new(corpus, progress, grammar, False, "fixed")
        self.assertEqual("weak", bucket)
        self.assertIsNone(fallback)
        self.assertEqual("a", selected["id"])

    def test_recent_sentence_is_not_repeated(self) -> None:
        corpus = [record("a", 2018, ["relative_clause"]), record("b", 2019, ["relative_clause"])]
        progress = default_progress()
        progress["recent_sentence_ids"] = ["a"]
        grammar = {"relative_clause": {"attempts": 2, "wrong": 2, "level": "weak"}}
        selected, _bucket, _fallback = choose_new(corpus, progress, grammar, False, "fixed")
        self.assertEqual("b", selected["id"])

    def test_stage_a_prompt_contains_no_answer_fields(self) -> None:
        text = prompt_for(record("a", 2018, ["relative_clause"]))
        self.assertIn("今日长难句", text)
        self.assertIn("请先独立完成", text)
        for forbidden in ("参考译文", "grammar_tags", "difficulty", "核心主干：", "词汇解析"):
            self.assertNotIn(forbidden, text)

    def test_unverified_ocr_is_never_selectable_even_when_unreviewed_is_allowed(self) -> None:
        candidate = record("ocr", 2025, ["relative_clause"])
        candidate.update(
            {
                "text_status": "auto_extracted",
                "needs_manual_review": True,
                "extraction_method": "ocrmypdf",
            }
        )
        self.assertFalse(_is_selectable(candidate, allow_unreviewed=True))
        candidate["text_status"] = "human_verified"
        candidate["needs_manual_review"] = False
        self.assertTrue(_is_selectable(candidate, allow_unreviewed=True))
        candidate["text_status"] = "auto_extracted"
        candidate["needs_manual_review"] = True
        candidate["extraction_method"] = "pdfplumber"
        candidate["extraction_origin"] = "embedded_text"
        candidate["source_file"] = "2025-reading-ocr-unverified.pdf"
        self.assertFalse(_is_selectable(candidate, allow_unreviewed=True))
        candidate["source_file"] = "2025-reading.pdf"
        candidate["extraction_method"] = "tesseract"
        candidate["extraction_origin"] = "ocr"
        candidate["source_locator"] = {"kind": "image_text"}
        self.assertFalse(_is_selectable(candidate, allow_unreviewed=True))

    def test_only_user_provided_question_sources_are_selectable(self) -> None:
        candidate = record("source", 2020, ["relative_clause"])
        self.assertTrue(_is_selectable(candidate, allow_unreviewed=False))
        candidate["source_status"] = "generated"
        self.assertFalse(_is_selectable(candidate, allow_unreviewed=False))

    def test_known_incomplete_article_is_never_selectable(self) -> None:
        candidate = record("gap", 2026, ["relative_clause"])
        candidate.update(
            {
                "source_completeness_status": "known_incomplete_source",
                "safe_for_training": False,
                "known_source_gap": {"description": "paragraphs omitted by source"},
            }
        )
        self.assertFalse(_is_selectable(candidate, allow_unreviewed=False))
        self.assertFalse(_is_selectable(candidate, allow_unreviewed=True))

    def test_pending_sentence_is_rechecked_before_reuse(self) -> None:
        candidate = record("pending", 2024, ["relative_clause"])
        active = {"stage": "awaiting_answer", "sentence_id": "pending"}
        self.assertEqual(candidate, safe_pending(active, {"pending": candidate}, False))
        candidate["needs_manual_review"] = True
        candidate["text_status"] = "auto_extracted"
        self.assertIsNone(safe_pending(active, {"pending": candidate}, False))

    def test_interrupted_selection_recovers_both_state_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="中文 路径 selection ") as temp:
            data = Path(temp)
            progress = {"version": 1, "recent_sentence_ids": ["a"]}
            active = {"version": 1, "stage": "awaiting_answer", "sentence_id": "a"}
            original_atomic = select_daily_sentence.atomic_json
            failed = False

            def flaky_atomic(path: Path, payload: object) -> None:
                nonlocal failed
                if path.name == "active_session.json" and not failed:
                    failed = True
                    raise OSError("injected selection write failure")
                original_atomic(path, payload)

            with patch.object(select_daily_sentence, "atomic_json", side_effect=flaky_atomic):
                with self.assertRaises(OSError):
                    commit_selection(data, progress, active)
            self.assertTrue((data / "pending_selection.json").exists())
            recover_pending_selection(data)
            self.assertEqual(progress, json.loads((data / "progress.json").read_text(encoding="utf-8")))
            self.assertEqual(active, json.loads((data / "active_session.json").read_text(encoding="utf-8")))
            self.assertFalse((data / "pending_selection.json").exists())

    def test_selector_recovers_older_progress_transaction_before_new_commit(self) -> None:
        from update_progress import recover_state_transactions

        with tempfile.TemporaryDirectory(prefix="中文 路径 transaction order ") as temp:
            data = Path(temp)
            old_progress = default_progress()
            old_progress["recent_sentence_ids"] = ["old"]
            old_progress["assigned_sentence_ids"] = ["old"]
            old_active = {"stage": "completed", "sentence_id": "old"}
            pending_update = {
                "version": 1,
                "created_at": "2026-07-18T00:00:00+00:00",
                "states": {"progress.json": old_progress, "active_session.json": old_active},
                "event": {
                    "version": 1,
                    "event": "graded",
                    "attempt_id": "old-attempt",
                    "sentence_id": "old",
                },
            }
            (data / "pending_update.json").write_text(json.dumps(pending_update), encoding="utf-8")
            corpus_path = data / "corpus.jsonl"
            corpus_path.write_text(json.dumps(record("new", 2020, ["relative_clause"])) + "\n", encoding="utf-8")
            args = argparse.Namespace(
                data_dir=data,
                corpus=corpus_path,
                mode="new",
                format="json",
                commit=True,
                force_new=False,
                allow_unreviewed=False,
                seed="ordered",
            )
            with redirect_stdout(io.StringIO()):
                select_daily_sentence._run(args)
            recover_state_transactions(data)
            progress = json.loads((data / "progress.json").read_text(encoding="utf-8"))
            active = json.loads((data / "active_session.json").read_text(encoding="utf-8"))
            self.assertEqual(["old", "new"], progress["recent_sentence_ids"])
            self.assertEqual("new", active["sentence_id"])
            self.assertEqual("awaiting_answer", active["stage"])


if __name__ == "__main__":
    unittest.main()
