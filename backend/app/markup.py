"""
密度编排引擎：决定「哪些候选标注最终留在纸上」。

这是体验成败的关键 —— 划满等于没划。
策略：按优先级排序 → 按等级预算截断 → 去重 → 解重叠 → 生成词表与句型表。
"""
from __future__ import annotations

import math
from collections import defaultdict

from .levels import get as get_level

# 词级标注互斥：同一 token 只能有一个词标记
WORD_TYPES = {"word_circle", "word_highlight", "word_rare"}

# 词级标注的分数门槛：宁可少标，不要标垃圾
WORD_MIN_SCORE = 0.32


def compute_budget(word_count: int, level: dict) -> dict[str, int]:
    """按文章长度换算各类标注的预算上限（至少给 1 个，避免短文本全空）。"""
    k = word_count / 1000.0
    return {
        "word_highlight": max(1, round(level["highlight_per_1000"] * k)),
        "word_circle": max(1, round(level["circle_per_1000"] * k)),
        "word_rare": max(0, round(level["deep_per_1000"] * k)),
        "pattern_wavy": 10_000,            # 加分句型不设上限（价值最高）
        "long_sentence": max(3, round(6 * k)),
    }


def _overlaps(a: dict, b: dict) -> bool:
    return not (a["end"] <= b["start"] or b["end"] <= a["start"])


def select(candidates: list[dict], budget: dict, level: dict) -> list[dict]:
    """从候选中按预算与优先级挑出最终标注。"""
    # 1. 同类型同区间去重：保留 confidence 最高
    best: dict[tuple, dict] = {}
    for c in candidates:
        key = (c["block_id"], c["type"], c["start"], c["end"])
        cur = best.get(key)
        if cur is None or c["confidence"] > cur["confidence"]:
            best[key] = c
    pool = list(best.values())

    # 2. 词级标注按分数排序后按预算截断
    words = [c for c in pool if c["type"] in WORD_TYPES
             and c["confidence"] >= WORD_MIN_SCORE]
    others = [c for c in pool if c["type"] not in WORD_TYPES]

    words.sort(key=lambda c: (-c["priority"], -c["confidence"], c["start"]))

    used: dict[str, int] = defaultdict(int)
    word_kept: list[dict] = []
    occupied: list[tuple[str, int, int]] = []   # 已占用的词位置

    for c in words:
        if used[c["type"]] >= budget.get(c["type"], 0):
            continue
        # 同一 token 不重复标记
        if any(b == c["block_id"] and not (c["end"] <= s or e <= c["start"])
               for b, s, e in occupied):
            continue
        occupied.append((c["block_id"], c["start"], c["end"]))
        used[c["type"]] += 1
        word_kept.append(c)

    # 3. 语法标注：每段限量
    grammar = [c for c in others if c["type"] == "grammar_underline"]
    grammar.sort(key=lambda c: (-c["confidence"], c["start"]))
    per_block: dict[str, int] = defaultdict(int)
    grammar_kept: list[dict] = []
    for c in grammar:
        if per_block[c["block_id"]] >= level["grammar_max_per_para"]:
            continue
        per_block[c["block_id"]] += 1
        grammar_kept.append(c)

    # 4. 句型与长难句
    pats = [c for c in others if c["type"] == "pattern_wavy"]
    longs = [c for c in others if c["type"] == "long_sentence"]
    longs.sort(key=lambda c: (-c["confidence"], c["start"]))
    longs = longs[: budget.get("long_sentence", 5)]

    # 5. 同句内语法与句型重叠：句型优先，语法让位
    final_pats = list(pats)
    final_grammar = []
    for g in grammar_kept:
        if any(g["block_id"] == p["block_id"] and _overlaps(g, p) for p in final_pats):
            continue
        final_grammar.append(g)

    return word_kept + final_grammar + final_pats + longs


def attach(blocks: list[dict], selected: list[dict]) -> list[dict]:
    """把选中的标注按 block_id 挂回区块，并按起始位置排序。"""
    by_block: dict[str, list[dict]] = defaultdict(list)
    for c in selected:
        by_block[c["block_id"]].append(c)

    out = []
    for b in blocks:
        anns = sorted(by_block.get(b["id"], []), key=lambda a: (a["start"], -a["priority"]))
        for i, a in enumerate(anns):
            a["id"] = f"{b['id']}-a{i:03d}"
        out.append({**b, "annotations": anns})
    return out


def _doc_key(selected: list[dict], blocks: list[dict]) -> dict:
    """
    标注 → 文档全局序号的映射。

    为什么需要：每个 block 的 `start` 偏移都是**从 0 起算**的，
    所以「只按 start 排序」根本分不清先后 —— 第 5 段第一个词（start=0）
    会和第 1 段第一个词（start=0）打平，排序结果既不是文章顺序、
    也不是任何稳定顺序，生词表看起来就是乱的。
    正确的键是 **(block 顺序, 段内偏移)**。
    """
    pos = {b["id"]: (i, b.get("order", i)) for i, b in enumerate(blocks)}
    return pos


def build_vocab(selected: list[dict], level_id: str,
                blocks: list[dict] | None = None) -> list[dict]:
    """汇总生词表（去重，按文章出现顺序）。"""
    seen: dict[str, dict] = {}
    ordered = sorted(selected, key=lambda x: (x["block_id"], x["start"]))
    if blocks:
        pos = _doc_key(selected, blocks)
        ordered = sorted(ordered, key=lambda x: pos.get(x["block_id"], (9999, 9999)))
    for c in ordered:
        if c["type"] not in WORD_TYPES:
            continue
        p = c["payload"]
        lemma = p.get("lemma") or c["surface"].lower()
        if lemma in seen:
            continue
        seen[lemma] = {
            "lemma": lemma,
            "surface": c["surface"],
            "phonetic": p.get("phonetic", ""),
            "gloss": p.get("gloss", ""),
            "pos": p.get("pos", ""),
            "kind": p.get("kind", ""),
            "example": p.get("example", ""),
            # 英释：英汉双解里英文那一半，渲染时挂在中文释义下面。
            "en": p.get("en", ""),
        }
    return list(seen.values())


def build_patterns(selected: list[dict], blocks: list[dict] | None = None) -> list[dict]:
    """汇总句型表（去重，按文章出现顺序）。"""
    seen: dict[str, dict] = {}
    ordered = sorted(selected, key=lambda x: (x["block_id"], x["start"]))
    if blocks:
        pos = _doc_key(selected, blocks)
        ordered = sorted(ordered, key=lambda x: pos.get(x["block_id"], (9999, 9999)))
    for c in ordered:
        if c["type"] != "pattern_wavy":
            continue
        p = c["payload"]
        name = p.get("name", "")
        if name in seen:
            continue
        seen[name] = {
            "name": name,
            "surface": c["surface"],
            "usage": p.get("usage", []),
            "imitation": p.get("imitation", ""),
        }
    return list(seen.values())


def build(parsed: dict, level_id: str) -> dict:
    """组装最终手账数据结构。"""
    level = get_level(level_id)
    word_count = max(parsed["word_count"], 1)
    budget = compute_budget(word_count, level)
    selected = select(parsed["candidates"], budget, level)
    blocks = attach(parsed["blocks"], selected)

    counters = {
        "word_highlight": sum(1 for c in selected if c["type"] == "word_highlight"),
        "word_circle": sum(1 for c in selected if c["type"] == "word_circle"),
        "word_rare": sum(1 for c in selected if c["type"] == "word_rare"),
        "grammar": sum(1 for c in selected if c["type"] == "grammar_underline"),
        "patterns": sum(1 for c in selected if c["type"] == "pattern_wavy"),
        "long_sentences": sum(1 for c in selected if c["type"] == "long_sentence"),
    }

    return {
        "level_id": level_id,
        "level_name": level["name"],
        "level_en": level["en"],
        "level_tagline": level["tagline"],
        "vocab_note": level["vocab_note"],
        "explain_depth": level["explain_depth"],
        # 等级自带的「是否默认显示译文」只是意图；真正呈现取决于是否有译文。
        # 见 main._run_pipeline 与 render.render_handbook。
        "show_translation": level["show_translation"],
        "trans_mode": "off",
        "translations": {},
        "trans_note": "",
        "word_count": word_count,
        "counters": counters,
        "budget": budget,
        "blocks": blocks,
        "vocab": build_vocab(selected, level_id, blocks),
        "patterns": build_patterns(selected, blocks),
        "raw_counters": parsed["counters"],
    }
