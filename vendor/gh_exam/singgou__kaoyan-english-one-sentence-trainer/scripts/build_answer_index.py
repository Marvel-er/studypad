#!/usr/bin/env python3
"""Validate reviewed local Reading Part A answer keys and build an index."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = SKILL_ROOT / "data"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise SystemExit(f"JSON root must be an object: {path}")
    return value


def atomic_text(path: Path, text: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = text.encode("utf-8")
    if path.exists() and path.read_bytes() == payload:
        return False
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)
    return True


def build(config_path: Path, source_root: Path, output_path: Path, report_path: Path) -> dict[str, Any]:
    config = load_json(config_path)
    records: list[dict[str, Any]] = []
    source_hashes: dict[Path, str] = {}
    for year_text, entry in sorted(config.get("years", {}).items()):
        year = int(year_text)
        answers = "".join(re.findall(r"[A-D]", str(entry.get("answers", "")).upper()))
        if len(answers) != 20:
            raise SystemExit(f"{year}: expected 20 answers, found {len(answers)}")
        source_file = source_root / str(entry["source_file"])
        if not source_file.is_file():
            raise SystemExit(f"{year}: answer source does not exist: {source_file}")
        if source_file not in source_hashes:
            source_hashes[source_file] = hashlib.sha256(source_file.read_bytes()).hexdigest()
        for offset, answer in enumerate(answers):
            number = 21 + offset
            records.append(
                {
                    "schema_version": 1,
                    "id": f"{year}-reading-a{number}",
                    "year": year,
                    "exam": "english_one",
                    "section": "Reading Part A",
                    "question_number": number,
                    "answer": answer,
                    "source_file": entry["source_file"],
                    "source_file_sha256": source_hashes[source_file],
                    "source_pages": entry.get("source_pages", []),
                    "extraction_method": entry.get("extraction_method"),
                    "review_note": entry.get("note"),
                    "source_status": "user_provided_answer_file",
                    "provenance_status": "source_unverified",
                    "answer_review_status": "locally_reviewed",
                }
            )
    expected_years = set(range(2001, 2027))
    years = {int(record["year"]) for record in records}
    if years != expected_years or len(records) != 520:
        raise SystemExit(f"answer index must contain 520 records for 2001-2026; years={sorted(years)}")
    payload = "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in records)
    changed = atomic_text(output_path, payload)
    report = {
        "records": len(records),
        "years": sorted(years),
        "source_files": len(source_hashes),
        "output_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "output_changed": changed,
        "important_boundary": "locally reviewed user-provided answer files; official provenance not authenticated",
    }
    atomic_text(report_path, json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_DATA_DIR / "answer_keys.reviewed.json")
    parser.add_argument("--source-root", type=Path, help="root containing user-provided answer sources")
    parser.add_argument("--output", type=Path, default=DEFAULT_DATA_DIR / "answer_index.jsonl")
    parser.add_argument("--report", type=Path, default=DEFAULT_DATA_DIR / "answer_build_report.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    if args.source_root is None:
        raise SystemExit("--source-root is required")
    result = build(args.config.resolve(), args.source_root.resolve(), args.output.resolve(), args.report.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
