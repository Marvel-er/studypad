#!/usr/bin/env python3
"""Analyze question-stem evidence, grammar candidates, and discourse signals.

The report keeps three evidence levels separate: observed question stems,
heuristic passage tags, and teaching inferences.  Locally reviewed answer labels
are indexed, but evidence-sentence links and distractor mechanisms are not; the
script therefore never claims those mechanisms were validated.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = SKILL_ROOT / "data"
TYPE_LABELS = {
    "detail_or_reference": "细节与指代",
    "example_or_rhetorical_function": "例证与修辞功能",
    "inference": "推断",
    "main_idea_or_title": "主旨与标题",
    "attitude_or_tone": "态度与语气",
    "word_or_phrase_meaning": "词句含义",
    "reason_or_cause": "原因与因果",
    "text_structure_or_purpose": "篇章结构与目的",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"required input does not exist: {path}")
    output: list[dict[str, Any]] = []
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
            output.append(value)
    return output


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


def era(year: int) -> str:
    if year <= 2004:
        return "2001-2004"
    if year <= 2009:
        return "2005-2009"
    if year <= 2014:
        return "2010-2014"
    if year <= 2019:
        return "2015-2019"
    return "2020-2026"


def article_id(record: dict[str, Any]) -> str:
    match = re.search(r"\d+", str(record.get("article", "")))
    article_number = match.group(0) if match else "unknown"
    return f"{int(record['year'])}-reading-text{article_number}-passage"


def analyze(
    questions: list[dict[str, Any]], corpus: list[dict[str, Any]], answers: list[dict[str, Any]]
) -> dict[str, Any]:
    answer_map = {
        (int(item["year"]), int(item["question_number"])): str(item["answer"])
        for item in answers
    }
    linked_answer_count = sum(
        (int(item["year"]), int(item["question_number"])) in answer_map
        for item in questions
    )
    question_types = Counter(str(item.get("question_type", "unknown")) for item in questions)
    anchors = Counter(str(item.get("anchor_type", "unknown")) for item in questions)
    logic_signals = Counter(
        signal for item in questions for signal in item.get("logic_signals", [])
    )
    question_status = Counter(str(item.get("text_status", "unknown")) for item in questions)
    per_year: dict[int, Counter[str]] = defaultdict(Counter)
    per_era: dict[str, Counter[str]] = defaultdict(Counter)
    examples: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in questions:
        year = int(item["year"])
        question_type = str(item.get("question_type", "unknown"))
        per_year[year][question_type] += 1
        per_era[era(year)][question_type] += 1
        if len(examples[question_type]) < 3:
            examples[question_type].append(
                {
                    "id": item["id"],
                    "year": year,
                    "question_number": item["question_number"],
                    "stem": item["stem"],
                    "source_file": item.get("source_file"),
                    "source_page": item.get("source_page"),
                }
            )

    grammar = Counter()
    grammar_pairs = Counter()
    rhetorical = Counter()
    rhetorical_patterns = {
        "contrast_or_concession": r"\b(?:although|but|despite|however|nevertheless|though|whereas|while|yet)\b",
        "cause_or_result": r"\b(?:as a result|because|consequently|due to|lead to|result in|since|therefore|thus)\b",
        "condition_or_qualification": r"\b(?:if|only if|provided|unless|whether)\b",
        "attribution_or_evidence": r"\b(?:according to|argue|evidence|find|report|research|show|study|suggest)\w*\b",
        "comparison": r"\b(?:as .* as|compared with|more .* than|less .* than|rather than)\b",
        "problem_or_response": r"\b(?:address|challenge|cope with|problem|response|solution|tackle)\w*\b",
    }
    for record in corpus:
        tags = sorted(set(record.get("grammar_tags", [])))
        grammar.update(tags)
        grammar_pairs.update(itertools.combinations(tags, 2))
        text = str(record.get("original", ""))
        for name, pattern in rhetorical_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                rhetorical[name] += 1

    years = sorted({int(item["year"]) for item in questions})
    expected_years = set(range(2001, 2027))
    incomplete: dict[str, dict[str, Any]] = {}
    for record in corpus:
        if record.get("source_completeness_status") != "known_incomplete_source":
            continue
        key = article_id(record)
        gap = record.get("known_source_gap") or {}
        incomplete.setdefault(
            key,
            {
                "article_id": key,
                "description": gap.get("description"),
                "evidence_source": gap.get("evidence_source"),
                "evidence_pages": gap.get("evidence_pages", []),
            },
        )
    return {
        "schema_version": 1,
        "coverage": {
            "question_years": years,
            "question_year_count": len(years),
            "missing_question_years": sorted(expected_years - set(years)),
            "question_records": len(questions),
            "expected_reading_part_a_questions": 520,
            "question_record_share": round(len(questions) / 520, 4),
            "passage_sentence_records": len(corpus),
            "safe_for_training_passage_sentences": sum(
                item.get("safe_for_training") is True for item in corpus
            ),
            "known_incomplete_source_sentence_records": sum(
                item.get("source_completeness_status") == "known_incomplete_source"
                for item in corpus
            ),
            "known_incomplete_articles": [incomplete[key] for key in sorted(incomplete)],
            "known_incomplete_article_ids": sorted(incomplete),
        },
        "evidence_levels": {
            "question_type_basis": "observed question-stem wording plus deterministic rules",
            "grammar_basis": "heuristic candidate tags; not human syntax annotation",
            "teaching_logic_basis": "inference from aggregate signals; not an examiner statement",
        },
        "answer_evidence": {
            "answer_keys_indexed": bool(answers),
            "answer_records": len(answers),
            "correct_answer_records_linked_to_questions": linked_answer_count,
            "answer_records_without_question_text": len(answers) - linked_answer_count,
            "answer_label_distribution": dict(sorted(Counter(item["answer"] for item in answers).items())),
            "evidence_sentence_links": 0,
            "distractor_mechanisms_validated": False,
        },
        "review_status": {
            "question_text_status_counts": dict(sorted(question_status.items())),
            "question_needs_manual_review": sum(
                bool(item.get("needs_manual_review")) for item in questions
            ),
            "grammar_human_reviewed_records": 0,
        },
        "question_types": [
            {
                "type": name,
                "label_zh": TYPE_LABELS.get(name, name),
                "count": count,
                "share": round(count / max(1, len(questions)), 4),
            }
            for name, count in question_types.most_common()
        ],
        "anchor_types": [
            {"anchor": name, "count": count, "share": round(count / max(1, len(questions)), 4)}
            for name, count in anchors.most_common()
        ],
        "logic_signals": [
            {"signal": name, "count": count, "share": round(count / max(1, len(questions)), 4)}
            for name, count in logic_signals.most_common()
        ],
        "question_types_by_year": {
            str(year): dict(sorted(counts.items())) for year, counts in sorted(per_year.items())
        },
        "question_types_by_era": {
            label: dict(sorted(counts.items())) for label, counts in sorted(per_era.items())
        },
        "question_examples": dict(sorted(examples.items())),
        "grammar_candidates": [
            {
                "tag": tag,
                "count": count,
                "share": round(count / max(1, len(corpus)), 4),
                "review_status": "heuristic_unreviewed",
            }
            for tag, count in grammar.most_common()
        ],
        "grammar_cooccurrence_candidates": [
            {"tags": list(pair), "count": count}
            for pair, count in grammar_pairs.most_common(30)
        ],
        "passage_discourse_signals": [
            {
                "signal": name,
                "count": count,
                "share": round(count / max(1, len(corpus)), 4),
            }
            for name, count in rhetorical.most_common()
        ],
    }


def markdown_report(stat: dict[str, Any]) -> str:
    coverage = stat["coverage"]
    incomplete_ids = coverage["known_incomplete_article_ids"]
    incomplete_text = "、".join(incomplete_ids) if incomplete_ids else "无"
    q_table = ["| 题型候选 | 题数 | 占比 |", "|---|---:|---:|"]
    for item in stat["question_types"]:
        q_table.append(f"| {item['label_zh']} | {item['count']} | {item['share']:.1%} |")
    g_table = ["| 语法候选标签 | 句数 | 占比 | 证据状态 |", "|---|---:|---:|---|"]
    for item in stat["grammar_candidates"][:14]:
        g_table.append(
            f"| {item['tag']} | {item['count']} | {item['share']:.1%} | 自动候选，未人工标注 |"
        )
    d_table = ["| 语篇信号 | 句数 | 占比 |", "|---|---:|---:|"]
    for item in stat["passage_discourse_signals"]:
        d_table.append(f"| {item['signal']} | {item['count']} | {item['share']:.1%} |")

    examples: list[str] = []
    for item in stat["question_types"]:
        question_type = item["type"]
        sample = stat["question_examples"].get(question_type, [])[:2]
        if not sample:
            continue
        examples.append(f"### {item['label_zh']}")
        for record in sample:
            examples.append(
                f"- {record['year']} Q{record['question_number']}：{record['stem']}"
            )

    return f"""# 英语一 Reading Part A 命题逻辑与考点审计

## 证据边界

当前已建立 {coverage['question_records']}/{coverage['expected_reading_part_a_questions']} 道题干与四选项记录，覆盖 {coverage['question_year_count']}/26 年，缺失年份为 {coverage['missing_question_years']}。题型统计来自真实题干措辞；语法统计来自正文自动候选标签；“教学逻辑”是统计推断，不是命题机构说明。

正文中已知原始文件缺段文章为 {incomplete_text}，涉及 {coverage['known_incomplete_source_sentence_records']} 条现有句子。这些句子保留用于检索，但整篇不进入默认训练池；凡题目证据落在缺失段落内，当前报告不会推断或补写真文，也不会声称已经建立完整证据链。

本地答案键已经结构化保存，并与现有题目中的 {stat['answer_evidence']['correct_answer_records_linked_to_questions']} 道建立题号关联；但正确选项文本、正文证据句和干扰项机制仍未建立人工证据链。因此当前可以回答“题干显式要求考什么”和“本地答案文件给出的选项字母”，仍不能据实回答“正确项如何同义改写、每个干扰项为何错误”。

## 题型候选分布

{chr(10).join(q_table)}

题干中的定位方式分为整篇综合、显式段落/行号、引语词句、命名例证和隐含局部区域。训练时先判定定位尺度，再处理同义改写；把局部细节题当作主旨题，或把主旨题锁死在单句，都会扩大错误范围。

## 题干证据示例

{chr(10).join(examples)}

## 正文语法考点候选

{chr(10).join(g_table)}

这些标签只适合检索和抽样。例如 `relative_clause`、`prepositional_postmodifier`、`complex_reference` 都由规则触发，并没有从句边界、修饰对象或指代先行词的人工金标准。不能把“双源正文一致”误写成“语法已经人工复核”。

## 语篇逻辑信号

{chr(10).join(d_table)}

可迁移的阅读顺序是：先识别转折/让步、因果、条件、证据归属和问题—回应，再判断题干要求的是局部复述、受约束推断、修辞功能还是全篇综合。信号词只能缩小搜索范围，不能直接替代答案证明。

## 长难句拆解与造句逻辑

1. 先写可独立成立的主干：主语 + 有限谓语 + 必需补足语。
2. 用定语从句、同位语或介词短语限定核心名词；每一层都必须说明修饰对象。
3. 用宾语从句或同位语从句承载观点、证据和结论，避免把所有 `that` 都当成定语从句。
4. 用 `to do`、`doing`、`done` 压缩次要动作，同时核对它的逻辑主语。
5. 用转折、让步、因果、条件和比较确定命题关系；翻译时保留方向，不做逐词平铺。
6. 最后检查代词、抽象名词和同义替换是否跨句承接。只有能指出先行内容，才算真正完成指代还原。

训练产出应明确分开：原文事实、结构候选、人工判断和教学推断。这样后续加入答案键和证据句时，可以增量升级，而不会把旧的启发式结论伪装成真题标准答案。
"""


def build(
    question_path: Path,
    corpus_path: Path,
    answer_path: Path,
    stats_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    questions = load_jsonl(question_path)
    corpus = load_jsonl(corpus_path)
    answers = load_jsonl(answer_path)
    stat = analyze(questions, corpus, answers)
    changed = {
        "stats": atomic_text(
            stats_path, json.dumps(stat, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ),
        "report": atomic_text(report_path, markdown_report(stat)),
    }
    return {
        "questions": stat["coverage"]["question_records"],
        "question_years": stat["coverage"]["question_years"],
        "missing_question_years": stat["coverage"]["missing_question_years"],
        "passage_sentences": stat["coverage"]["passage_sentence_records"],
        "changed": changed,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=Path, default=DEFAULT_DATA_DIR / "question_index.jsonl")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_DATA_DIR / "corpus.jsonl")
    parser.add_argument("--answers", type=Path, default=DEFAULT_DATA_DIR / "answer_index.jsonl")
    parser.add_argument("--stats", type=Path, default=DEFAULT_DATA_DIR / "exam_point_stats.json")
    parser.add_argument(
        "--report", type=Path, default=SKILL_ROOT / "references" / "exam-points.md"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    result = build(
        args.questions.resolve(),
        args.corpus.resolve(),
        args.answers.resolve(),
        args.stats.resolve(),
        args.report.resolve(),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
