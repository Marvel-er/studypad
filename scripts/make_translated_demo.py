"""
用「人工译文」渲染一份真实的译文手账，供肉眼验收版式。

为什么需要它：译文版式是本功能的核心观感，但本机没有可用的大模型 Key，
接口层只能验到「有没有译文块」，**看不出排出来好不好读**。
所以这里准备一份人工翻译的样例译文（`samples/translations_zh.json`），
把两种版式真跑一遍，产出可以直接打开的 HTML。

顺带它还是**回归夹具**：以后改渲染不用等模型，就能验中文排版。

用法：
    python scripts/make_translated_demo.py --dump     # 列出待翻译句子，补齐 json
    python scripts/make_translated_demo.py            # 渲染两种版式
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import analyzer, annotator, markup, parsers, render  # noqa: E402

SRC = ROOT / "samples" / "sample_article.md"
TRANS = ROOT / "samples" / "translations_zh.json"
OUT = ROOT / "out"
LEVEL = "cet4"
TITLE = "The Cost of Convenience"


def collect_blocks() -> list[dict]:
    raw = SRC.read_bytes()
    blocks, _info = parsers.parse(SRC.name, raw)
    parsed = annotator.analyze_document([b.as_dict() for b in blocks], LEVEL)
    hb = markup.build(parsed, LEVEL)
    return hb["blocks"]


def sentences(blocks: list[dict]) -> list[str]:
    """按渲染时的同一套切分取出所有要翻译的句子（跳过代码/图表/表格与空块）。"""
    out: list[str] = []
    for b in blocks:
        if b.get("meta", {}).get("skip") or (b.get("type") or "") in ("code", "figure", "table"):
            continue
        text = (b.get("text") or "").strip()
        if len(text) < 2:
            continue
        for _s, _e, sent in analyzer.split_spans(text):
            out.append(sent)
    return out


def load_map() -> dict[str, str]:
    if TRANS.exists():
        try:
            d = json.loads(TRANS.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                return {str(k): str(v) for k, v in d.items()}
        except ValueError:
            pass
    return {}


def main() -> int:
    blocks = collect_blocks()
    sents = sentences(blocks)
    m = load_map()

    missing = [s for s in sents if not m.get(s)]
    if "--dump" in sys.argv or missing:
        merged = {s: m.get(s, "") for s in sents}
        # 保留已经在别处翻过、但这篇文章不再出现的句子，避免手翻成果被覆盖掉
        for k, v in m.items():
            merged.setdefault(k, v)
        TRANS.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"句子数={len(sents)}  待翻译/缺失={len(missing)}  → 已写入 {TRANS.name}")
        for s in missing:
            print("  ·", s)
        if missing:
            print("\n请补齐 samples/translations_zh.json 后重跑（不带 --dump）。")
            return 0

    translations: dict[str, dict] = {}
    zh_all = 0
    for b in blocks:
        if b.get("meta", {}).get("skip") or (b.get("type") or "") in ("code", "figure", "table"):
            continue
        text = (b.get("text") or "").strip()
        if len(text) < 2:
            continue
        spans = analyzer.split_spans(text)
        items = []
        for s, e, sent in spans:
            zh = m.get(sent, "")
            if not zh:
                continue
            items.append({"start": s, "end": e, "en": sent, "zh": zh})
        if not items:
            continue
        all_zh = len(items) == len(spans)
        translations[b["id"]] = {
            "sentences": items,
            "zh": "".join(x["zh"] for x in items) if all_zh else "",
            "partial": not all_zh,
        }
        zh_all += len(items)

    hb = markup.build(annotator.analyze_document(
        [b.as_dict() for b in parsers.parse(SRC.name, SRC.read_bytes())[0]], LEVEL), LEVEL)
    hb["title"] = TITLE

    written = []
    for mode, label in (("sentence", "逐句对照"), ("paragraph", "整段附译")):
        hb["translations"] = translations
        hb["trans_mode"] = mode
        hb["trans_note"] = (f"中文译文 {len(translations)}/{len(translations)} 段"
                            "（本样例为人手译文，用于验收版式）")
        html = render.render_handbook(hb, TITLE)
        p = OUT / f"handbook-{LEVEL}-译文-{label}.html"
        p.write_text(html, encoding="utf-8")
        written.append((p, len(html)))

    lines = [f"源文件   : {SRC.name}",
             f"段落数   : {len(translations)}  译文句数: {zh_all}",
             f"标注计数 : {hb['counters']}"]
    for p, n in written:
        lines.append(f"渲染输出 : {p.name}  ({n} 字符)")
    (OUT / "_demo.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
