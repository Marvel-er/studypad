#!/usr/bin/env python3
"""Discover authentic exam files and build a deterministic Reading Part A corpus."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from extract_sentences import ExtractionError, detect_kind, extract_source, normalized_key


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = SKILL_ROOT / "data"
SUPPORTED_SUFFIXES = {".pdf", ".doc", ".docx", ".txt", ".md", ".markdown"}
EXCLUDED_FILENAME_TERMS = ("答案", "解析", "详解", "合集", "速查")
EXCLUDED_DIRECTORY_PARTS = {
    ".git", ".tmp", "__pycache__", "audit", "audits", "render", "renders",
    "rendered", "temp", "tmp", "kaoyan-english-one-sentence-trainer",
}
YEAR_RE = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")
YEAR_RANGE_RE = re.compile(r"(?:19|20)\d{2}\s*[-—–至]\s*(?:19|20)\d{2}")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def atomic_write_text(path: Path, text: str) -> bool:
    """Write only when content changes; return whether the file changed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = text.encode("utf-8")
    if path.exists() and path.read_bytes() == encoded:
        return False
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("wb") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)
    return True


def atomic_write_json(path: Path, payload: Any) -> bool:
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return atomic_write_text(path, text)


def discover_sources(root: Path, year_start: int, year_end: int) -> tuple[dict[int, list[Path]], list[dict[str, str]]]:
    by_year: dict[int, list[Path]] = defaultdict(list)
    excluded: list[dict[str, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: str(item).lower()):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        relative = str(path.relative_to(root))
        directory_parts = {
            part.casefold() for part in path.relative_to(root).parts[:-1]
        }
        if directory_parts & EXCLUDED_DIRECTORY_PARTS:
            excluded.append({"file": relative, "reason": "derived_or_temporary_directory"})
            continue
        if suffix == ".qkdownloading" or path.name.lower().endswith(".qkdownloading"):
            excluded.append({"file": relative, "reason": "incomplete_download"})
            continue
        if suffix not in SUPPORTED_SUFFIXES:
            continue
        if "解析部分" in relative:
            excluded.append({"file": relative, "reason": "analysis_directory"})
            continue
        if any(term in path.name for term in EXCLUDED_FILENAME_TERMS):
            excluded.append({"file": relative, "reason": "answer_analysis_or_collection"})
            continue
        if YEAR_RANGE_RE.search(path.name):
            excluded.append({"file": relative, "reason": "multi_year_collection"})
            continue
        years = [int(match.group(1)) for match in YEAR_RE.finditer(path.name)]
        years = [year for year in years if year_start <= year <= year_end]
        if len(set(years)) != 1:
            if years:
                excluded.append({"file": relative, "reason": "ambiguous_year"})
            continue
        by_year[years[0]].append(path)
    return dict(by_year), excluded


def source_priority(path: Path) -> int:
    try:
        kind = detect_kind(path)
    except ExtractionError:
        return 0
    return {"docx": 50, "text": 45, "pdf": 40, "doc": 30}.get(kind, 0)


def expected_article_count(year: int) -> int:
    return 5 if year == 2001 else 4


def _quality_score(path: Path, info: dict[str, Any], year: int) -> int:
    expected = expected_article_count(year)
    complete = info.get("article_count") == expected
    count = int(info.get("sentence_count", 0))
    plausible = 25 <= count <= 180
    method_penalty = 30 if info.get("extraction_method") == "raw-ooxml" else 0
    return (
        (10000 if complete else 0)
        + (1000 if plausible else 0)
        + source_priority(path)
        + min(count, 200)
        - 20 * len(info.get("warnings", []))
        - method_penalty
    )


def _article_records(records: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        result[record["article"]].append(record)
    return dict(result)


def corroborate(
    selected: list[dict[str, Any]],
    alternatives: list[tuple[list[dict[str, Any]], dict[str, Any]]],
) -> dict[str, int]:
    exact_matches = 0
    fuzzy_matches = 0
    unmatched = 0
    alternate_indexes: list[tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]], dict[str, Any]]] = []
    for records, info in alternatives:
        exact = {record["normalized_sha256"]: record for record in records}
        alternate_indexes.append((exact, _article_records(records), info))

    for record in selected:
        best: dict[str, Any] | None = None
        best_ratio = 0.0
        exact_hit = False
        alternates_meta: list[dict[str, Any]] = []
        for exact_index, article_index, info in alternate_indexes:
            hit = exact_index.get(record["normalized_sha256"])
            if hit is not None:
                exact_hit = True
                ratio = 1.0
                candidate = hit
            else:
                candidate = None
                ratio = 0.0
                target_key = normalized_key(record["original"])
                for option in article_index.get(record["article"], []):
                    option_key = normalized_key(option["original"])
                    current = difflib.SequenceMatcher(None, target_key, option_key, autojunk=False).ratio()
                    if current > ratio:
                        ratio = current
                        candidate = option
            if candidate is not None:
                alternates_meta.append(
                    {
                        "source_file": info["relative_path"],
                        "source_page": candidate.get("source_page"),
                        "similarity": round(ratio, 4),
                    }
                )
                if ratio > best_ratio:
                    best_ratio = ratio
                    best = alternates_meta[-1]

        record["alternate_sources"] = alternates_meta
        if exact_hit and best is not None:
            record["text_status"] = "cross_checked"
            record["needs_manual_review"] = False
            record["corroboration"] = best
            exact_matches += 1
        elif best is not None and best_ratio >= 0.97:
            record["text_status"] = "fuzzy_cross_checked"
            record["needs_manual_review"] = True
            record["corroboration"] = best
            fuzzy_matches += 1
        else:
            record["text_status"] = "auto_extracted"
            record["needs_manual_review"] = True
            record["corroboration"] = best
            unmatched += 1
    return {"exact": exact_matches, "fuzzy": fuzzy_matches, "unmatched": unmatched}


def _stable_jsonl(records: Iterable[dict[str, Any]]) -> str:
    ordered = sorted(
        records,
        key=lambda item: (
            item["year"], int(str(item["article"]).split()[-1]), item["sentence_number"], item["id"]
        ),
    )
    return "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in ordered)


def build(
    source_root: Path,
    year_start: int,
    year_end: int,
    output: Path,
    manifest_path: Path,
    report_path: Path,
    cross_check: bool = True,
    allowed_unusable_years: set[int] | None = None,
    allow_incomplete: bool = False,
    allow_regression: bool = False,
) -> dict[str, Any]:
    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise SystemExit(f"source root is not a directory: {source_root}")

    sources, excluded = discover_sources(source_root, year_start, year_end)
    all_records: list[dict[str, Any]] = []
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "source_root": str(source_root),
        "year_start": year_start,
        "year_end": year_end,
        "years": {},
        "excluded": excluded,
    }
    missing: list[int] = []
    unusable: list[int] = []

    for year in range(year_start, year_end + 1):
        candidates = sorted(sources.get(year, []), key=lambda item: (-source_priority(item), str(item).lower()))
        year_entry: dict[str, Any] = {"expected_articles": expected_article_count(year), "candidates": []}
        successful: list[tuple[Path, list[dict[str, Any]], dict[str, Any], int]] = []
        if not candidates:
            missing.append(year)
            year_entry["status"] = "missing_source"
            manifest["years"][str(year)] = year_entry
            continue

        for path in candidates:
            candidate_entry: dict[str, Any] = {"file": str(path.relative_to(source_root))}
            before = path.stat()
            try:
                records, info = extract_source(path, year, source_root)
                after = path.stat()
                if before.st_size != after.st_size or before.st_mtime_ns != after.st_mtime_ns:
                    raise ExtractionError("file changed during extraction; download may still be active")
                score = _quality_score(path, info, year)
                candidate_entry.update({"status": "ok", "quality_score": score, **info})
                successful.append((path, records, info, score))
            except (ExtractionError, OSError, ValueError) as exc:
                candidate_entry.update({"status": "error", "error": str(exc)})
            year_entry["candidates"].append(candidate_entry)

        expected = expected_article_count(year)
        complete = [item for item in successful if item[2].get("article_count") == expected]
        if not complete:
            unusable.append(year)
            year_entry["status"] = "no_complete_extractable_source"
            manifest["years"][str(year)] = year_entry
            continue

        chosen = max(complete, key=lambda item: (item[3], -len(str(item[0]))))
        chosen_path, chosen_records, chosen_info, chosen_score = chosen
        alternatives = [
            (records, info)
            for path, records, info, _score in successful
            if path != chosen_path
        ]
        match_counts = corroborate(chosen_records, alternatives) if cross_check else {"exact": 0, "fuzzy": 0, "unmatched": len(chosen_records)}
        if not cross_check:
            for record in chosen_records:
                record["alternate_sources"] = []
        all_records.extend(chosen_records)
        year_entry.update(
            {
                "status": "built",
                "selected_source": str(chosen_path.relative_to(source_root)),
                "selected_method": chosen_info["extraction_method"],
                "selected_quality_score": chosen_score,
                "sentence_count": len(chosen_records),
                "corroboration": match_counts,
            }
        )
        manifest["years"][str(year)] = year_entry

    allowed_unusable_years = set(allowed_unusable_years or set())
    unexpected_incomplete = sorted(
        set(missing) | (set(unusable) - allowed_unusable_years)
    )
    if unexpected_incomplete and not allow_incomplete:
        raise SystemExit(
            "refusing to write an unexpectedly incomplete corpus; "
            f"years={unexpected_incomplete}. Install the required readers or use "
            "--allow-incomplete after reviewing the manifest."
        )

    # IDs are hash-derived; this protects against accidental duplicate sources.
    unique: dict[str, dict[str, Any]] = {}
    duplicate_ids: list[str] = []
    for record in all_records:
        if record["id"] in unique:
            duplicate_ids.append(record["id"])
            continue
        unique[record["id"]] = record
    if not unique:
        raise SystemExit("no usable corpus records; refusing to overwrite the corpus")
    corpus_text = _stable_jsonl(unique.values())
    new_years = {int(record["year"]) for record in unique.values()}
    if output.exists() and not allow_regression:
        try:
            old_records = [
                json.loads(line)
                for line in output.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"existing corpus cannot be audited before replacement: {exc}") from exc
        old_years = {int(record["year"]) for record in old_records if "year" in record}
        if len(unique) < len(old_records) or not old_years.issubset(new_years):
            raise SystemExit(
                "refusing corpus regression: "
                f"existing={len(old_records)} records/{len(old_years)} years, "
                f"new={len(unique)} records/{len(new_years)} years. "
                "Use --allow-regression only after inspecting the cause."
            )
    corpus_changed = atomic_write_text(output, corpus_text)
    manifest["summary"] = {
        "records": len(unique),
        "built_years": sorted({record["year"] for record in unique.values()}),
        "missing_source_years": missing,
        "unusable_years": unusable,
        "duplicate_ids_dropped": sorted(set(duplicate_ids)),
        "corpus_sha256": hashlib.sha256(corpus_text.encode("utf-8")).hexdigest(),
    }
    atomic_write_json(manifest_path, manifest)

    report = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source_root),
        "corpus": str(output),
        "manifest": str(manifest_path),
        "corpus_changed": corpus_changed,
        **manifest["summary"],
        "incomplete_downloads_ignored": sum(
            item["reason"] == "incomplete_download" for item in excluded
        ),
    }
    atomic_write_json(report_path, report)
    return report


def build_parser() -> argparse.ArgumentParser:
    config = read_json(DEFAULT_DATA_DIR / "config.json", {})
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=config.get("source_root"), help="root containing user-provided exam files")
    parser.add_argument("--year-start", type=int, default=int(config.get("year_start", 2001)))
    parser.add_argument("--year-end", type=int, default=int(config.get("year_end", 2026)))
    parser.add_argument("--output", type=Path, default=DEFAULT_DATA_DIR / "corpus.jsonl")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_DATA_DIR / "source_manifest.json")
    parser.add_argument("--report", type=Path, default=DEFAULT_DATA_DIR / "build_report.json")
    parser.add_argument("--no-cross-check", action="store_true", help="skip same-year alternate-source matching")
    parser.add_argument(
        "--allowed-unusable-year",
        type=int,
        action="append",
        default=list(config.get("allowed_unusable_years", [])),
        help="year known to lack a usable source; repeatable",
    )
    parser.add_argument("--allow-incomplete", action="store_true", help="write despite unexpected missing/unusable years")
    parser.add_argument("--allow-regression", action="store_true", help="allow fewer records/years than an existing corpus")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    if args.source_root is None:
        raise SystemExit("--source-root is required when data/config.json has no source_root")
    report = build(
        Path(args.source_root), args.year_start, args.year_end,
        args.output, args.manifest, args.report, not args.no_cross_check,
        set(args.allowed_unusable_year), args.allow_incomplete, args.allow_regression,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
