"""
探针：验证 `wordlist._compound_entry` 的复合词兜底，以及六档生词表的字段覆盖率。

为什么单独写一个探针：上一轮 `entry()` 只往低档回退导致生词表整列空白，
修完之后必须有一套「拿具体词逐个查」的验收，否则改坏了也没人发现。

用法：python scripts/run_selftest.py scripts/probe_compound.py out/_compound.txt
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import annotator, markup, parsers, wordlist  # noqa: E402

fail = 0


def check(cond: bool, msg: str) -> None:
    global fail
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        fail += 1


def show(word: str, level: str = "cet4") -> dict | None:
    hit = wordlist.lookup_entry(word, level)
    if not hit:
        print(f"  {word:<16} (无词条)")
        return None
    lemma, e = hit
    tag = f"[合成 c={e.get('c')}]" if e.get("c") else ""
    print(
        f"  {word:<16} -> {lemma:<16} "
        f"p={e.get('p', ''):<18} pos={(e.get('pos') or ''):<11} "
        f"t={(e.get('t') or '')[:26]:<28} s={'有' if e.get('s') else '无'} {tag}"
    )
    return e


print("=" * 96)
print("一、复合词兜底（_compound_entry）")
print("=" * 96)

COMPOUNDS = [
    ("Policymakers", "policy", "makers"),
    ("policymaker", "policy", "maker"),
    ("policymaking", "policy", "making"),
    ("groundbreaking", "ground", "breaking"),
    ("wellbeing", "well", "being"),
    ("healthcare", "health", "care"),
    ("breakthrough", "break", "through"),
]
for w, a, b in COMPOUNDS:
    e = show(w, "cet4")
    if e and e.get("c"):
        # 合成的释义必须写成 "A + B"，不能编一个中文词组出来
        check(" + " in (e.get("t") or ""), f"{w}: 合成释义含 ' + '（{e.get('t')}）")
        check(
            f"{a} + {b}" in (e.get("e") or ""),
            f"{w}: e 注明由 {a} + {b} 合成（{e.get('e')}）",
        )

print()
print("二、**反向**断言：常见短词不许被拆成复合词")
print("=" * 96)
# 这些词若走复合词分支会得到荒谬释义（there -> the + re）
for w in ["there", "where", "which", "other", "under", "water", "never", "about"]:
    hit = wordlist.lookup_entry(w, "cet4")
    check(hit is None or not hit[1].get("c"), f"{w}: 未走复合词合成（c 标记不存在）")

print()
print("三、上一轮实测缺字段的词，现在是否补齐")
print("=" * 96)
MUST = {
    "high_school": ["Policymakers"],
    "cet6": ["Policymakers", "deepened"],
    "kaoyan": ["Policymakers"],
    "ielts": ["Policymakers"],
    "toefl": ["Policymakers"],
}
for lv, words in MUST.items():
    print(f"  -- {lv} --")
    for w in words:
        e = show(w, lv)
        if e:
            check(bool(e.get("p")), f"{lv}/{w}: 有音标")
            check(bool(e.get("pos")), f"{lv}/{w}: 有词性")
            check(bool(e.get("t")), f"{lv}/{w}: 有释义")

print()
print("四、派生 / 拼写变体回归（上一轮已修，防回退）")
print("=" * 96)
# 注意：这里断言的是「词形反查**能命中一条有释义的词条**」。
# `decisive` / `organised` / `analysing` 本身就在六档词表里，
# 命中自身是正确的 —— 硬要求它派生成 `decision` / `organize` 反而是错的
# （那会用别的词的词条去解释它）。所以每个词给一个可接受集合。
DERIVED = [
    ("convulsive", {"convulsion"}),
    ("optimise", {"optimize", "optimise"}),
    ("hauling", {"haul"}),
    ("seized", {"seize"}),
    ("fulfils", {"fulfil", "fulfill"}),
    ("decisive", {"decisive", "decision"}),
    ("organised", {"organise", "organize"}),
    ("analysing", {"analyse", "analyze"}),
]
for w, ok in DERIVED:
    hit = wordlist.lookup_entry(w, "cet4")
    got = hit[0] if hit else None
    check(got in ok, f"{w} -> {got}（可接受：{'/'.join(sorted(ok))}）")
    check(bool(hit and (hit[1].get("t"))), f"{w}: 命中的词条有释义")

print()
print("=" * 96)
print("六、字段级补全（_fill）的收益：六档词表里有多少条目本该有音标却是空的")
print("=" * 96)
from app.levels import ORDER  # noqa: E402

n_empty_p = n_filled_p = 0
for lv in ORDER:
    d = wordlist._detail(lv)
    for w, e in d.items():
        if e.get("p"):
            continue
        n_empty_p += 1
        if (wordlist.entry(w, lv) or {}).get("p"):
            n_filled_p += 1
print(f"  六档词表里 p 为空的条目：{n_empty_p} 条")
if n_empty_p:
    print(f"  其中经字段级补全后拿到音标：{n_filled_p} 条"
          f"（{n_filled_p / n_empty_p * 100:.1f}%）")
else:
    print("  没有空音标条目（数据比预期好）")
check(n_filled_p > 0, "字段级补全确实补上了音标")
check(n_filled_p <= n_empty_p, "补全数不超过缺口数（没凭空造音标）")

print()
print("=" * 96)
print("五、真实文章的六档生词表字段覆盖率")
print("=" * 96)
src = ROOT / "samples" / "sample_article.md"
if not src.exists():
    print("  跳过：samples/sample_article.md 不存在")
else:
    blocks, _info = parsers.parse(src.name, src.read_bytes())
    for lv in ["high_school", "cet4", "cet6", "kaoyan", "ielts", "toefl"]:
        parsed = annotator.analyze_document([b.as_dict() for b in blocks], lv)
        hb = markup.build(parsed, lv)
        rows = hb.get("vocab") or []
        n = len(rows)
        has_p = sum(1 for r in rows if r.get("phonetic"))
        has_pos = sum(1 for r in rows if r.get("pos"))
        has_t = sum(1 for r in rows if r.get("gloss"))
        has_s = sum(1 for r in rows if r.get("example"))
        missing = [r.get("surface") for r in rows if not r.get("gloss")]
        print(
            f"  {lv:<12} 生词 {n:>2}  音标 {has_p:>2}  词性 {has_pos:>2} "
            f"释义 {has_t:>2}  例句 {has_s:>2}   仍缺: {missing if missing else '无'}"
        )
        check(not missing, f"{lv}: 生词表无缺释义的词")

print()
print("=" * 96)
print(f"结果：{'全部通过' if fail == 0 else str(fail) + ' 项失败'}")
print("=" * 96)
sys.exit(1 if fail else 0)
