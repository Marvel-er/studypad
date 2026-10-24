"""
主题（暗色模式）相关断言的**反向验证**。

`check_inline_js.check_theme()` 守四条红线：页面内不许浅色硬编码、
暗色令牌必须齐全、防闪烁脚本必须在样式表之前、切换逻辑与按钮齐全。
每一条都可能变成恒真的假绿 —— 比如令牌解析正则失配、
浅色扫描漏了某个色值形态。所以这里逐条构造破坏，**确认它会失败**。

跑法：
    python scripts/run_selftest.py scripts/probe_theme.py out/_theme.txt
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_inline_js as CI  # noqa: E402

STATIC = ROOT / "backend" / "static"
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


def main() -> int:
    print("== 反向验证：主题（暗色模式）断言 ==")

    index = (STATIC / "index.html").read_text(encoding="utf-8")
    library = (STATIC / "library.html").read_text(encoding="utf-8")
    css = (STATIC / "common.css").read_text(encoding="utf-8")
    cjs = (STATIC / "common.js").read_text(encoding="utf-8")

    # 前置：确认被验对象真的存在（否则下面全在验空气）
    check("存在 index.html", bool(index))
    check("存在 library.html", bool(library))
    check("common.css 有 :root 令牌块", ":root{" in css or ":root {" in css)
    check("common.css 有暗色覆盖块", '[data-theme="dark"]' in css)
    check("common.js 有主题逻辑", "themeApply" in cjs)

    # 现状必须不报错（防误报）
    ok = CI.check_theme({"index.html": index, "library.html": library})
    check("现状不报错（防误报）", ok == [], str(ok)[:300])

    # ---- ① 浅色硬编码 ----
    cases_1 = [
        ("页面里写回 background:#fff",
         {**{"index.html": index}, "library.html": library.replace(
             ".kb-hero{", ".kb-hero{background:#fff;")}),
        ("页面里写回浅色 #f6f7f9",
         {"index.html": index.replace(
             ".lv{border:1px solid var(--border);background:var(--card);",
             ".lv{border:1px solid var(--border);background:#f6f7f9;"),
          "library.html": library}),
    ]
    for label, pages in cases_1:
        mutated = pages["index.html"] + pages["library.html"]
        orig_pair = index + library
        check(f"构造的坏样本确实不同（{label}）", mutated != orig_pair)
        bad = CI.check_theme(pages)
        check(f"能抓住：{label}", any("浅色硬编码" in m for m in bad), str(bad)[:200])

    # @media print 里的浅色**不该**被报出来
    print_pdf = library.replace(
        ".kb-hero{", "@media print{.kb-hero{background:#fff;}/*x*/}\n.kb-hero{")
    bad = CI.check_theme({"index.html": index, "library.html": print_pdf})
    check("打印块里的浅色不误报",
          not any("浅色硬编码" in m for m in bad), str(bad)[:200])

    # ---- ② 令牌完整性 ----
    # 故意从暗色块里删掉一个令牌定义
    m = re.search(r'\[data-theme="dark"\]\s*\{(.*?)\n\}', css, re.S)
    check("能解析到暗色块", m is not None)
    body = m.group(1)
    var_m = re.search(r"\n\s*(--[\w-]+)\s*:[^;]*;", body)
    check("暗色块里能定位到令牌", var_m is not None)
    if var_m:
        broken = css[:m.start(1)] + body.replace(var_m.group(0), "") + css[m.end(1):]
        old_css = CI.STATIC.joinpath("common.css")
        backup = old_css.read_text(encoding="utf-8")
        try:
            old_css.write_text(broken, encoding="utf-8")
            bad = CI.check_theme({"index.html": index, "library.html": library})
            check("能抓住：暗色块漏令牌", any("暗色块漏了" in x for x in bad),
                  str(bad)[:200])
        finally:
            old_css.write_text(backup, encoding="utf-8")

    # 删掉整个暗色块
    no_dark = re.sub(r'\[data-theme="dark"\]\s*\{.*?\n\}', "", css, flags=re.S)
    old_css = STATIC / "common.css"
    backup = old_css.read_text(encoding="utf-8")
    try:
        old_css.write_text(no_dark, encoding="utf-8")
        bad = CI.check_theme({"index.html": index, "library.html": library})
        check("能抓住：暗色块整个没了", any("没有 [data-theme" in x for x in bad),
              str(bad)[:200])
    finally:
        old_css.write_text(backup, encoding="utf-8")

    # ---- ③ 防闪烁脚本 ----
    # 定位方式与被验逻辑一致：脚本内容出现在 <head> 里、且在 common.css 之前。
    head = index.split("</head>")[0]
    guard = head.find("studypad.theme")
    css_at = index.find('href="/static/common.css"')
    check("防闪烁脚本确实在样式表之前（现状正确）",
          guard >= 0 and css_at >= 0 and guard < css_at,
          f"guard={guard} css={css_at}")

    # 把**脚本那一段**（从 `<script>` 到 `</script>`）剪出来，贴到
    # `<link ... common.css>` 的**后面**。
    # ⚠ 必须按字符位置重组，不能用字符串 replace 整段 head ——
    #   那样会把 head 结构一起弄乱，报出来的错变成「没有防闪烁脚本」，
    #   验的就不是「位置放错」这条规则了。
    gs = index.rfind("<script>", 0, guard)
    ge = index.find("</script>", guard) + len("</script>")
    block = index[gs:ge]
    rest = index[:gs] + index[ge:]
    link = '<link rel="stylesheet" href="/static/common.css">'
    at = rest.find(link) + len(link)
    late = rest[:at] + "\n" + block + rest[at:]
    # 确认构造真的把脚本挪到了 link 之后
    check("构造的样本确实把脚本挪到了样式表之后",
          late.find("studypad.theme") > late.find(link))
    bad = CI.check_theme({"index.html": late, "library.html": library})
    check("能抓住：防闪烁脚本在样式表之后",
          any("之后" in m for m in bad), str(bad)[:200])

    gone = index[:gs] + index[ge:]
    bad = CI.check_theme({"index.html": gone, "library.html": library})
    check("能抓住：防闪烁脚本没了", any("防闪烁" in m for m in bad), str(bad)[:200])

    # ---- ④ 切换按钮与逻辑 ----
    bad = CI.check_theme({"index.html": index.replace('id="btnTheme"', 'id="btnThemeX"'),
                          "library.html": library})
    check("能抓住：切换按钮没了", any("btnTheme" in m for m in bad), str(bad)[:200])

    old_js = STATIC / "common.js"
    backup = old_js.read_text(encoding="utf-8")
    try:
        old_js.write_text(backup.replace("prefers-color-scheme", "xxx"),
                          encoding="utf-8")
        bad = CI.check_theme({"index.html": index, "library.html": library})
        check("能抓住：不再跟随系统", any("prefers-color-scheme" in m for m in bad),
              str(bad)[:200])
    finally:
        old_js.write_text(backup, encoding="utf-8")

    print(f"\n{N - len(FAILED)}/{N} 通过")
    if FAILED:
        print("失败项：" + "; ".join(FAILED))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())