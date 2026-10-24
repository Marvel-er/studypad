#!/usr/bin/env python3
"""Build occurrence-level and aggregate vocabulary artifacts from local data.

The script indexes every English token in Reading Part A passage sentences,
question stems, and options.  It deliberately reports normalized surface forms
instead of pretending that a suffix-stripping heuristic is a reliable lemma or
word-family analyser.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from classify_sentences import WORD_RE
from extract_sentences import load_text_correction_config


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = SKILL_ROOT / "data"
FUNCTION_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "hers", "herself", "him", "himself", "his", "how", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its",
    "itself", "just", "me", "more", "most", "must", "mustn't", "my", "myself",
    "may", "might", "mightn't", "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other",
    "our", "ours", "ourselves", "out", "over", "own", "same", "she", "she'd",
    "she'll", "she's", "shall", "shan't", "should", "shouldn't", "so", "some", "such", "than", "that",
    "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
    "what's", "when", "where", "which", "while", "who", "whom", "whose", "why",
    "will", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're",
    "you've", "your", "yours", "yourself", "yourselves",
}
CORRUPT_TOKEN_INPUT_RE = re.compile(
    r"(?:\ufffd|\(cid:|\^\^|[\u4e00-\u9fff]|i[½¼]|\bfbr\b|"
    r"[A-Za-z]5s\b|s[59]\b|[A-Za-z]9\s+s\b|[A-Za-z]55\b|~~)",
    re.IGNORECASE,
)


def load_jsonl(path: Path, required: bool = True) -> list[dict[str, Any]]:
    if not path.exists():
        if required:
            raise SystemExit(f"required input does not exist: {path}")
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid JSON at {path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise SystemExit(f"record at {path}:{line_number} must be an object")
            records.append(value)
    return records


def sha256_path(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


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


def normalize_token(surface: str) -> str:
    return surface.lower().replace("’", "'").replace("‘", "'")


def is_safe(record: dict[str, Any]) -> bool:
    return (
        record.get("safe_for_training", True) is True
        and
        record.get("text_status") in {"cross_checked", "human_verified"}
        and not bool(record.get("needs_manual_review"))
    )


def tokenization_input_errors(
    passage_records: list[dict[str, Any]], question_records: list[dict[str, Any]]
) -> list[str]:
    """Reject unmistakable extraction noise before it can enter token outputs."""

    errors: list[str] = []
    correction_config = load_text_correction_config()

    def has_reviewed_residue(text: str) -> bool:
        return any(
            re.search(rf"(?<![A-Za-z]){re.escape(token)}(?![A-Za-z])", text)
            for token in correction_config["token_replacements"]
        ) or any(
            str(item.get("expected", "")) in text
            for item in correction_config["phrase_corrections"]
            if item.get("expected")
        )
    if not passage_records:
        errors.append("passage index contains no records")
    if not question_records:
        errors.append("question index contains no records")
    for record in passage_records:
        record_id = record.get("id", "<missing>")
        completeness_status = record.get("source_completeness_status")
        safe_for_training = record.get("safe_for_training")
        gap = record.get("known_source_gap")
        if completeness_status not in {"no_known_gap", "known_incomplete_source"}:
            errors.append(f"{record_id}: missing or invalid source completeness status")
        if not isinstance(safe_for_training, bool):
            errors.append(f"{record_id}: safe_for_training must be boolean")
        if completeness_status == "no_known_gap" and (
            safe_for_training is not True or gap is not None
        ):
            errors.append(f"{record_id}: inconsistent complete-source metadata")
        if completeness_status == "known_incomplete_source" and (
            safe_for_training is not False or not isinstance(gap, dict)
        ):
            errors.append(f"{record_id}: inconsistent incomplete-source metadata")
        text = str(record.get("text", ""))
        if not text.strip():
            errors.append(f"{record_id}: empty passage text")
        elif CORRUPT_TOKEN_INPUT_RE.search(text) or has_reviewed_residue(text):
            errors.append(f"{record_id}: corrupt passage text")
    for record in question_records:
        options = record.get("options", {})
        texts = [str(record.get("stem", ""))]
        if isinstance(options, dict):
            texts.extend(str(options.get(label, "")) for label in "ABCD")
        combined = " ".join(texts)
        if CORRUPT_TOKEN_INPUT_RE.search(combined) or has_reviewed_residue(combined):
            errors.append(f"{record.get('id', '<missing>')}: corrupt question text")
        if any(
            marker.lower() in combined.lower()
            for marker in ("Part B", "ANSWER SHEET", "Questions 41", "Directions:")
        ):
            errors.append(f"{record.get('id', '<missing>')}: later-section contamination")
    return errors


def _fields_for_passage(record: dict[str, Any]) -> Iterable[tuple[str, str, str]]:
    yield "passage_article", "text", str(record.get("text", ""))


def _fields_for_question(record: dict[str, Any]) -> Iterable[tuple[str, str, str]]:
    yield "question_stem", "stem", str(record.get("stem", ""))
    options = record.get("options", {})
    for label in "ABCD":
        yield "question_option", f"options.{label}", str(options.get(label, ""))


def occurrences(
    passage_records: list[dict[str, Any]], question_records: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    output: list[dict[str, Any]] = []
    covered_passages: set[str] = set()
    covered_questions: set[str] = set()

    def add(record: dict[str, Any], fields: Iterable[tuple[str, str, str]]) -> None:
        record_id = str(record["id"])
        field_seen = False
        for scope, field, text in fields:
            for token_index, match in enumerate(WORD_RE.finditer(text), 1):
                surface = match.group(0)
                normalized = normalize_token(surface)
                output.append(
                    {
                        "schema_version": 1,
                        "occurrence_id": f"{record_id}:{field}:{token_index}",
                        "source_record_id": record_id,
                        "scope": scope,
                        "field": field,
                        "token_index": token_index,
                        "char_start": match.start(),
                        "char_end": match.end(),
                        "surface": surface,
                        "normalized": normalized,
                        "lemma": None,
                        "lemma_status": "not_computed",
                        "year": int(record["year"]),
                        "article": record.get("article"),
                        "question_number": record.get("question_number"),
                        "source_file": record.get("source_file"),
                        "source_page": record.get("source_page", record.get("source_page_start")),
                        "text_status": record.get("text_status", "unknown"),
                        "source_completeness_status": record.get(
                            "source_completeness_status", "not_applicable"
                        ),
                        "safe_text": is_safe(record),
                    }
                )
                field_seen = True
        if field_seen:
            if record.get("question_number") is not None:
                covered_questions.add(record_id)
            else:
                covered_passages.add(record_id)

    for record in passage_records:
        add(record, _fields_for_passage(record))
    for record in question_records:
        add(record, _fields_for_question(record))
    return output, {
        "passage_article_records_input": len(passage_records),
        "passage_article_records_tokenized": len(covered_passages),
        "question_records_input": len(question_records),
        "question_records_tokenized": len(covered_questions),
    }


def frequency_tier(occurrence_count: int, year_count: int) -> str:
    if occurrence_count >= 10 and year_count >= 5:
        return "core_cross_year"
    if occurrence_count >= 5 and year_count >= 3:
        return "broad_cross_year"
    if occurrence_count >= 2:
        return "repeated_long_tail"
    return "singleton"


def build_lexicon(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["normalized"]].append(row)
    lexicon: list[dict[str, Any]] = []
    for token, items in grouped.items():
        years = sorted({int(item["year"]) for item in items})
        safe_items = [item for item in items if item["safe_text"]]
        safe_years = sorted({int(item["year"]) for item in safe_items})
        form_counts = Counter(item["surface"] for item in items)
        scope_counts = Counter(item["scope"] for item in items)
        record_ids = {item["source_record_id"] for item in items}
        review_flags: list[str] = []
        if len(items) >= 5 and len(years) == 1:
            review_flags.append("concentrated_single_year")
        if len(items) >= 5 and not safe_items:
            review_flags.append("no_cross_checked_occurrence")
        if len(token) == 1 and token not in {"a", "i"}:
            review_flags.append("single_character_token")
        lexicon.append(
            {
                "schema_version": 1,
                "normalized": token,
                "lemma": None,
                "lemma_status": "not_computed",
                "is_function_word": token in FUNCTION_WORDS,
                "occurrence_count": len(items),
                "record_count": len(record_ids),
                "year_count": len(years),
                "years": years,
                "first_year": years[0],
                "last_year": years[-1],
                "safe_occurrence_count": len(safe_items),
                "safe_year_count": len(safe_years),
                "safe_years": safe_years,
                "safe_occurrence_share": round(len(safe_items) / len(items), 4),
                "surface_forms": [
                    {"form": form, "count": count}
                    for form, count in sorted(
                        form_counts.items(), key=lambda pair: (-pair[1], pair[0].lower(), pair[0])
                    )
                ],
                "scope_counts": dict(sorted(scope_counts.items())),
                "frequency_tier": frequency_tier(len(items), len(years)),
                "review_flags": review_flags,
                "example_refs": [
                    {
                        "source_record_id": item["source_record_id"],
                        "field": item["field"],
                        "token_index": item["token_index"],
                        "year": item["year"],
                        "safe_text": item["safe_text"],
                    }
                    for item in sorted(
                        items,
                        key=lambda row: (
                            not row["safe_text"], row["year"], row["source_record_id"],
                            row["field"], row["token_index"],
                        ),
                    )[:8]
                ],
            }
        )
    return sorted(lexicon, key=lambda item: item["normalized"])


def _tier_summary(
    lexicon: list[dict[str, Any]], tier_names: set[str]
) -> dict[str, Any]:
    items = [item for item in lexicon if item["frequency_tier"] in tier_names]
    total_occurrences = sum(item["occurrence_count"] for item in items)
    safe_occurrences = sum(item["safe_occurrence_count"] for item in items)
    safe_types = sum(item["safe_occurrence_count"] > 0 for item in items)
    robust_safe_types = sum(
        item["safe_occurrence_count"] >= 5 and item["safe_year_count"] >= 3
        for item in items
    )
    return {
        "types": len(items),
        "types_with_any_safe_occurrence": safe_types,
        "type_safe_presence_share": round(safe_types / max(1, len(items)), 4),
        "types_with_at_least_5_safe_occurrences_across_3_years": robust_safe_types,
        "robust_safe_type_share": round(robust_safe_types / max(1, len(items)), 4),
        "occurrences": total_occurrences,
        "safe_occurrences": safe_occurrences,
        "safe_occurrence_share": round(safe_occurrences / max(1, total_occurrences), 4),
    }


def stats(
    occurrence_rows: list[dict[str, Any]],
    lexicon: list[dict[str, Any]],
    record_coverage: dict[str, Any],
    passage_records: list[dict[str, Any]],
    passage_path: Path,
    question_path: Path,
    sentence_corpus_path: Path,
) -> dict[str, Any]:
    scope_counts = Counter(row["scope"] for row in occurrence_rows)
    years = sorted({int(row["year"]) for row in occurrence_rows})
    safe_rows = [row for row in occurrence_rows if row["safe_text"]]
    known_incomplete_passage_ids = sorted(
        str(record["id"])
        for record in passage_records
        if record.get("source_completeness_status") == "known_incomplete_source"
    )
    tier_counts = Counter(item["frequency_tier"] for item in lexicon)
    return {
        "schema_version": 1,
        "scope": "machine-extracted Reading Part A full passage records, question stems, and options",
        "vocabulary_unit": "case-folded normalized surface form",
        "lemma_status": "not_computed",
        "high_frequency_definitions": {
            "broad_cross_year": "occurrence_count >= 5 and year_count >= 3",
            "core_cross_year": "occurrence_count >= 10 and year_count >= 5",
        },
        "coverage_claim": {
            "complete_2001_2026": years == list(range(2001, 2027)),
            "complete_source_text_2001_2026": (
                years == list(range(2001, 2027)) and not known_incomplete_passage_ids
            ),
            "available_years": years,
            "missing_years": sorted(set(range(2001, 2027)) - set(years)),
            "known_incomplete_passage_ids": known_incomplete_passage_ids,
            "known_incomplete_passages_excluded_from_safe_evidence": True,
            "covered_exam_sections": ["Reading Part A"],
            "excluded_exam_sections": [
                "Use of English / cloze",
                "Reading Part B",
                "Translation",
                "Writing",
            ],
            "official_wordlist_coverage_tested": False,
        },
        "input_sha256": {
            "passage_index_jsonl": sha256_path(passage_path),
            "sentence_candidate_corpus_jsonl": sha256_path(sentence_corpus_path),
            "question_index_jsonl": sha256_path(question_path),
        },
        "record_coverage": record_coverage,
        "known_incomplete_passage_count": len(known_incomplete_passage_ids),
        "token_count": len(occurrence_rows),
        "safe_token_count": len(safe_rows),
        "safe_token_share": round(len(safe_rows) / max(1, len(occurrence_rows)), 4),
        "unique_surface_forms": len(lexicon),
        "scope_token_counts": dict(sorted(scope_counts.items())),
        "frequency_tier_counts": dict(sorted(tier_counts.items())),
        "broad_cross_year": _tier_summary(
            lexicon, {"broad_cross_year", "core_cross_year"}
        ),
        "core_cross_year": _tier_summary(lexicon, {"core_cross_year"}),
        "review_queue": {
            "types_with_flags": sum(bool(item["review_flags"]) for item in lexicon),
            "no_safe_evidence": [
                item["normalized"]
                for item in lexicon
                if "no_cross_checked_occurrence" in item["review_flags"]
            ],
            "single_year_frequency_ge_5": [
                item["normalized"]
                for item in lexicon
                if "concentrated_single_year" in item["review_flags"]
            ],
        },
    }


def markdown_report(stat: dict[str, Any], lexicon: list[dict[str, Any]]) -> str:
    claim = stat["coverage_claim"]
    verdict = "是" if claim["complete_2001_2026"] else "否"
    broad = stat["broad_cross_year"]
    core = stat["core_cross_year"]
    top_content = sorted(
        (
            item
            for item in lexicon
            if not item["is_function_word"]
            and item["frequency_tier"] in {"core_cross_year", "broad_cross_year"}
        ),
        key=lambda item: (-item["occurrence_count"], -item["year_count"], item["normalized"]),
    )[:60]
    table = [
        "| 词形 | 出现次数 | 年份数 | 安全文本次数 | 安全占比 | 层级 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for item in top_content:
        table.append(
            f"| {item['normalized']} | {item['occurrence_count']} | {item['year_count']} | "
            f"{item['safe_occurrence_count']} | {item['safe_occurrence_share']:.1%} | "
            f"{item['frequency_tier']} |"
        )
    return f"""# 本地词汇覆盖审计

## 结论

2001—2026年份完整覆盖：**{verdict}**。当前可追溯年份为 {len(claim['available_years'])}/26，缺失年份：{claim['missing_years']}。已知源文件缺段的篇章：{claim['known_incomplete_passage_ids'] or '无'}；这些篇章的现有文本仍进入全量表层词形索引，但不会进入“安全文本”证据池。本索引只覆盖 Reading Part A 的正文、题干与选项；完形、阅读 Part B、翻译和写作尚未进入统计，所以不得表述为“整张试卷全部词汇”。

本报告统计的是大小写归一化后的**表层词形**，不是词元、词族或词义。未安装并验证可靠词形还原器之前，`lemma` 保持为空，避免用简单删后缀制造伪精确结果。

## 可复核数据量

- 阅读文章记录：{stat['record_coverage']['passage_article_records_tokenized']}/{stat['record_coverage']['passage_article_records_input']} 篇均已逐词索引。
- 每日训练句候选：{stat['record_coverage']['training_sentence_candidates']} 条；它们是文章索引的检索子集，不重复计入词频。
- 题目记录：{stat['record_coverage']['question_records_tokenized']}/{stat['record_coverage']['question_records_input']} 道均已逐词索引；每题包含题干和 A—D 四个选项。
- token 总数：{stat['token_count']}；唯一表层词形：{stat['unique_surface_forms']}。
- 安全文本 token：{stat['safe_token_count']}，占 {stat['safe_token_share']:.1%}。这里的“安全”只表示同年双源精确一致或人工核验，不表示官方来源。

## 高频口径与安全覆盖

- 广义跨年高频：出现至少5次且跨至少3年，共 {broad['types']} 个；至少有一次安全例证的词形占 {broad['type_safe_presence_share']:.1%}，安全文本只覆盖其全部出现次数的 {broad['safe_occurrence_share']:.1%}。
- 核心跨年高频：出现至少10次且跨至少5年，共 {core['types']} 个；至少有一次安全例证的词形占 {core['type_safe_presence_share']:.1%}，达到“安全池至少5次且跨3年”的占 {core['robust_safe_type_share']:.1%}。

“某词在安全池出现过”不等于“该词在26年中的所有出现都已核验”。完整结论必须同时报告词形覆盖、出现次数覆盖、年份覆盖和题型范围。

## 停用词表过滤后的高频词形前60项

{chr(10).join(table)}

## 复核队列

- 出现至少5次但没有任何安全例证的词形：{', '.join(stat['review_queue']['no_safe_evidence']) or '无'}。
- 出现至少5次但只集中在单一年份的词形会进入 `concentrated_single_year` 队列；其中可能包含专名，也可能包含提取噪声，不能自动判错。
- 词义、熟词僻义、搭配和词族需要在真实句境中另行人工标注；表层频率本身不能完成词义消歧。
"""


def build(
    passage_path: Path,
    question_path: Path,
    sentence_corpus_path: Path,
    occurrences_path: Path,
    lexicon_path: Path,
    stats_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    passage_records = load_jsonl(passage_path)
    question_records = load_jsonl(question_path)
    sentence_candidates = load_jsonl(sentence_corpus_path)
    input_errors = tokenization_input_errors(passage_records, question_records)
    if input_errors:
        raise SystemExit(
            "refusing vocabulary build because source indexes are unsafe: "
            + "; ".join(input_errors[:20])
        )
    rows, record_coverage = occurrences(passage_records, question_records)
    record_coverage["training_sentence_candidates"] = len(sentence_candidates)
    record_coverage["passages_safe_for_training"] = sum(
        record.get("safe_for_training") is True for record in passage_records
    )
    record_coverage["passages_excluded_for_known_source_gaps"] = sum(
        record.get("source_completeness_status") == "known_incomplete_source"
        for record in passage_records
    )
    lexicon = build_lexicon(rows)
    stat = stats(
        rows,
        lexicon,
        record_coverage,
        passage_records,
        passage_path,
        question_path,
        sentence_corpus_path,
    )

    occurrences_text = "".join(
        json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in rows
    )
    lexicon_text = "".join(
        json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in lexicon
    )
    stats_text = json.dumps(stat, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    report_text = markdown_report(stat, lexicon)
    changed = {
        "occurrences": atomic_text(occurrences_path, occurrences_text),
        "lexicon": atomic_text(lexicon_path, lexicon_text),
        "stats": atomic_text(stats_path, stats_text),
        "report": atomic_text(report_path, report_text),
    }
    return {
        "records": record_coverage,
        "token_count": len(rows),
        "unique_surface_forms": len(lexicon),
        "available_years": stat["coverage_claim"]["available_years"],
        "missing_years": stat["coverage_claim"]["missing_years"],
        "core_cross_year_types": stat["core_cross_year"]["types"],
        "broad_cross_year_types": stat["broad_cross_year"]["types"],
        "changed": changed,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--passages", type=Path, default=DEFAULT_DATA_DIR / "passage_index.jsonl")
    parser.add_argument("--questions", type=Path, default=DEFAULT_DATA_DIR / "question_index.jsonl")
    parser.add_argument("--sentence-corpus", type=Path, default=DEFAULT_DATA_DIR / "corpus.jsonl")
    parser.add_argument("--occurrences", type=Path, default=DEFAULT_DATA_DIR / "vocabulary_occurrences.jsonl")
    parser.add_argument("--lexicon", type=Path, default=DEFAULT_DATA_DIR / "vocabulary_lexicon.jsonl")
    parser.add_argument("--stats", type=Path, default=DEFAULT_DATA_DIR / "vocabulary_stats.json")
    parser.add_argument(
        "--report",
        type=Path,
        default=SKILL_ROOT / "references" / "vocabulary-coverage.md",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    result = build(
        args.passages.resolve(),
        args.questions.resolve(),
        args.sentence_corpus.resolve(),
        args.occurrences.resolve(),
        args.lexicon.resolve(),
        args.stats.resolve(),
        args.report.resolve(),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
