"""
探针：确认 check_inline_js 的「class / id 交叉校验」真的会拦错，而不是恒真。

为什么值得单独写：这个项目已经被「假绿断言」咬过好几次 ——
`"tr-zh" in html` 恒真（类名写在内嵌 CSS 里）、假模型不管几条都返回一条、
`cb-empty not in text` 恒真（CSS 里有定义）、列数正则只数数字。
断言本身不成立时，测试全过也说明不了任何事。

做法：把**被校验的那个文件**复制一份到临时目录、只改一处，
用同一份检测代码跑一遍，必须报错；原文必须通过。

⚠ **2026-10-15 拆页后重写过**：老版本靠 `CI.HTML = 临时文件` 覆盖单页路径，
而 `check_inline_js` 改成按 `page_names` 列表逐页读取之后，这个覆盖**完全失效** ——
探针改的是临时文件，检测代码读的还是真页面，于是「用例 2/3」看起来是漏报，
其实**改动根本没被应用**。教训：探针必须改在**检测代码真正会读的那个位置**。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_inline_js as CI  # noqa: E402

STATIC = ROOT / "backend" / "static"

log: list[str] = []


def run(src: Path, html: str, tag: str) -> int:
    """
    把 `src` 替换成 `html`，跑一次检测。

    通过**改 `CI.page_names` 指向临时目录 + 临时文件名** 来生效，
    而不是改一个早已不存在的单页常量（那正是老探针失效的原因）。
    """
    tmp_dir = Path(__file__).resolve().parent.parent / "out" / "_cssprobe"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_file = tmp_dir / src.name
    tmp_file.write_text(html, encoding="utf-8")
    # ⚠ 公共层也要复制过去。检测代码现在把「本页 <style> + common.css」一起当
    # 已定义类名，而 `check_common` 还会去看 `STATIC/common.js` 是否存在。
    # 只复制 HTML 的话，临时目录下没有公共层 →
    # 检查会**误报**几十个「.card/.hint/… 没有 CSS 定义」，
    # 退出码恒为 1，于是「原文应通过」与「应被拦下」全都判不出来 ——
    # 探针看起来全错，其实是被环境噪声淹了。
    for extra in ("common.css", "common.js"):
        s = STATIC / extra
        if s.exists():
            (tmp_dir / extra).write_text(s.read_text(encoding="utf-8"),
                                         encoding="utf-8")

    old_names = list(CI.PAGE_NAMES)
    old_static = CI.STATIC
    old_out, old_log = CI.OUT, CI.LOG
    # 检测代码是 `STATIC / PAGE_NAMES[i]` 这样拼路径的，
    # 所以要**同时**换掉 STATIC（指向临时目录）与 PAGE_NAMES（只留这一个文件）。
    # 少改一个，它读的还是真页面 —— 探针会误报「漏报」，而改动其实没生效。
    CI.STATIC = tmp_dir
    CI.PAGE_NAMES = [src.name]
    CI.OUT = tmp_dir / f"_inline_{tag}.js"
    CI.LOG = tmp_dir / f"_check_{tag}.txt"
    try:
        code = CI.main()
        text = CI.LOG.read_text(encoding="utf-8")
    finally:
        CI.PAGE_NAMES = old_names
        CI.STATIC = old_static
        CI.OUT, CI.LOG = old_out, old_log
    log.append(f"--- {tag}: exit={code}")
    log.append(text)
    return code


def main() -> int:
    ok = 0
    bad = 0

    # 两个页面都要验：它们的类名/id 各不相同，只验一个会漏
    for page in ("index.html", "library.html"):
        src = STATIC / page
        clean = src.read_text(encoding="utf-8")
        log.append(f"\n=========== {page} ===========")

        c1 = run(src, clean, f"{src.stem}_clean")
        log.append(("[PASS] " if c1 == 0 else "[FAIL] ") + f"{page} 原文应通过")
        ok += c1 == 0
        bad += c1 != 0

        # 1) 用了但没定义的类名（少个字母）—— 最典型的手滑。
        #    ⚠ 必须选**字面量出现**的类名：三态的 s-known 在 JS 里是
        #    `'s-' + s` 拼出来的，`re` 匹配不到那种形式 ——
        #    拿它当用例会直接触发下面的 assert（探针失效），
        #    而那正是「用例选错」而不是「检查漏报」。
        if page == "index.html":
            typo_old, typo_new = "'prog waiting'", "'prog waitng'"
        else:
            # ⚠ 必须挑一个**真正写在 HTML 属性里**的类（如 `class="kb-count"`）。
            # 校验扫的是去掉 <script> 后的 `class="..."`，所以 JS 字符串里拼出来的
            # 类名（kb-ex-flag、三态的 s-known）**不在覆盖范围内**——
            # 拿它们当用例会得到一个假的失败，看起来像「检查漏报」。
            typo_old, typo_new = 'class="kb-count"', 'class="kb-cout"'
        typo = clean.replace(typo_old, typo_new, 1)
        assert typo != clean, f"探针失效：{page} 里没找到 {typo_old}，替换没生效"
        c2 = run(src, typo, f"{src.stem}_typo")
        log.append(("[PASS] " if c2 != 0 else "[FAIL] ")
                   + f"{page} 类名少个字母应被拦下")
        ok += c2 != 0
        bad += c2 == 0

        # 2) HTML 写了类名，但 CSS 里的规则被删掉 —— 静默失效的另一种形态。
        #    要删**全部**提到该类的规则：只删一条的话类名仍被别的规则定义着，
        #    检查报「没问题」是**对的** —— 这里第一次跑就踩过这个坑。
        #    ⚠ 同上，类名必须**真的出现在 class="..." 属性里**。
        #    s-known 只由 JS 的 `'s-' + s` 拼出来、从不进 class 属性，
        #    删它的 CSS 规则本来就检不出来 —— 拿它当用例会得到一个假的失败。
        sel = r"\.prog\.waiting" if page == "index.html" else r"\.kb-doc\b"
        dropped, n_drop = re.subn(sel + r"[^}]*\}", "", clean)
        assert n_drop >= 1, f"探针失效：{page} 里没找到 {sel} 规则，删除没生效"
        c3 = run(src, dropped, f"{src.stem}_dropped")
        log.append(f"（{page} 删掉了 {n_drop} 条 {sel} 规则）")
        log.append(("[PASS] " if c3 != 0 else "[FAIL] ")
                   + f"{page} CSS 规则被删掉后应被拦下")
        ok += c3 != 0
        bad += c3 == 0

        # 3) id 写错的老检查也要仍然有效
        old_id, new_id = ("$('progBar')", "$('progBarr')") if page == "index.html" \
            else ("$('kbBody')", "$('kbBodz')")
        idtypo = clean.replace(old_id, new_id, 1)
        assert idtypo != clean, f"探针失效：{page} 里没找到 {old_id}，替换没生效"
        c4 = run(src, idtypo, f"{src.stem}_idtypo")
        log.append(("[PASS] " if c4 != 0 else "[FAIL] ")
                   + f"{page} id 写错应被拦下")
        ok += c4 != 0
        bad += c4 == 0

    # 4) 公共层接线：把 common.js 的引用挪到页面脚本之后，必须被拦下。
    #    这是拆页后**新增**的一类静默失效 —— 整块脚本 ReferenceError，
    #    而其它面板看着一切正常。
    src = STATIC / "library.html"
    clean = src.read_text(encoding="utf-8")
    swapped = clean.replace(
        '<script src="/static/common.js"></script>\n<script>', '<script>')
    swapped = swapped.replace(
        "</script>\n</body>",
        '</script>\n<script src="/static/common.js"></script>\n</body>')
    assert swapped != clean, "探针失效：没能把 common.js 挪到页面脚本之后"
    c5 = run(src, swapped, "lib_order")
    log.append(("[PASS] " if c5 != 0 else "[FAIL] ")
               + "common.js 引用顺序错误应被拦下")
    ok += c5 != 0
    bad += c5 == 0

    log.append("")
    log.append(f"探针结果：{ok} 项符合预期，{bad} 项不符合预期")

    (ROOT / "out" / "_cssprobe.txt").write_text(
        "\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())