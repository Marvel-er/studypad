"""
把 docs/智能英语学习应用-开发文档.md 渲染成单文件 HTML 阅读版（左侧固定 TOC）。

用 markdown-it-py 而不是 python-markdown：
python-markdown 的 fenced_code 是文档级预处理器，要求围栏在**行首**，
而本文档大量使用「引用块 + 表格/代码」的排版（`> | ... |`），会渲染失败。

TOC 从 token 流生成而不是正则扫 HTML —— 这样能判断 `level`，
把引用块内的 `### 实现变更` 排除在目录之外（否则目录会被这种小节污染）。
"""
from __future__ import annotations

import html as html_mod
import re
from pathlib import Path

from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SRC = DOCS / "智能英语学习应用-开发文档.md"
OUT = DOCS / "index.html"

CSS = """
:root{
  --ink:#1f2328; --ink2:#57606a; --ink3:#8b949e;
  --bg:#ffffff; --panel:#f6f8fa; --border:#d8dee4; --accent:#0b62d6;
  --code-bg:#f6f8fa; --quote-bg:#f2f7fd;
}
*{box-sizing:border-box}
html{scroll-padding-top:20px}
body{margin:0;background:var(--bg);color:var(--ink);
  font:15px/1.78 -apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  -webkit-font-smoothing:antialiased}
.wrap{display:flex;align-items:flex-start;max-width:1500px;margin:0 auto}
nav{position:sticky;top:0;height:100vh;overflow-y:auto;flex:0 0 318px;
  border-right:1px solid var(--border);background:var(--panel);padding:20px 0 40px}
nav .brand{padding:0 20px 14px;font-weight:700;font-size:14px;line-height:1.5;
  border-bottom:1px solid var(--border);margin-bottom:10px}
nav .brand s{display:block;text-decoration:none;color:var(--ink3);font-weight:400;font-size:12px;margin-top:4px}
nav a{display:block;padding:5px 20px;color:var(--ink2);text-decoration:none;font-size:13px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;border-left:3px solid transparent}
nav a:hover{background:#eaeef2;color:var(--ink)}
nav a.h3{padding-left:38px;font-size:12.5px;color:var(--ink3)}
nav a.on{color:var(--accent);background:#e7f0fc;border-left-color:var(--accent);font-weight:600}
main{flex:1 1 auto;min-width:0;padding:44px 60px 120px;max-width:960px}
h1,h2,h3,h4{line-height:1.35;font-weight:700}
h1{font-size:29px;margin:0 0 26px;padding-bottom:14px;border-bottom:2px solid var(--border)}
h2{font-size:22px;margin:52px 0 16px;padding-bottom:9px;border-bottom:1px solid var(--border);scroll-margin-top:20px}
h3{font-size:17px;margin:32px 0 11px;color:#24292f;scroll-margin-top:20px}
h4{font-size:15px;margin:22px 0 9px;color:var(--ink2)}
p{margin:11px 0}
a{color:var(--accent)}
ul,ol{padding-left:26px;margin:11px 0}
li{margin:5px 0}
code{background:#eff1f3;padding:1.5px 5px;border-radius:4px;font-size:13px;
  font-family:"Cascadia Code",Consolas,Monaco,monospace}
pre{background:var(--code-bg);border:1px solid var(--border);border-radius:9px;
  padding:14px 16px;overflow-x:auto;margin:14px 0}
pre code{background:none;padding:0;font-size:12.8px;line-height:1.62}
.highlight{border-radius:9px;border:1px solid var(--border);margin:14px 0;overflow:hidden}
.highlight pre{border:none;margin:0;border-radius:0}
blockquote{margin:15px 0;padding:12px 18px;background:var(--quote-bg);
  border-left:4px solid var(--accent);border-radius:0 8px 8px 0;color:#2b3a4a}
blockquote p{margin:7px 0}
blockquote blockquote{background:#e9f1fa;margin:10px 0}
blockquote pre,blockquote .highlight pre{background:#eef1f4}
blockquote table{margin:12px 0}
table{border-collapse:separate;border-spacing:0;width:100%;margin:16px 0;font-size:13.5px;
  border:1px solid var(--border);border-radius:9px;overflow:hidden}
th,td{padding:9px 13px;text-align:left;border-bottom:1px solid var(--border);vertical-align:top}
th{background:#f0f3f6;font-weight:600;white-space:nowrap}
tr:last-child td{border-bottom:none}
tbody tr:hover td{background:#fafbfc}
hr{border:none;border-top:1px solid var(--border);margin:34px 0}
img{max-width:100%}
@media(max-width:1080px){
  nav{display:none}
  main{padding:26px 20px 90px}
}
"""

JS = """
(function(){
  var links = Array.prototype.slice.call(document.querySelectorAll('nav a'));
  var target = links.map(function(a){ return document.getElementById(a.dataset.id); });
  var ticking = false;
  function sync(){
    ticking = false;
    var y = window.scrollY + 96, best = 0;
    for (var i = 0; i < target.length; i++) {
      if (target[i] && target[i].offsetTop <= y) best = i;
    }
    links.forEach(function(a, i){ a.classList.toggle('on', i === best); });
  }
  window.addEventListener('scroll', function(){
    if (!ticking) { ticking = true; requestAnimationFrame(sync); }
  }, { passive: true });
  sync();
})();
"""


def pyg_highlight(code: str, lang: str, attrs) -> str:
    """容错高亮：未知语言不能抛异常，否则整个渲染崩掉。"""
    try:
        lexer = get_lexer_by_name(lang or "text", stripall=False)
    except ClassNotFound:
        lexer = get_lexer_by_name("text")
    return highlight(code, lexer, HtmlFormatter(cssclass="highlight", nowrap=False))


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = html_mod.unescape(text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text).strip("-")
    return text.lower() or "sec"


def build() -> None:
    text = SRC.read_text(encoding="utf-8")
    # linkify 必须显式关掉：gfm-like 预设默认开启，但依赖 linkify-it-py，
    # 没装会在渲染阶段抛 ModuleNotFoundError（而 PowerShell 的管道会吞掉这个错误，
    # 表现为「退出码 0 但产物没更新」，极易误判）。本渲染不需要自动链接。
    md = MarkdownIt("gfm-like", {
        "highlight": pyg_highlight, "html": True, "linkify": False,
    })

    used: set[str] = set()
    toc: list[tuple[str, str, str]] = []

    def unique(base: str) -> str:
        sid, n = base, 2
        while sid in used:
            sid = f"{base}-{n}"
            n += 1
        used.add(sid)
        return sid

    def heading_open(tokens, idx, options, env):  # noqa: ANN001
        t = tokens[idx]
        # level == 0 表示不在引用块 / 列表内 —— 只有这类标题进目录
        if t.level == 0 and t.tag in ("h1", "h2", "h3"):
            inline = tokens[idx + 1]
            sid = unique(slugify(inline.content))
            if t.tag in ("h2", "h3"):
                toc.append((t.tag, sid, inline.content))
            return f'<{t.tag} id="{sid}">'
        return md.renderer.renderToken(tokens, idx, options, env)

    md.renderer.rules["heading_open"] = heading_open

    body = md.render(text)

    nav = "\n".join(
        '<a class="{}" data-id="{}" href="#{}" title="{}">{}</a>'.format(
            "h3" if tag == "h3" else "", sid, sid,
            html_mod.escape(re.sub(r"<[^>]+>", "", name)),
            html_mod.escape(re.sub(r"<[^>]+>", "", name)))
        for tag, sid, name in toc
    )

    pyg_css = HtmlFormatter(style="friendly").get_style_defs(".highlight")

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>智能英语学习应用 · 开发文档</title>
<style>{CSS}
{pyg_css}
</style>
</head>
<body>
<div class="wrap">
<nav>
  <div class="brand">智能英语学习应用<s>开发文档 v1.0</s></div>
  {nav}
</nav>
<main>
{body}
</main>
</div>
<script>{JS}</script>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8")

    # ---- 自检
    fences = len(re.findall(r"^```", body, flags=re.M))
    tables = len(re.findall(r"<table>", body))
    quotes = len(re.findall(r"<blockquote>", body))
    heads = len(re.findall(r"<h[23][ >]", body))
    print(f"[CHECK] 残留未渲染的 ``` 行数: {fences}   (应为 0)")
    print(f"[CHECK] 表格数: {tables}")
    print(f"[CHECK] 引用块数: {quotes}")
    print(f"[CHECK] 正文 h2/h3 数: {heads}")
    print(f"[CHECK] 生成锚点: {len(toc)}")
    print(f"[CHECK] 输出: {OUT}  {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    build()
