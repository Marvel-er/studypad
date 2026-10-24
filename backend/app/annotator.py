"""
标注生成器：把「一篇文章」变成「一堆候选标注」。

规则引擎负责产出所有候选；LLM 只做锦上添花（重写讲解、补充长难句拆解）。
最终保留哪些、保留多少，交给 markup.py 的密度编排决定。
"""
from __future__ import annotations

from . import analyzer, patterns
from .analyzer import analyze_text, annotation_value, split_sentences, threshold_for, word_score
from .levels import get as get_level

# 各类词的优先级（越大越先保留）
KIND_PRIORITY = {"overflow": 85, "beyond": 50, "rare": 40, "target": 55}

# 词归类 → 标注类型
KIND_TYPE = {
    "overflow": "word_circle",
    "beyond": "word_rare",
    "rare": "word_rare",
    "target": "word_highlight",
}

KIND_COLOR = {
    "overflow": "#DC2626",
    "rare": "#0284C7",
    "beyond": "#0284C7",
    "target": "#D97706",
}


def analyze_block(text: str, level_id: str) -> dict:
    """对单个区块产出全部候选标注（未做密度裁剪）。"""
    lv = get_level(level_id)
    th = threshold_for(level_id)

    res = analyze_text(text, level_id)
    toks = res["tokens"]
    sentences = split_sentences(text)

    candidates: list[dict] = []
    sentence_reports: list[dict] = []

    for sent, sstart in sentences:
        if len(sent) < 8:
            continue
        g_raw = patterns.detect_grammar(sent)
        p_raw = patterns.detect_patterns(sent, lv["pattern_level"])

        g_hits = []
        for g in g_raw:
            g = dict(g)
            g["start"] += sstart
            g["end"] += sstart
            g["explain"] = patterns.explain_at(g, lv["explain_depth"])
            g_hits.append(g)

        p_hits = []
        for p in p_raw:
            p = dict(p)
            p["start"] += sstart
            p["end"] += sstart
            p_hits.append(p)

        sent_toks = [t for t in toks if sstart <= t.start < sstart + len(sent)]
        words = [t for t in sent_toks if t.kind != "skip"]

        value = annotation_value(sent, sent_toks, g_hits, p_hits, level_id)

        is_long = len(words) >= lv["sentence_split_min_words"]
        if value < th and not p_hits and not is_long:
            continue

        sentence_reports.append({
            "text": sent,
            "start": sstart,
            "value": round(value, 3),
            "words": len(words),
            "grammar": [g["label"] for g in g_hits],
            "patterns": [p["name"] for p in p_hits],
            "long": is_long,
        })

        # --- 句型（最高优先级，永远保留） ---
        for p in p_hits:
            candidates.append({
                "type": "pattern_wavy",
                "start": p["start"], "end": p["end"],
                "surface": p["surface"],
                "priority": 100,
                "confidence": 0.9,
                "source": "rule",
                "payload": {
                    "name": p["name"],
                    "usage": p["usage"],
                    "imitation": p["imitation"],
                },
            })

        # --- 语法结构 ---
        for g in g_hits:
            candidates.append({
                "type": "grammar_underline",
                "start": g["start"], "end": g["end"],
                "surface": g["surface"],
                "priority": 70,
                "confidence": 0.85,
                "source": "rule",
                "payload": {
                    "grammar_id": g["grammar_id"],
                    "label": g["label"],
                    "color": g["color"],
                    "explain": g["explain"],
                },
            })

        # --- 单词 ---
        for t in words:
            if t.kind in ("known", "skip"):
                continue
            atype = KIND_TYPE.get(t.kind)
            if not atype:
                continue
            info = t.info or {}
            payload = {
                "lemma": t.lemma or t.surface.lower(),
                "phonetic": info.get("p", ""),
                "gloss": info.get("t", ""),
                "pos": info.get("pos", ""),
                "example": info.get("s", ""),
                # 英释（英汉双解的那一半）：六档词表里那一格是基础释义，
                # 兜底全量库那一层是 WordNet 的权威英文释义 + 例句。
                "en": info.get("e", ""),
                "kind": t.kind,
                "levels": t.mask,
                "color": KIND_COLOR[t.kind],
            }
            candidates.append({
                "type": atype,
                "start": t.start, "end": t.end,
                "surface": t.surface,
                "priority": KIND_PRIORITY[t.kind],
                "confidence": round(word_score(t.kind, t.mask, t.surface, t.new_at_level), 3),
                "source": "rule",
                "payload": payload,
            })

        # --- 长难句标记 ---
        if is_long:
            candidates.append({
                "type": "long_sentence",
                "start": sstart, "end": sstart + len(sent),
                "surface": sent,
                "priority": 60,
                "confidence": 0.7,
                "source": "rule",
                "payload": {
                    "words": len(words),
                    "value": round(value, 3),
                    "grammar": [g["label"] for g in g_hits],
                },
            })

    return {
        "candidates": candidates,
        "sentences": sentence_reports,
        "stats": res["counters"],
        "word_count": res["word_count"],
    }


def analyze_document(blocks: list[dict], level_id: str, on_progress=None) -> dict:
    """
    对整篇文档逐区块分析。blocks 是 parsers.Block 的 dict 形式。

    `on_progress(done, total)` 是可选的进度回调 —— 逐块上报，
    让前端在长文档上也能看到进度在动（而不是只在阶段边界跳一下）。
    回调失败不影响分析：进度丢了是小事，任务失败是大事。
    """
    out_blocks = []
    all_candidates: list[dict] = []
    total_words = 0
    agg = {"target": 0, "overflow": 0, "rare": 0, "beyond": 0, "known": 0, "skip": 0}
    n_blocks = len(blocks)

    for bi, b in enumerate(blocks):
        if on_progress:
            try:
                on_progress(bi, n_blocks)
            except Exception:  # noqa: BLE001
                pass
        if b.get("meta", {}).get("skip"):
            out_blocks.append({**b, "candidates": [], "sentences": []})
            continue
        text = b.get("text") or ""
        if not text.strip():
            out_blocks.append({**b, "candidates": [], "sentences": []})
            continue

        r = analyze_block(text, level_id)
        for k in agg:
            agg[k] += r["stats"].get(k, 0)
        total_words += r["word_count"]
        for c in r["candidates"]:
            c["block_id"] = b["id"]
        all_candidates.extend(r["candidates"])
        out_blocks.append({**b, "candidates": r["candidates"], "sentences": r["sentences"]})

    if on_progress:
        try:
            on_progress(n_blocks, n_blocks)
        except Exception:  # noqa: BLE001
            pass

    return {
        "blocks": out_blocks,
        "candidates": all_candidates,
        "word_count": total_words,
        "counters": agg,
    }
