#!/usr/bin/env python3
"""Build a traceable Reading Part A question-stem and option index.

This artifact is intentionally separate from ``corpus.jsonl``.  The sentence
trainer must never mistake a question stem or an option for passage prose.
The index supports evidence-based question-type and exam-point statistics.
Answer labels live in a separate index; neither layer claims to validate the
evidence sentence or distractor mechanism.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from extract_sentences import (
    Block,
    ExtractionError,
    _heading_number,
    _is_part_b,
    _is_section_three,
    _roman_normalized,
    clean_common_extraction_artifacts,
    extract_blocks,
    normalize_space,
    normalized_key,
    sha256_file,
)


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = SKILL_ROOT / "data"
DEFAULT_CORRECTIONS_PATH = DEFAULT_DATA_DIR / "question_text_corrections.reviewed.json"
DEFAULT_LAYOUT_CORRECTIONS_PATH = (
    DEFAULT_DATA_DIR / "question_layout_corrections.reviewed.json"
)
STANDALONE_GARBLED_FOOTER_RE = re.compile(
    r"^\s*(?:\*?-?\s*)?\ufffd?i[½¼][\s\S]*\(\s*\ufffd\s*14\s*(?:Jf|N)\s*\)\s*$",
    re.IGNORECASE,
)
QUESTION_START_RE = re.compile(r"^\s*(2[1-9]|3\d|40)\s*[.．、:)]\s*(.*)$")
ANY_NUMBERED_QUESTION_RE = re.compile(r"^\s*(\d{2})\s*[.．、:)]\s*(.*)$")
OPTION_MARKER_RE = re.compile(
    r"(?:[\[［]\s*([A-D])\s*(?:[\]］]|J)?|\(\s*([A-D])\s*\)|(?<![A-Za-z])([A-D])\s*[.．、])",
    re.IGNORECASE,
)
PAGE_NOISE_RE = re.compile(r"^(?:\d{4}\s*[-—–]\s*\d+|[-—–]?\s*\d+\s*[-—–]?)$")
QUESTION_SECTION_END_RE = re.compile(
    r"^(?:Part\s*[.\s]*B\b|Section\s*III\b|Questions?\s*4[1-9]\b|Directions\s*:)|ANSWER\s+SHEET",
    re.IGNORECASE,
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ExtractionError(f"JSON root must be an object: {path}")
    return value


def atomic_text(path: Path, text: str) -> bool:
    """Write UTF-8 text only when bytes changed."""
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


def question_count_per_article(year: int) -> int:
    return 4 if year == 2001 else 5


def expected_article_count(year: int) -> int:
    return 5 if year == 2001 else 4


def _reading_headings(blocks: list[Block], expected: int) -> list[tuple[int, int]]:
    reading_index = next(
        (
            index
            for index, block in enumerate(blocks)
            if re.search(
                r"Section\s*II\s+Reading\s+Comprehension",
                _roman_normalized(block.text),
                re.IGNORECASE,
            )
        ),
        None,
    )
    search_start = reading_index + 1 if reading_index is not None else 0
    headings: list[tuple[int, int]] = []
    for index in range(search_start, len(blocks)):
        if _is_section_three(blocks[index].text):
            break
        number = _heading_number(blocks[index].text, headings, expected)
        if number is not None and 1 <= number <= expected:
            if not any(existing == number for existing, _index in headings):
                headings.append((number, index))
        if len(headings) == expected:
            break
    if len(headings) != expected:
        raise ExtractionError(
            f"expected {expected} Reading Part A headings, found {headings}"
        )
    return headings


def _trim_noise(blocks: list[Block]) -> list[Block]:
    result = list(blocks)
    while result and (
        PAGE_NOISE_RE.fullmatch(normalize_space(result[-1].text))
        or not normalize_space(result[-1].text)
    ):
        result.pop()
    return result


def _question_region(
    region: list[Block], year: int, article: int
) -> tuple[list[Block], int]:
    """Return question blocks and their offset within an article region.

    PDF files normally preserve explicit question numbers.  Word numbering is
    frequently stored as list metadata and disappears from plain-text
    extraction.  In that documented fallback, each question is represented by
    one stem paragraph plus four option paragraphs, so the final 20/25 blocks
    form the question region.
    """
    expected_questions = question_count_per_article(year)
    start_number = 21 + (article - 1) * expected_questions
    end_number = start_number + expected_questions - 1
    for index, block in enumerate(region):
        match = QUESTION_START_RE.match(normalize_space(block.text))
        if match and start_number <= int(match.group(1)) <= end_number:
            return _trim_noise(region[index:]), index

    cleaned = _trim_noise(region)
    required = expected_questions * 5
    if len(cleaned) < required:
        raise ExtractionError(
            f"Text {article}: no explicit question number and only "
            f"{len(cleaned)} blocks; {required} are required for list fallback"
        )
    start = len(cleaned) - required
    return cleaned[start:], start


def _append_fragment(existing: str, fragment: str) -> str:
    return normalize_space(f"{existing} {fragment}" if existing else fragment)


def _clean_fragment(text: str) -> tuple[str, list[str]]:
    """Remove only an unmistakable corrupt/page-tail suffix and record it."""
    if STANDALONE_GARBLED_FOOTER_RE.fullmatch(text):
        return "", ["discarded_garbled_page_footer_block"]
    warnings: list[str] = []
    cut_positions: list[tuple[int, str]] = []
    for marker, label in (("�", "replacement_character"), ("(cid:", "cid_marker")):
        position = text.lower().find(marker.lower())
        if position >= 0:
            cut_positions.append((position, label))
    chinese = re.search(r"[\u4e00-\u9fff]", text)
    if chinese:
        cut_positions.append((chinese.start(), "non_english_page_tail"))
    garbled_footer = re.search(r"\s+\*?-?\s*i[½¼]", text, re.IGNORECASE)
    if garbled_footer:
        cut_positions.append((garbled_footer.start(), "garbled_page_footer"))
    if cut_positions:
        position, label = min(cut_positions)
        if re.search(r"[A-Za-z]", text[:position]):
            text = text[:position]
            warnings.append(f"truncated_{label}_tail")
    text, common_warnings = clean_common_extraction_artifacts(text)
    warnings.extend(common_warnings)
    return normalize_space(text), warnings


def _option_fragments(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Split one block that may contain one or several labelled options."""
    matches = list(OPTION_MARKER_RE.finditer(text))
    if not matches:
        return "", []
    prefix = normalize_space(text[: matches[0].start()])
    fragments: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        label = next(value.upper() for value in match.groups() if value)
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        fragments.append((label, normalize_space(text[match.end() : end])))
    return prefix, fragments


def _parse_explicit(
    blocks: list[Block], expected_numbers: list[int]
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_option: str | None = None

    def finish() -> None:
        nonlocal current, current_option
        if current is not None:
            current["stem"] = normalize_space(current["stem"])
            current["options"] = {
                key: normalize_space(value) for key, value in current["options"].items()
            }
            records.append(current)
        current = None
        current_option = None

    for local_index, block in enumerate(blocks):
        text = normalize_space(block.text)
        if not text or PAGE_NOISE_RE.fullmatch(text):
            continue
        if QUESTION_SECTION_END_RE.search(text):
            finish()
            break
        any_question = ANY_NUMBERED_QUESTION_RE.match(text)
        if any_question and int(any_question.group(1)) not in expected_numbers:
            finish()
            break
        question_match = QUESTION_START_RE.match(text)
        if question_match:
            number = int(question_match.group(1))
            if number not in expected_numbers:
                continue
            finish()
            stem, stem_warnings = _clean_fragment(question_match.group(2))
            current = {
                "question_number": number,
                "stem": stem,
                "options": {},
                "source_page": block.page,
                "start_block": local_index,
                "end_block": local_index,
                "extraction_warnings": stem_warnings,
            }
            continue
        if current is None:
            continue
        prefix, option_fragments = _option_fragments(text)
        if option_fragments:
            prefix, prefix_warnings = _clean_fragment(prefix)
            current["extraction_warnings"].extend(prefix_warnings)
            if (
                len(option_fragments) == 1
                and prefix in {"He", "It", "She", "That", "They", "This"}
            ):
                label, value = option_fragments[0]
                option_fragments = [(label, _append_fragment(prefix, value))]
                current["extraction_warnings"].append(
                    "reattached_repeated_option_lead_prefix"
                )
                prefix = ""
            if prefix and re.search(r"[A-Za-z]", prefix):
                if current_option is None:
                    current["stem"] = _append_fragment(current["stem"], prefix)
                else:
                    current["options"][current_option] = _append_fragment(
                        current["options"].get(current_option, ""), prefix
                    )
            for label, value in option_fragments:
                value, value_warnings = _clean_fragment(value)
                current["extraction_warnings"].extend(value_warnings)
                current_option = label
                current["options"][label] = _append_fragment(
                    current["options"].get(label, ""), value
                )
        elif current_option is None:
            text, fragment_warnings = _clean_fragment(text)
            current["extraction_warnings"].extend(fragment_warnings)
            current["stem"] = _append_fragment(current["stem"], text)
        else:
            text, fragment_warnings = _clean_fragment(text)
            current["extraction_warnings"].extend(fragment_warnings)
            current["options"][current_option] = _append_fragment(
                current["options"].get(current_option, ""), text
            )
        current["end_block"] = local_index
    finish()
    return records


def _parse_list_fallback(
    blocks: list[Block], expected_numbers: list[int]
) -> list[dict[str, Any]]:
    required = len(expected_numbers) * 5
    if len(blocks) != required:
        raise ExtractionError(
            f"list fallback expected exactly {required} blocks, found {len(blocks)}"
        )
    records: list[dict[str, Any]] = []
    for offset, number in enumerate(expected_numbers):
        chunk = blocks[offset * 5 : offset * 5 + 5]
        stem, stem_warnings = _clean_fragment(chunk[0].text)
        option_values: dict[str, str] = {}
        extraction_warnings = list(stem_warnings)
        for index, label in enumerate("ABCD", 1):
            value, value_warnings = _clean_fragment(chunk[index].text)
            option_values[label] = value
            extraction_warnings.extend(value_warnings)
        records.append(
            {
                "question_number": number,
                "stem": stem,
                "options": option_values,
                "source_page": chunk[0].page,
                "start_block": offset * 5,
                "end_block": offset * 5 + 4,
                "extraction_warnings": extraction_warnings,
            }
        )
    return records


def classify_question(stem: str) -> dict[str, Any]:
    """Classify the overt test point signaled by a question stem."""
    lower = stem.lower().replace("’", "'")
    question_type = "detail_or_reference"
    confidence = 0.74
    signals: list[str] = ["localized_paraphrase"]

    if re.search(r"\b(?:word|phrase|statement|term)\b.*\b(?:mean|means|imply|refers? to)\b", lower) or re.search(
        r"\bmost probably means\b|\bclosest in meaning\b", lower
    ):
        question_type = "word_or_phrase_meaning"
        confidence = 0.94
        signals = ["semantic_replacement", "local_context"]
    elif re.search(r"\b(?:best title|mainly about|main idea|subject of the text|best summar)", lower):
        question_type = "main_idea_or_title"
        confidence = 0.95
        signals = ["global_synthesis", "topic_scope_control"]
    elif re.search(r"\b(?:attitude|tone)\b|\bhow does the author feel\b|\bauthor's view\b", lower):
        question_type = "attitude_or_tone"
        confidence = 0.94
        signals = ["author_stance", "evaluative_language"]
    elif re.search(r"\b(?:can be inferred|may be inferred|infer from|implies? that)\b", lower):
        question_type = "inference"
        confidence = 0.94
        signals = ["supported_inference", "boundary_control"]
    elif re.search(
        r"\b(?:example|case|study|survey|experiment)\b.*\b(?:used|mentioned|cited|shows?|illustrate|demonstrate|highlight)",
        lower,
    ) or re.search(r"\b(?:mentions?|cites?|uses?)\b.*\b(?:to|because)\b", lower):
        question_type = "example_or_rhetorical_function"
        confidence = 0.90
        signals = ["evidence_claim_link", "rhetorical_role"]
    elif re.search(
        r"\b(?:purpose|introduces? (?:his|her|the) topic|concludes? the text|opens? (?:the text|paragraph)|organized|structure)\b",
        lower,
    ):
        question_type = "text_structure_or_purpose"
        confidence = 0.90
        signals = ["discourse_structure", "rhetorical_role"]
    elif re.search(r"\bwhy\b|\breason\b|\bbecause\b", lower):
        question_type = "reason_or_cause"
        confidence = 0.84
        signals = ["causal_reasoning", "localized_paraphrase"]
    elif re.search(r"\baccording to\b|\bwhich of the following is true\b|\bcan be learned\b|\bwe learn\b", lower):
        question_type = "detail_or_reference"
        confidence = 0.88
        signals = ["answer_location", "localized_paraphrase"]

    if re.search(r"\bparagraphs?\s*\d|\bpara\.?\s*\d|\bline\s*\d", lower):
        anchor = "explicit_paragraph_or_line"
    elif re.search(r"[\"“”']", stem) or question_type == "word_or_phrase_meaning":
        anchor = "quoted_expression"
    elif question_type in {"main_idea_or_title", "attitude_or_tone"}:
        anchor = "whole_text"
    elif question_type == "example_or_rhetorical_function":
        anchor = "named_example_or_evidence"
    else:
        anchor = "implicit_local_region"
    return {
        "question_type": question_type,
        "type_confidence": None,
        "type_review_status": "heuristic_unreviewed",
        "type_rule_version": "1.0",
        "anchor_type": anchor,
        "logic_signals": signals,
    }


def extract_questions(path: Path, year: int, source_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    blocks, method = extract_blocks(path)
    expected_articles = expected_article_count(year)
    per_article = question_count_per_article(year)
    headings = _reading_headings(blocks, expected_articles)
    output: list[dict[str, Any]] = []
    relative_path = str(path.resolve().relative_to(source_root.resolve()))
    source_hash = sha256_file(path)

    for position, (article, heading_index) in enumerate(headings):
        next_heading = headings[position + 1][1] if position + 1 < len(headings) else len(blocks)
        if position + 1 == len(headings):
            for index in range(heading_index + 1, len(blocks)):
                if _is_part_b(blocks[index].text) or _is_section_three(blocks[index].text):
                    next_heading = index
                    break
        region = blocks[heading_index + 1 : next_heading]
        question_blocks, region_offset = _question_region(region, year, article)
        start_number = 21 + (article - 1) * per_article
        expected_numbers = list(range(start_number, start_number + per_article))
        if any(QUESTION_START_RE.match(normalize_space(block.text)) for block in question_blocks):
            parsed = _parse_explicit(question_blocks, expected_numbers)
        else:
            parsed = _parse_list_fallback(question_blocks, expected_numbers)
        found_numbers = [item["question_number"] for item in parsed]
        if found_numbers != expected_numbers:
            raise ExtractionError(
                f"Text {article}: expected questions {expected_numbers}, found {found_numbers}"
            )
        for item in parsed:
            if sorted(item["options"]) != list("ABCD"):
                raise ExtractionError(
                    f"question {item['question_number']}: expected options A-D, "
                    f"found {sorted(item['options'])}"
                )
            if not item["stem"] or any(not item["options"][label] for label in "ABCD"):
                raise ExtractionError(f"question {item['question_number']}: empty stem or option")
            item.update(classify_question(item["stem"]))
            item.update(
                {
                    "schema_version": 1,
                    "id": f"{year}-reading-q{item['question_number']}",
                    "year": year,
                    "exam": "english_one",
                    "section": "Reading Part A",
                    "article": f"Text {article}",
                    "source_file": relative_path,
                    "source_file_sha256": source_hash,
                    "source_locator": {
                        "kind": "question_blocks",
                        "start_block": heading_index + 1 + region_offset + item.pop("start_block"),
                        "end_block": heading_index + 1 + region_offset + item.pop("end_block"),
                        "page": item["source_page"],
                    },
                    "extraction_method": method,
                    "source_status": "user_provided_question_file",
                    "provenance_status": "source_unverified",
                }
            )
            output.append(item)
    if len(output) != 20:
        raise ExtractionError(f"expected 20 Reading Part A questions, found {len(output)}")
    return output, {
        "file": relative_path,
        "source_file_sha256": source_hash,
        "extraction_method": method,
        "question_count": len(output),
    }


def _question_key(record: dict[str, Any]) -> str:
    text = " ".join(
        [record["stem"]] + [record["options"][label] for label in "ABCD"]
    )
    return normalized_key(text)


def load_reviewed_corrections(path: Path) -> list[dict[str, Any]]:
    value = load_json(path)
    if value.get("schema_version") != 1 or not isinstance(value.get("corrections"), list):
        raise ExtractionError(f"invalid reviewed-correction schema: {path}")
    corrections: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(value["corrections"], 1):
        if not isinstance(item, dict):
            raise ExtractionError(f"correction {index}: must be an object")
        record_id = str(item.get("record_id", ""))
        field = str(item.get("field", ""))
        key = (record_id, field)
        if not re.fullmatch(r"\d{4}-reading-q(?:2[1-9]|3\d|40)", record_id) or field not in {
            "stem",
            *(f"options.{label}" for label in "ABCD"),
        }:
            raise ExtractionError(f"correction {index}: invalid record_id/field")
        if key in seen:
            raise ExtractionError(f"correction {index}: duplicate target {record_id} {field}")
        seen.add(key)
        if not all(str(item.get(name, "")) for name in ("expected", "replacement", "evidence_source")):
            raise ExtractionError(f"correction {index}: missing expected/replacement/evidence_source")
        if item["expected"] == item["replacement"]:
            raise ExtractionError(f"correction {index}: expected and replacement are identical")
        corrections.append(item)
    return corrections


def load_reviewed_layout_corrections(path: Path) -> list[dict[str, Any]]:
    """Expand compact, page-reviewed stem-layout corrections."""

    value = load_json(path)
    if (
        value.get("schema_version") != 1
        or not isinstance(value.get("evidence_sources"), dict)
        or not isinstance(value.get("corrections"), dict)
    ):
        raise ExtractionError(f"invalid reviewed-layout-correction schema: {path}")
    evidence_sources = value["evidence_sources"]
    corrections: list[dict[str, Any]] = []
    for record_id, compact in value["corrections"].items():
        if not re.fullmatch(r"20\d{2}-reading-q(?:2[1-9]|3\d|40)", str(record_id)):
            raise ExtractionError(f"invalid layout-correction record_id: {record_id}")
        if not isinstance(compact, dict):
            raise ExtractionError(f"layout correction {record_id}: must be an object")
        year = str(record_id)[:4]
        evidence_source = evidence_sources.get(year)
        expected = compact.get("expected")
        replacement = compact.get("replacement")
        page = compact.get("page")
        if (
            not isinstance(evidence_source, str)
            or not evidence_source
            or not isinstance(expected, str)
            or not expected
            or not isinstance(replacement, str)
            or not replacement
            or expected == replacement
            or not isinstance(page, int)
            or page < 1
        ):
            raise ExtractionError(f"layout correction {record_id}: invalid fields")
        corrections.append(
            {
                "record_id": str(record_id),
                "field": "stem",
                "expected": expected,
                "replacement": replacement,
                "evidence_source": evidence_source,
                "evidence_method": "visual_page_layout_review",
                "evidence_page": page,
                "evidence_strength": str(compact.get("evidence_strength", "high")),
                "correction_class": "layout_normalization",
                "note": str(
                    compact.get(
                        "note",
                        "Blank or spacing normalized from the rendered question page.",
                    )
                ),
            }
        )
    return corrections


def _question_field(record: dict[str, Any], field: str) -> str:
    if field == "stem":
        return str(record["stem"])
    return str(record["options"][field.split(".", 1)[1]])


def _set_question_field(record: dict[str, Any], field: str, value: str) -> None:
    if field == "stem":
        record["stem"] = value
    else:
        record["options"][field.split(".", 1)[1]] = value


def apply_reviewed_corrections(
    records: list[dict[str, Any]],
    corrections: list[dict[str, Any]],
    source_root: Path | None = None,
) -> set[tuple[str, str]]:
    """Apply exact preconditioned corrections backed by reviewed local evidence."""

    index = {str(record["id"]): record for record in records}
    applied: set[tuple[str, str]] = set()
    for item in corrections:
        record_id = str(item["record_id"])
        record = index.get(record_id)
        if record is None:
            continue
        field = str(item["field"])
        current = _question_field(record, field)
        expected = str(item["expected"])
        replacement = str(item["replacement"])
        if current != expected:
            raise ExtractionError(
                f"reviewed correction precondition changed for {record_id} {field}: "
                f"expected {expected!r}, found {current!r}"
            )
        _set_question_field(record, field, replacement)
        evidence_source = str(item["evidence_source"])
        evidence_hash: str | None = None
        if source_root is not None:
            evidence_path = source_root / evidence_source
            if not evidence_path.is_file():
                raise ExtractionError(
                    f"reviewed correction evidence source is missing: {evidence_source}"
                )
            evidence_hash = sha256_file(evidence_path)
        record.setdefault("extraction_warnings", []).append(
            f"reviewed_text_correction:{field}"
        )
        record.setdefault("reviewed_text_corrections", []).append(
            {
                "field": field,
                "original_extraction": expected,
                "replacement": replacement,
                "evidence_source": evidence_source,
                "evidence_source_sha256": evidence_hash,
                "evidence_method": str(
                    item.get("evidence_method", "alternate_source_text_review")
                ),
                "evidence_page": item.get("evidence_page"),
                "evidence_strength": item.get("evidence_strength"),
                "evidence_url": item.get("evidence_url"),
                "correction_class": item.get("correction_class", "text_correction"),
                "note": str(item.get("note", "")),
            }
        )
        applied.add((record_id, field))
    return applied


def corroborate(
    selected: list[dict[str, Any]], alternatives: list[tuple[list[dict[str, Any]], dict[str, Any]]]
) -> dict[str, int]:
    counts = Counter()
    alternate_indexes = [
        ({item["question_number"]: item for item in records}, info)
        for records, info in alternatives
    ]
    for record in selected:
        target = _question_key(record)
        best_similarity = 0.0
        best: dict[str, Any] | None = None
        alternates: list[dict[str, Any]] = []
        for index, info in alternate_indexes:
            candidate = index.get(record["question_number"])
            if candidate is None:
                continue
            candidate_key = _question_key(candidate)
            similarity = difflib.SequenceMatcher(
                None, target, candidate_key, autojunk=False
            ).ratio()
            alternate = {
                "source_file": info["file"],
                "source_page": candidate.get("source_page"),
                "similarity": round(similarity, 4),
            }
            alternates.append(alternate)
            if similarity > best_similarity:
                best_similarity = similarity
                best = alternate
        record["alternate_sources"] = alternates
        record["corroboration"] = best
        if record.get("extraction_warnings"):
            record["text_status"] = "auto_extracted"
            record["needs_manual_review"] = True
            counts["unmatched"] += 1
        elif best_similarity == 1.0:
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
    corrections_path: Path | None = DEFAULT_CORRECTIONS_PATH,
    layout_corrections_path: Path | None = DEFAULT_LAYOUT_CORRECTIONS_PATH,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    source_root = Path(manifest["source_root"])
    all_records: list[dict[str, Any]] = []
    years_report: dict[str, Any] = {}
    failed_years: list[int] = []
    if corrections_path is not None and not corrections_path.exists():
        raise SystemExit(f"required reviewed-correction file is missing: {corrections_path}")
    if layout_corrections_path is not None and not layout_corrections_path.exists():
        raise SystemExit(
            f"required reviewed-layout-correction file is missing: {layout_corrections_path}"
        )
    all_corrections = load_reviewed_corrections(corrections_path) if corrections_path else []
    if layout_corrections_path is not None:
        all_corrections.extend(
            load_reviewed_layout_corrections(layout_corrections_path)
        )
    targets = [
        (str(item["record_id"]), str(item["field"])) for item in all_corrections
    ]
    if len(targets) != len(set(targets)):
        duplicates = sorted(target for target, count in Counter(targets).items() if count > 1)
        raise SystemExit(f"duplicate reviewed-correction targets: {duplicates}")
    corrections = [
        item
        for item in all_corrections
        if year_start <= int(str(item["record_id"])[:4]) <= year_end
    ]
    applied_corrections: set[tuple[str, str]] = set()

    for year in range(year_start, year_end + 1):
        entry = manifest.get("years", {}).get(str(year), {})
        selected_relative = entry.get("selected_source")
        if not selected_relative:
            failed_years.append(year)
            years_report[str(year)] = {
                "status": "unavailable",
                "reason": entry.get("status", "no selected source"),
            }
            continue
        selected_path = source_root / selected_relative
        try:
            selected, selected_info = extract_questions(selected_path, year, source_root)
        except (ExtractionError, OSError, ValueError) as exc:
            failed_years.append(year)
            years_report[str(year)] = {"status": "error", "error": str(exc)}
            continue

        year_corrections = [
            item for item in corrections if str(item["record_id"]).startswith(f"{year}-")
        ]
        applied_corrections.update(
            apply_reviewed_corrections(selected, year_corrections, source_root)
        )

        alternatives: list[tuple[list[dict[str, Any]], dict[str, Any]]] = []
        alternate_errors: list[dict[str, str]] = []
        for candidate in entry.get("candidates", []):
            relative = candidate.get("file")
            if candidate.get("status") != "ok" or not relative or relative == selected_relative:
                continue
            try:
                alternate_records, alternate_info = extract_questions(
                    source_root / relative, year, source_root
                )
                alternatives.append((alternate_records, alternate_info))
            except (ExtractionError, OSError, ValueError) as exc:
                alternate_errors.append({"file": relative, "error": str(exc)})
        match_counts = corroborate(selected, alternatives)
        all_records.extend(selected)
        years_report[str(year)] = {
            "status": "built",
            "selected_source": selected_info["file"],
            "question_count": len(selected),
            "corroboration": match_counts,
            "alternate_errors": alternate_errors,
        }

    allowed = set(allowed_unusable_years or set())
    unexpected = sorted(set(failed_years) - allowed)
    if unexpected and not allow_incomplete:
        raise SystemExit(
            f"refusing incomplete question index; unexpected failed years={unexpected}"
        )
    if not all_records:
        raise SystemExit("no question records; refusing to overwrite the question index")
    correction_targets = {
        (str(item["record_id"]), str(item["field"])) for item in corrections
    }
    unapplied_corrections = sorted(correction_targets - applied_corrections)
    if unapplied_corrections:
        raise SystemExit(
            f"reviewed question corrections were not applied: {unapplied_corrections}"
        )
    ordered = sorted(all_records, key=lambda item: (item["year"], item["question_number"]))
    if output_path.exists() and not allow_regression:
        try:
            old_records = [
                json.loads(line)
                for line in output_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"existing question index cannot be audited: {exc}") from exc
        old_years = {int(item["year"]) for item in old_records}
        new_years = {int(item["year"]) for item in ordered}
        if len(ordered) < len(old_records) or not old_years.issubset(new_years):
            raise SystemExit(
                f"refusing question-index regression: old={len(old_records)}, new={len(ordered)}"
            )
    payload = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in ordered
    )
    changed = atomic_text(output_path, payload)
    report = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "manifest": str(manifest_path),
        "output": str(output_path),
        "records": len(ordered),
        "built_years": sorted({item["year"] for item in ordered}),
        "failed_years": failed_years,
        "output_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "output_changed": changed,
        "reviewed_corrections_path": str(corrections_path) if corrections_path else None,
        "reviewed_corrections_sha256": (
            sha256_file(corrections_path)
            if corrections_path is not None and corrections_path.exists()
            else None
        ),
        "reviewed_corrections_applied": len(applied_corrections),
        "reviewed_layout_corrections_path": (
            str(layout_corrections_path) if layout_corrections_path else None
        ),
        "reviewed_layout_corrections_sha256": (
            sha256_file(layout_corrections_path)
            if layout_corrections_path is not None and layout_corrections_path.exists()
            else None
        ),
        "years": years_report,
    }
    atomic_text(
        report_path,
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    return report


def build_parser() -> argparse.ArgumentParser:
    config_path = DEFAULT_DATA_DIR / "config.json"
    config = load_json(config_path) if config_path.exists() else {}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_DATA_DIR / "source_manifest.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_DATA_DIR / "question_index.jsonl")
    parser.add_argument("--report", type=Path, default=DEFAULT_DATA_DIR / "question_build_report.json")
    parser.add_argument("--corrections", type=Path, default=DEFAULT_CORRECTIONS_PATH)
    parser.add_argument(
        "--layout-corrections", type=Path, default=DEFAULT_LAYOUT_CORRECTIONS_PATH
    )
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
        args.manifest.resolve(),
        args.output.resolve(),
        args.report.resolve(),
        args.year_start,
        args.year_end,
        set(args.allowed_unusable_year),
        args.allow_incomplete,
        args.allow_regression,
        args.corrections.resolve(),
        args.layout_corrections.resolve(),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
