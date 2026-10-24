"""
生成「翻译失败」的视觉对照：修复前 vs 修复后。

为什么要单独做这个：留白是个**视觉**问题，断言只能验「没有空绿框」，
验不了「用户看到的整页留白确实消失了」。所以这里把同一份「部分翻译失败」
的语料分别喂给旧实现和新实现，各出一份 HTML，再用 Chrome 截图肉眼比对。

旧实现怎么来：把 `_render_block_sentence` 换成修复前的版本（在
`test_translate_e2e.py` 之前的历史里），也就是给「这句没译文」也产出一个
`<div class="tr-zh partial">（本句未译出）</div>`。其余代码完全一致，
保证对照的只有这一个变量。

用法：
    python scripts/run_selftest.py scripts/make_trans_fail_demo.py out/_demo.txt
    python scripts/run_selftest.py scripts/make_trans_fail_demo.py out/_demo_long.txt long_article.md

（第 2 个位置参数是 samples 下的文件名；长文夹具用 long_article.md，
  它才会跨页，才能验「留白分页」。）

产物：out/visual/<stem>_before.html  out/visual/<stem>_after.html
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import annotator, markup, parsers, render  # noqa: E402
from app.analyzer import split_spans  # noqa: E402

OUT = ROOT / "out" / "visual"
OUT.mkdir(parents=True, exist_ok=True)

SRC_NAME = sys.argv[1] if len(sys.argv) > 1 else "sample_article.md"
SRC = Path(SRC_NAME) if Path(SRC_NAME).is_absolute() else (ROOT / "samples" / SRC_NAME)
TAG = SRC.stem

# ---------------------------------------------------------------- 语料
blocks, _ = parsers.parse(SRC.name, SRC.read_bytes())

hb = markup.build(annotator.analyze_document([b.as_dict() for b in blocks], "cet4"), "cet4")
hb["title"] = SRC.stem.replace("_", " ").title()
hb["trans_mode"] = "sentence"
hb["llm_note"] = "已接入 deepseek / deepseek-v4-pro，增强 12 处讲解"

# ---------------------------------------------------------------- 造「一批失败」
#
# 真实成因：`translate_blocks` 把跨段落的句子合批并发发给模型，
# 某一批撞上 429 / 超时 → `_translate_group` 捕到异常 → 该批**整批**返回空串。
# 一批 8 句，落在一页上就是 3~4 个段落各丢 2~3 句 —— 于是每段都变成 partial。
# 这就是用户那张截图里「一排绿框、框里没字」的形状。
FAIL_EVERY = 3      # 每 3 句漏掉 2 句，模拟一批大批量失败


def _simulate(b: dict) -> dict | None:
    text = (b.get("text") or "").strip()
    if not text or len(text) < 2:
        return None
    spans = split_spans(text)
    if not spans:
        return None
    sents, missing = [], 0
    for i, (s, e, t) in enumerate(spans):
        if i % FAIL_EVERY == 0:
            sents.append({"start": s, "end": e, "en": t, "zh": f"【第{i + 1}句译文】{t[:24]}"})
        else:
            missing += 1
    if not sents:
        return None
    return {"sentences": sents, "zh": "", "partial": True, "missing": missing}


trans = {}
for b in hb["blocks"]:
    if b.get("meta", {}).get("skip"):
        continue
    r = _simulate(b)
    if r:
        trans[b["id"]] = r
hb["translations"] = trans
hb["trans_note"] = (f"中文译文 {len(trans)}/{len(trans)} 段，"
                    f"{sum(r['missing'] for r in trans.values())} 句对齐失败已跳过")

# ---------------------------------------------------------------- 修复后的产物
html_after = render.render_handbook(hb, hb["title"])
(OUT / f"{TAG}_after.html").write_text(html_after, encoding="utf-8")

# ---------------------------------------------------------------- 修复前的产物
_OLD = '''def _old_sentence(block, tr):
    """修复前的逐句渲染：没有译文也产出一个绿框。"""
    text = block.get("text") or ""
    if not tr:
        return render._render_block_paragraph(block, None)
    zh_map = {s["start"]: s["zh"] for s in tr.get("sentences", [])
              if render._visible(s.get("zh"))}
    spans = split_spans(text)
    if not spans:
        return render._render_block_paragraph(block, None)
    parts, cursor = [], 0
    for s, e, _sent in spans:
        if s > cursor and text[cursor:s].strip():
            parts.append('<div class="text">%s</div>' % render._esc(text[cursor:s]))
        inner = render._render_block_text(block, s, e)
        zh = zh_map.get(s)
        cursor = e
        if not render._visible(re.sub(r"<[^>]+>", "", inner)) and not render._visible(zh):
            continue
        if render._visible(zh):
            parts.append('<div class="tr-pair"><div class="text">%s</div>'
                         '<div class="tr-zh">%s</div></div>' % (inner, render._esc(zh)))
        else:
            parts.append('<div class="tr-pair"><div class="text">%s</div>'
                         '<div class="tr-zh partial">（本句未译出）</div></div>' % inner)
    if cursor < len(text) and text[cursor:].strip():
        parts.append('<div class="text">%s</div>' % render._esc(text[cursor:]))
    if not parts:
        return ""
    return '<div class="%s">%s</div>' % (
        render._block_classes(block, "tr-sent"), "".join(parts))
'''
_ns: dict = {"render": render, "re": re, "split_spans": split_spans}
exec(_OLD, _ns)                                   # noqa: S102 — 自建对照实现，非外部输入

_OLD_PRINT = """@media print{
  body{background:#fff}
  .sheet{box-shadow:none;margin:0;max-width:none;border-radius:0;padding:0 0 10mm}
  .sheet::before{opacity:.5}
  .block{break-inside:avoid}
  .note{break-inside:avoid}
  #tip{display:none}
  .w-target{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  .note{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  .no-print{display:none!important}
}"""


def _old_css(html: str) -> str:
    """
    把产物里的打印分页规则换回修复前的版本。

    为什么必须一起换：`before` 与 `after` 共用同一份 `render.CSS`，
    如果只回退 `_render_block_sentence`，那份「修复前」的产物照样享受着
    **新的分页 CSS**（.block 允许断），于是留白分页测不出来 —— 对照被混淆。
    而「留白分页」恰恰是分页 CSS 与占位框**共同**造成的，两个变量都得回退。
    """
    return re.sub(r"@media print\{[\s\S]*?\n\}", _OLD_PRINT, html, count=1)


_new_sentence = render._render_block_sentence
render._render_block_sentence = _ns["_old_sentence"]
try:
    html_before = _old_css(render.render_handbook(hb, hb["title"]))
finally:
    render._render_block_sentence = _new_sentence
(OUT / f"{TAG}_before.html").write_text(html_before, encoding="utf-8")

# ---------------------------------------------------------------- 量化对比
def stats(html: str) -> dict:
    boxes = re.findall(r'<div class="tr-zh[^"]*">(.*?)</div>', html, re.S)
    plain = [re.sub(r"<[^>]+>", "", b).strip() for b in boxes]
    blank = [t for t in plain if not t]
    ph = [t for t in plain if "本句未译出" in t]
    real = [t for t in plain if t and "本句未译出" not in t]
    return {
        "boxes": len(boxes), "blank": len(blank), "ph": len(ph), "real": len(real),
        # 「无译文绿框」= 空框 + 占位框 —— 用户看到的就是这个
        "useless": len(blank) + len(ph),
        "miss": len(re.findall(r'class="tr-miss"', html)),
        "note": len(re.findall(r'class="hb-note"', html)),
        "size": len(html),
    }


sb, sa = stats(html_before), stats(html_after)

print("=" * 96)
print(f"翻译失败视觉对照 · {TAG}（同一份语料，唯一变量是渲染器）")
print("=" * 96)
for name, s in (("修复前", sb), ("修复后", sa)):
    print(f"  {name}：绿框 {s['boxes']:>2} 个"
          f"（真译文 {s['real']:>2} / 空 {s['blank']:>2} / 「（本句未译出）」占位 {s['ph']:>2}）"
          f" | **无译文绿框 {s['useless']:>2} 个**"
          f" | 汇总说明 {s['miss']} 条 | 告警条 {s['note']} | {s['size']} 字节")
print()
print(f"对照文件：{OUT / (TAG + '_before.html')}")
print(f"          {OUT / (TAG + '_after.html')}")
print()
print("断言：")
checks = [
    (sb["ph"] > 0, f"修复前确实复现了占位空绿框（{sb['ph']} 个）"),
    (sb["useless"] > sa["useless"],
     f"无译文绿框大幅减少：{sb['useless']} → {sa['useless']}"),
    (sa["useless"] == 0, "修复后：无译文绿框为 0"),
    (sa["real"] == sb["real"], f"修复后真译文一个不少（{sa['real']} 个，与修复前一致）"),
    (sa["miss"] > 0, f"修复后：未译出的句子汇总成 {sa['miss']} 条灰色说明"),
    ('class="hb-note"' in html_after,
     "修复后：顶部给出降级原因（按句报数，段覆盖满也会报）"),
]
ok = True
for cond, label in checks:
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    ok = ok and cond

print()
print("说明：两份产物共用同一份 render_handbook（含告警条逻辑），"
      "**唯一变量是 _render_block_sentence**，")
print("      所以 before 里也会出现告警条 —— 那是本轮另一处修复，不属于这次对照。")
print("      这次对照要看的只有一件事：那 11 个「没有译文的绿框」有没有消失。")

sys.exit(0 if ok else 1)
