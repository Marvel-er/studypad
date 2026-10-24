#!/usr/bin/env python3
"""Validate the sentence, question, vocabulary, and source-traceability layers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from build_question_index import (
    DEFAULT_CORRECTIONS_PATH as QUESTION_CORRECTIONS_PATH,
    DEFAULT_LAYOUT_CORRECTIONS_PATH as QUESTION_LAYOUT_CORRECTIONS_PATH,
    load_reviewed_corrections,
    load_reviewed_layout_corrections,
)
from build_vocabulary import is_safe, normalize_token
from classify_sentences import WORD_RE
from extract_sentences import ExtractionError, load_text_correction_config
from validate_corpus import validate as validate_sentence_corpus


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = SKILL_ROOT / "data"
QUESTION_TYPES = {
    "attitude_or_tone", "detail_or_reference", "example_or_rhetorical_function",
    "inference", "main_idea_or_title", "reason_or_cause",
    "text_structure_or_purpose", "word_or_phrase_meaning",
}
PASSAGE_PAGE_TAIL_RE = re.compile(
    r"(?:i½|\(\s*\ufffd\s*\d+\s*(?:jf|n)\s*\))",
    re.IGNORECASE,
)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def vocabulary_input_hash_errors(
    vocabulary_stats: dict[str, Any],
    passage_path: Path,
    corpus_path: Path,
    question_path: Path,
) -> list[str]:
    """Verify that vocabulary lineage hashes still match all tokenized inputs."""

    declared = vocabulary_stats.get("input_sha256")
    if not isinstance(declared, dict):
        return ["vocabulary_stats: input_sha256 is missing or invalid"]
    expected_paths = {
        "passage_index_jsonl": passage_path,
        "sentence_candidate_corpus_jsonl": corpus_path,
        "question_index_jsonl": question_path,
    }
    errors: list[str] = []
    for label, path in expected_paths.items():
        expected_hash = sha256_path(path)
        if declared.get(label) != expected_hash:
            errors.append(f"vocabulary_stats: input_sha256 mismatch for {label}")
    return errors


def passage_corruption_reasons(text: str) -> list[str]:
    """Return unmistakable extraction artifacts that must not reach vocabulary."""

    reasons: list[str] = []
    if "\ufffd" in text:
        reasons.append("replacement_character")
    if "(cid:" in text.lower():
        reasons.append("pdf_cid_marker")
    if "^^" in text:
        reasons.append("double_caret_quote_artifact")
    if re.search(r"[\u4e00-\u9fff]", text):
        reasons.append("cjk_extraction_artifact")
    if PASSAGE_PAGE_TAIL_RE.search(text):
        reasons.append("garbled_page_footer")
    if text.count("“") != text.count("”"):
        reasons.append("unbalanced_curly_double_quotes")
    if text.count('"') % 2:
        reasons.append("unbalanced_straight_double_quotes")
    if re.search(r"(?<=[A-Za-z])“|”(?=[A-Za-z])", text):
        reasons.append("glued_double_quote_boundary")
    if re.search(r'(?<=[A-Za-z])"(?=[A-Za-z])', text):
        reasons.append("glued_straight_quote_between_letters")
    if re.search(r"(?<!www)(?<=[a-z])[.!?](?=[A-Z])", text):
        reasons.append("missing_space_after_sentence_punctuation")
    if re.search(r"(?<=[a-z]),(?=[A-Za-z])", text):
        reasons.append("missing_space_after_comma")
    if re.search(r"\b[A-Za-z]+s[’'][a-z]{3,}\b", text):
        reasons.append("glued_plural_possessive_boundary")
    if re.search(r"\b[A-Za-z]+\s+[’']\s+[A-Za-z]+\b", text):
        reasons.append("spaced_apostrophe_artifact")
    if re.search(r"<[A-Za-z]", text):
        reasons.append("angle_bracket_ocr_artifact")
    if re.search(
        r"\bfbr\b|[A-Za-z]5s\b|s[59]\b|[A-Za-z]9\s+s\b|[A-Za-z]55\b|~~",
        text,
        re.IGNORECASE,
    ):
        reasons.append("known_ocr_glyph_artifact")
    correction_config = load_text_correction_config()
    for token in correction_config["token_replacements"]:
        if re.search(rf"(?<![A-Za-z]){re.escape(token)}(?![A-Za-z])", text):
            reasons.append(f"reviewed_mixed_case_token:{token}")
    for correction in correction_config["phrase_corrections"]:
        expected = str(correction.get("expected", ""))
        if expected and expected in text:
            reasons.append("unapplied_reviewed_phrase_correction")
    return reasons


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(path)
    output: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"{path}:{line_number}: record must be an object")
            output.append(value)
    return output


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if path.exists() and path.read_bytes() == payload:
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _record_fields(
    passage_records: list[dict[str, Any]], question_records: list[dict[str, Any]]
) -> dict[tuple[str, str], str]:
    fields: dict[tuple[str, str], str] = {}
    for record in passage_records:
        fields[(record["id"], "text")] = str(record["text"])
    for record in question_records:
        fields[(record["id"], "stem")] = str(record["stem"])
        for label in "ABCD":
            fields[(record["id"], f"options.{label}")] = str(record["options"][label])
    return fields


def _word_key(text: str) -> str:
    return " ".join(token.group(0).lower().replace("’", "'") for token in WORD_RE.finditer(text))


def question_overlap_errors(
    passages: list[dict[str, Any]],
    corpus: list[dict[str, Any]],
    questions: list[dict[str, Any]],
) -> list[str]:
    """Reject article tails containing multiple exact question/option fragments.

    One quoted phrase can legitimately occur in both prose and a question.  Two
    independent six-word fragments from the same question set are treated as
    unmistakable cross-layer contamination.
    """

    fragments: dict[tuple[int, int], list[tuple[str, str]]] = defaultdict(list)
    for question in questions:
        article_match = re.search(r"\d+", str(question.get("article", "")))
        if article_match is None:
            continue
        key = (int(question["year"]), int(article_match.group(0)))
        values = [(f"q{question.get('question_number')}.stem", str(question.get("stem", "")))]
        options = question.get("options")
        if isinstance(options, dict):
            values.extend(
                (f"q{question.get('question_number')}.{label}", str(options.get(label, "")))
                for label in "ABCD"
            )
        for label, value in values:
            normalized = _word_key(value)
            if len(normalized.split()) >= 6:
                fragments[key].append((label, normalized))

    errors: list[str] = []
    for passage in passages:
        article_match = re.search(r"\d+", str(passage.get("article", "")))
        if article_match is None:
            continue
        key = (int(passage["year"]), int(article_match.group(0)))
        passage_key = _word_key(str(passage.get("text", "")))
        matches = [label for label, fragment in fragments.get(key, []) if fragment in passage_key]
        if len(set(matches)) >= 2:
            errors.append(
                f"passage {passage.get('id')}: question/option tail contamination: "
                + ", ".join(sorted(set(matches))[:4])
            )

    corpus_matches: dict[tuple[int, int], set[str]] = defaultdict(set)
    for sentence in corpus:
        article_match = re.search(r"\d+", str(sentence.get("article", "")))
        if article_match is None:
            continue
        key = (int(sentence["year"]), int(article_match.group(0)))
        sentence_key = _word_key(str(sentence.get("original", "")))
        if len(sentence_key.split()) < 6:
            continue
        for label, fragment in fragments.get(key, []):
            if fragment in sentence_key or sentence_key in fragment:
                corpus_matches[key].add(label)
    for (year, article), matches in sorted(corpus_matches.items()):
        if len(matches) >= 2:
            errors.append(
                f"corpus {year}-reading-text{article}: question/option contamination: "
                + ", ".join(sorted(matches)[:4])
            )
    return errors


def validate(
    corpus_path: Path,
    passage_path: Path,
    question_path: Path,
    answer_path: Path,
    occurrence_path: Path,
    lexicon_path: Path,
    vocabulary_stats_path: Path,
    source_root: Path,
    year_start: int,
    year_end: int,
    allowed_unusable_years: set[int] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        corpus = load_jsonl(corpus_path)
        passages = load_jsonl(passage_path)
        questions = load_jsonl(question_path)
        answers = load_jsonl(answer_path)
        occurrences = load_jsonl(occurrence_path)
        lexicon = load_jsonl(lexicon_path)
        vocabulary_stats = load_json(vocabulary_stats_path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError, ExtractionError) as exc:
        return {"valid": False, "errors": [str(exc)], "warnings": []}

    sentence_report = validate_sentence_corpus(
        corpus_path, source_root, year_start, year_end
    )
    errors.extend(f"sentence_corpus: {item}" for item in sentence_report["errors"])
    warnings.extend(f"sentence_corpus: {item}" for item in sentence_report["warnings"])

    allowed_unusable_years = set(allowed_unusable_years or set())
    passage_config = load_text_correction_config()
    configured_gap_map: dict[tuple[int, int], dict[str, Any]] = {}
    for configured_gap in passage_config["known_source_gaps"]:
        if not isinstance(configured_gap, dict):
            errors.append("passage_completeness: configured gap must be an object")
            continue
        try:
            gap_key = (int(configured_gap["year"]), int(configured_gap["article"]))
        except (KeyError, TypeError, ValueError):
            errors.append("passage_completeness: configured gap has invalid target")
            continue
        if gap_key in configured_gap_map:
            errors.append(f"passage_completeness: duplicate configured target {gap_key}")
        configured_gap_map[gap_key] = configured_gap

    passages_by_year: dict[int, list[str]] = defaultdict(list)
    passage_ids: set[str] = set()
    passage_source_hash_cache: dict[Path, str] = {}
    passage_records_by_key: dict[tuple[int, int], dict[str, Any]] = {}
    reviewed_passage_correction_count = 0
    known_incomplete_passage_ids: set[str] = set()
    for record in passages:
        passage_id = str(record.get("id", "<missing>"))
        if passage_id in passage_ids:
            errors.append(f"passage: duplicate id {passage_id}")
        passage_ids.add(passage_id)
        try:
            year = int(record["year"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"passage {passage_id}: invalid year")
            continue
        article = str(record.get("article", ""))
        passages_by_year[year].append(article)
        article_match = re.fullmatch(r"Text ([1-5])", article)
        if article_match:
            passage_records_by_key[(year, int(article_match.group(1)))] = record
        passage_text = str(record.get("text", ""))
        if not passage_text.strip():
            errors.append(f"passage {passage_id}: empty text")
        for reason in passage_corruption_reasons(passage_text):
            errors.append(f"passage {passage_id}: corrupt extraction marker: {reason}")
        completeness_status = record.get("source_completeness_status")
        safe_for_training = record.get("safe_for_training")
        known_gap = record.get("known_source_gap")
        if completeness_status == "no_known_gap":
            if safe_for_training is not True or known_gap is not None:
                errors.append(f"passage {passage_id}: inconsistent complete-source metadata")
        elif completeness_status == "known_incomplete_source":
            known_incomplete_passage_ids.add(passage_id)
            if safe_for_training is not False or not isinstance(known_gap, dict):
                errors.append(f"passage {passage_id}: inconsistent incomplete-source metadata")
            else:
                gap_evidence = source_root / str(known_gap.get("evidence_source", ""))
                evidence_pages = known_gap.get("evidence_pages")
                if not str(known_gap.get("description", "")).strip():
                    errors.append(f"passage {passage_id}: source gap lacks description")
                if (
                    not isinstance(evidence_pages, list)
                    or not evidence_pages
                    or any(not isinstance(page, int) or page < 1 for page in evidence_pages)
                ):
                    errors.append(f"passage {passage_id}: source gap has invalid evidence pages")
                if not gap_evidence.is_file():
                    errors.append(f"passage {passage_id}: source-gap evidence missing")
                elif sha256_path(gap_evidence) != known_gap.get("evidence_source_sha256"):
                    errors.append(f"passage {passage_id}: source-gap evidence hash mismatch")
                urls = known_gap.get("external_corroboration_urls")
                if not isinstance(urls, list) or any(
                    not isinstance(url, str) or not url.startswith(("https://", "http://"))
                    for url in urls
                ):
                    errors.append(f"passage {passage_id}: invalid source-gap corroboration URLs")
        else:
            errors.append(f"passage {passage_id}: missing or invalid source completeness status")
        extraction_warnings = record.get("extraction_warnings", [])
        if not isinstance(extraction_warnings, list) or not all(
            isinstance(item, str) for item in extraction_warnings
        ):
            errors.append(f"passage {passage_id}: extraction_warnings must be a string list")
        reviewed_corrections = record.get("reviewed_text_corrections", [])
        if not isinstance(reviewed_corrections, list):
            errors.append(f"passage {passage_id}: reviewed_text_corrections must be a list")
            reviewed_corrections = []
        for correction in reviewed_corrections:
            if not isinstance(correction, dict):
                errors.append(f"passage {passage_id}: malformed reviewed correction")
                continue
            reviewed_passage_correction_count += 1
            if correction.get("replacement") not in passage_text:
                errors.append(f"passage {passage_id}: reviewed replacement absent")
            evidence_file = source_root / str(correction.get("evidence_source", ""))
            if not evidence_file.is_file():
                errors.append(f"passage {passage_id}: correction evidence source missing")
            elif hashlib.sha256(evidence_file.read_bytes()).hexdigest() != correction.get(
                "evidence_source_sha256"
            ):
                errors.append(f"passage {passage_id}: correction evidence hash mismatch")
        source_file = source_root / str(record.get("source_file", ""))
        if not source_file.is_file():
            errors.append(f"passage {passage_id}: source file missing")
        else:
            if source_file not in passage_source_hash_cache:
                passage_source_hash_cache[source_file] = hashlib.sha256(source_file.read_bytes()).hexdigest()
            if passage_source_hash_cache[source_file] != record.get("source_file_sha256"):
                errors.append(f"passage {passage_id}: source hash mismatch")
        status = record.get("text_status")
        corroboration = record.get("corroboration")
        if status == "cross_checked" and (
            not isinstance(corroboration, dict) or corroboration.get("similarity") != 1.0
        ):
            errors.append(f"passage {passage_id}: exact status lacks exact corroboration")
        if status in {"auto_extracted", "fuzzy_cross_checked"} and not record.get("needs_manual_review"):
            errors.append(f"passage {passage_id}: non-exact text must require manual review")
    for year in range(year_start, year_end + 1):
        articles = sorted(passages_by_year.get(year, []))
        expected = [f"Text {number}" for number in range(1, 6 if year == 2001 else 5)]
        if not articles and year in allowed_unusable_years:
            warnings.append(f"passage_index: allowed unavailable year {year}")
        elif articles != expected:
            errors.append(f"passage_index: {year} expected {expected}, found {articles}")

    for configured in passage_config["phrase_corrections"]:
        key = (int(configured["year"]), int(configured["article"]))
        if not year_start <= key[0] <= year_end:
            continue
        passage = passage_records_by_key.get(key)
        if passage is None:
            errors.append(f"passage_corrections: missing target {key}")
            continue
        matches = [
            item
            for item in passage.get("reviewed_text_corrections", [])
            if isinstance(item, dict)
            and item.get("original_extraction") == configured.get("expected")
        ]
        if len(matches) != 1:
            errors.append(f"passage_corrections: {key} expected one applied correction")
            continue
        for config_key, record_key in (
            ("replacement", "replacement"),
            ("evidence_source", "evidence_source"),
            ("evidence_method", "evidence_method"),
        ):
            if matches[0].get(record_key) != configured.get(config_key):
                errors.append(f"passage_corrections: {key} metadata mismatch for {config_key}")

    for key, configured_gap in configured_gap_map.items():
        if not year_start <= key[0] <= year_end:
            continue
        passage = passage_records_by_key.get(key)
        if passage is None:
            errors.append(f"passage_completeness: missing configured target {key}")
            continue
        gap = passage.get("known_source_gap")
        if (
            passage.get("source_completeness_status") != "known_incomplete_source"
            or passage.get("safe_for_training") is not False
            or not isinstance(gap, dict)
        ):
            errors.append(f"passage_completeness: configured gap not applied to {key}")
            continue
        for config_key in (
            "description",
            "evidence_source",
            "evidence_pages",
            "evidence_method",
            "external_corroboration_urls",
            "note",
        ):
            expected_value = configured_gap.get(config_key)
            if config_key == "evidence_method" and expected_value is None:
                expected_value = "visual_structure_review"
            if config_key in {"external_corroboration_urls"} and expected_value is None:
                expected_value = []
            if config_key == "note" and expected_value is None:
                expected_value = ""
            if gap.get(config_key) != expected_value:
                errors.append(
                    f"passage_completeness: {key} metadata mismatch for {config_key}"
                )

    expected_gap_ids = {
        f"{year}-reading-text{article}-passage"
        for year, article in configured_gap_map
        if year_start <= year <= year_end
    }
    if known_incomplete_passage_ids != expected_gap_ids:
        errors.append(
            "passage_completeness: applied known-incomplete passage set differs from configuration"
        )

    question_ids: set[str] = set()
    questions_by_id: dict[str, dict[str, Any]] = {}
    questions_by_year: dict[int, list[int]] = defaultdict(list)
    file_hash_cache: dict[Path, str] = {}
    for record in questions:
        question_id = str(record.get("id", "<missing>"))
        if question_id in question_ids:
            errors.append(f"question: duplicate id {question_id}")
        question_ids.add(question_id)
        questions_by_id[question_id] = record
        try:
            year = int(record["year"])
            number = int(record["question_number"])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"question {question_id}: invalid year/question_number: {exc}")
            continue
        questions_by_year[year].append(number)
        if question_id != f"{year}-reading-q{number}":
            errors.append(f"question {question_id}: unstable id")
        if not 21 <= number <= 40:
            errors.append(f"question {question_id}: number outside 21-40")
        options = record.get("options")
        if not isinstance(options, dict) or sorted(options) != list("ABCD"):
            errors.append(f"question {question_id}: options must contain A-D exactly")
        elif any(not str(options[label]).strip() for label in "ABCD"):
            errors.append(f"question {question_id}: empty option")
        if not str(record.get("stem", "")).strip():
            errors.append(f"question {question_id}: empty stem")
        if record.get("question_type") not in QUESTION_TYPES:
            errors.append(f"question {question_id}: unknown question_type")
        if record.get("type_confidence") is not None:
            errors.append(f"question {question_id}: uncalibrated type confidence must be null")
        if record.get("type_review_status") not in {"heuristic_unreviewed", "human_verified"}:
            errors.append(f"question {question_id}: invalid type_review_status")
        texts = [str(record.get("stem", ""))]
        if isinstance(options, dict):
            texts.extend(str(options.get(label, "")) for label in "ABCD")
        combined = " ".join(texts)
        if any(marker.lower() in combined.lower() for marker in ("Part B", "ANSWER SHEET", "Questions 41", "Directions:")):
            errors.append(f"question {question_id}: later-section contamination")
        if "�" in combined or "(cid:" in combined.lower() or re.search(r"[\u4e00-\u9fff]", combined):
            errors.append(f"question {question_id}: corrupt/non-English extraction marker")
        if re.search(r"(?:i[½¼]|\^\^)", combined, re.IGNORECASE):
            errors.append(f"question {question_id}: garbled page-tail/quote marker")
        if re.search(r"[A-Za-z]{2,}[59](?:s)?\b|\bfbr\b", combined, re.IGNORECASE):
            errors.append(f"question {question_id}: likely OCR word corruption")
        if re.search(
            r"\b(?:faUed|kecping|learmed|ldaho|Raviteh)\b|\boff er\b|"
            r"\bIn contras\b|\bMc Whorter\b|\bSlaves owners\b|"
            r"\bKing Juan Carl\b|\bvital dues\b|\bdeep-root belief\b|"
            r"\bfocus on trivialities\b|\bMillennial's opinions\b|\bERA’S\b",
            combined,
        ):
            errors.append(f"question {question_id}: known reviewed text anomaly remains")
        if re.search(r"\?\s+(?:He|It|She|That|They|This)$", texts[0]):
            errors.append(f"question {question_id}: likely option-prefix shift in stem")
        if combined.count("“") != combined.count("”") or combined.count('"') % 2:
            errors.append(f"question {question_id}: unmatched double quotation mark")
        if re.search(r"(?<!_)_{1,7}(?!_)|(?<!_)_{9,}(?!_)", texts[0]):
            errors.append(f"question {question_id}: non-canonical blank width")
        if re.search(r"\w________|\?\s+________\.$|\s+\.$", texts[0]):
            errors.append(f"question {question_id}: non-canonical blank spacing")
        if question_id == "2021-reading-q38" and (
            texts[0].endswith(" It")
            or not isinstance(options, dict)
            or any(not str(options.get(label, "")).startswith("It ") for label in "ABCD")
        ):
            errors.append(f"question {question_id}: reviewed option-prefix invariant failed")
        if len(WORD_RE.findall(texts[0])) > 100:
            errors.append(f"question {question_id}: implausibly long stem")
        if isinstance(options, dict):
            for label in "ABCD":
                if len(WORD_RE.findall(str(options.get(label, "")))) > 80:
                    errors.append(f"question {question_id}: implausibly long option {label}")
        source_file = source_root / str(record.get("source_file", ""))
        if not source_file.is_file():
            errors.append(f"question {question_id}: source file missing: {source_file}")
        else:
            if source_file not in file_hash_cache:
                file_hash_cache[source_file] = hashlib.sha256(source_file.read_bytes()).hexdigest()
            if file_hash_cache[source_file] != record.get("source_file_sha256"):
                errors.append(f"question {question_id}: source hash mismatch")
        status = record.get("text_status")
        corroboration = record.get("corroboration")
        if status == "cross_checked" and (
            not isinstance(corroboration, dict) or corroboration.get("similarity") != 1.0
        ):
            errors.append(f"question {question_id}: exact status lacks exact corroboration")
        if status in {"auto_extracted", "fuzzy_cross_checked"} and not record.get("needs_manual_review"):
            errors.append(f"question {question_id}: non-exact text must require manual review")
        corrections = record.get("reviewed_text_corrections", [])
        if corrections and not isinstance(corrections, list):
            errors.append(f"question {question_id}: reviewed_text_corrections must be a list")
        elif isinstance(corrections, list):
            for correction in corrections:
                if not isinstance(correction, dict):
                    errors.append(f"question {question_id}: malformed reviewed correction")
                    continue
                evidence_file = source_root / str(correction.get("evidence_source", ""))
                if not evidence_file.is_file():
                    errors.append(f"question {question_id}: correction evidence source missing")
                elif hashlib.sha256(evidence_file.read_bytes()).hexdigest() != correction.get(
                    "evidence_source_sha256"
                ):
                    errors.append(f"question {question_id}: correction evidence hash mismatch")
                field = str(correction.get("field", ""))
                if field == "stem":
                    corrected_value = str(record.get("stem", ""))
                elif field.startswith("options.") and isinstance(options, dict):
                    corrected_value = str(options.get(field.split(".", 1)[1], ""))
                else:
                    corrected_value = ""
                if corrected_value != correction.get("replacement"):
                    errors.append(f"question {question_id}: reviewed correction value mismatch")

    reviewed_correction_count = 0
    try:
        configured_corrections = load_reviewed_corrections(QUESTION_CORRECTIONS_PATH)
        configured_corrections.extend(
            load_reviewed_layout_corrections(QUESTION_LAYOUT_CORRECTIONS_PATH)
        )
        configured_targets = [
            (str(item["record_id"]), str(item["field"]))
            for item in configured_corrections
        ]
        if len(configured_targets) != len(set(configured_targets)):
            raise ValueError("duplicate correction target across correction files")
    except (FileNotFoundError, ValueError, json.JSONDecodeError, ExtractionError) as exc:
        errors.append(f"question_corrections: {exc}")
        configured_corrections = []
    for configured in configured_corrections:
        if not isinstance(configured, dict):
            errors.append("question_corrections: non-object correction")
            continue
        record_id = str(configured.get("record_id", ""))
        field = str(configured.get("field", ""))
        record = questions_by_id.get(record_id)
        if record is None:
            errors.append(f"question_corrections: missing target record {record_id}")
            continue
        matches = [
            item
            for item in record.get("reviewed_text_corrections", [])
            if isinstance(item, dict) and item.get("field") == field
        ]
        if len(matches) != 1:
            errors.append(
                f"question_corrections: {record_id} {field} expected one applied correction"
            )
            continue
        reviewed_correction_count += 1
        applied = matches[0]
        if applied.get("original_extraction") != configured.get("expected"):
            errors.append(
                f"question_corrections: {record_id} {field} metadata mismatch for expected"
            )
        for key in (
            "replacement",
            "evidence_source",
            "evidence_method",
            "evidence_page",
            "evidence_strength",
            "evidence_url",
            "correction_class",
        ):
            configured_value = configured.get(key)
            if key == "correction_class" and configured_value is None:
                configured_value = "text_correction"
            if applied.get(key) != configured_value:
                errors.append(
                    f"question_corrections: {record_id} {field} metadata mismatch for {key}"
                )

    for year in range(year_start, year_end + 1):
        numbers = sorted(questions_by_year.get(year, []))
        if year in allowed_unusable_years and not numbers:
            warnings.append(f"question_index: allowed unavailable year {year}")
        elif numbers != list(range(21, 41)):
            errors.append(f"question_index: {year} expected q21-q40, found {numbers}")

    errors.extend(question_overlap_errors(passages, corpus, questions))

    answer_ids: set[str] = set()
    answers_by_year: dict[int, list[int]] = defaultdict(list)
    answer_keys: set[tuple[int, int]] = set()
    answer_source_hash_cache: dict[Path, str] = {}
    for record in answers:
        answer_id = str(record.get("id", "<missing>"))
        if answer_id in answer_ids:
            errors.append(f"answer: duplicate id {answer_id}")
        answer_ids.add(answer_id)
        try:
            year = int(record["year"])
            number = int(record["question_number"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"answer {answer_id}: invalid year/question_number")
            continue
        answers_by_year[year].append(number)
        answer_keys.add((year, number))
        if answer_id != f"{year}-reading-a{number}":
            errors.append(f"answer {answer_id}: unstable id")
        if record.get("answer") not in list("ABCD"):
            errors.append(f"answer {answer_id}: answer must be A-D")
        if record.get("source_status") != "user_provided_answer_file":
            errors.append(f"answer {answer_id}: invalid source_status")
        if record.get("provenance_status") != "source_unverified":
            errors.append(f"answer {answer_id}: provenance must remain source_unverified")
        source_file = source_root / str(record.get("source_file", ""))
        if not source_file.is_file():
            errors.append(f"answer {answer_id}: source file missing")
        else:
            if source_file not in answer_source_hash_cache:
                answer_source_hash_cache[source_file] = hashlib.sha256(source_file.read_bytes()).hexdigest()
            if answer_source_hash_cache[source_file] != record.get("source_file_sha256"):
                errors.append(f"answer {answer_id}: source hash mismatch")
    for year in range(year_start, year_end + 1):
        numbers = sorted(answers_by_year.get(year, []))
        if numbers != list(range(21, 41)):
            errors.append(f"answer_index: {year} expected a21-a40, found {numbers}")
    for record in questions:
        key = (int(record["year"]), int(record["question_number"]))
        if key not in answer_keys:
            errors.append(f"question {record['id']}: no answer-key record")

    fields = _record_fields(passages, questions)
    source_records_by_id = {
        str(record["id"]): record for record in [*passages, *questions]
    }
    expected_occurrence_ids: set[str] = set()
    for (record_id, field), text in fields.items():
        for token_index, match in enumerate(WORD_RE.finditer(text), 1):
            expected_occurrence_ids.add(f"{record_id}:{field}:{token_index}")
    seen_occurrence_ids: set[str] = set()
    occurrence_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in occurrences:
        occurrence_id = str(item.get("occurrence_id", "<missing>"))
        if occurrence_id in seen_occurrence_ids:
            errors.append(f"vocabulary occurrence: duplicate id {occurrence_id}")
        seen_occurrence_ids.add(occurrence_id)
        key = (str(item.get("source_record_id")), str(item.get("field")))
        text = fields.get(key)
        if text is None:
            errors.append(f"vocabulary occurrence {occurrence_id}: unknown record/field {key}")
            continue
        try:
            start = int(item["char_start"])
            end = int(item["char_end"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"vocabulary occurrence {occurrence_id}: invalid span")
            continue
        if not 0 <= start < end <= len(text):
            errors.append(f"vocabulary occurrence {occurrence_id}: span outside source text")
            continue
        if text[start:end] != item.get("surface"):
            errors.append(f"vocabulary occurrence {occurrence_id}: span does not reproduce surface")
        if normalize_token(str(item.get("surface", ""))) != item.get("normalized"):
            errors.append(f"vocabulary occurrence {occurrence_id}: normalized form mismatch")
        source_record = source_records_by_id.get(str(item.get("source_record_id")))
        if source_record is not None:
            expected_safe = is_safe(source_record)
            if item.get("safe_text") is not expected_safe:
                errors.append(f"vocabulary occurrence {occurrence_id}: safe_text mismatch")
            expected_completeness = source_record.get(
                "source_completeness_status", "not_applicable"
            )
            if item.get("source_completeness_status") != expected_completeness:
                errors.append(
                    f"vocabulary occurrence {occurrence_id}: completeness status mismatch"
                )
        occurrence_groups[str(item.get("normalized"))].append(item)
    missing_occurrences = expected_occurrence_ids - seen_occurrence_ids
    extra_occurrences = seen_occurrence_ids - expected_occurrence_ids
    if missing_occurrences:
        errors.append(f"vocabulary occurrences: {len(missing_occurrences)} expected IDs missing")
    if extra_occurrences:
        errors.append(f"vocabulary occurrences: {len(extra_occurrences)} unexpected IDs")

    lexicon_by_token: dict[str, dict[str, Any]] = {}
    for item in lexicon:
        token = str(item.get("normalized", ""))
        if token in lexicon_by_token:
            errors.append(f"vocabulary lexicon: duplicate token {token}")
        lexicon_by_token[token] = item
    if set(lexicon_by_token) != set(occurrence_groups):
        errors.append(
            "vocabulary lexicon: token set differs from occurrence aggregation "
            f"({len(lexicon_by_token)} vs {len(occurrence_groups)})"
        )
    for token, items in occurrence_groups.items():
        entry = lexicon_by_token.get(token)
        if entry is None:
            continue
        if int(entry.get("occurrence_count", -1)) != len(items):
            errors.append(f"vocabulary lexicon {token}: occurrence_count mismatch")
        years = sorted({int(item["year"]) for item in items})
        if entry.get("years") != years or int(entry.get("year_count", -1)) != len(years):
            errors.append(f"vocabulary lexicon {token}: year aggregation mismatch")
        safe_count = sum(bool(item.get("safe_text")) for item in items)
        if int(entry.get("safe_occurrence_count", -1)) != safe_count:
            errors.append(f"vocabulary lexicon {token}: safe count mismatch")
        if entry.get("lemma") is not None or entry.get("lemma_status") != "not_computed":
            errors.append(f"vocabulary lexicon {token}: unverified lemma must not be asserted")

    if int(vocabulary_stats.get("token_count", -1)) != len(occurrences):
        errors.append("vocabulary_stats: token_count mismatch")
    if int(vocabulary_stats.get("unique_surface_forms", -1)) != len(lexicon):
        errors.append("vocabulary_stats: unique_surface_forms mismatch")
    errors.extend(
        vocabulary_input_hash_errors(
            vocabulary_stats,
            passage_path,
            corpus_path,
            question_path,
        )
    )
    coverage_claim = vocabulary_stats.get("coverage_claim", {})
    available_years = sorted({int(item["year"]) for item in occurrences})
    if coverage_claim.get("available_years") != available_years:
        errors.append("vocabulary_stats: available_years mismatch")
    actual_missing = sorted(set(range(year_start, year_end + 1)) - set(available_years))
    if coverage_claim.get("missing_years") != actual_missing:
        errors.append("vocabulary_stats: missing_years mismatch")
    expected_complete = not actual_missing
    if coverage_claim.get("complete_2001_2026") is not expected_complete:
        errors.append("vocabulary_stats: complete_2001_2026 does not match actual years")
    actual_gap_ids = sorted(known_incomplete_passage_ids)
    if coverage_claim.get("known_incomplete_passage_ids") != actual_gap_ids:
        errors.append("vocabulary_stats: known incomplete passage IDs mismatch")
    expected_source_complete = expected_complete and not actual_gap_ids
    if coverage_claim.get("complete_source_text_2001_2026") is not expected_source_complete:
        errors.append("vocabulary_stats: complete source text claim is incorrect")
    if coverage_claim.get("known_incomplete_passages_excluded_from_safe_evidence") is not True:
        errors.append("vocabulary_stats: incomplete passages are not declared excluded")
    if vocabulary_stats.get("known_incomplete_passage_count") != len(actual_gap_ids):
        errors.append("vocabulary_stats: known incomplete passage count mismatch")
    record_coverage = vocabulary_stats.get("record_coverage", {})
    if record_coverage.get("passages_excluded_for_known_source_gaps") != len(actual_gap_ids):
        errors.append("vocabulary_stats: excluded passage count mismatch")
    if record_coverage.get("passages_safe_for_training") != sum(
        record.get("safe_for_training") is True for record in passages
    ):
        errors.append("vocabulary_stats: safe passage count mismatch")
    if coverage_claim.get("official_wordlist_coverage_tested") is not False:
        errors.append("vocabulary_stats: official wordlist coverage was not tested")

    if not questions:
        warnings.append("question_index: no question evidence")
    warnings.append(
        "answer_evidence: answer labels are indexed; correct-option text linkage, evidence-sentence links, and distractor mechanisms are not manually validated"
    )
    return {
        "valid": not errors,
        "sentence_corpus_valid": sentence_report["valid"],
        "counts": {
            "passage_sentences": len(corpus),
            "passage_articles": len(passages),
            "reviewed_passage_text_corrections": reviewed_passage_correction_count,
            "known_incomplete_passages": len(known_incomplete_passage_ids),
            "questions": len(questions),
            "reviewed_question_text_corrections": reviewed_correction_count,
            "answers": len(answers),
            "vocabulary_occurrences": len(occurrences),
            "vocabulary_surface_forms": len(lexicon),
            "traced_source_files": len(set(file_hash_cache) | set(passage_source_hash_cache) | set(answer_source_hash_cache)),
        },
        "question_year_counts": {
            str(year): len(questions_by_year.get(year, []))
            for year in range(year_start, year_end + 1)
        },
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
    }


def build_parser() -> argparse.ArgumentParser:
    config_path = DEFAULT_DATA_DIR / "config.json"
    config = load_json(config_path) if config_path.exists() else {}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_DATA_DIR / "corpus.jsonl")
    parser.add_argument("--passages", type=Path, default=DEFAULT_DATA_DIR / "passage_index.jsonl")
    parser.add_argument("--questions", type=Path, default=DEFAULT_DATA_DIR / "question_index.jsonl")
    parser.add_argument("--answers", type=Path, default=DEFAULT_DATA_DIR / "answer_index.jsonl")
    parser.add_argument("--occurrences", type=Path, default=DEFAULT_DATA_DIR / "vocabulary_occurrences.jsonl")
    parser.add_argument("--lexicon", type=Path, default=DEFAULT_DATA_DIR / "vocabulary_lexicon.jsonl")
    parser.add_argument("--vocabulary-stats", type=Path, default=DEFAULT_DATA_DIR / "vocabulary_stats.json")
    parser.add_argument("--source-root", type=Path, default=config.get("source_root"))
    parser.add_argument("--year-start", type=int, default=int(config.get("year_start", 2001)))
    parser.add_argument("--year-end", type=int, default=int(config.get("year_end", 2026)))
    parser.add_argument("--allowed-unusable-year", type=int, action="append", default=list(config.get("allowed_unusable_years", [])))
    parser.add_argument("--report", type=Path, default=DEFAULT_DATA_DIR / "artifact_validation.json")
    parser.add_argument("--strict", action="store_true", help="also fail when warnings remain")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    if args.source_root is None:
        raise SystemExit("--source-root is required when data/config.json has no source_root")
    report = validate(
        args.corpus.resolve(),
        args.passages.resolve(),
        args.questions.resolve(),
        args.answers.resolve(),
        args.occurrences.resolve(),
        args.lexicon.resolve(),
        args.vocabulary_stats.resolve(),
        Path(args.source_root).resolve(),
        args.year_start,
        args.year_end,
        set(args.allowed_unusable_year),
    )
    atomic_json(args.report.resolve(), report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if not report["valid"] or (args.strict and report["warnings"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
