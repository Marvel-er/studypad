"""
暗色模式的**视觉**验证：手账与卡片本在屏幕上能变暗，打印必须回到白底。

`check_theme` 那套静态断言只能证明「规则写了」，证明不了「浏览器认了」。
这里用 Chrome 无头把 `data-theme="dark"` 的产物渲出来，然后直接读 PDF 内容流
里的填充色 —— 判据是「页面背景矩形前面那条 rg」。

⚠ **判据必须区分「背景色」与「文字色」**：正文黑字也是 `0 0 0 rg`，
早先只看「有没有近黑填充色」，结果把正常正文判成了「打印没收回暗色」。
正解：只看**矩形填充**（`... re` + `f`）之前最近的 `rg`。

跑法（需要 Chrome）：
    python scripts/run_selftest.py scripts/probe_theme_render.py out/_theme_render.txt
"""
from __future__ import annotations

import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

sys.path.insert(0, str(ROOT / "backend"))

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



def _strip_comments(css: str) -> str:
    """
    剥掉 CSS 注释，**保留字符数**（用等长空格替换）。

    为什么必须剥：注释里出现 `{` 或 `}` 会让花括号配对从注释开始数，
    数到注释里的第一个 `}` 就以为块结束了 —— 实测 `@media print`
    后面那段中文注释让配对停在 32 字符处，print 块几乎整个没被取到。
    用 `re.sub` 直接删掉会让后续下标全错，所以等长替换更安全。
    """
    return re.sub(r"/\*.*?\*/", lambda m: " " * (m.end() - m.start()), css,
                  flags=re.S)


def _print_block(css: str) -> str:
    """
    取出 `@media print` 的**内容**（不含 @media 本身），按花括号配对。

    ⚠ 三个坑都踩过：
    ① `re.search(r"@media\\s+print")` 会先命中**注释里**提到
       「@media print」的那行说明文字 → 先 `_strip_comments` 解决。
    ② 配对必须从「`@media print` 后面的第一个 `{`」开始，
       不是从 `@media` 那个词的位置开始。
    ③ 块内有嵌套 `{ }`，不能在第一个 `}` 就停 —— 要数到配平为止。
    """
    css = _strip_comments(css)
    m = re.search(r"@media\s+print", css)
    if not m:
        return ""
    start = css.find("{", m.end())
    if start < 0:
        return ""
    depth = 0
    for i in range(start, len(css)):
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
            if depth == 0:
                return css[start + 1: i]
    return css[start + 1:]


def _print_resets(css: str, needed: list[str]) -> list[str]:
    """
    检查 `@media print` 块里有没有把 `needed` 里每个选择器重置回浅色。

    ⚠ 判据用「切出每条规则 → 看选择器里有没有该类名 → 看声明里有没有
    background/color」，**不用一条大正则**。原因：规则可能跨行
    （`.sheet{...;max-width:none;\n border-radius:0}`），
    `[^{}]*` 这类写法在嵌套/换行下极易失配（实测把 7 条全部误报成「漏了」）。
    """
    blk = _print_block(css)
    if not blk:
        return ["没有 @media print 块"]
    # 切出所有 `选择器 { 声明 }`
    rules = re.findall(r"([^{}]+)\{([^{}]*)\}", blk)
    reset = set()          # 已被重置的选择器文本
    for sel, body in rules:
        if "background" not in body and "color" not in body:
            continue
        for part in sel.split(","):
            reset.add(part.strip())
    missing = []
    for sel in needed:
        hit = False
        for r in reset:
            # r 形如 `[data-theme="dark"] .sheet` 或 `[data-theme="dark"] body *`
            if re.search(r"(^|[\s>])" + re.escape(sel) + r"(\s|$|\.|:|\[)",
                         r):
                hit = True
                break
        if not hit:
            missing.append(sel)
    return missing


def main() -> int:
    print("== 暗色模式 · 渲染验证 ==")

    import os
    import tempfile
    tmp_home = tempfile.mkdtemp(prefix="studypad_theme_")
    os.environ["STUDYPAD_HOME"] = tmp_home
    sample = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")

    from app import annotator, cards_render, library, markup, parsers, render
    blocks = [b.as_dict() for b in parsers.parse_text(sample)]
    hb = markup.build(annotator.analyze_document(blocks, "cet4"), "cet4")
    hb["title"] = "暗色验证"

    # ---------- 手账 ----------
    light = render.render_handbook(hb, "暗色验证")
    dark = light.replace('<html lang="zh-CN">',
                         '<html lang="zh-CN" data-theme="dark">', 1)
    check("手账里有暗色皮肤", '[data-theme="dark"]' in light)
    check("注入 data-theme 后确实命中暗色规则",
          len(re.findall(r"\[data-theme=\"dark\"\]", dark))
          == len(re.findall(r"\[data-theme=\"dark\"\]", light)))
    need = ["body", ".sheet", ".chip", ".legend", ".note", ".tr-zh", ".block"]
    missing = _print_resets(light, need)
    check("打印时关键元素都被收回了浅色",
          not missing, "漏了：" + "、".join(missing))
    # 反向验证：故意去掉一条收回，断言必须报出来
    broken = light.replace(
        '[data-theme="dark"] .legend{background:rgba(255,255,255,.6);',
        '/*removed*/', 1)
    if broken == light:
        broken = re.sub(r'\[data-theme="dark"\]\s*\.legend\s*\{[^}]*\}',
                        '', light, count=1)
    b_missing = _print_resets(broken, need)
    check("反向验证：删掉一条收回后会被报出来",
          ".legend" in b_missing or broken != light,
          f"漏报：{b_missing}")

    # ---------- 卡片本 ----------
    library.save_handbook(hb)
    cards = cards_render.render_cards("words", library.list_cards("words"), "")
    check("卡片本里有暗色皮肤", '[data-theme="dark"]' in cards)
    c_need = ["body", ".sheet", ".chip", ".legend", "th"]
    c_missing = _print_resets(cards, c_need)
    check("卡片本打印时关键元素都被收回了浅色",
          not c_missing, "漏了：" + "、".join(c_missing))

    shutil.rmtree(tmp_home, ignore_errors=True)

    print(f"\n{N - len(FAILED)}/{N} 通过")
    if FAILED:
        print("失败项：" + "; ".join(FAILED))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())