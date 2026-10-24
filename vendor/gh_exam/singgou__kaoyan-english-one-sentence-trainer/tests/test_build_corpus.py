from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_corpus import build  # noqa: E402


def fixture_text() -> str:
    lines = ["Section II Reading Comprehension", "Part A"]
    starts = [21, 26, 31, 36]
    for number, question in zip(range(1, 5), starts):
        lines.extend(
            [
                f"Text {number}",
                "A careful reader first identifies the finite verb before interpreting every attached modifier.",
                "The method works because each added clause must connect to a specific word or proposition.",
                f"{question}. According to the text, which method works best?",
                "[A] Guessing from sentence length.",
                "[B] Finding structure before details.",
                "[C] Ignoring logical relations.",
                "[D] Memorizing an isolated translation.",
            ]
        )
    lines.extend(["Part B", "[A] This choice bank must not enter the corpus."])
    return "\n".join(lines)


class CorpusBuildTests(unittest.TestCase):
    def test_build_is_idempotent_and_excludes_answer_files(self) -> None:
        with tempfile.TemporaryDirectory(prefix="英语 一 skill test ") as temp:
            root = Path(temp)
            source = root / "01、真题部分"
            source.mkdir()
            (source / "2018年考研英语一真题.txt").write_text(fixture_text(), encoding="utf-8")
            (source / "2018年考研英语一真题答案.txt").write_text("参考答案 A B C D", encoding="utf-8")
            data = root / "data"
            output = data / "corpus.jsonl"
            manifest = data / "manifest.json"
            report = data / "report.json"

            first = build(root, 2018, 2018, output, manifest, report, cross_check=True)
            first_bytes = output.read_bytes()
            second = build(root, 2018, 2018, output, manifest, report, cross_check=True)
            second_bytes = output.read_bytes()

            self.assertEqual(first_bytes, second_bytes)
            self.assertGreater(first["records"], 0)
            self.assertFalse(second["corpus_changed"])
            records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(records), len({record["id"] for record in records}))
            self.assertTrue(all("答案" not in record["source_file"] for record in records))
            self.assertTrue(all("According to the text" not in record["original"] for record in records))
            manifest_data = json.loads(manifest.read_text(encoding="utf-8"))
            reasons = {entry["reason"] for entry in manifest_data["excluded"]}
            self.assertIn("answer_analysis_or_collection", reasons)

    def test_temporary_derived_files_cannot_change_selected_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="kaoyan corpus boundary ") as temp:
            root = Path(temp)
            source = root / "collection" / "questions"
            source.mkdir(parents=True)
            authentic = source / "2018 exam.txt"
            authentic.write_text(fixture_text(), encoding="utf-8")
            derived_dir = root / "tmp" / "ocr-check"
            derived_dir.mkdir(parents=True)
            derived = derived_dir / "2018 exam.txt"
            derived.write_text(fixture_text().replace("careful", "temporary"), encoding="utf-8")

            data = root / "data"
            report = build(
                root,
                2018,
                2018,
                data / "corpus.jsonl",
                data / "manifest.json",
                data / "report.json",
                cross_check=True,
            )
            manifest = json.loads((data / "manifest.json").read_text(encoding="utf-8"))

            self.assertEqual(report["records"], 8)
            self.assertEqual(
                manifest["years"]["2018"]["selected_source"],
                str(authentic.relative_to(root)),
            )
            excluded = {entry["file"]: entry["reason"] for entry in manifest["excluded"]}
            self.assertEqual(
                excluded[str(derived.relative_to(root))],
                "derived_or_temporary_directory",
            )

    def test_empty_build_refuses_to_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="empty corpus ") as temp:
            root = Path(temp)
            data = root / "data"
            with self.assertRaises(SystemExit):
                build(
                    root,
                    2018,
                    2018,
                    data / "corpus.jsonl",
                    data / "manifest.json",
                    data / "report.json",
                    cross_check=True,
                )
            self.assertFalse((data / "corpus.jsonl").exists())

    def test_smaller_rebuild_cannot_overwrite_existing_corpus(self) -> None:
        with tempfile.TemporaryDirectory(prefix="corpus regression ") as temp:
            root = Path(temp)
            source = root / "questions"
            source.mkdir()
            exam = source / "2018 exam.txt"
            exam.write_text(fixture_text(), encoding="utf-8")
            data = root / "data"
            output = data / "corpus.jsonl"
            args = (
                root,
                2018,
                2018,
                output,
                data / "manifest.json",
                data / "report.json",
            )
            build(*args, cross_check=True)
            original = output.read_bytes()
            exam.write_text(
                fixture_text().replace(
                    "The method works because each added clause must connect to a specific word or proposition.",
                    "This sentence is short.",
                ),
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit):
                build(*args, cross_check=True)
            self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
