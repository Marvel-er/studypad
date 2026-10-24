#!/usr/bin/env python3
"""Build full Reading Part A passage records for vocabulary analysis.

Unlike ``corpus.jsonl``, which contains sentence candidates suitable for daily
training, this index keeps each machine-extractable passage as one full text so
short sentences are not silently omitted from vocabulary counts.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from extract_sentences import (
    ExtractionError,
    clean_reading_text,
    extract_blocks,
    extract_reading_articles,
    normalize_space,
    normalized_key,
    passage_completeness_metadata,
    sha256_file,
)


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = SKILL_ROOT / "data"
GARBLED_PAGE_FOOTER_RE = re.compile(
    r"\s+(?:\*?-?\s*)?\ufffd?i½[^\n]*\(\s*\ufffd\s*14\s*(?:Jf|N)\s*\)\s*$",
    re.IGNORECASE,
)
INTERWORD_CJK_DASH_RE = re.compile(r"(?<=[A-Za-z])一(?=\s*[A-Za-z])")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ExtractionError(f"JSON root must be an object: {path}")
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


def expected_articles(year: int) -> int:
    return 5 if year == 2001 else 4


def clean_passage_text(text: str) -> tuple[str, list[str]]:
    """Normalize narrowly identified extraction artifacts without rewriting prose.

    The rules intentionally target artifacts observed in the local 2020--2022
    sources.  Anything outside these patterns remains visible so validation can
    reject it instead of silently guessing at the original wording.
    """

    cleaned = text
    warnings: list[str] = []
    footer = GARBLED_PAGE_FOOTER_RE.search(cleaned)
    if footer and footer.start() >= max(0, len(cleaned) - 320):
        candidate = cleaned[: footer.start()].rstrip()
        if candidate and candidate[-1] in ".?!\"'”’":
            cleaned = candidate
            warnings.append("trimmed_garbled_page_footer")

    cleaned, caret_count = re.subn(
        r"(?<=[A-Za-z.!?])\^\^(?=(?:\s|$))", "”", cleaned
    )
    if caret_count:
        warnings.append(f"normalized_pdf_double_caret_closing_quote:{caret_count}")

    cleaned, dash_count = INTERWORD_CJK_DASH_RE.subn("—", cleaned)
    if dash_count:
        warnings.append(f"normalized_cjk_dash_artifact:{dash_count}")

    return normalize_space(cleaned), warnings


def extract_passages(path: Path, year: int, source_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    blocks, method = extract_blocks(path)
    article_blocks, warnings = extract_reading_articles(blocks, expected_articles(year))
    if set(article_blocks) != set(range(1, expected_articles(year) + 1)):
        raise ExtractionError(f"incomplete passage headings: {sorted(article_blocks)}")
    relative = str(path.resolve().relative_to(source_root.resolve()))
    source_hash = sha256_file(path)
    output: list[dict[str, Any]] = []
    for article in range(1, expected_articles(year) + 1):
        items = article_blocks[article]
        common_text, common_warnings, reviewed_corrections = clean_reading_text(
            normalize_space(" ".join(item.text for item in items)),
            year,
            article,
            source_root,
        )
        text, passage_warnings = clean_passage_text(common_text)
        cleanup_warnings = common_warnings + passage_warnings
        completeness = passage_completeness_metadata(year, article, source_root)
        if not text:
            raise ExtractionError(f"Text {article}: empty passage")
        pages = [item.page for item in items if item.page is not None]
        locators = [item.locator for item in items if item.locator is not None]
        output.append(
            {
                "schema_version": 1,
                "id": f"{year}-reading-text{article}-passage",
                "year": year,
                "exam": "english_one",
                "section": "Reading Part A",
                "article": f"Text {article}",
                "text": text,
                "block_count": len(items),
                "source_file": relative,
                "source_file_sha256": source_hash,
                "source_page_start": min(pages) if pages else None,
                "source_page_end": max(pages) if pages else None,
                "source_locator": {
                    "kind": "passage_blocks",
                    "start_block": min(locators) if locators else None,
                    "end_block": max(locators) if locators else None,
                    "page_start": min(pages) if pages else None,
                    "page_end": max(pages) if pages else None,
                },
                "extraction_method": method,
                "source_status": "user_provided_question_file",
                "provenance_status": "source_unverified",
                "extraction_warnings": cleanup_warnings,
                "reviewed_text_corrections": reviewed_corrections,
                **completeness,
            }
        )
    return output, {
        "file": relative,
        "source_file_sha256": source_hash,
        "extraction_method": method,
        "article_count": len(output),
        "warnings": warnings,
        "cleanup_warning_count": sum(
            len(record["extraction_warnings"]) for record in output
        ),
    }


def corroborate(
    selected: list[dict[str, Any]], alternatives: list[tuple[list[dict[str, Any]], dict[str, Any]]]
) -> dict[str, int]:
    counts = Counter()
    indexes = [({item["article"]: item for item in records}, info) for records, info in alternatives]
    for record in selected:
        target = normalized_key(record["text"])
        best_similarity = 0.0
        best: dict[str, Any] | None = None
        alternate_sources: list[dict[str, Any]] = []
        for index, info in indexes:
            candidate = index.get(record["article"])
            if candidate is None:
                continue
            similarity = difflib.SequenceMatcher(
                None, target, normalized_key(candidate["text"]), autojunk=False
            ).ratio()
            alternate = {
                "source_file": info["file"],
                "similarity": round(similarity, 4),
            }
            alternate_sources.append(alternate)
            if similarity > best_similarity:
                best_similarity = similarity
                best = alternate
        record["alternate_sources"] = alternate_sources
        record["corroboration"] = best
        if best_similarity == 1.0:
            record["text_status"] = "cross_checked"
            record["needs_manual_review"] = False
            counts["exact"] += 1
        elif best_similarity >= 0.97:
            record["text_status"] = "fuzzy_cross_checked"
            record["needs_manual_review"] = True
            counts["fuzzy"] += 1
        else:
            record["text_status"] = "auto_extracted"
            record["needs_manual_review"] = True
            counts["unmatched"] += 1
    return {key: counts[key] for key in ("exact", "fuzzy", "unmatched")}


def build(
    manifest_path: Path,
    output_path: Path,
    report_path: Path,
    year_start: int,
    year_end: int,
    allowed_unusable_years: set[int] | None = None,
    allow_incomplete: bool = False,
    allow_regression: bool = False,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    source_root = Path(manifest["source_root"])
    allowed = set(allowed_unusable_years or set())
    records: list[dict[str, Any]] = []
    years_report: dict[str, Any] = {}
    failed_years: list[int] = []

    for year in range(year_start, year_end + 1):
        entry = manifest.get("years", {}).get(str(year), {})
        selected_relative = entry.get("selected_source")
        if not selected_relative:
            failed_years.append(year)
            years_report[str(year)] = {"status": "unavailable", "reason": entry.get("status")}
            continue
        try:
            selected, selected_info = extract_passages(source_root / selected_relative, year, source_root)
        except (ExtractionError, OSError, ValueError) as exc:
            failed_years.append(year)
            years_report[str(year)] = {"status": "error", "error": str(exc)}
            continue
        alternatives: list[tuple[list[dict[str, Any]], dict[str, Any]]] = []
        alternate_errors: list[dict[str, str]] = []
        for candidate in entry.get("candidates", []):
            relative = candidate.get("file")
            if candidate.get("status") != "ok" or not relative or relative == selected_relative:
                continue
            try:
                alternatives.append(extract_passages(source_root / relative, year, source_root))
            except (ExtractionError, OSError, ValueError) as exc:
                alternate_errors.append({"file": relative, "error": str(exc)})
        match_counts = corroborate(selected, alternatives)
        records.extend(selected)
        years_report[str(year)] = {
            "status": "built",
            "selected_source": selected_info["file"],
            "article_count": len(selected),
            "corroboration": match_counts,
            "cleanup_warning_count": selected_info["cleanup_warning_count"],
            "alternate_errors": alternate_errors,
        }

    unexpected = sorted(set(failed_years) - allowed)
    if unexpected and not allow_incomplete:
        raise SystemExit(
            f"refusing incomplete passage index; unexpected failed years={unexpected}"
        )
    if not records:
        raise SystemExit("no passage records; refusing to overwrite the passage index")
    ordered = sorted(records, key=lambda item: (item["year"], item["article"]))
    if output_path.exists() and not allow_regression:
        old = [json.loads(line) for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        old_years = {int(item["year"]) for item in old}
        new_years = {int(item["year"]) for item in ordered}
        if len(ordered) < len(old) or not old_years.issubset(new_years):
            raise SystemExit(
                f"refusing passage-index regression: old={len(old)}, new={len(ordered)}"
            )
    payload = "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in ordered)
    changed = atomic_text(output_path, payload)
    report = {
        "manifest": str(manifest_path),
        "output": str(output_path),
        "records": len(ordered),
        "built_years": sorted({int(item["year"]) for item in ordered}),
        "failed_years": failed_years,
        "output_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "output_changed": changed,
        "years": years_report,
    }
    atomic_text(report_path, json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return report


def build_parser() -> argparse.ArgumentParser:
    config_path = DEFAULT_DATA_DIR / "config.json"
    config = load_json(config_path) if config_path.exists() else {}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_DATA_DIR / "source_manifest.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_DATA_DIR / "passage_index.jsonl")
    parser.add_argument("--report", type=Path, default=DEFAULT_DATA_DIR / "passage_build_report.json")
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
    report = build(
        args.manifest.resolve(), args.output.resolve(), args.report.resolve(),
        args.year_start, args.year_end, set(args.allowed_unusable_year),
        args.allow_incomplete, args.allow_regression,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
