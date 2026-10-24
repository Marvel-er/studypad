#!/usr/bin/env python3
"""Validate corpus integrity, contamination boundaries, and source traceability."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from classify_sentences import words
from extract_sentences import load_text_correction_config, normalized_key


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = SKILL_ROOT / "data"
ID_RE = re.compile(r"^(?:19|20)\d{2}-reading-text[1-5]-[0-9a-f]{12}$")
QUESTION_RE = re.compile(r"^(?:2[1-9]|3\d|40)\s*[.．、:]\s*")
OPTION_RE = re.compile(r"^(?:\[[ABCD]\]|\([ABCD]\)|[ABCD]\s*[.．、])\s*", re.IGNORECASE)
CONTAMINATION_TERMS = (
    "ANSWER SHEET", "Directions:", "Read the following four texts", "参考答案",
    "真题答案", "【答案】", "【解析】",
)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    records = []
    errors = []
    if not path.exists():
        return records, [f"corpus file does not exist: {path}"]
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {line_number}: invalid JSON: {exc}")
                continue
            if not isinstance(value, dict):
                errors.append(f"line {line_number}: record must be an object")
                continue
            records.append(value)
    return records, errors


def numeric_similarity(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return -1.0


def validate(
    corpus_path: Path,
    source_root: Path | None,
    year_start: int,
    year_end: int,
) -> dict[str, Any]:
    records, errors = load_jsonl(corpus_path)
    warnings: list[str] = []
    ids: set[str] = set()
    normalized_seen: dict[tuple[int, str], str] = {}
    global_texts: dict[str, list[str]] = defaultdict(list)
    year_articles: dict[int, set[str]] = defaultdict(set)
    year_counts: Counter[int] = Counter()
    text_status_counts: Counter[str] = Counter()
    manual_review_count = 0
    source_hash_cache: dict[Path, str] = {}
    reviewed_correction_count = 0
    text_correction_config = load_text_correction_config()
    corrupt_case_tokens = set(text_correction_config["token_replacements"])
    configured_gap_map: dict[tuple[int, int], dict[str, Any]] = {}
    known_incomplete_articles: set[tuple[int, int]] = set()
    for configured_gap in text_correction_config["known_source_gaps"]:
        if not isinstance(configured_gap, dict):
            errors.append("passage completeness config contains a non-object entry")
            continue
        try:
            gap_key = (int(configured_gap["year"]), int(configured_gap["article"]))
        except (KeyError, TypeError, ValueError):
            errors.append("passage completeness config contains an invalid target")
            continue
        if gap_key in configured_gap_map:
            errors.append(f"duplicate passage completeness target: {gap_key}")
        configured_gap_map[gap_key] = configured_gap

    if not records:
        errors.append("corpus contains no records")

    required = {
        "id", "year", "section", "article", "paragraph", "sentence_number",
        "original", "source_file", "source_page", "word_count", "difficulty",
        "grammar_tags", "vocabulary_tags", "source_status", "text_status",
        "needs_manual_review", "normalized_sha256", "source_file_sha256",
        "provenance_status", "tag_review_status", "tag_rule_version",
        "block_extraction_warnings", "reviewed_text_corrections",
        "source_completeness_status", "safe_for_training", "known_source_gap",
    }
    for index, record in enumerate(records, 1):
        label = record.get("id", f"record#{index}")
        missing = sorted(required - set(record))
        if missing:
            errors.append(f"{label}: missing fields {missing}")
            continue
        sentence_id = str(record["id"])
        if sentence_id in ids:
            errors.append(f"{sentence_id}: duplicate ID")
        ids.add(sentence_id)
        if not ID_RE.fullmatch(sentence_id):
            errors.append(f"{sentence_id}: invalid stable ID format")

        try:
            year = int(record["year"])
        except (TypeError, ValueError):
            errors.append(f"{sentence_id}: year must be an integer")
            continue
        if not year_start <= year <= year_end:
            errors.append(f"{sentence_id}: year outside configured range")
        expected_articles = 5 if year == 2001 else 4
        article_match = re.fullmatch(r"Text ([1-5])", str(record["article"]))
        if not article_match or int(article_match.group(1)) > expected_articles:
            errors.append(f"{sentence_id}: invalid article for {year}")
            article_number = -1
        else:
            article_number = int(article_match.group(1))
        year_articles[year].add(str(record["article"]))
        year_counts[year] += 1

        completeness_status = record.get("source_completeness_status")
        safe_for_training = record.get("safe_for_training")
        known_gap = record.get("known_source_gap")
        if completeness_status == "no_known_gap":
            if safe_for_training is not True or known_gap is not None:
                errors.append(f"{sentence_id}: inconsistent complete-source metadata")
        elif completeness_status == "known_incomplete_source":
            if article_number > 0:
                known_incomplete_articles.add((year, article_number))
            if safe_for_training is not False or not isinstance(known_gap, dict):
                errors.append(f"{sentence_id}: inconsistent incomplete-source metadata")
            else:
                configured_gap = configured_gap_map.get((year, article_number))
                if configured_gap is None:
                    errors.append(f"{sentence_id}: unconfigured source gap")
                else:
                    for field in (
                        "description",
                        "evidence_source",
                        "evidence_pages",
                        "evidence_method",
                        "external_corroboration_urls",
                        "note",
                    ):
                        expected = configured_gap.get(field)
                        if field == "evidence_method" and expected is None:
                            expected = "visual_structure_review"
                        if field == "external_corroboration_urls" and expected is None:
                            expected = []
                        if field == "note" and expected is None:
                            expected = ""
                        if known_gap.get(field) != expected:
                            errors.append(
                                f"{sentence_id}: source-gap metadata mismatch for {field}"
                            )
                if source_root is not None:
                    evidence_file = source_root / str(known_gap.get("evidence_source", ""))
                    if not evidence_file.is_file():
                        errors.append(f"{sentence_id}: source-gap evidence missing")
                    else:
                        if evidence_file not in source_hash_cache:
                            source_hash_cache[evidence_file] = hashlib.sha256(
                                evidence_file.read_bytes()
                            ).hexdigest()
                        if known_gap.get("evidence_source_sha256") != source_hash_cache[evidence_file]:
                            errors.append(f"{sentence_id}: source-gap evidence hash mismatch")
        else:
            errors.append(f"{sentence_id}: invalid source completeness status")

        original = str(record["original"]).strip()
        key = normalized_key(original)
        expected_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()
        if record.get("normalized_sha256") != expected_hash:
            errors.append(f"{sentence_id}: normalized hash mismatch")
        if not sentence_id.endswith(expected_hash[:12]):
            errors.append(f"{sentence_id}: ID hash does not match original")
        if len(words(original)) != int(record["word_count"]):
            errors.append(f"{sentence_id}: word_count mismatch")
        if not 1 <= int(record["difficulty"]) <= 5:
            errors.append(f"{sentence_id}: difficulty must be 1-5")
        if not isinstance(record["grammar_tags"], list) or not isinstance(record["vocabulary_tags"], list):
            errors.append(f"{sentence_id}: tags must be lists")
        if record["source_page"] is not None and (not isinstance(record["source_page"], int) or record["source_page"] < 1):
            errors.append(f"{sentence_id}: source_page must be null or a 1-based integer")
        if "(cid:" in original.lower() or "�" in original or "\x00" in original:
            errors.append(f"{sentence_id}: corrupt extraction marker in original")
        if re.search(
            r"\bfbr\b|\^\^|[A-Za-z]5s\b|s[59]\b|[A-Za-z]9\s+s\b|[A-Za-z]55\b|~~",
            original,
            re.IGNORECASE,
        ):
            errors.append(f"{sentence_id}: known OCR/glyph artifact remains in original")
        for token in corrupt_case_tokens:
            if re.search(rf"(?<![A-Za-z]){re.escape(token)}(?![A-Za-z])", original):
                errors.append(f"{sentence_id}: reviewed mixed-case OCR token remains: {token}")
        block_warnings = record.get("block_extraction_warnings")
        if not isinstance(block_warnings, list) or not all(
            isinstance(item, str) for item in block_warnings
        ):
            errors.append(f"{sentence_id}: block_extraction_warnings must be a string list")
        corrections = record.get("reviewed_text_corrections")
        if not isinstance(corrections, list):
            errors.append(f"{sentence_id}: reviewed_text_corrections must be a list")
            corrections = []
        for correction in corrections:
            if not isinstance(correction, dict):
                errors.append(f"{sentence_id}: malformed reviewed text correction")
                continue
            reviewed_correction_count += 1
            if correction.get("replacement") not in original:
                errors.append(f"{sentence_id}: reviewed replacement is absent from sentence")
            if source_root is not None:
                evidence_file = source_root / str(correction.get("evidence_source", ""))
                if not evidence_file.is_file():
                    errors.append(f"{sentence_id}: correction evidence source missing")
                elif hashlib.sha256(evidence_file.read_bytes()).hexdigest() != correction.get(
                    "evidence_source_sha256"
                ):
                    errors.append(f"{sentence_id}: correction evidence hash mismatch")
        if QUESTION_RE.match(original) or OPTION_RE.match(original):
            errors.append(f"{sentence_id}: appears to be a question or option")
        if any(term.lower() in original.lower() for term in CONTAMINATION_TERMS):
            errors.append(f"{sentence_id}: answer/direction contamination detected")
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", original))
        if chinese_chars:
            errors.append(f"{sentence_id}: Chinese analysis text detected in original")

        pair = (year, key)
        if pair in normalized_seen:
            errors.append(f"{sentence_id}: duplicate normalized sentence in year; first={normalized_seen[pair]}")
        normalized_seen[pair] = sentence_id
        global_texts[key].append(sentence_id)

        source_file = Path(str(record["source_file"]))
        if source_file.is_absolute():
            warnings.append(f"{sentence_id}: source_file should be relative")
        if source_root is not None:
            resolved_source = source_root / source_file
            if not resolved_source.is_file():
                errors.append(f"{sentence_id}: source file cannot be traced: {source_file}")
            else:
                if resolved_source not in source_hash_cache:
                    source_hash_cache[resolved_source] = hashlib.sha256(resolved_source.read_bytes()).hexdigest()
                if record.get("source_file_sha256") != source_hash_cache[resolved_source]:
                    errors.append(f"{sentence_id}: source_file_sha256 mismatch")

        status = str(record.get("text_status"))
        text_status_counts[status] += 1
        if record.get("needs_manual_review"):
            manual_review_count += 1
        if status == "ocr_unverified" and not record.get("needs_manual_review"):
            errors.append(f"{sentence_id}: unverified OCR cannot be marked review-complete")
        if status not in {"auto_extracted", "cross_checked", "fuzzy_cross_checked", "human_verified", "ocr_unverified"}:
            errors.append(f"{sentence_id}: unknown text_status {status}")
        corroboration = record.get("corroboration")
        if status == "cross_checked":
            if not isinstance(corroboration, dict) or numeric_similarity(corroboration.get("similarity")) != 1.0:
                errors.append(f"{sentence_id}: cross_checked requires exact corroboration")
            elif source_root is not None:
                alternate = source_root / str(corroboration.get("source_file", ""))
                if not alternate.is_file():
                    errors.append(f"{sentence_id}: corroborating source cannot be traced")
            if record.get("needs_manual_review"):
                errors.append(f"{sentence_id}: exact cross_checked record cannot require manual review")
        elif status == "fuzzy_cross_checked":
            similarity = numeric_similarity(corroboration.get("similarity")) if isinstance(corroboration, dict) else -1
            if not 0.97 <= similarity < 1.0:
                errors.append(f"{sentence_id}: fuzzy_cross_checked requires 0.97<=similarity<1")
            if not record.get("needs_manual_review"):
                errors.append(f"{sentence_id}: fuzzy text must require manual review")
        elif status in {"auto_extracted", "ocr_unverified"} and not record.get("needs_manual_review"):
            errors.append(f"{sentence_id}: uncorroborated text must require manual review")
        if record.get("tag_review_status") not in {"heuristic_unreviewed", "human_verified"}:
            errors.append(f"{sentence_id}: invalid tag_review_status")
        if record.get("provenance_status") != "source_unverified":
            warnings.append(f"{sentence_id}: official provenance is not explicitly marked source_unverified")

    for year in range(year_start, year_end + 1):
        expected = 5 if year == 2001 else 4
        if year_counts[year] == 0:
            warnings.append(f"{year}: no usable corpus records")
            continue
        if len(year_articles[year]) != expected:
            errors.append(f"{year}: expected {expected} articles, found {sorted(year_articles[year])}")
        if year_counts[year] < expected * 5:
            warnings.append(f"{year}: unusually few sentences ({year_counts[year]})")

    for key, sentence_ids in global_texts.items():
        if len(sentence_ids) > 1:
            warnings.append(f"same normalized sentence appears across records: {sentence_ids}")

    expected_incomplete_articles = {
        key for key in configured_gap_map if year_start <= key[0] <= year_end
    }
    if known_incomplete_articles != expected_incomplete_articles:
        errors.append(
            "known-incomplete article set differs from reviewed completeness configuration"
        )

    report = {
        "valid": not errors,
        "corpus": str(corpus_path),
        "record_count": len(records),
        "year_counts": {str(year): year_counts[year] for year in range(year_start, year_end + 1)},
        "article_counts": {str(year): len(year_articles[year]) for year in sorted(year_articles)},
        "text_status_counts": dict(sorted(text_status_counts.items())),
        "needs_manual_review": manual_review_count,
        "reviewed_text_corrections": reviewed_correction_count,
        "known_incomplete_articles": [
            f"{year}-reading-text{article}-passage"
            for year, article in sorted(known_incomplete_articles)
        ],
        "errors": errors,
        "warnings": sorted(set(warnings)),
    }
    return report


def build_parser() -> argparse.ArgumentParser:
    config = load_json(DEFAULT_DATA_DIR / "config.json", {})
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_DATA_DIR / "corpus.jsonl")
    parser.add_argument("--source-root", type=Path, default=config.get("source_root"))
    parser.add_argument("--year-start", type=int, default=int(config.get("year_start", 2001)))
    parser.add_argument("--year-end", type=int, default=int(config.get("year_end", 2026)))
    parser.add_argument("--report", type=Path, default=DEFAULT_DATA_DIR / "corpus_validation.json")
    parser.add_argument("--strict", action="store_true", help="also fail on warnings")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    source_root = args.source_root.resolve() if args.source_root else None
    report = validate(args.corpus.resolve(), source_root, args.year_start, args.year_end)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["valid"] or (args.strict and report["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
