#!/usr/bin/env python3
"""Rebuild and validate every derived corpus artifact in dependency order."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import analyze_corpus
import analyze_exam_points
import build_answer_index
import build_corpus
import build_passage_index
import build_question_index
import build_vocabulary
import validate_artifacts
import validate_corpus


SKILL_ROOT = Path(__file__).resolve().parents[1]
DATA = SKILL_ROOT / "data"
REFERENCES = SKILL_ROOT / "references"


def rebuild(
    source_root: Path,
    year_start: int,
    year_end: int,
    allowed_unusable_years: set[int],
    allow_incomplete: bool,
    allow_regression: bool,
) -> dict[str, object]:
    corpus_report = build_corpus.build(
        source_root, year_start, year_end,
        DATA / "corpus.jsonl", DATA / "source_manifest.json", DATA / "build_report.json",
        True, allowed_unusable_years, allow_incomplete, allow_regression,
    )
    sentence_validation = validate_corpus.validate(
        DATA / "corpus.jsonl", source_root, year_start, year_end
    )
    validate_artifacts.atomic_json(DATA / "corpus_validation.json", sentence_validation)
    if not sentence_validation["valid"]:
        raise SystemExit("sentence corpus validation failed; downstream artifacts were not rebuilt")

    passage_report = build_passage_index.build(
        DATA / "source_manifest.json", DATA / "passage_index.jsonl",
        DATA / "passage_build_report.json", year_start, year_end,
        allowed_unusable_years, allow_incomplete, allow_regression,
    )
    question_report = build_question_index.build(
        DATA / "source_manifest.json", DATA / "question_index.jsonl",
        DATA / "question_build_report.json", year_start, year_end,
        allowed_unusable_years, allow_incomplete, allow_regression,
    )
    answer_report = build_answer_index.build(
        DATA / "answer_keys.reviewed.json", source_root,
        DATA / "answer_index.jsonl", DATA / "answer_build_report.json",
    )
    vocabulary_report = build_vocabulary.build(
        DATA / "passage_index.jsonl", DATA / "question_index.jsonl", DATA / "corpus.jsonl",
        DATA / "vocabulary_occurrences.jsonl", DATA / "vocabulary_lexicon.jsonl",
        DATA / "vocabulary_stats.json", REFERENCES / "vocabulary-coverage.md",
    )

    all_sentences = analyze_corpus.load_jsonl(DATA / "corpus.jsonl")
    full_stats = analyze_corpus.analyze(all_sentences, source_records=all_sentences)
    analyze_corpus.atomic_text(
        DATA / "corpus_stats.json",
        json.dumps(full_stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    analyze_corpus.atomic_text(
        REFERENCES / "corpus-insights.md", analyze_corpus.markdown_report(full_stats)
    )
    reviewed_sentences = [
        item for item in all_sentences
        if item.get("text_status") in {"cross_checked", "human_verified"}
        and not item.get("needs_manual_review")
    ]
    reviewed_stats = analyze_corpus.analyze(
        reviewed_sentences, source_records=all_sentences
    )
    analyze_corpus.atomic_text(
        DATA / "corpus_stats_reviewed.json",
        json.dumps(reviewed_stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    analyze_corpus.atomic_text(
        REFERENCES / "corpus-insights-reviewed.md",
        analyze_corpus.markdown_report(reviewed_stats),
    )
    exam_report = analyze_exam_points.build(
        DATA / "question_index.jsonl", DATA / "corpus.jsonl", DATA / "answer_index.jsonl",
        DATA / "exam_point_stats.json", REFERENCES / "exam-points.md",
    )
    final_validation = validate_artifacts.validate(
        DATA / "corpus.jsonl", DATA / "passage_index.jsonl", DATA / "question_index.jsonl",
        DATA / "answer_index.jsonl", DATA / "vocabulary_occurrences.jsonl",
        DATA / "vocabulary_lexicon.jsonl", DATA / "vocabulary_stats.json",
        source_root, year_start, year_end, allowed_unusable_years,
    )
    validate_artifacts.atomic_json(DATA / "artifact_validation.json", final_validation)
    if not final_validation["valid"]:
        raise SystemExit("final artifact validation failed")
    return {
        "corpus": {"records": corpus_report["records"], "years": corpus_report["built_years"]},
        "passages": {"records": passage_report["records"], "years": passage_report["built_years"]},
        "questions": {"records": question_report["records"], "years": question_report["built_years"]},
        "answers": {"records": answer_report["records"], "years": answer_report["years"]},
        "vocabulary": vocabulary_report,
        "exam_points": exam_report,
        "validation": final_validation,
    }


def build_parser() -> argparse.ArgumentParser:
    config = json.loads((DATA / "config.json").read_text(encoding="utf-8"))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=config.get("source_root"))
    parser.add_argument("--year-start", type=int, default=int(config.get("year_start", 2001)))
    parser.add_argument("--year-end", type=int, default=int(config.get("year_end", 2026)))
    parser.add_argument("--allowed-unusable-year", type=int, action="append", default=list(config.get("allowed_unusable_years", [])))
    parser.add_argument("--allow-incomplete", action="store_true")
    parser.add_argument("--allow-regression", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    if args.source_root is None:
        raise SystemExit("--source-root is required when data/config.json has no source_root")
    result = rebuild(
        Path(args.source_root).resolve(), args.year_start, args.year_end,
        set(args.allowed_unusable_year), args.allow_incomplete, args.allow_regression,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
