"""探针：`--`（em dash 的 ASCII 写法）不能被当成构词连字符吃进同一个 token。

背景（2026-10-15 用户反馈）：导入《A Mystery of Heroism》后生词表里出现一行
词头写着 `anticipation--anticipation`、音标/词性/释义/例句四列全空。

真因是 `lemmatize._WORD_RE` 允许任意连续连字符，把 `--` 两侧的两个词粘成了一个
谁都认不得的 token → 判成「六档之外」+ 查不到词条 → 全空。

这个探针做两件事：
  1. 词形层面：`--` 必须断开；复合词 / 撇号形式必须**保持不断**（别修出新洞）；
  2. 真实文档层面：把用户那篇的实际 blocks 重跑一遍标注，断言
     「生词表里没有 `--` 词头」且「全空行的数量比修复前少」。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import annotator, markup  # noqa: E402
from app.lemmatize import tokenize  # noqa: E402

LIBRARY = Path.home() / ".studypad" / "library" / "handbooks"

out: list[str] = []
bad: list[str] = []

# ---------------------------------------------------------------- 1. 词形
# (原文, 期望切出的 token)
CASES: list[tuple[str, list[str]]] = [
    # `--` 是分隔符：必须断开
    ("with anticipation--anticipation of a blow", ["with", "anticipation", "anticipation", "of", "a", "blow"]),
    ("them--in", ["them", "in"]),
    ('"Well--ah," he said', ["Well", "ah", "he", "said"]),
    ('the lad--"don\'t', ["the", "lad", "don't"]),
    ("heroes.--They", ["heroes", "They"]),
    # 真正的 em dash 本来就断得开，不能被本次修改影响
    ("anticipation\u2014anticipation", ["anticipation", "anticipation"]),
    # 单连字符复合词要保留（补充词典里有这些词条）
    ("death-wound swift-boiling black-bearded", ["death-wound", "swift-boiling", "black-bearded"]),
    # 撇号 / 所有格要保留
    ("girl's don't brother-in-law's o'clock", ["girl's", "don't", "brother-in-law's", "o'clock"]),
    # 尾随连字符不该产出带 `-` 的假词
    ("well- top-", ["well", "top"]),
]

out.append("== 1. 词形切分 ==")
for src, want in CASES:
    got = [t for t, _s, _e in tokenize(src)]
    ok = got == want
    out.append(f"  {'OK ' if ok else 'FAIL'} {src!r}")
    if not ok:
        bad.append(f"tokenize({src!r}) = {got}，期望 {want}")
        out.append(f"       得到 {got}")
        out.append(f"       期望 {want}")
out.append(f"  词形用例 {len(CASES)} 个，失败 {len([b for b in bad])} 个")

# ---------------------------------------------------------------- 2. 真实文档
out.append("")
out.append("== 2. 真实文档（知识库里的历史手账）==")
docs = sorted(LIBRARY.glob("*.json")) if LIBRARY.exists() else []
if not docs:
    out.append("  （知识库为空，跳过 —— 这一节需要一篇用户实际导入过的手账）")
else:
    for f in docs:
        rec = json.load(open(f, encoding="utf-8"))
        # 修复前的现状：库里存的那份 vocab（由旧正则产出）
        before = [v for v in (rec.get("vocab") or [])
                  if not (v.get("phonetic") and v.get("gloss"))]
        dash_before = [v for v in (rec.get("vocab") or []) if "--" in (v.get("lemma") or "")]

        blocks = [{"id": b["id"], "type": b.get("type"), "text": b.get("text") or "",
                   "meta": b.get("meta") or {}} for b in rec.get("blocks") or []]
        parsed = annotator.analyze_document(blocks, rec["level_id"])
        hb = markup.build(parsed, rec["level_id"])
        after = [v for v in hb["vocab"] if not (v.get("phonetic") and v.get("gloss"))]
        dash_after = [v for v in hb["vocab"] if "--" in (v.get("lemma") or "")]

        out.append(f"  {rec.get('title')}（{rec['level_id']}）")
        out.append(f"    词头带 `--` 的行：修复前 {len(dash_before)} → 重跑后 {len(dash_after)}")
        out.append(f"    信息不全的行    ：修复前 {len(before)} → 重跑后 {len(after)}")
        if dash_before:
            out.append(f"    修复前那几行    ：{[v['lemma'] for v in dash_before][:5]}")
        if dash_after:
            bad.append(f"{rec.get('title')}：重跑后仍有带 `--` 的词头 {[v['lemma'] for v in dash_after][:5]}")
        if len(after) > len(before):
            bad.append(f"{rec.get('title')}：重跑后信息不全的行反而变多了（{len(before)} → {len(after)}）")

        # anticipation 这一行必须有完整信息（它在 ielts 词表里，有音标/释义/例句）
        row = [v for v in hb["vocab"] if (v.get("lemma") or "").lower() == "anticipation"]
        if row:
            v = row[0]
            have = bool(v.get("phonetic")) and bool(v.get("gloss")) and bool(v.get("pos"))
            out.append(f"    anticipation 行  ：音标={v.get('phonetic')!r} 词性={v.get('pos')!r} "
                       f"释义={v.get('gloss')!r} 例句={'有' if v.get('example') else '无'} → "
                       f"{'OK' if have else 'FAIL'}")
            if not have:
                bad.append("anticipation 行信息仍不全")
        else:
            out.append("    （这篇文档里没有 anticipation，跳过单行断言）")

# ---------------------------------------------------------------- 结论
out.append("")
out.append(f"结果：{'全部通过' if not bad else '有失败 ' + str(len(bad)) + ' 项'}")
for b in bad:
    out.append(f"  ✗ {b}")
print("\n".join(out))
sys.exit(1 if bad else 0)
