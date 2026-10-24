"""
抽取各页面里的内联 <script> 并交给 node --check 做语法校验，
同时交叉校验 JS 里引用的元素 id、以及用到的 CSS 类名。

2026-10-15 拆页后覆盖**多个文件**：`index.html`（制作页）与
`library.html`（知识库页），外加共用的 `common.js`。
只校验主页的话，新页面的语法错误与 id 错配就完全没人把关了 ——
而这类错误的表现恰恰是「只有新加的功能没反应」，最难发现。

为什么要单独做这一步：前端是单文件内联 JS，改完之后只有「打开浏览器点一遍」才能发现问题，
而下面三类错误都会让功能**静默失效**（其它面板看着正常，只有新加的功能没反应）：

1. 语法错误 —— 整块脚本都跑不起来（`node --check` 秒挡）。
2. `$('useTrans')` 里的 id 写错或漏了对应元素 —— 取到 null，要么当场抛错，
   要么被 `if (el)` 兜住之后**永远不生效**，而且不报任何错。
   第 2 类更阴，因为它看起来「加上了」。
3. `className = 'prog waiting'` 里的类名在 <style> 里没有对应规则 ——
   不会有任何报错，只是「进度条卡住时变成琥珀色条纹」这类反馈**悄悄不生效**。
   id 写错反而容易察觉（元素取到 null、行为全无）；类名写错时元素还在、
   样式也对了一半，看着就像「能跑」。
   只认 `className = '字面量'` 这种写法：`className = epTabClass(...)` 这类动态拼接
   没法静态判断，宁可漏报也不要误报（误报会让人开始无视这个检查）。

用法：
    python scripts/check_inline_js.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "backend" / "static"

# ⚠ 公共层（common.js）里定义的 $ / api / esc / fmtDateTime
# 也是被各页面引用的 —— 只校验「本页 <style>」的话，
# 「公共层里删了一个函数」这类错误查不出来（它不属于任何一页的 style）。
EXTERNAL_CSS = ["common.css"]

# ⚠ 提成模块级而不是写在 main() 里：`probe_css_check.py` 要用「改坏的副本」
# 覆盖它来验证断言真的会失败。写成局部变量的话探针改不动 ——
# 探针会以为「检查漏报」，其实是**改动根本没被应用**（2026-10-15 踩过）。
# **新增页面必须登记到这里**，否则它的语法与 id 错配就无人把关。
PAGE_NAMES = ["index.html", "library.html"]

OUT = ROOT / "out" / "_inline.js"
LOG = ROOT / "out" / "_nodecheck.txt"

NODE = Path(r"C:\Users\刘永键\.workbuddy\binaries\node\versions\22.22.2-5\node.exe")


def check_kb_cols(js: str) -> list[str]:
    """
    知识库表格的「表头列数」必须与「列宽数组」逐本相等。

    为什么单列一条：列数对不上时**页面上完全不会报错**，
    表头会多出或少掉空列，而 `<col>` 与 `<td>` 数量不匹配时浏览器
    会把多出来的列压成**竖排单字**（截图实测：整列一个字母一行）。
    id/class 交叉校验都发现不了这种问题 —— 它只查「引用的东西存不存在」，
    不查「数量对不对得上」。
    """
    bad: list[str] = []

    def arr(name: str) -> list[list]:
        """
        解析 `var KB_XXX = { key: [ ... ], ... };` 里的每一行。

        ⚠ KB_HEAD 的值是**字符串数组**（表头文字），KB_COLS 的是**数字数组**（百分比），
        两者元素长得完全不一样。早先只按数字解析，KB_HEAD 解析出 0 项，
        而 `if not heads: return bad` 直接返回空 —— 这条断言就成了一条
        **恒真的假绿断言**（反向验证：故意把列宽删一个，它依然报「一致」）。
        所以改成「数 [] 里有多少个元素」，两种数组都能数对。
        另一个教训：**解析不出来必须当成失败**，不能让「断言失效」和
        「断言通过」长得一模一样。
        """
        m = re.search(r"var\s+" + name + r"\s*=\s*\{(.*?)\n\};", js, re.S)
        if not m:
            return []
        out = []
        for line in m.group(1).splitlines():
            line = line.strip()
            if not line or not line.endswith(","):
                continue
            inner = re.search(r":\s*\[(.*)\],?\s*$", line)
            if not inner:
                continue
            out.append(inner.group(1).count(",") + 1 if inner.group(1).strip() else 0)
        return out

    heads = arr("KB_HEAD")
    cols = arr("KB_COLS")
    if not heads:
        # 解析不出来必须**当成失败**，不能默默返回空 ——
        # 否则「断言失效」和「断言通过」在这里长得一模一样。
        return ["没解析到 KB_HEAD —— 断言本身失效了（不是代码没问题）"]
    if not cols:
        return ["没解析到 KB_COLS —— 断言本身失效了（不是代码没问题）"]
    if len(heads) != len(cols):
        return [f"KB_HEAD 有 {len(heads)} 本但 KB_COLS 有 {len(cols)} 本"]
    for (h, c) in zip(heads, cols):
        if h != c:
            bad.append(f"某一本：表头 {h} 列 vs 列宽 {c} 列")
    # 列宽合计也要验：超了/不足 100 浏览器会自己缩放，列宽就白设了
    for kind, total in widths_of(js).items():
        if total >= 0 and abs(total - 100) > 2:
            bad.append(f"{kind} 本列宽合计 {total}%，应约等于 100%")
    return bad


def widths_of(js: str) -> dict[str, int]:
    """每本列宽的合计，验它约等于 100%（超了浏览器会自己缩放）。"""
    m = re.search(r"var\s+KB_COLS\s*=\s*\{(.*?)\n\};", js, re.S)
    if not m:
        return {}
    out: dict[str, int] = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"\s*(\w+)\s*:\s*\[(.*)\]", line)
        if not mm:
            continue
        out[mm.group(1)] = sum(int(x) for x in re.findall(r"\d+", mm.group(2)))
    return out


def check_kb_readability(html: str, js: str = "") -> list[str]:
    """
    知识库列表的两条**可读性/布局**红线。

    参数顺序刻意是 `(html, js)`：CSS 在 html 的 `<style>` 里，
    列宽在 JS 里。叫错顺序会静默取到空串 → 全部检查失效（踩过）。

    ① 单词列不得用手写体（Segoe Script 那类连笔字体）——
       用户反馈「根本看不清」：l/1、r/v、a/d 分不开。
       纸面手账（render.py）用它是有意的观感，但知识库是天天要读几十个词的
       工具界面，辨识度优先于风格。
    ② 掌握度列宽不得低于 10%。`table-layout:fixed` 下内容**不会**撑宽单元格，
       超了直接溢出（用户截图：掌握列被挤出卡片右边界）。
       三个按钮 + gap + 单元格 padding 至少要 ~104px，容器约 1086px。
    """
    bad: list[str] = []
    style = re.search(r"<style>(.*?)</style>", html, re.S)
    css = style.group(1) if style else ""

    # ⚠ 两个前置步骤都不能省：
    #   ① 先剥 CSS 注释 —— 否则 `/* ... .kb-w{...} ... */` 这类注释里的
    #      花括号会参与配对，选择器被拼成一堆垃圾，`sel == ".kb-w"` 永远不成立
    #      （反向验证直接抓出来的：明明有 .kb-w 规则，却报「没找到」）。
    #   ② 再按选择器**精确**匹配，不能 `re.search(r"\.kb-w\s*\{")` ——
    #      那会先命中 `table.kb tr.done .kb-w{text-decoration:line-through}`，
    #      取到一条没有 font-family 的规则，字体检查就恒真了。
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules = [(sel.strip(), body) for sel, body in
             re.findall(r"([^{}]+)\{([^}]*)\}", css)]
    hit = [b for sel, b in rules if sel == ".kb-w"]
    if not hit:
        bad.append("没找到 .kb-w 规则 —— 单词列样式可能被改名了")
    else:
        fams = re.findall(r"font-family\s*:\s*([^;}]+)", hit[0])
        if not fams:
            bad.append(".kb-w 没有声明 font-family，会继承页面的手写体栈")
        for f in fams:
            low = f.lower()
            if any(h in low for h in ("script", "comic sans", "brush", "hand")):
                bad.append(f".kb-w 用了手写体 {f.strip()}（连笔字看不清）")
            elif not any(g in low for g in ("georgia", "times", "serif", "sans",
                                            "arial", "helvetica", "verdana")):
                bad.append(f".kb-w 的字体无法判断是否清晰：{f.strip()}")

    # ② 掌握列宽下限
    m = re.search(r"var\s+KB_COLS\s*=\s*\{(.*?)\n\};", js, re.S)
    if not m:
        bad.append("没解析到 KB_COLS —— 无法校验掌握列宽")
    else:
        for line in m.group(1).splitlines():
            mm = re.match(r"\s*(\w+)\s*:\s*\[(.*)\]", line)
            if not mm:
                continue
            nums = [int(x) for x in re.findall(r"\d+", mm.group(2))]
            if not nums:
                continue
            mark = nums[-1]          # 掌握列固定是最后一列
            if mark < 10:
                bad.append(f"{mm.group(1)} 本掌握列只给了 {mark}%，"
                           f"三态按钮会被挤出单元格（需 ≥10%）")
    return bad


def _css_classes(path: Path) -> set[str]:
    """一个 CSS 文件里定义的选择器里出现的类名。"""
    if not path.exists():
        return set()
    text = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)
    return set(re.findall(r"\.([A-Za-z][\w-]*)", text))


def check_common(js: str, pages: dict[str, str]) -> list[str]:
    """
    公共层与页面的接线检查。

    拆分后最容易出、也最难发现的一类错误：
      · 页面引了 common.js，但**顺序在页面 script 之后** →
        `$` / `api` / `esc` 还没定义就跑页面脚本，整块脚本直接抛 ReferenceError；
      · 页面根本没引 common.js（忘了）；
      · 页面用了 `common.css` 里的类，但没引那个 css（样式静默失效）；
      · 页面引的公共文件不存在 → 404，整个公共层丢失。
    这些都不会让任何自检变红，只有用户打开页面才发现。
    """
    bad: list[str] = []
    common_js = (STATIC / "common.js")
    if not common_js.exists():
        bad.append("common.js 不存在（两页共用的助手全丢了）")
    for name, html in pages.items():
        srcs = re.findall(r'<script[^>]*\bsrc="([^"]+)"', html)
        idx_common = next((i for i, u in enumerate(srcs) if "common.js" in u), -1)
        if idx_common < 0:
            bad.append(f"{name} 没有引用 common.js（$ / api / esc 会未定义）")
        else:
            # 判定用「外链与页面脚本在 <body> 里的相对位置」，**不**用
            # 「<script> 首次出现位置」——
            # 防闪烁脚本（主题用）本来就故意放在 common.js **之前**，
            # 用后者判会把正确写法误报成错误（2026-10-15 踩过）。
            body = html[html.find("<body"):]
            c_pos = body.find("common.js")
            # <body> 之后第一个不带 src 的 <script> 才是页面自己的脚本
            m = re.search(r"<script>(?![\s\S]{0,40}?src=)", body)
            i_pos = m.start() if m else -1
            if i_pos >= 0 and c_pos > i_pos:
                bad.append(f"{name} 的 common.js 引用在页面脚本之后"
                           f"（页面脚本会先跑，$ / api 还没定义）")
        links = re.findall(r'<link[^>]*href="([^"]+)"', html)
        for l in links:
            if l.startswith("/static/"):
                if not (ROOT / "backend" / l.lstrip("/")).exists():
                    bad.append(f"{name} 引用了不存在的静态文件 {l}")
        if not any("common.css" in l for l in links):
            bad.append(f"{name} 没有引用 common.css"
                       f"（按钮 / 卡片 / 配色会全部走样）")
    del js
    return bad


def check_theme(pages: dict[str, str]) -> list[str]:
    """
    主题相关的红线（暗色模式，2026-10-15）。

    三条都会导致「暗色模式下页面上一块亮白」：

    ① **页面 `<style>` 里不许出现浅色硬编码**（`#fff` / `#f6f7f9` 之类）。
       它们覆盖不到 `--card` 这类令牌，暗色下就是一块白斑。
       例外：`@media print` 块 —— 打印必须白底，那是有意为之。
    ② `common.css` 必须同时定义 `:root` 与 `[data-theme="dark"]` 两套令牌，
       且**每个令牌名都要在暗色块里出现**。漏一个就是「那个元素暗色不变」。
    ③ 两页都要有防闪烁脚本（在 `common.css` 之前）——
       否则刷新时先白一下再变黑，夜间刺眼。
    """
    bad: list[str] = []

    # ---- ① 页面内不许有浅色硬编码 ----
    light = re.compile(r"#(fff\b|f6f7f9|fbfcfd|fafbfc|f2f4f7|f8fafc|f7f8fa"
                       r"|fbfcfd|f0f2f5|eef2f7|fffbeb|fef2f2|f3f4f6|"
                       r"|fff7ed|fff7e0|fef4e3|e3f5ec|f1f0f6)", re.I)
    for name, html in pages.items():
        st = re.search(r"<style>(.*?)</style>", html, re.S)
        if not st:
            continue
        css = st.group(1)
        # ⚠ 打印块里的浅色是**有意**的，必须放过。
        # 只把 `@media print{` 改名是不够的：块内仍然是普通花括号，
        # 后面的扫描照样会进去（反向验证当场抓出这个漏网）。
        # 正解：把整块内容（花括号配对）挖掉。
        out, i = [], 0
        while True:
            j = css.find("@media print", i)
            if j < 0:
                out.append(css[i:])
                break
            out.append(css[i:j])
            k = css.find("{", j)
            if k < 0:
                break
            depth = 0
            for t in range(k, len(css)):
                if css[t] == "{":
                    depth += 1
                elif css[t] == "}":
                    depth -= 1
                    if depth == 0:
                        i = t + 1
                        break
            else:
                i = len(css)
        css_noprint = "".join(out)
        for ln, line in enumerate(css_noprint.splitlines(), 1):
            for m in light.finditer(line):
                bad.append(f"{name}: <style> 有浅色硬编码 {m.group(0)}"
                           f"（暗色下会是一块白斑）→ 改用 var(--*)")

    # ---- ② 令牌完整性 ----
    css_path = STATIC / "common.css"
    css = css_path.read_text(encoding="utf-8")
    root_blk = re.search(r":root\s*\{(.*?)\n\}", css, re.S)
    dark_blk = re.search(r'\[data-theme="dark"\]\s*\{(.*?)\n\}', css, re.S)
    if not root_blk:
        bad.append("common.css 没有 :root 令牌块")
        return bad
    if not dark_blk:
        bad.append('common.css 没有 [data-theme="dark"] 覆盖块（暗色模式不会生效）')
        return bad
    root_vars = set(re.findall(r"(--[\w-]+)\s*:", root_blk.group(1)))
    dark_vars = set(re.findall(r"(--[\w-]+)\s*:", dark_blk.group(1)))
    missing = sorted(root_vars - dark_vars)
    if missing:
        bad.append("暗色块漏了这些令牌（那些元素在暗色下不变）："
                   + "、".join(missing[:8])
                   + ("…" if len(missing) > 8 else ""))

    # ---- ③ 防闪烁脚本 ----
    for name, html in pages.items():
        has = "studypad.theme" in html.split("</head>")[0]
        if not has:
            bad.append(f"{name} 没有防闪烁脚本（刷新时会先白一下再变黑）")
            continue
        css_pos = html.find('href="/static/common.css"')
        script_pos = html.find("studypad.theme")
        if script_pos > css_pos:
            bad.append(f"{name} 的防闪烁脚本在样式表**之后**（起不到作用）")

    # ---- ④ 切换开关与逻辑 ----
    cjs = (STATIC / "common.js").read_text(encoding="utf-8")
    for key in ("studypad.theme", "prefers-color-scheme", "data-theme",
                "btnTheme", "studypad:theme"):
        if key not in cjs:
            bad.append(f"common.js 里没有 {key}（主题切换逻辑缺了一块）")
    for name, html in pages.items():
        if 'id="btnTheme"' not in html:
            bad.append(f"{name} 没有主题切换按钮 #btnTheme")

    return bad


def main() -> int:
    # 要校验的页面见模块级 PAGE_NAMES（探针会覆盖它来验「断言真的会失败」）。
    pages: dict[str, str] = {}
    for n in PAGE_NAMES:
        f = STATIC / n
        if not f.exists():
            LOG.write_text(f"★ 缺少页面 {n}\n", encoding="utf-8")
            return 1
        pages[n] = f.read_text(encoding="utf-8")

    lines = [f"node={NODE}",
             "页面：" + "、".join(
                 f"{n}({len(h)}字符)" for n, h in pages.items()),
             f"公共层：common.css + common.js"
             f"（{', '.join(EXTERNAL_CSS)}）"]

    all_js: list[str] = []
    missing: list[str] = []
    cls_missing: list[str] = []
    col_bad: list[str] = []

    # 公共层自己也过一遍语法
    cjs = STATIC / "common.js"
    if cjs.exists():
        ctext = cjs.read_text(encoding="utf-8")
        all_js.append("// ===== common.js =====\n" + ctext)
        # 公共层定义的函数：被页面调用的那些必须真的存在
        defined_fns = set(re.findall(r"function\s+([A-Za-z_$][\w$]*)\s*\(",
                                     ctext)) | {
            m for m in re.findall(r"var\s+([A-Za-z_$][\w$]*)\s*=", ctext)}
        pages_js = "\n".join(
            "\n;\n".join(re.findall(
                r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", h, re.S))
            for h in pages.values())
        for fn in ("esc", "api", "fmtDateTime"):
            if re.search(r"(?<![\w.$])" + fn + r"\s*\(", pages_js) and fn not in defined_fns:
                missing.append(f"common.js 没有定义 {fn}（页面在用它）")

    for name, html in pages.items():
        blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",
                            html, re.S)
        if not blocks:
            missing.append(f"{name} 没有内联 script")
            continue
        js = "\n;\n".join(b.strip() for b in blocks)
        all_js.append(f"// ===== {name} =====\n{js}")

        # ---- id 交叉校验（只认字面量；模板拼出来的动态 id 没法静态判断）----
        used = set(re.findall(r"\$\(\s*'([A-Za-z_][\w-]*)'\s*\)", js))
        defined = set(re.findall(r'\bid="([^"]+)"', html))
        for i in sorted(used - defined):
            missing.append(f"{name}: $('{i}') 在 HTML 里找不到")

        # ---- class 交叉校验 ----
        # 扫 class="..." 前**必须先摘掉内联 JS 与 <style>**：
        # JS 字符串里到处是 `'<span class="' + esc(...)` 这种拼接，
        # 直接扫会把 `+`、`:`、`esc(x)` 当成类名，报一堆假失败。
        markup = re.sub(r"<script\b.*?</script>", "", html, flags=re.S)
        markup = re.sub(r"<style\b.*?</style>", "", markup, flags=re.S)
        css = _css_classes(STATIC / "common.css")
        st = re.search(r"<style>(.*?)</style>", html, re.S)
        if st:
            css |= set(re.findall(r"\.([A-Za-z][\w-]*)", st.group(1)))
        cls_used: set[str] = set()
        for m in re.findall(r'class="([^"]+)"', markup):
            cls_used |= set(m.split())
        # 两条来源缺一不可：① `className = 'prog done'` 直接赋值；
        # ② `setProgressClass('prog waiting')` 这种「以 Class 结尾的函数 + 字面量」。
        # 只做 ① 曾漏掉过一个写错的类名，因为那处走的是 ②。
        # 命名约定就来自这里：函数名以 Class 结尾 ⇒ 字符串参数直接给 className。
        for m in re.findall(r"className\s*=\s*'([A-Za-z][\w\- ]*)'", js):
            cls_used |= set(m.split())
        for m in re.findall(r"\b\w*Class\w*\s*\(\s*'([A-Za-z][\w\- ]*)'", js):
            cls_used |= set(m.split())
        for c in sorted(cls_used - css):
            cls_missing.append(f"{name}: .{c} 被用到但没有任何 CSS 定义")

        # ---- 知识库表格：列数一致 + 可读性红线 ----
        if "library" in name:
            col_bad += [f"{name}: {m}" for m in check_kb_cols(js)]
            col_bad += [f"{name}: {m}" for m in check_kb_readability(html, js)]

    js_all = "\n;\n".join(all_js)
    OUT.write_text(js_all, encoding="utf-8")
    lines.append(f"抽出 JS 合计 {len(js_all)} 字符 → {OUT.name}")

    # ---- 语法 ----
    syntax_ok = True
    if NODE.exists():
        proc = subprocess.run([str(NODE), "--check", str(OUT)],
                              capture_output=True, text=True)
        syntax_ok = proc.returncode == 0
        lines.append(f"node --check 退出码 = {proc.returncode}")
        for stream in (proc.stdout, proc.stderr):
            if stream.strip():
                lines.append(stream.strip())
    else:
        lines.append(f"跳过语法校验：node 不存在（{NODE}）")

    lines.append("语法：" + ("通过" if syntax_ok else "有错，必须修复"))
    lines.append("id 交叉校验：" + ("全部命中" if not missing else "★ 有对不上的"))
    for m in missing:
        lines.append(f"    {m}")
    lines.append("class 交叉校验：" + ("全部命中" if not cls_missing else "★ 有对不上的"))
    for m in cls_missing:
        lines.append(f"    {m}")
    if col_bad:
        lines.append("★ 知识库表格：")
        for m in col_bad:
            lines.append(f"    {m}")
    else:
        lines.append("知识库表格：列数一致、字体与掌握列宽合规")

    wiring = check_common(js_all, pages)
    lines.append("公共层接线：" + ("正常" if not wiring else "★ 有问题"))
    for m in wiring:
        lines.append(f"    {m}")

    theme_bad = check_theme(pages)
    lines.append("主题（暗色模式）：" + ("正常" if not theme_bad else "★ 有问题"))
    for m in theme_bad:
        lines.append(f"    {m}")

    ok = (syntax_ok and not missing and not cls_missing and not col_bad
          and not wiring and not theme_bad)
    lines.append("结果：" + ("全部通过" if ok else "有问题，需修复"))
    LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
