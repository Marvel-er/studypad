"""探针：原文带前导空白时，译文还能不能挂到句子上。

曾有的 bug（2026-10-14 修）：`translate_blocks` 用 `text.strip()` 之后的文本
算 span，而 `annotator`（标注偏移）与 `render`（切片偏移）都用**未 strip** 的
`block["text"]`。strip 会吃掉前导空白，第二句及以后的起始位置整体前移
（实测 `[(2,69),(70,178)]` → `[(0,67),(68,176)]`），于是 render 拿着 70 去
`zh_map` 里找、只找到 68 → **一个绿框都不出**，还顺手误报
「本段另有 N 句未取到译文」和「中文译文只覆盖 0/N 句」。静默全丢，比报错更难发现。

这里跑**真实的** `translate_blocks`（假模型，不发请求），端到端验证。
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

TMP = Path(tempfile.gettempdir()) / "_studypad_wstest"
os.environ["STUDYPAD_HOME"] = str(TMP)

from app import annotator, llm, markup, render, translate  # noqa: E402
from app.analyzer import split_spans  # noqa: E402

out: list[str] = []
fails: list[str] = []


def check(cond: bool, label: str, detail: str = "") -> None:
    out.append(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  → {detail}" if detail else ""))
    if not cond:
        fails.append(label)


# 关键：**前导空格**。_from_specs（PDF/OCR 通道）不 strip 文本，
# 这正是可能产生这种形态的地方。
TEXT = ("  The pandemic had forced millions of employees out of their offices. "
        "Companies discovered how much of their success depended on informal "
        "conversations in corridors and kitchens.")

out.append("--- 1. strip 与否，span 偏移真的不一样吗（bug 的前提）---")
a = split_spans(TEXT)
b = split_spans(TEXT.strip())
out.append(f"  未 strip：{[x[:2] for x in a]}")
out.append(f"  已 strip：{[x[:2] for x in b]}")
check([x[:2] for x in a] != [x[:2] for x in b],
      "strip 会改变 span 偏移",
      "相同" if [x[:2] for x in a] == [x[:2] for x in b] else "不同")

out.append("")
out.append("--- 2. 跑真实 translate_blocks（假模型）---")

CFG = llm.LLMConfig(provider="deepseek", api_key="sk-fake",
                    base_url="http://fake/v1", model="fake")
translate.clear_cache()

_calls: list[int] = []


def fake_chat(cfg, messages, **kw):
    user = messages[-1]["content"]
    sents = re.findall(r"^\d+\.\s?(.*)$", user, re.M)
    _calls.append(len(sents))
    return json.dumps({"t": [f"译文{i}" for i in range(len(sents))]}, ensure_ascii=False)


llm.chat, _orig = fake_chat, llm.chat
try:
    blocks = [{"id": "b0000", "type": "paragraph", "order": 0, "text": TEXT,
               "page": 1, "level": None, "bbox": None, "meta": {}, "annotations": []}]
    tr = translate.translate_blocks(blocks, CFG)
finally:
    llm.chat = _orig

rec = (tr["blocks"] or {}).get("b0000") or {}
starts = [s["start"] for s in rec.get("sentences") or []]
out.append(f"  translate 产出的句子起始 = {starts}")
out.append(f"  render 将会使用的 span 起始 = {[x[0] for x in a]}")
check(starts == [x[0] for x in a],
      "translate 的 span 偏移与 render 的一致（都用未 strip 的原文）",
      f"{starts} vs {[x[0] for x in a]}")

out.append("")
out.append("--- 3. 端到端：绿框、误报、覆盖率 ---")
parsed = annotator.analyze_document([dict(x) for x in blocks], "cet4")
hb = markup.build(parsed, "cet4")
hb["trans_mode"] = "sentence"
hb["translations"] = tr["blocks"]
html = render.render_handbook(hb, "前导空白")

n_boxes = html.count('class="tr-zh"')
out.append(f"  绿框数量 = {n_boxes}（期望 {len(a)}）")
check(n_boxes == len(a), "每句译文都配上了绿框", f"{n_boxes}/{len(a)}")
check("未取到译文" not in html, "没有误报「另有 N 句未取到译文」",
      "出现了误报" if "未取到译文" in html else "无")
check("中文译文只覆盖" not in html, "全部译出时页眉不谎报「只覆盖 N/M 句」",
      "误报了" if "中文译文只覆盖" in html else "正常")
check(tr["done"] == 1 and tr["skipped"] == 0,
      "translate 统计如实（done=1, skipped=0）",
      f"done={tr['done']} skipped={tr['skipped']}")

out.append("")
out.append(f"结果：{'全部通过' if not fails else str(len(fails)) + ' 项失败 — ' + '、'.join(fails)}")
print("\n".join(out))
sys.exit(1 if fails else 0)
