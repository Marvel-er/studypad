from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import update_progress  # noqa: E402
from update_progress import (  # noqa: E402
    backup_state,
    record_result,
    recover_state_transactions,
    reset_state,
    restore_state,
    skip_active,
)


class ProgressTests(unittest.TestCase):
    def test_record_and_skip_require_a_real_active_sentence_by_default(self) -> None:
        with tempfile.TemporaryDirectory(prefix="active stage guard ") as temp:
            data = Path(temp)
            sentence_id = "2018-reading-text1-abcdef123456"
            (data / "corpus.jsonl").write_text(
                json.dumps({"id": sentence_id, "original": "A valid sentence appears here."}) + "\n",
                encoding="utf-8",
            )
            record_args = argparse.Namespace(
                data_dir=data, corpus=None, sentence_id=sentence_id, attempt_id="guarded",
                main_structure=20, grammar_score=20, word_meaning=15,
                completeness=15, chinese_expression=10, grammar=[], wrong_word=[],
                correct_word=[], confused_word=[], error=[], note=None,
                allow_nonactive=False,
            )
            with self.assertRaises(SystemExit):
                record_result(record_args)
            with self.assertRaises(SystemExit):
                skip_active(
                    argparse.Namespace(
                        data_dir=data, corpus=None, sentence_id="not-in-corpus",
                        attempt_id="skip-guarded", reason="test",
                    )
                )
            self.assertFalse((data / "session_history.jsonl").exists())

    def test_record_is_idempotent_and_updates_profiles(self) -> None:
        with tempfile.TemporaryDirectory(prefix="中文 路径 progress ") as temp:
            data = Path(temp)
            sentence_id = "2018-reading-text1-abcdef123456"
            corpus_record = {"id": sentence_id, "original": "A valid sentence appears here for testing."}
            (data / "corpus.jsonl").write_text(json.dumps(corpus_record) + "\n", encoding="utf-8")
            (data / "active_session.json").write_text(
                json.dumps({"session_id": "attempt-fixed", "sentence_id": sentence_id, "stage": "awaiting_answer"}),
                encoding="utf-8",
            )
            args = argparse.Namespace(
                data_dir=data,
                sentence_id=None,
                attempt_id=None,
                main_structure=20,
                grammar_score=18,
                word_meaning=12,
                completeness=15,
                chinese_expression=8,
                grammar=["relative_clause=wrong"],
                wrong_word=["address|处理"],
                correct_word=[],
                confused_word=[],
                error=["predicate_identification:misidentified finite verb"],
                note="fixture",
                allow_nonactive=False,
            )
            first = record_result(args)
            second = record_result(args)
            self.assertEqual("recorded", first["status"])
            self.assertEqual("duplicate_ignored", second["status"])
            progress = json.loads((data / "progress.json").read_text(encoding="utf-8"))
            vocabulary = json.loads((data / "vocabulary.json").read_text(encoding="utf-8"))
            grammar = json.loads((data / "grammar_profile.json").read_text(encoding="utf-8"))
            self.assertEqual(1, progress["session_count"])
            self.assertEqual(1, vocabulary["address"]["wrong_count"])
            self.assertEqual(1, grammar["relative_clause"]["wrong"])

    def test_backup_and_guarded_reset_keep_corpus(self) -> None:
        with tempfile.TemporaryDirectory(prefix="中文 路径 backup ") as temp:
            data = Path(temp)
            (data / "corpus.jsonl").write_text("{}\n", encoding="utf-8")
            (data / "progress.json").write_text("{}\n", encoding="utf-8")
            archive = backup_state(data, data / "state.zip")
            self.assertTrue(archive.exists())
            with zipfile.ZipFile(archive) as bundle:
                self.assertIn("progress.json", bundle.namelist())
                self.assertNotIn("corpus.jsonl", bundle.namelist())
            with self.assertRaises(SystemExit):
                reset_state(argparse.Namespace(data_dir=data, confirm="NO", no_backup=True))
            result = reset_state(argparse.Namespace(data_dir=data, confirm="RESET"))
            self.assertIn("progress.json", result["removed"])
            self.assertTrue((data / "corpus.jsonl").exists())
            self.assertTrue(Path(result["backup"]).exists())

    def test_interrupted_record_recovers_without_double_counting(self) -> None:
        with tempfile.TemporaryDirectory(prefix="中文 路径 transaction ") as temp:
            data = Path(temp)
            sentence_id = "2019-reading-text2-abcdef123456"
            (data / "corpus.jsonl").write_text(
                json.dumps({"id": sentence_id, "original": "A recoverable transaction is tested here."}) + "\n",
                encoding="utf-8",
            )
            (data / "active_session.json").write_text(
                json.dumps({"session_id": "attempt-recovery", "sentence_id": sentence_id, "stage": "awaiting_answer"}),
                encoding="utf-8",
            )
            args = argparse.Namespace(
                data_dir=data,
                corpus=None,
                sentence_id=None,
                attempt_id=None,
                main_structure=20,
                grammar_score=18,
                word_meaning=12,
                completeness=15,
                chinese_expression=8,
                grammar=["relative_clause=wrong"],
                wrong_word=["address|处理"],
                correct_word=[],
                confused_word=[],
                error=[],
                note="recovery fixture",
                allow_nonactive=False,
            )
            original_atomic = update_progress.atomic_json
            failed = False

            def flaky_atomic(path: Path, payload: object) -> None:
                nonlocal failed
                if path.name == "vocabulary.json" and not failed:
                    failed = True
                    raise OSError("injected write failure")
                original_atomic(path, payload)

            with patch.object(update_progress, "atomic_json", side_effect=flaky_atomic):
                with self.assertRaises(OSError):
                    record_result(args)
            self.assertTrue((data / "pending_update.json").exists())

            retry = record_result(args)
            self.assertEqual("duplicate_ignored", retry["status"])
            self.assertFalse((data / "pending_update.json").exists())
            progress = json.loads((data / "progress.json").read_text(encoding="utf-8"))
            vocabulary = json.loads((data / "vocabulary.json").read_text(encoding="utf-8"))
            history = [json.loads(line) for line in (data / "session_history.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(1, progress["session_count"])
            self.assertEqual(1, vocabulary["address"]["wrong_count"])
            self.assertEqual(1, len(history))

    def test_invalid_update_transaction_cannot_modify_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="中文 路径 invalid transaction ") as temp:
            data = Path(temp)
            original = {"session_count": 3}
            (data / "progress.json").write_text(json.dumps(original), encoding="utf-8")
            invalid = {
                "version": 1,
                "created_at": "2026-07-18T00:00:00+00:00",
                "states": {"progress.json": {"session_count": 999}},
                "event": {"event": "graded"},
            }
            (data / "pending_update.json").write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaises(SystemExit):
                recover_state_transactions(data)
            self.assertEqual(original, json.loads((data / "progress.json").read_text(encoding="utf-8")))

            invalid["event"]["attempt_id"] = "bad-payload"
            invalid["states"]["progress.json"] = "not-an-object"
            (data / "pending_update.json").write_text(json.dumps(invalid), encoding="utf-8")
            with self.assertRaises(SystemExit):
                recover_state_transactions(data)
            self.assertEqual(original, json.loads((data / "progress.json").read_text(encoding="utf-8")))

    def test_same_created_at_uses_filesystem_order_without_rollback(self) -> None:
        with tempfile.TemporaryDirectory(prefix="中文 路径 same timestamp ") as temp:
            data = Path(temp)
            created_at = "2026-07-18T00:00:00+00:00"
            update_path = data / "pending_update.json"
            selection_path = data / "pending_selection.json"
            update_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "created_at": created_at,
                        "states": {
                            "progress.json": {"recent_sentence_ids": ["old"]},
                            "active_session.json": {"sentence_id": "old", "stage": "completed"},
                        },
                        "event": {"event": "graded", "attempt_id": "old-attempt", "sentence_id": "old"},
                    }
                ),
                encoding="utf-8",
            )
            selection_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "created_at": created_at,
                        "progress": {"recent_sentence_ids": ["old", "new"]},
                        "active": {"sentence_id": "new", "stage": "awaiting_answer"},
                    }
                ),
                encoding="utf-8",
            )
            os.utime(update_path, ns=(1_000_000_000, 1_000_000_000))
            os.utime(selection_path, ns=(2_000_000_000, 2_000_000_000))
            recover_state_transactions(data)
            progress = json.loads((data / "progress.json").read_text(encoding="utf-8"))
            active = json.loads((data / "active_session.json").read_text(encoding="utf-8"))
            self.assertEqual(["old", "new"], progress["recent_sentence_ids"])
            self.assertEqual("new", active["sentence_id"])

    def test_malformed_pending_json_blocks_without_state_change(self) -> None:
        with tempfile.TemporaryDirectory(prefix="中文 路径 malformed pending ") as temp:
            data = Path(temp)
            (data / "progress.json").write_text('{"session_count": 2}\n', encoding="utf-8")
            (data / "pending_update.json").write_text('{broken', encoding="utf-8")
            (data / "pending_selection.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "created_at": "2026-07-18T00:00:01+00:00",
                        "progress": {"session_count": 99},
                        "active": {"sentence_id": "new", "stage": "awaiting_answer"},
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit):
                recover_state_transactions(data)
            self.assertEqual(2, json.loads((data / "progress.json").read_text(encoding="utf-8"))["session_count"])
            self.assertFalse((data / "active_session.json").exists())

    def test_verified_restore_round_trip(self) -> None:
        with tempfile.TemporaryDirectory(prefix="中文 路径 restore ") as temp:
            data = Path(temp)
            (data / "progress.json").write_text('{"session_count": 1}\n', encoding="utf-8")
            snapshot = backup_state(data, data / "snapshot.zip")
            (data / "progress.json").write_text('{"session_count": 9}\n', encoding="utf-8")
            result = restore_state(argparse.Namespace(data_dir=data, archive=snapshot, confirm="RESTORE"))
            restored = json.loads((data / "progress.json").read_text(encoding="utf-8"))
            self.assertEqual(1, restored["session_count"])
            self.assertTrue(Path(result["safety_backup"]).exists())

    def test_interrupted_restore_recovers_automatically(self) -> None:
        with tempfile.TemporaryDirectory(prefix="中文 路径 restore recovery ") as temp:
            data = Path(temp)
            (data / "progress.json").write_text('{"session_count": 1}\n', encoding="utf-8")
            (data / "vocabulary.json").write_text('{"address": {"wrong_count": 1}}\n', encoding="utf-8")
            snapshot = backup_state(data, data / "snapshot.zip")
            (data / "progress.json").write_text('{"session_count": 9}\n', encoding="utf-8")
            (data / "vocabulary.json").write_text('{}\n', encoding="utf-8")
            original_atomic_bytes = update_progress.atomic_bytes
            failed = False

            def flaky_bytes(path: Path, payload: bytes) -> None:
                nonlocal failed
                if path.name == "vocabulary.json" and not failed:
                    failed = True
                    raise OSError("injected restore failure")
                original_atomic_bytes(path, payload)

            with patch.object(update_progress, "atomic_bytes", side_effect=flaky_bytes):
                with self.assertRaises(OSError):
                    restore_state(argparse.Namespace(data_dir=data, archive=snapshot, confirm="RESTORE"))
            self.assertTrue((data / "pending_restore.json").exists())
            recover_state_transactions(data)
            self.assertFalse((data / "pending_restore.json").exists())
            self.assertEqual(1, json.loads((data / "progress.json").read_text(encoding="utf-8"))["session_count"])
            self.assertEqual(1, json.loads((data / "vocabulary.json").read_text(encoding="utf-8"))["address"]["wrong_count"])

    def test_restore_rejects_tampered_backup(self) -> None:
        with tempfile.TemporaryDirectory(prefix="中文 路径 tampered backup ") as temp:
            data = Path(temp)
            (data / "progress.json").write_text('{"session_count": 1}\n', encoding="utf-8")
            snapshot = backup_state(data, data / "snapshot.zip")
            tampered = data / "tampered.zip"
            with zipfile.ZipFile(snapshot) as source, zipfile.ZipFile(tampered, "w") as target:
                for name in source.namelist():
                    payload = source.read(name)
                    if name == "progress.json":
                        payload = b'{"session_count": 999}\n'
                    target.writestr(name, payload)
            with self.assertRaises(SystemExit):
                restore_state(argparse.Namespace(data_dir=data, archive=tampered, confirm="RESTORE"))

    def test_failed_backup_replace_leaves_no_final_archive(self) -> None:
        with tempfile.TemporaryDirectory(prefix="中文 路径 backup replace ") as temp:
            data = Path(temp)
            (data / "progress.json").write_text('{}\n', encoding="utf-8")
            output = data / "state.zip"
            original_replace = update_progress.os.replace

            def flaky_replace(source: object, destination: object) -> None:
                if Path(destination) == output:
                    raise OSError("injected final replace failure")
                original_replace(source, destination)

            with patch.object(update_progress.os, "replace", side_effect=flaky_replace):
                with self.assertRaises(OSError):
                    backup_state(data, output)
            self.assertFalse(output.exists())
            self.assertFalse(any(path.suffix == ".tmp" for path in data.iterdir()))


if __name__ == "__main__":
    unittest.main()
