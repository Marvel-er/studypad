"""
`check_inline_js.py` 里那条「知识库表格列数」断言的反向验证。

**为什么单独一个文件**：这条断言本身是被反向验证才敢信的。
项目里栽过三次「假绿断言」（`"tr-zh" in html` 恒真、假模型恰好合法对齐、
`cb-empty not in text` 恒真），每次都是「断言看起来合理、从没真正失败过」。
所以每加一条静态断言，就得先证明它**会失败**。

它验的是自己「能不能失败」，不是验业务代码：
  · 故意把列数改少 / 改多 / 改合计 → 必须报错
  · 故意把 KB_COLS / KB_HEAD 整块删掉 → 必须报「断言本身失效」
    （而不是默默返回空 —— 「断言失效」和「断言通过」长得一模一样是最危险的）
  · 原文不动 → 必须不报错（防误报）

跑法：
    python scripts/run_selftest.py scripts/probe_kb_cols.py out/_kbcols.txt
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

# ⚠ 知识库搬到独立页后，这里必须指向 **library.html**。
# 曾经指着 index.html，于是探针验的是「主页里残留的知识库代码」——
# 拆完页那部分已经不存在，替换全部失败、断言全成恒真。
HTML = ROOT / "backend" / "static" / "library.html"

FAILED: list[str] = []
N = 0


def check(label: str, cond, extra: str = "") -> None:
    global N
    N += 1
    if cond:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label} {extra}")
        FAILED.append(label)


def _load():
    spec = importlib.util.spec_from_file_location(
        "chk", ROOT / "scripts" / "check_inline_js.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _js_of(html: str) -> str:
    blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)
    return "\n;\n".join(b.strip() for b in blocks)


def _set_last_width(html: str, kind: str, pct: int) -> str:
    """把某一本的最后一列（掌握列）改成 pct%。动态定位，不写死具体数字 ——
    列宽值会随排版调整而变，写死替换串的话，改一次列宽这个探针就静默失效。"""
    pat = re.compile(r"(\b" + kind + r":\s*\[)([\d,\s]+)(\])")
    m = pat.search(html)
    assert m, f"没找到 {kind} 的列宽定义"
    nums = [int(x) for x in m.group(2).replace(" ", "").strip(",").split(",") if x]
    nums[-1] = pct
    return html[:m.start()] + m.group(1) + ", ".join(str(n) for n in nums) \
        + m.group(3) + html[m.end():]


def _swap_font(html: str, new_font: str) -> str:
    """把 `.kb-w{...}` 里的 font-family 换掉。动态定位，不写死原值。"""
    pat = re.compile(r"(\.kb-w\s*\{[^}]*?font-family\s*:\s*)([^;}]+)")
    m = pat.search(html)
    assert m, "没找到 .kb-w 的 font-family"
    return html[:m.start(2)] + new_font + html[m.end(2):]


def main() -> int:
    print("== 反向验证：知识库表格列数断言 ==")
    chk = _load()
    orig = HTML.read_text(encoding="utf-8")

    # 先确认原文里确实有这两张表 —— 否则下面的反向验证都在验空气
    check("原文里存在 KB_HEAD", "var KB_HEAD" in orig)
    check("指向的是知识库页（拆页后 kbCard 已不在主页）",
          "kbCard" in orig, HTML.name)
    check("原文里存在 KB_COLS", "var KB_COLS" in orig)
    check("原文本身不报错（防误报）", chk.check_kb_cols(_js_of(orig)) == [],
          str(chk.check_kb_cols(_js_of(orig))))
    check("列宽合计都是 100%",
          all(abs(v - 100) <= 2 for v in chk.widths_of(_js_of(orig)).values()),
          str(chk.widths_of(_js_of(orig))))

    # 每一种破坏都必须被抓住。
    # 列宽相关的用例**动态构造**：写死 `words: [13, 11, ...]` 这种替换串的话，
    # 哪天为了排版调整了列宽数字，探针就会「构造失败」而静默放过 —— 
    # 这类「替换不到就跳过」的写法等于没有断言。
    cases = [
        ("列数少一个", lambda s: re.sub(
            r"(\bwords:\s*\[)([\d,\s]+)(\])",
            lambda m: m.group(1) + ",".join(
                m.group(2).replace(" ", "").strip(",").split(",")[:-1]) + m.group(3),
            s, count=1)),
        ("列数多一个", lambda s: re.sub(
            r"(\bwords:\s*\[)([\d,\s]+)(\])",
            lambda m: m.group(1) + ",".join(
                m.group(2).replace(" ", "").strip(",").split(",") + ["5"]) + m.group(3),
            s, count=1)),
        ("列宽合计不足 100", lambda s: _set_last_width(s, "words", 4)),
        ("KB_COLS 整块删掉",
         lambda s: re.sub(r"var KB_COLS = \{.*?\n\};", "", s, flags=re.S)),
        ("KB_HEAD 整块删掉",
         lambda s: re.sub(r"var KB_HEAD = \{.*?\n\};", "", s, flags=re.S)),
    ]
    for name, mutate in cases:
        mutated = mutate(orig)
        check(f"构造出的坏样本确实与原文不同（{name}）", mutated != orig)
        if mutated == orig:
            continue          # 构造失败就跳过断言，别留一条恒真
        bad = chk.check_kb_cols(_js_of(mutated))
        check(f"能抓住：{name}", bool(bad), str(bad))

    # 断言失效必须**报出来**，不能返回空 —— 「失效」与「通过」长得一样最危险
    gone = re.sub(r"var KB_HEAD = \{.*?\n\};", "", orig, flags=re.S)
    bad = chk.check_kb_cols(_js_of(gone))
    check("KB_HEAD 缺失时报的是「断言失效」而不是「通过」",
          any("失效" in m for m in bad), str(bad))

    # ---- 可读性/布局两条红线 ----
    print("\n-- 字体与掌握列宽 --")
    ok = chk.check_kb_readability(orig, _js_of(orig))
    check("现状不报问题（防误报）", ok == [], str(ok))

    read_cases = [
        ("单词列改回手写体",
         lambda s: _swap_font(s, "'Segoe Script','Bradley Hand',cursive")),
        ("单词列换成 Comic Sans",
         lambda s: _swap_font(s, "'Comic Sans MS',cursive")),
        ("单词列换成未知字体",
         lambda s: _swap_font(s, "SomeWeirdFont")),
        ("语法本掌握列给 6%", lambda s: _set_last_width(s, "grammar", 6)),
        ("句型本掌握列给 6%", lambda s: _set_last_width(s, "patterns", 6)),
        (".kb-w 规则被改名（字体那条）",
         # 必须改**带 font-family 的那一条**，不能改第一条匹配 ——
         # 第一条是 `table.kb tr.done .kb-w{text-decoration...}`，改它不影响检查。
         lambda s: re.sub(r"(\n)\.kb-w\s*\{", r"\1.kb-word{", s, count=1)),
    ]
    for name, mutate in read_cases:
        mutated = mutate(orig)
        check(f"构造出的坏样本确实与原文不同（{name}）", mutated != orig)
        if mutated == orig:
            continue
        bad = chk.check_kb_readability(mutated, _js_of(mutated))
        check(f"能抓住：{name}", bool(bad), str(bad))

    # 改列宽后列数断言也要仍然成立（两个断言不互相掩盖）
    narrowed = _set_last_width(orig, "grammar", 6)
    bad = chk.check_kb_cols(_js_of(narrowed))
    check("掌握列改窄时列数断言仍报合计不足",
          any("100%" in m for m in bad), str(bad))

    print(f"\n{N - len(FAILED)}/{N} 通过")
    if FAILED:
        print("失败项：" + "; ".join(FAILED))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())