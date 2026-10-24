"""
卡片本渲染：把知识库里的生词本 / 句型本 / 语法本渲染成**可打印的 HTML**。

为什么不直接让用户去打印前端页面：前端页面是工具界面（按钮、筛选器、状态标记），
打印出来全是控件。三本卡片本要做的是**背诵清单** —— 一页一页的表格，
看得清、勾得动、打印出来能直接夹进活页��。

所以这里另起一套渲染，**视觉沿用手账的纸面与手绘观感**（同一套 CSS 变量名，
配色与 `render.CSS` 对齐），但布局换成表格式清单，且：
  · **不引入任何图片素材**，与手账一致；
  · 保留打印规则（`@page` A4、表头每页重复、行不跨页断开）；
  · 掌握度用「○ 未掌握 / △ 模糊 / ● 掌握」三个空心符号画在每行末尾，
    打印出来可以手写打勾 —— 屏幕上的标记是电子的，纸面上得能画。

⚠ 判空一律用 `render._visible()`，不要用 `str.strip()`：零宽字符全都能通过
`strip()`，会让「整格只有零宽字符」的行占着位置却一个字都看不见。
"""
from __future__ import annotations

from .render import _esc, _visible

# 掌握度 → 可打印的标记符号 + 中文
STATUS_DOT = {"new": "○", "fuzzy": "△", "known": "●"}
STATUS_TEXT = {"new": "未掌握", "fuzzy": "模糊", "known": "掌握"}

TITLE = {"words": "生词本", "patterns": "句型本", "grammar": "语法本"}

CSS = r"""
:root{
  --sp-paper:#fdfaf3;
  --sp-paper-line:rgba(120,150,190,.16);
  --sp-ink:#2b2b2b;
  --sp-ink-soft:#6b6b6b;
  --sp-line:#d9d4c6;
  /* ⚠ 这里**刻意没有**英文手写体（Segoe Script 那类）。
     手账纸面（render.py）用它是有意的观感，但背诵清单是天天要读的工具页：
     连笔字体的 l/1、r/v、a/d 几乎分不开（用户反馈「根本看不清」）。
     中文标题仍用楷体（中文手写体辨识度尚可，且与纸面观感一致）。 */
  --sp-font-hand-zh:'KaiTi','楷体','STKaiti','Kaiti SC',serif;
  --sp-font-body:Georgia,'Times New Roman','Songti SC','SimSun',serif;
}
*{box-sizing:border-box}
body{
  margin:0;background:#e9e5da;color:var(--sp-ink);
  font-family:var(--sp-font-body);font-size:15.5px;line-height:1.85;
  -webkit-font-smoothing:antialiased;
}
.sheet{
  max-width:920px;margin:28px auto;background:var(--sp-paper);
  border-radius:6px;box-shadow:0 2px 6px rgba(0,0,0,.10),0 18px 48px rgba(0,0,0,.10);
  padding:48px 52px 60px;position:relative;overflow:hidden;
}
.sheet::before{
  content:'';position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(to bottom,rgba(120,150,190,0) 0,rgba(120,150,190,0) 31px,rgba(120,150,190,.14) 31px,rgba(120,150,190,.14) 32px);
  opacity:.85;
}
/* 手账有红色装订线（.sheet::after），卡片本**刻意不要** ——
   这里的主体是表格，那条线会从「单词」列中间穿过去，
   叠在手写体单词上看起来像划掉了它。表格不需要装订线。 */
.sheet>*{position:relative;z-index:1}

.cb-head{border-bottom:2px solid rgba(0,0,0,.10);padding-bottom:16px;margin-bottom:22px}
.cb-title{font-family:var(--sp-font-hand-zh);font-size:26px;font-weight:700;margin:0 0 8px}
.cb-sub{font-size:13px;color:var(--sp-ink-soft);display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.chip{display:inline-block;padding:2px 10px;border-radius:99px;font-size:12px;border:1px solid rgba(0,0,0,.12);background:#fff}
.chip.lv{background:#FEF3C7;border-color:#FCD34D;font-weight:700}
.chip.k{background:#EFF6FF;border-color:#BFDBFE}

.legend{display:flex;flex-wrap:wrap;gap:16px;margin:0 0 22px;padding:10px 14px;
  background:rgba(255,255,255,.6);border:1px dashed rgba(0,0,0,.14);border-radius:10px;
  font-size:12.5px;font-family:var(--sp-font-hand-zh)}
.legend span{color:var(--sp-ink-soft)}
.dot{width:9px;height:9px;border-radius:99px;display:inline-block;margin-right:5px;vertical-align:0}

table{width:100%;border-collapse:collapse;font-size:14.5px;table-layout:fixed}
th{
  text-align:left;font-family:var(--sp-font-hand-zh);font-size:13.5px;font-weight:700;
  color:var(--sp-ink);background:rgba(255,255,255,.72);
  border-bottom:1.5px solid var(--sp-line);padding:7px 9px;white-space:nowrap;
}
td{border-bottom:1px dashed var(--sp-line);padding:7px 9px;vertical-align:top;
  overflow-wrap:anywhere}
tr{break-inside:avoid}
/* `white-space:normal` 是必须的：单词列固定宽度后，
   `productivity`（12 字）会把音标列顶出去、两列文字叠在一起
   （截图里就是这样）。让它换行比让它压着邻居好看。 */
td.en{font-size:16px;font-weight:600;
  white-space:normal;overflow-wrap:anywhere;line-height:1.5;letter-spacing:.01em}
td.ph{color:#555;font-size:13px;white-space:normal;overflow-wrap:anywhere}
td.pos{color:#666;font-size:13px;white-space:normal}
td.ex{color:var(--sp-ink-soft);font-size:13.5px;line-height:1.7}
.ex-tag{margin-top:3px;font-size:11px;color:#9a6b00;background:#fff7e0;
  border:1px solid #fde68a;border-radius:5px;padding:1px 6px;display:inline-block}
td.src{color:var(--sp-ink-soft);font-size:11.5px;line-height:1.6}
td.mark{text-align:center;font-size:17px;white-space:nowrap}
td.mark .st{font-size:11px;color:var(--sp-ink-soft);display:block;line-height:1.2}
tr.done td.en{opacity:.5;text-decoration:line-through;text-decoration-color:rgba(0,0,0,.25)}

.grp-td{font-family:var(--sp-font-hand-zh);font-weight:700;font-size:14px;
  white-space:normal;overflow-wrap:anywhere;line-height:1.6}
.usage{margin:4px 0 0;padding-left:17px;color:var(--sp-ink-soft);font-size:13px;line-height:1.65}
.usage li{margin:1px 0}
.imitation{margin-top:4px;color:#7a5b12;font-size:13px}
.imitation b{color:var(--sp-ink)}

.cb-empty{padding:40px 0;text-align:center;color:var(--sp-ink-soft);font-size:15px}

/* ---------- 暗色（屏幕预览用） ----------
   与手账同一个道理：屏幕上可以深色，打印必须是白底纸面。
   `[data-theme="dark"]` 由前端预览时注入到 <html> 上；
   打印时下面的 @media print 逐条收回。 */
[data-theme="dark"] body{background:#0e1013;color:#d9d5cc}
[data-theme="dark"] .sheet{background:#1b1d22;box-shadow:0 2px 6px rgba(0,0,0,.5),0 18px 48px rgba(0,0,0,.45)}
[data-theme="dark"] .sheet::before{
  background:repeating-linear-gradient(to bottom,rgba(140,165,200,0) 0,rgba(140,165,200,0) 31px,rgba(140,165,200,.10) 31px,rgba(140,165,200,.10) 32px)}
[data-theme="dark"] .chip{background:#26282e;border-color:rgba(255,255,255,.10);color:#d9d5cc}
[data-theme="dark"] .chip.lv{background:#3a3220;border-color:#5c4a24;color:#e8cf9a}
[data-theme="dark"] .legend{background:rgba(255,255,255,.045);border-color:rgba(255,255,255,.12)}
[data-theme="dark"] .legend span{color:#a8a49c}
[data-theme="dark"] th{background:rgba(255,255,255,.05)}
[data-theme="dark"] td{border-bottom-color:rgba(255,255,255,.07)}
[data-theme="dark"] td.en,[data-theme="dark"] td.grp-td{color:#e4e1da}
[data-theme="dark"] td.ex,[data-theme="dark"] td.src,.usage,[data-theme="dark"] .cb-empty{color:#a8a49c}
[data-theme="dark"] .ex-tag{background:#33291c;border-color:#5c4a24;color:#e8cf9a}

@page{size:A4;margin:15mm 12mm}
@media print{
  /* ⚠ 打印必须永远是浅色纸面：上面那条暗色覆盖在打印时同样会命中，
     少收一条就会印出深底白字 —— 既费墨，PDF 也不像样。 */
  body{background:#fff;color:#2b2b2b}
  [data-theme="dark"] body,[data-theme="dark"] body *{color:#2b2b2b}
  [data-theme="dark"] .sheet{background:#fdfaf3;box-shadow:none;margin:0;max-width:none;
    border-radius:0;padding:0 0 8mm}
  [data-theme="dark"] .chip{background:#fff;border-color:rgba(0,0,0,.12);color:#2b2b2b}
  [data-theme="dark"] .chip.lv{background:#FEF3C7;border-color:#FCD34D}
  [data-theme="dark"] .legend{background:rgba(255,255,255,.6);border-color:rgba(0,0,0,.14)}
  [data-theme="dark"] .legend span{color:#6b6b6b}
  [data-theme="dark"] th{background:rgba(255,255,255,.72)}
  [data-theme="dark"] .ex-tag{background:#fff7e0;border-color:#fde68a;color:#9a6b00}
  body{background:#fff;font-size:11.5pt}
  .sheet{box-shadow:none;margin:0;max-width:none;border-radius:0;padding:0 0 8mm}
  .sheet::before{opacity:.5}
  .sheet::after{display:none}
  /* 表头每页重复：打印 5 页生词本时，第 5 页也得能看出这一列是什么 */
  thead{display:table-header-group}
  tfoot{display:table-footer-group}
  tr{break-inside:avoid;page-break-inside:avoid}
  th,td{padding:4px 6px}
  thead th{-webkit-print-color-adjust:exact;print-color-adjust:exact;background:#f2efe6}
  .cb-head,.legend{break-inside:avoid}
  td.ex{font-size:10.5pt}
  a{color:inherit;text-decoration:none}
}
"""

# 三本卡片本的表头（顺序即列顺序）与列宽。
# 列宽**必须显式给定**并配 `table-layout:fixed`：中文释义天然比音标长，
# 让浏览器自己分配会把「释义」挤成「走廊，回 / 廊，道路」这样的碎行，
# 而音标那一列却空着一大片 —— 一眼看上去像数据不全，其实只是排版。
COLS = {
    "words": ["单词", "音标", "词性", "释义", "例句（来自你读过的原文）", "出处", "掌握"],
    "patterns": ["句型", "用法", "仿写示例", "例句（来自你读过的原文）", "出处", "掌握"],
    "grammar": ["语法点", "讲解", "例句（来自你读过的原文）", "出处", "掌握"],
}
WIDTHS = {
    "words": [19, 12, 7, 17, 27, 10, 8],
    "patterns": [16, 24, 19, 24, 10, 7],
    "grammar": [18, 33, 30, 12, 7],
}
HEAD = COLS


def _mark_cell(it: dict) -> str:
    st = it.get("status") or "new"
    return (f'<td class="mark">{STATUS_DOT.get(st, "○")}'
            f'<span class="st">{STATUS_TEXT.get(st, "未掌握")}</span></td>')


def _src_cell(it: dict) -> str:
    srcs = it.get("sources") or []
    if not srcs:
        return '<td class="src">—</td>'
    lines = []
    for s in srcs[:3]:
        lines.append(f"{_esc(s.get('title') or '未命名')}"
                     f'<br><span style="opacity:.75">{_esc(s.get("level") or "")}</span>')
    more = len(srcs) - 3
    tail = f'<br>…另有 {more} 篇' if more > 0 else ""
    return f'<td class="src">{"".join(lines)}{tail}</td>'


def _ex_cell(it: dict) -> str:
    """
    例句格。词典例句要**标出来** —— 用户默认以为每条例句都来自自己读过的原文，
    混进几句无关的词典例句会让他复习时找不着语境，还以为是自己记错了。
    """
    ex = it.get("example") or ""
    if not _visible(ex):
        return '<td class="ex">—</td>'
    if it.get("ex_from") == "text":
        return f'<td class="ex">{_esc(ex)}</td>'
    return (f'<td class="ex">{_esc(ex)}'
            f'<div class="ex-tag">词典例句（原文未出现该词形）</div></td>')


def _row(it: dict) -> str:
    st = it.get("status") or "new"
    cls = ' class="done"' if st == "known" else ""
    return f"<tr{cls}>{_cells(it)}{_src_cell(it)}{_mark_cell(it)}</tr>"


def _cells(it: dict) -> str:
    ex_html = _ex_cell(it)
    if "phonetic" in it:                                   # 生词
        return (f'<td class="en">{_esc(it.get("surface") or it.get("lemma") or "")}</td>'
                f'<td class="ph">{_esc(it.get("phonetic") or "")}</td>'
                f'<td class="pos">{_esc(it.get("pos") or "")}</td>'
                f'<td>{_esc(it.get("gloss") or "")}</td>'
                f'{ex_html}')
    if "usage" in it:                                      # 句型
        usage = it.get("usage") or []
        ul = f'<ul class="usage">{"".join(f"<li>{_esc(u)}</li>" for u in usage)}</ul>' \
            if usage else '<span class="usage">—</span>'
        imit = it.get("imitation") or ""
        im = f'<div class="imitation"><b>仿写：</b>{_esc(imit)}</div>' \
            if _visible(imit) else ""
        return (f'<td class="grp-td">{_esc(it.get("name") or "")}</td>'
                f'<td>{ul}</td><td>{im}</td>{ex_html}')
    # 语法
    return (f'<td class="grp-td">{_esc(it.get("label") or it.get("name") or "")}</td>'
            f'<td>{_esc(it.get("explain") or "")}</td>{ex_html}')


def render_cards(kind: str, data: dict, path_hint: str = "") -> str:
    """
    渲染一整本卡片。`data` 就是 `library.list_cards()` 的返回。

    只渲染**用户当前筛选得到的那一批** —— 导出「未掌握的 60 个词」
    就该只有 60 行，而不是把整本都印出来让用户自己划掉。

    `path_hint` 容忍 `Path`：调用方多半直接传 `library.root()`，
    而 `_esc` 走 `html.escape` 只吃 str，传 Path 会在渲染时抛
    `TypeError: Path.replace() takes 2 positional arguments` ——
    一个把用户数据搞崩的、看起来毫不相关的类型错误。
    """
    title = TITLE.get(kind, "卡片本")
    items = data.get("items") or []
    tally = data.get("tally") or {}

    if items:
        cols = HEAD.get(kind, ["名称", "例句", "出处", "掌握"])
        widths = WIDTHS.get(kind) or [40, 30, 20, 10][:len(cols)]
        cg = "".join(f'<col style="width:{w}%">' for w in widths)
        rows = "".join(_row(it) for it in items)
        body = (f'<table><colgroup>{cg}</colgroup>'
                f'<thead><tr>{"".join(f"<th>{c}</th>" for c in cols)}</tr></thead>'
                f"<tbody>{rows}</tbody></table>")
    else:
        body = '<div class="cb-empty">这一本还没有卡片。<br>' \
               '导入文章生成手账后，生词/句型/语法会自动收进这里。</div>'

    chips = [
        f'<span class="chip lv">{title} {len(items)} 条</span>',
        f'<span class="chip">未掌握 {tally.get("new", 0)}</span>',
        f'<span class="chip">模糊 {tally.get("fuzzy", 0)}</span>',
        f'<span class="chip">掌握 {tally.get("known", 0)}</span>',
    ]
    legend = (
        '<div class="legend">'
        '<span>掌握度：<b>○</b> 未掌握　<b>△</b> 模糊　<b>●</b> 掌握</span>'
        '<span>例句全部来自你自己读过的原文，方便回想语境</span>'
        '</div>'
    )
    hint = ""
    if path_hint:
        # str() 兜住 Path；_esc 再做 HTML 转义（Windows 路径里有 \ 与空格）
        hint = (f'<div class="cb-sub" style="margin-top:10px">'
                f'知识库：{_esc(str(path_hint))}</div>')

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>StudyPad · {title}</title><style>{CSS}</style></head>
<body><div class="sheet">
<div class="cb-head">
  <h1 class="cb-title">{title}</h1>
  <div class="cb-sub">{"".join(chips)}</div>
</div>
{hint}
{legend}
{body}
</div></body></html>"""


def render_csv(kind: str, data: dict) -> str:
    """
    导出 CSV（UTF-8 BOM，Excel 双击能正确认出中文）。

    不是用户勾选的格式，但**备份/迁移数据需要一个纯文本出口** ——
    只给 HTML 的话，想把生词搬到别的软件、或怕项目目录出问题时留个底，
    都只能去翻 json。加它成本极低。
    """
    import csv
    import io
    buf = io.StringIO()
    if kind == "words":
        head = ["word", "phonetic", "pos", "meaning", "status", "sources", "example"]
        rows = [[i.get("lemma"), i.get("phonetic"), i.get("pos"), i.get("gloss"),
                 (i.get("status") or "new"),
                 " | ".join(s.get("title") or "" for s in (i.get("sources") or [])),
                 i.get("example")] for i in (data.get("items") or [])]
    elif kind == "patterns":
        head = ["pattern", "usage", "imitation", "sources", "example"]
        rows = [[i.get("name"), " / ".join(i.get("usage") or []), i.get("imitation"),
                 " | ".join(s.get("title") or "" for s in (i.get("sources") or [])),
                 i.get("example")] for i in (data.get("items") or [])]
    else:
        head = ["grammar", "label", "explain", "sources", "example"]
        rows = [[i.get("name"), i.get("label"), i.get("explain"),
                 " | ".join(s.get("title") or "" for s in (i.get("sources") or [])),
                 i.get("example")] for i in (data.get("items") or [])]
    w = csv.writer(buf)
    w.writerow(head)
    w.writerows(rows)
    return "﻿" + buf.getvalue()


__all__ = ["render_cards", "render_csv", "TITLE", "STATUS_DOT", "STATUS_TEXT"]