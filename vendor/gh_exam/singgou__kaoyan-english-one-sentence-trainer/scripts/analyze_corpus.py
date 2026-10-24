#!/usr/bin/env python3
"""Generate evidence-backed statistics and an exam-logic brief from the corpus."""

from __future__ import annotations

import argparse
import itertools
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from classify_sentences import ACADEMIC_VERBS, words


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = SKILL_ROOT / "data"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"invalid JSON at {path}:{line_number}: {exc}") from exc
    return records


def percentile(values: list[int], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(len(ordered) - 1, lower + 1)
    weight = position - lower
    return round(ordered[lower] * (1 - weight) + ordered[upper] * weight, 2)


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


def sentence_has(text: str, pattern: str) -> bool:
    return bool(re.search(pattern, text, re.IGNORECASE))


def article_id(record: dict[str, Any]) -> str:
    match = re.search(r"\d+", str(record.get("article", "")))
    article_number = match.group(0) if match else "unknown"
    return f"{int(record['year'])}-reading-text{article_number}-passage"


def source_completeness_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    incomplete: dict[str, dict[str, Any]] = {}
    for record in records:
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
        "known_incomplete_articles": [incomplete[key] for key in sorted(incomplete)],
        "known_incomplete_article_ids": sorted(incomplete),
        "known_incomplete_sentence_records": sum(
            record.get("source_completeness_status") == "known_incomplete_source"
            for record in records
        ),
        "safe_for_training_sentence_records": sum(
            record.get("safe_for_training") is True for record in records
        ),
    }


def analyze(
    records: list[dict[str, Any]],
    *,
    source_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    source_records = source_records if source_records is not None else records
    lengths = [int(record["word_count"]) for record in records]
    years: dict[int, list[dict[str, Any]]] = defaultdict(list)
    eras: dict[str, list[dict[str, Any]]] = defaultdict(list)
    difficulty = Counter()
    grammar = Counter()
    vocabulary = Counter()
    pairs = Counter()
    academic_verbs = Counter()
    rhetorical = Counter()
    text_status = Counter()

    rhetorical_patterns = {
        "contrast_or_concession": r"\b(?:although|but|despite|however|nevertheless|though|whereas|while|yet)\b",
        "cause_or_result": r"\b(?:as a result|because|consequently|due to|lead to|result in|since|therefore|thus)\b",
        "condition_or_qualification": r"\b(?:if|only if|provided|unless|whether)\b",
        "attribution_or_evidence": r"\b(?:according to|argue|evidence|find|report|research|show|study|suggest)\w*\b",
        "comparison": r"\b(?:as .* as|compared with|more .* than|less .* than|rather than)\b",
        "problem_or_response": r"\b(?:address|challenge|cope with|problem|response|solution|tackle)\w*\b",
    }

    for record in records:
        years[int(record["year"])].append(record)
        eras[era(int(record["year"]))].append(record)
        difficulty[int(record["difficulty"])] += 1
        tags = sorted(set(record.get("grammar_tags", [])))
        grammar.update(tags)
        vocabulary.update(record.get("vocabulary_tags", []))
        pairs.update(itertools.combinations(tags, 2))
        text_status[str(record.get("text_status", "unknown"))] += 1
        token_set = set(words(record["original"]))
        academic_verbs.update(token_set & ACADEMIC_VERBS)
        for name, pattern in rhetorical_patterns.items():
            if sentence_has(record["original"], pattern):
                rhetorical[name] += 1

    year_stats = {}
    for year, items in sorted(years.items()):
        year_stats[str(year)] = {
            "sentences": len(items),
            "average_words": round(mean(int(item["word_count"]) for item in items), 2),
            "difficulty_4_5_share": round(sum(int(item["difficulty"]) >= 4 for item in items) / len(items), 4),
            "articles": sorted({item["article"] for item in items}),
        }
    era_stats = {}
    for label, items in sorted(eras.items()):
        era_stats[label] = {
            "sentences": len(items),
            "average_words": round(mean(int(item["word_count"]) for item in items), 2),
            "average_difficulty": round(mean(int(item["difficulty"]) for item in items), 2),
        }

    total = max(1, len(records))
    return {
        "record_count": len(records),
        "years": sorted(years),
        "year_count": len(years),
        "word_count": {
            "mean": round(mean(lengths), 2) if lengths else 0,
            "p50": percentile(lengths, 0.50),
            "p75": percentile(lengths, 0.75),
            "p90": percentile(lengths, 0.90),
            "p95": percentile(lengths, 0.95),
            "max": max(lengths, default=0),
        },
        "difficulty_counts": {str(level): difficulty[level] for level in range(1, 6)},
        "grammar_tags": [
            {"tag": tag, "count": count, "share": round(count / total, 4)}
            for tag, count in grammar.most_common()
        ],
        "grammar_cooccurrence": [
            {"tags": list(pair), "count": count}
            for pair, count in pairs.most_common(20)
        ],
        "vocabulary_tags": [
            {"tag": tag, "count": count, "share": round(count / total, 4)}
            for tag, count in vocabulary.most_common()
        ],
        "academic_verbs": [
            {"word": word, "sentence_count": count}
            for word, count in academic_verbs.most_common(20)
        ],
        "rhetorical_functions": [
            {"function": name, "count": count, "share": round(count / total, 4)}
            for name, count in rhetorical.most_common()
        ],
        "text_status_counts": dict(sorted(text_status.items())),
        "needs_manual_review": sum(bool(record.get("needs_manual_review")) for record in records),
        "analyzed_safe_for_training_sentence_records": sum(
            record.get("safe_for_training") is True for record in records
        ),
        "analyzed_known_incomplete_sentence_records": sum(
            record.get("source_completeness_status") == "known_incomplete_source"
            for record in records
        ),
        "source_completeness": source_completeness_summary(source_records),
        "year_stats": year_stats,
        "era_stats": era_stats,
    }


def _table(rows: Iterable[tuple[str, Any, Any]]) -> str:
    lines = ["| 项目 | 数量 | 占比 |", "|---|---:|---:|"]
    for name, count, share in rows:
        lines.append(f"| {name} | {count} | {share:.1%} |")
    return "\n".join(lines)


def markdown_report(stats: dict[str, Any]) -> str:
    total = max(1, stats["record_count"])
    grammar_rows = [
        (item["tag"], item["count"], item["share"])
        for item in stats["grammar_tags"][:12]
    ]
    rhetoric_rows = [
        (item["function"], item["count"], item["share"])
        for item in stats["rhetorical_functions"]
    ]
    top_pairs = "、".join(
        f"{'+'.join(item['tags'])}（{item['count']}）"
        for item in stats["grammar_cooccurrence"][:8]
    ) or "暂无"
    top_verbs = "、".join(
        f"{item['word']}（{item['sentence_count']}）" for item in stats["academic_verbs"][:12]
    ) or "暂无"
    years = stats["years"]
    year_range = f"{min(years)}—{max(years)}" if years else "无"
    incomplete_ids = stats["source_completeness"]["known_incomplete_article_ids"]
    incomplete_text = "、".join(incomplete_ids) if incomplete_ids else "无"

    return f"""# 英语一真题长难句与出题逻辑：语料统计

> 本报告由本地真题句库自动生成。计数是语料事实；“命题逻辑”部分是基于这些计数的教学性推断，不代表命题机关说明。自动语法标签仅用于检索，最终判断必须回到原句。

## 语料边界与质量

- 范围：{year_range}，已形成可用语料的年份 {stats['year_count']} 个。
- 句子：{stats['record_count']} 条 Reading Part A 原文候选。
- 文本状态：{json.dumps(stats['text_status_counts'], ensure_ascii=False)}。
- 仍需人工逐句复核：{stats['needs_manual_review']} 条；默认每日选句器不会选择未核验 OCR 或单源低置信文本。
- 已知原始文件缺段文章：{incomplete_text}；这些文章的现有文本仅供检索，整篇均排除在默认每日训练和安全词汇证据池之外。
- 本报告所分析记录中，`safe_for_training=true` 为 {stats['analyzed_safe_for_training_sentence_records']} 条，来自已知缺段文章的记录为 {stats['analyzed_known_incomplete_sentence_records']} 条。

## 句长不是难度本身

词数均值为 {stats['word_count']['mean']}，中位数 {stats['word_count']['p50']}，P75 为 {stats['word_count']['p75']}，P90 为 {stats['word_count']['p90']}，P95 为 {stats['word_count']['p95']}。因此，“长”应理解为主干跨度和修饰层次增加，而不是见到超过某个词数就机械判为难句。

难度分布：{json.dumps(stats['difficulty_counts'], ensure_ascii=False)}。自动难度同时考虑从句、非谓语、后置介词结构、插入语、并列、指代和逻辑标记。

## 高频结构信号

{_table(grammar_rows)}

高频共现组合：{top_pairs}。

从训练角度看，英语一长难句通常不是“先写一个很长的主句”，而是按以下方式扩展：先提出一个可独立成立的核心判断，再用从句限定名词或补足观点，用非谓语压缩次要动作，用介词短语继续后置修饰，最后通过转折、让步、因果或比较确定作者立场。拆句时应反向操作：先删除可移动修饰，找到有限谓语，再恢复各层关系。

## 论证功能

{_table(rhetoric_rows)}

这表明阅读难度不只来自语法。命题常把关键信息放在转折、让步、因果、条件、证据归属和问题—回应关系上。翻译若只逐词对应、没有保留逻辑方向，即使词义大致正确也可能误解作者立场。

## 词汇逻辑

语料中高频学术动词候选：{top_verbs}。

词汇学习应优先记录“本句中承担什么论证动作”：例如表示提出观点、限定结论、构成关系、导致结果、处理问题或反映证据。熟词僻义不能靠词形猜测，应结合宾语类型、介词搭配和上下文主题判断。词根词缀只用于可靠的构词关系，不能替代语境取义。

## 长难句造句与拆解逻辑

1. 先写核心命题：谁或什么，做了什么，处于什么状态。
2. 给核心名词增加限定：定语从句、同位语或介词短语回答“是哪一个”。
3. 给动作增加条件和立场：原因、让步、条件、比较或结果回答“在什么逻辑下成立”。
4. 把次要动作压缩为 `to do`、`doing` 或 `done`，降低表面上的完整从句数量，却提高谓语辨认难度。
5. 用插入语、破折号、括号或多重并列拉开主语与谓语，制造主干跨度。
6. 用抽象名词和代词承接前文，让理解依赖跨句指代，而不是单句词义。

训练时每句都应完成四次还原：最小主干 → 从句边界 → 非谓语与后置修饰 → 逻辑和自然中文。真正掌握的标准不是记住一版译文，而是能把相同结构迁移到另一年份的陌生句。

## 使用边界

本报告不能证明本地文件具有官方电子版来源，也不能把 OCR 或自动标签当作最终答案。对扫描件、单源文本和双源冲突句，应先核对页面或补充独立来源，再允许进入默认每日训练。
"""


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temp, path)


def default_output_paths(reviewed_only: bool) -> tuple[Path, Path]:
    return (
        DEFAULT_DATA_DIR
        / ("corpus_stats_reviewed.json" if reviewed_only else "corpus_stats.json"),
        SKILL_ROOT
        / "references"
        / ("corpus-insights-reviewed.md" if reviewed_only else "corpus-insights.md"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_DATA_DIR / "corpus.jsonl")
    parser.add_argument(
        "--output-json",
        type=Path,
        help="default: corpus_stats.json, or corpus_stats_reviewed.json with --reviewed-only",
    )
    parser.add_argument(
        "--output-markdown",
        type=Path,
        help="default: corpus-insights.md, or corpus-insights-reviewed.md with --reviewed-only",
    )
    parser.add_argument("--reviewed-only", action="store_true", help="analyze only cross-checked or human-verified records")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    default_json, default_markdown = default_output_paths(args.reviewed_only)
    output_json = args.output_json or default_json
    output_markdown = args.output_markdown or default_markdown
    source_records = load_jsonl(args.corpus)
    records = source_records
    if args.reviewed_only:
        records = [record for record in records if record.get("text_status") in {"cross_checked", "human_verified"} and not record.get("needs_manual_review")]
    if not records:
        raise SystemExit("no corpus records available for analysis")
    stats = analyze(records, source_records=source_records)
    atomic_text(output_json, json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    atomic_text(output_markdown, markdown_report(stats))
    print(json.dumps({"records": stats["record_count"], "years": stats["years"], "json": str(output_json), "markdown": str(output_markdown)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
