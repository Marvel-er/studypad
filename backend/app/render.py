"""
手账渲染器：把「区块 + 标注」渲染成一份可观感的自包含 HTML。

设计参考：
  · ai-dokkai 的「等级双色高亮」机制（粉=本级考纲词 / 蓝=超纲词）→ 扩展为三色
  · handwriting-web 的「手写体 + 纸面」观感 → 用 CSS 渐变与系统手写字体实现，零素材依赖

产物可直接：浏览器预览 / 打印成 PDF（矢量、可搜索）/ 另存为 HTML。
"""
from __future__ import annotations

import html
import json
import re

from .analyzer import split_spans

# ---------------------------------------------------------------- 样式

CSS = r"""
:root{
  --sp-paper:#fdfaf3;
  --sp-paper-line:rgba(120,150,190,.16);
  --sp-ink:#2b2b2b;
  --sp-ink-soft:#6b6b6b;
  --sp-hl:#FFE066;          /* 本级考纲词：荧光黄 */
  --sp-circle:#E02424;      /* 超纲常见词：红圈 */
  --sp-rare:#0284C7;        /* 超纲生僻词：天蓝虚线 */
  --sp-pattern:#DC2626;     /* 加分句型：红色波浪线 */
  --sp-note:#FFF6C9;        /* 便利贴 */
  --sp-font-hand-en:'Segoe Script','Bradley Hand','Comic Sans MS','Yu Gothic',cursive;
  --sp-font-hand-zh:'KaiTi','楷体','STKaiti','Kaiti SC',serif;
  --sp-font-body:Georgia,'Times New Roman','Songti SC','SimSun',serif;
}
*{box-sizing:border-box}
body{
  margin:0;background:#e9e5da;color:var(--sp-ink);
  font-family:var(--sp-font-body);font-size:16.5px;line-height:2.0;
  -webkit-font-smoothing:antialiased;
}
.sheet{
  max-width:920px;margin:28px auto;background:var(--sp-paper);
  border-radius:6px;box-shadow:0 2px 6px rgba(0,0,0,.10),0 18px 48px rgba(0,0,0,.10);
  padding:52px 56px 64px;position:relative;overflow:hidden;
}
.sheet::before{
  content:'';position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(to bottom,rgba(120,150,190,0) 0,rgba(120,150,190,0) 31px,rgba(120,150,190,.16) 31px,rgba(120,150,190,.16) 32px);
  opacity:.85;
}
.sheet::after{
  content:'';position:absolute;top:0;bottom:0;left:64px;width:1px;background:rgba(220,80,80,.22);
}
.sheet>*{position:relative;z-index:1}

/* ---------- 页眉 ---------- */
.hb-head{border-bottom:2px solid rgba(0,0,0,.10);padding-bottom:18px;margin-bottom:26px}
.hb-title{font-family:var(--sp-font-hand-zh);font-size:27px;font-weight:700;letter-spacing:.5px;margin:0 0 8px}
.hb-sub{font-size:13px;color:var(--sp-ink-soft);display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.chip{display:inline-block;padding:2px 10px;border-radius:99px;font-size:12px;border:1px solid rgba(0,0,0,.12);background:#fff}
.chip.lv{background:#FEF3C7;border-color:#FCD34D;font-weight:700}
.chip.k{background:#EFF6FF;border-color:#BFDBFE}
.chip.warn{background:#FEF2F2;border-color:#FCA5A5;color:#B91C1C;font-weight:700}

/* ---------- 图例 ---------- */
.legend{display:flex;flex-wrap:wrap;gap:14px;margin:0 0 26px;padding:12px 14px;background:rgba(255,255,255,.6);border:1px dashed rgba(0,0,0,.14);border-radius:10px;font-size:12.5px;font-family:var(--sp-font-hand-zh)}
.legend span{display:flex;align-items:center;gap:6px;color:var(--sp-ink-soft)}
.sw{width:16px;height:12px;border-radius:3px;display:inline-block}

/* ---------- 正文块 ---------- */
.block{margin:0 0 22px;padding-left:14px;border-left:3px solid transparent}
.block.title{margin-top:6px}
.block.title .text{font-family:var(--sp-font-hand-zh);font-size:23px;font-weight:700;line-height:1.75}
.block.heading .text{font-family:var(--sp-font-hand-zh);font-size:19px;font-weight:700;line-height:1.8}
.block.list{padding-left:30px;position:relative}
.block.list::before{content:'·';position:absolute;left:12px;font-size:22px;color:var(--sp-ink-soft)}
.block.quote{background:rgba(255,255,255,.55);border-left:3px solid #d8d2c4;border-radius:0 8px 8px 0;padding:8px 14px}
.block.code .text{font-family:Consolas,'Cascadia Code',monospace;font-size:12px;color:#555;white-space:pre-wrap}
.text{font-size:16.5px;line-height:2.05;text-align:justify}
.block.long{border-left-color:#f0c9c9;background:rgba(255,240,240,.45)}

/* ---------- 标注 ---------- */
.w-target{background:linear-gradient(180deg,rgba(255,224,102,0) 52%,#FFE066 52%,#FFE066 92%,rgba(255,224,102,0) 92%);border-radius:2px}
.w-circle{
  display:inline-block;padding:0 7px;border:1.6px solid var(--sp-circle);border-radius:50% 46% 52% 48%/58% 50% 60% 46%;
  transform:rotate(-.6deg);color:var(--sp-circle);font-weight:600;
}
.w-rare{border-bottom:1.5px dashed var(--sp-rare);color:#0b4a6f}
.g-gram{border-bottom:2px solid var(--sp-gc,#2563EB);padding-bottom:1px}
.g-pat{
  text-decoration:underline wavy var(--sp-pattern);
  text-decoration-thickness:1.6px;text-underline-offset:5px;
}
[data-tip]{cursor:help;position:relative}

/* ---------- 边栏批注 ---------- */
.side{margin:10px 0 4px 14px;display:flex;flex-direction:column;gap:8px}
.note{
  font-family:var(--sp-font-hand-zh);font-size:13.5px;line-height:1.72;color:#3d3d3d;
  background:var(--sp-note);border-radius:3px;padding:8px 12px 8px 13px;
  box-shadow:0 1px 3px rgba(0,0,0,.10);position:relative;max-width:88%;
}
.note::before{
  content:'';position:absolute;left:-7px;top:12px;width:14px;height:1.5px;background:rgba(0,0,0,.18);
}
.note.gram{background:#EDF5FF}
.note.pat{background:#FFF1F0}
.note.long{background:#F5F3FF}
.note b{font-family:var(--sp-font-hand-zh);font-size:13.5px}
.note .tag{display:inline-block;font-size:11px;background:rgba(0,0,0,.07);border-radius:3px;padding:0 5px;margin-right:5px}
.note .imit{display:block;margin-top:5px;color:#5a5a5a;font-style:italic;font-family:var(--sp-font-body);font-size:12.5px}
.note .use{color:#8a5a00}

/* ---------- 译文 ---------- */
.tr-zh{
  font-family:var(--sp-font-hand-zh);font-size:14.5px;line-height:1.95;color:#2c4a45;
  background:rgba(157,199,189,.16);border-left:2.5px solid #9dc7bd;
  border-radius:0 6px 6px 0;padding:6px 13px;margin:9px 0 0;
}
.tr-zh.partial{background:rgba(255,243,205,.55);border-left-color:#e8c979;color:#7a5a15}
.tr-pair{margin:0 0 15px}
.tr-pair:last-child{margin-bottom:0}
.tr-pair .text{line-height:1.95}
.block.tr-sent{padding-left:14px;border-left:3px solid rgba(157,199,189,.55)}
.tr-flag{font-size:11.5px;color:#7a8a86;font-family:var(--sp-font-hand-zh);margin-left:8px}
/* 未译出提示：**一条**灰色说明，替代过去「每句一个空绿框」的做法。
   空绿框堆满一页，在打印时又因 .block{break-inside:avoid} 被整体推到下一页，
   看起来就是「整页留白、还分页了」—— 用户截图反馈的正是这个。 */
.tr-miss{
  font-family:var(--sp-font-hand-zh);font-size:12px;color:#8a8a8a;
  border-left:2px dashed rgba(0,0,0,.18);padding:2px 0 2px 10px;margin:7px 0 0;
  break-before:avoid;
}

/* 顶部提示条：译文降级 / 大模型失败时说清「为什么」。
   以前 trans_note / llm_note 只挂在数据上、从未渲染，用户只看到满页空绿框，
   拿不到任何解释 —— 比留白本身更让人困惑。 */
.hb-note{
  font-family:var(--sp-font-hand-zh);font-size:13px;line-height:1.8;color:#7a4a12;
  background:#FFF7E6;border:1px solid #F5D9A8;border-left:4px solid #E8A33D;
  border-radius:8px;padding:10px 14px;margin:0 0 22px;
}
.hb-note b{color:#B45309}

/* ---------- 页尾附表 ---------- */
.section{margin-top:44px;padding-top:22px;border-top:2px dashed rgba(0,0,0,.15)}
.section h2{font-family:var(--sp-font-hand-zh);font-size:20px;margin:0 0 14px}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{text-align:left;padding:7px 9px;border-bottom:1px solid rgba(0,0,0,.08);vertical-align:top}
th{font-family:var(--sp-font-hand-zh);font-weight:700;background:rgba(0,0,0,.035)}
td.ph{font-family:Consolas,monospace;color:#666;font-size:12.5px;white-space:nowrap}
td.en{font-weight:600}
.dot{display:inline-block;width:7px;height:7px;border-radius:50%;margin-right:5px;vertical-align:middle}
.foot{margin-top:34px;text-align:center;color:#9a9a9a;font-size:12px;font-family:var(--sp-font-hand-zh)}

/* ---------- tooltip ---------- */
#tip{
  position:fixed;z-index:99;max-width:330px;background:rgba(30,30,30,.96);color:#fff;
  font-family:var(--sp-font-hand-zh);font-size:13px;line-height:1.7;padding:10px 13px;border-radius:9px;
  pointer-events:none;opacity:0;transition:opacity .12s;box-shadow:0 8px 26px rgba(0,0,0,.3)
}
#tip.on{opacity:1}
#tip .t-h{font-size:15px;font-weight:700;margin-bottom:3px}
#tip .t-p{color:#bbb;font-size:12px;font-family:Consolas,monospace}
#tip .t-g{color:#ffd479;margin-top:5px}

/* ---------- 暗色（屏幕预览用，2026-10-15） ----------
   手账是「纸面产物」：打印、导出 PDF、下载 HTML 都必须是白底。
   但用户在深色界面里看预览时，一整块刺眼的白纸很难受。
   所以做**只在屏幕上生效**的暗色皮肤，打印时由下面的 @media print
   强制收回浅色 —— 那里必须把每一条都写死，不能依赖变量。

   触发方式：`<html data-theme="dark">`（前端预览时注入）。
   不用 prefers-color-scheme —— 那是给「系统级」用的，
   而这里是「跟应用自己的主题开关」，两者可能不一致。
*/
[data-theme="dark"] body{background:#0e1013;color:#d9d5cc}
[data-theme="dark"] .sheet{background:#1b1d22;box-shadow:0 2px 6px rgba(0,0,0,.5),0 18px 48px rgba(0,0,0,.45)}
[data-theme="dark"] .sheet::before{
  background:repeating-linear-gradient(to bottom,rgba(140,165,200,0) 0,rgba(140,165,200,0) 31px,rgba(140,165,200,.10) 31px,rgba(140,165,200,.10) 32px)}
[data-theme="dark"] .sheet::after{background:rgba(220,80,80,.34)}
[data-theme="dark"] .chip{background:#26282e;border-color:rgba(255,255,255,.10);color:#d9d5cc}
[data-theme="dark"] .chip.lv{background:#3a3220;border-color:#5c4a24;color:#e8cf9a}
[data-theme="dark"] .chip.k{background:#1e2836;border-color:#31435c;color:#b7cbe6}
[data-theme="dark"] .chip.warn{background:#33201f;border-color:#6b3232;color:#f0a9a0}
[data-theme="dark"] .legend{background:rgba(255,255,255,.045);border-color:rgba(255,255,255,.12)}
[data-theme="dark"] .legend span{color:#a8a49c}
[data-theme="dark"] .block.quote{background:rgba(255,255,255,.035);border-left-color:#3c3f46}
[data-theme="dark"] .block.long{background:rgba(200,90,90,.07);border-left-color:#5e3a3a}
[data-theme="dark"] .note{background:#33291c;border-color:#5c4a24;color:#e8cf9a}
[data-theme="dark"] .note .n-idx{color:#a88b52}
[data-theme="dark"] .tr-zh{background:rgba(90,130,110,.16);border-left-color:#4e7a68;color:#cfdcd4}
[data-theme="dark"] .tr-zh.partial{border-left-color:#8a6a2c;color:#e0cfa8}
[data-theme="dark"] .tr-miss{color:#8a8378}
[data-theme="dark"] .hb-note{background:#33291c;border-color:#5c4a24;color:#e8cf9a}
[data-theme="dark"] table th{background:rgba(255,255,255,.05)}
[data-theme="dark"] table td{border-bottom-color:rgba(255,255,255,.07)}
[data-theme="dark"] .tip{background:#26282e;border-color:rgba(255,255,255,.12);color:#d9d5cc}

/* ---------- 打印 ---------- */
@page{size:A4;margin:15mm 14mm}
@media print{
  /* ⚠ 打印必须永远是浅色纸面。上面那条 `[data-theme="dark"]` 的覆盖在
     打印时同样会命中（媒体查询不影响选择器），所以这里必须逐条收回。
     少收一条就会出现「某一类批注印出来是深底白字」——
     既费墨，PDF 也不像样。 */
  body{background:#fff;color:#2b2b2b}
  [data-theme="dark"] body,[data-theme="dark"] body *{color:#2b2b2b}
  [data-theme="dark"] .sheet{background:#fdfaf3;box-shadow:none;margin:0;max-width:none;
    border-radius:0;padding:0 0 10mm}
  [data-theme="dark"] .chip{background:#fff;border-color:rgba(0,0,0,.12);color:#2b2b2b}
  [data-theme="dark"] .chip.lv{background:#FEF3C7;border-color:#FCD34D}
  [data-theme="dark"] .chip.k{background:#EFF6FF;border-color:#BFDBFE}
  [data-theme="dark"] .legend{background:rgba(255,255,255,.6);border-color:rgba(0,0,0,.14)}
  [data-theme="dark"] .legend span{color:#6b6b6b}
  [data-theme="dark"] .note,[data-theme="dark"] .hb-note{background:#FFF6C9;
    border-color:rgba(0,0,0,.08);color:#2b2b2b}
  [data-theme="dark"] .tr-zh{background:rgba(238,242,234,.9);color:#2b2b2b}
  [data-theme="dark"] .block.quote{background:rgba(255,255,255,.55)}
  [data-theme="dark"] .block.long{background:rgba(255,240,240,.45)}
  [data-theme="dark"] table th{background:rgba(255,255,255,.72)}
  .sheet{box-shadow:none;margin:0;max-width:none;border-radius:0;padding:0 0 10mm}
  .sheet::before{opacity:.5}
  /* 分页规则 —— 这里是「留白分页」的正解，改之前务必看清：
     从前是 `.block{break-inside:avoid}` 一刀切，但**逐句对照的块
     （.tr-sent）动辄比一整页还高**。浏览器无法既避免断开又放下它，
     只好先把整块推到下一页 —— 前一页尾部于是空出一大片（实测空白
     909px ≈ 页高 72%，用户截图反馈的「留白分页」就是这个）。
     现在只对「注定装得下」的元素禁止断开：
       · .tr-pair 句对不拆 → 不会出现「原文在这页、译文在下一页」的错位；
       · .note / .tr-zh 便利贴不拆 → 半张便利贴跨页很难看；
       · 标题不拆 → 标题不带正文孤零零留在页尾。
     整块 .block 则允许断（break-inside:auto），让它把每一页填满。 */
  .block{break-inside:auto}
  /* 只有「注定装得下」的小块才禁止断开。列表/引用块也可能很高，
     一律 avoid 会重演同一个留白问题，所以它们也允许断。 */
  .block.title,.block.heading{break-inside:avoid}
  .tr-pair{break-inside:avoid}
  .note{break-inside:avoid}
  .tr-zh{break-inside:avoid}
  .tr-miss{break-inside:avoid}
  .hb-head,.legend,.hb-note{break-inside:avoid}
  .text,.tr-zh{orphans:2;widows:2}
  #tip{display:none}
  .w-target{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  .note{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  .hb-note{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  .no-print{display:none!important}
}
"""

JS = r"""
(function(){
  var tip=document.getElementById('tip');
  function show(e){
    var el=e.target.closest('[data-tip]'); if(!el) return;
    var d; try{ d=JSON.parse(el.getAttribute('data-tip')); }catch(_){ return; }
    var h='';
    if(d.title) h+='<div class="t-h">'+d.title+'</div>';
    if(d.phonetic) h+='<div class="t-p">'+d.phonetic+'</div>';
    if(d.body) h+='<div>'+d.body+'</div>';
    if(d.extra) h+='<div class="t-g">'+d.extra+'</div>';
    tip.innerHTML=h; tip.classList.add('on'); move(e);
  }
  function move(e){
    var w=tip.offsetWidth||320,h=tip.offsetHeight||80;
    var x=Math.min(e.clientX+14, innerWidth-w-12);
    var y=e.clientY-h-14; if(y<8) y=e.clientY+20;
    tip.style.left=x+'px'; tip.style.top=y+'px';
  }
  document.addEventListener('mouseover',show);
  document.addEventListener('mousemove',function(e){ if(tip.classList.contains('on')) move(e); });
  document.addEventListener('mouseout',function(e){
    if(e.target.closest('[data-tip]')) tip.classList.remove('on');
  });
})();
"""

# ---------------------------------------------------------------- 渲染


def _esc(s: str) -> str:
    return html.escape(s or "", quote=True)


# 零宽 / 不可见字符：从 PDF 文字层、OCR、以及大模型返回里来得很勤
#   · U+200B 零宽空格、U+200C/U+200D 零宽连接符、U+2060 word-joiner、U+FEFF BOM 残留
#   · 以及 C0/C1 控制字符（除 \t \n）
# 它们**全都能通过 `str.strip()`**，于是一个「看起来是空的」文本会被当成有内容，
# 渲染成一个占着位置、却一个字都看不见的框 —— 用户看到的就是"一片留白"。
#
# 注意：`_visible` 只用来回答「这块到底有没有东西」，**不做输出转换**，
# 所以这里删得宽一点是安全的（输出仍原样保留控制字符以外的全部内容）。
_ZERO_WIDTH = dict.fromkeys(
    [0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0x00AD, 0x180E]
    + [c for c in range(0x00, 0x20) if c not in (0x09, 0x0A)]
    + [0x7F] + list(range(0x80, 0xA0)),
    None,
)


def _visible(s: str) -> str:
    """去掉零宽 / 控制 / 不可见字符后的文本。判断「这块到底有没有东西」必须用它。"""
    return (s or "").translate(_ZERO_WIDTH).strip()


def _tip(obj: dict) -> str:
    return f' data-tip="{_esc(json.dumps(obj, ensure_ascii=False))}"'


def _render_block_text(block: dict, lo: int = 0, hi: int | None = None) -> str:
    """
    按字符级别切分，正确处理语法 / 单词 / 句型三层嵌套重叠。

    `lo` / `hi` 用来只渲染文本的一段（逐句对照模式按句切片）。
    标记数组仍按整块建立，因此 tip 的偏移始终是绝对位置，切片不会让 tooltip 错位。
    """
    text = block.get("text") or ""
    anns = block.get("annotations") or []
    if not text:
        return ""

    n = len(text)
    lo = max(0, lo)
    hi = n if hi is None else min(hi, n)
    if lo >= hi:
        return ""

    w_kind = [None] * n          # word 层：hl / circle / rare
    g_col = [None] * n           # grammar 层：颜色
    p_on = [False] * n           # pattern 层
    tips: dict[int, dict] = {}

    for a in anns:
        s, e = max(0, a["start"]), min(n, a["end"])
        if s >= e:
            continue
        t = a["type"]
        if t in ("word_highlight", "word_circle", "word_rare"):
            cls = {"word_highlight": "hl", "word_circle": "circle", "word_rare": "rare"}[t]
            for i in range(s, e):
                w_kind[i] = cls
            tips[s] = {
                "title": a["surface"],
                "phonetic": a["payload"].get("phonetic", ""),
                "body": a["payload"].get("gloss", ""),
                "extra": {
                    "overflow": "超纲词 · 六档词表都收了它，最值得优先背",
                    "rare": "超纲生僻词 · 认识即可，不必强记",
                    "beyond": "六档词表之外 · 属于更高阶词汇",
                    "target": "本级考纲词 · 需要巩固",
                }.get(a["payload"].get("kind"), ""),
            }
        elif t == "grammar_underline":
            col = a["payload"].get("color", "#2563EB")
            for i in range(s, e):
                g_col[i] = col
            tips[s] = {
                "title": a["payload"].get("label", "语法结构"),
                "body": a["payload"].get("explain", ""),
            }
        elif t == "pattern_wavy":
            for i in range(s, e):
                p_on[i] = True
            tips[s] = {
                "title": a["payload"].get("name", "加分句型"),
                "body": "可用于：" + "、".join(a["payload"].get("usage", [])),
                "extra": a["payload"].get("imitation", ""),
            }

    # 按「标记状态」把文本切成等状态片段
    out: list[str] = []
    i = lo
    while i < hi:
        key = (w_kind[i], g_col[i], p_on[i])
        j = i
        while j < hi and (w_kind[j], g_col[j], p_on[j]) == key:
            j += 1
        seg = _esc(text[i:j])
        w, g, p = key
        if w == "circle":
            seg = f'<span class="w-circle">{seg}</span>'
        elif w == "hl":
            seg = f'<span class="w-target">{seg}</span>'
        elif w == "rare":
            seg = f'<span class="w-rare">{seg}</span>'
        if g:
            seg = f'<span class="g-gram" style="--sp-gc:{g}">{seg}</span>'
        if p:
            seg = f'<span class="g-pat">{seg}</span>'
        if i in tips:
            seg = f"<span{_tip(tips[i])}>{seg}</span>"
        out.append(seg)
        i = j
    return "".join(out)


def _block_classes(block: dict, extra: str | None = None) -> str:
    cls = ["block", block.get("type", "paragraph")]
    if extra:
        cls.append(extra)
    if any(a["type"] == "long_sentence" for a in block.get("annotations") or []):
        cls.append("long")
    return " ".join(cls)


def _zh_of(tr: dict | None) -> str:
    if not tr:
        return ""
    return tr.get("zh") or "".join(s.get("zh", "") for s in tr.get("sentences", []))


def _render_block_paragraph(block: dict, tr: dict | None) -> str:
    """整段附译：原文保持一个整体，译文挂在段落下方。"""
    inner = _render_block_text(block)
    # 正文整体为空（或只剩零宽字符）时不要产出空框：那会在页面上留下一块
    # 有背景没内容的空白，比不渲染更糟。
    if not _visible(re.sub(r"<[^>]+>", "", inner)):
        return ""
    out = f'<div class="{_block_classes(block)}"><div class="text">{inner}</div>'
    zh = _zh_of(tr)
    if _visible(zh):
        pc = " partial" if (tr or {}).get("partial") else ""
        flag = ('<span class="tr-flag">（本段有句子未译出）</span>'
                if (tr or {}).get("partial") else "")
        out += f'<div class="tr-zh{pc}">{_esc(zh)}{flag}</div>'
    return out + "</div>"


def _render_block_sentence(block: dict, tr: dict | None) -> str:
    """
    逐句对照：每句一行原文 + 一行译文。

    依赖 `split_spans` 给出的精确 span。译文的 key 是句子的起始偏移，
    与原文 span 一一对应 —— 对不上就**不配框**，不猜、不挪。

    ⚠ 这里有个曾把整页变成「留白」的坑（用户截图反馈过）：
    `translate_blocks` 在部分失败时，只会把**成功译出的句子**放进
    `tr["sentences"]`（并置 `partial=True`），而本函数是按**全部 span** 遍历的。
    早先的实现给「这句没译文」也产出一个
    `<div class="tr-zh partial">（本句未译出）</div>` ——
    于是一页里只要有几段部分失败，就会堆出十几到几十个**空的绿色译文框**：
    通篇绿框、框里没字；打印时 `.block{break-inside:avoid}` 又把这一大坨
    整体推到下一页，看起来就是「整页留白、还分页了」。

    现在的规则：
      · 整段**一句都没译出** → 完全退回「原文照排」，连一个绿框都不出；
      · 部分译出 → 只给真的译出来的句子配绿框；没译出的句子**只排原文、不配框**，
        末尾用**一条**灰色提示说明丢了几句（N 个空框 → 1 行说明）。
    """
    text = block.get("text") or ""
    if not tr:
        return _render_block_paragraph(block, None)

    zh_map = {s["start"]: s["zh"] for s in tr.get("sentences", []) if _visible(s.get("zh"))}
    spans = split_spans(text)
    if not spans:
        return _render_block_paragraph(block, None)

    # 整段一句都没译出：退回原文照排。**绝不能**逐句产出空绿框。
    if not any(s in zh_map for s, _e, _t in spans):
        return _render_block_paragraph(block, None)

    parts: list[str] = []
    cursor = 0
    missing = 0
    for s, e, _sent in spans:
        if s > cursor and text[cursor:s].strip():
            # span 之间的非空白残留（罕见）：原样保留，避免丢字
            parts.append(f'<div class="text">{_esc(text[cursor:s])}</div>')
        inner = _render_block_text(block, s, e)
        zh = zh_map.get(s)
        cursor = e
        # 原文与译文都没东西（PDF 文字层里常见「只有零宽字符」的假句子）：整对跳过。
        if not _visible(re.sub(r"<[^>]+>", "", inner)) and not _visible(zh):
            continue
        if _visible(zh):
            parts.append(f'<div class="tr-pair"><div class="text">{inner}</div>'
                         f'<div class="tr-zh">{_esc(zh)}</div></div>')
        else:
            # 没有译文就**不配绿框**，只排原文 —— 空框堆起来就是整页留白
            missing += 1
            parts.append(f'<div class="text">{inner}</div>')
    if cursor < len(text) and text[cursor:].strip():
        parts.append(f'<div class="text">{_esc(text[cursor:])}</div>')

    if not parts:
        return ""
    if missing:
        parts.append(
            f'<div class="tr-miss">本段另有 {missing} 句未取到译文'
            f'（大模型该批未返回）。点「重新生成」可重试。</div>')
    return f'<div class="{_block_classes(block, "tr-sent")}">' + "".join(parts) + "</div>"


def _render_side(block: dict) -> str:
    """右侧批注栏：语法讲解 / 句型用途 / 长难句提示。"""
    notes: list[str] = []
    seen: set[tuple] = set()
    for a in block.get("annotations") or []:
        t = a["type"]
        p = a["payload"]
        if t == "grammar_underline":
            # 同一区块内语法讲解是**按标签查表得到**的通用模板，不随具体句子变。
            # 一段里出现两次「名词性从句」就会原样打印两遍同样的说明 ——
            # 截图上看就是一堆重复的便利贴，既占地方又没有新信息。
            key = ("grammar_underline", p.get("label", ""), p.get("explain", ""))
            if key in seen:
                continue
            seen.add(key)
            notes.append(
                f'<div class="note gram"><span class="tag">语法</span>'
                f'<b>{_esc(p.get("label",""))}</b> — {_esc(p.get("explain",""))}</div>'
            )
        elif t == "pattern_wavy":
            key = ("pattern_wavy", p.get("name", ""))
            if key in seen:
                continue
            seen.add(key)
            uses = "、".join(p.get("usage", []))
            notes.append(
                f'<div class="note pat"><span class="tag">加分句型</span>'
                f'<b>{_esc(p.get("name",""))}</b>'
                f'<div class="use">可用于：{_esc(uses)}</div>'
                f'<span class="imit">仿写：{_esc(p.get("imitation",""))}</span></div>'
            )
        elif t == "long_sentence":
            notes.append(
                f'<div class="note long"><span class="tag">长难句</span>'
                f'本句 {p.get("words",0)} 词，含 {_esc("、".join(p.get("grammar", [])) or "结构复杂")}，'
                f'建议先找主谓宾再回填修饰成分。</div>'
            )
    if not notes:
        return ""
    return '<div class="side">' + "".join(notes) + "</div>"


def _legend(counters: dict) -> str:
    items = [
        ("#FFE066", "本级考纲词", "需巩固，已用荧光笔标出"),
        ("#E02424", "超纲常见词", "红圈，最该优先背"),
        ("#0284C7", "超纲生僻词", "蓝色虚线，认识即可"),
        ("none", "语法结构", "彩色下划线，右侧有讲解"),
        ("#DC2626", "作文加分句型", "红色波浪线"),
    ]
    parts = []
    for color, name, desc in items:
        sw = (f'<i class="sw" style="background:{color}"></i>' if color != "none"
              else '<i class="sw" style="background:#fff;border:1.5px solid #2563EB;border-bottom-width:3px"></i>')
        parts.append(f"<span>{sw}{name} · {desc}</span>")
    return '<div class="legend">' + "".join(parts) + "</div>"


def _vocab_gloss(v: dict) -> str:
    """
    生词表「释义」列：**英汉双解**（中文释义在上，权威英释在下）。

    ⚠ 空释义不能留空（2026-10-15 用户反馈「生词表里有的单词信息没有完全显示」）：
    五层词典（六档词表 → general.json → extra.json → ecdict.json → 全量兜底库）
    都查不到的词，这一列原来渲染成**空白单元格**，一行里四个空格子
    （音标/词性/释义/例句），看着像渲染坏了或者数据丢了。用户第一反应必然是
    「程序有问题」，而真实原因是「这个词太生僻，词典都没收」—— 这两件事必须能区分开。

    所以：两样都没有就如实写一句「词典未收录」，灰色斜体弱化，读起来像注解而不是释义。
    有英释没中文（WordNet 有、ECDICT 没有的那批）也照实显示英释，不留白。
    """
    zh = (v.get("gloss") or "").strip()
    en = (v.get("en") or "").strip()
    if not zh and not en:
        return '<span style="color:#9aa0a6;font-style:italic">词典未收录</span>'
    out = [_esc(zh)] if zh else []
    if en:
        # 英释压暗、小一号、另起一行：它是**权威出处**，中文那行才是给人一眼看懂的。
        # 两行并存就是英汉双解；只有英文的（ECDICT 没中文释义）也不会留白。
        out.append(f'<span style="display:block;color:#9aa0a6;font-size:11px">'
                   f'{_esc(en)}</span>')
    return "".join(out)


def _text_blocks(hb: dict) -> list[dict]:
    """
    正文里「有内容、且应该被翻译」的区块。

    必须与 `translate.SKIP_TYPES` 口径一致 —— 否则覆盖率算出来永远差一截，
    页眉会一直谎报「只翻译了 N/M 段」。这里不 import translate 是为了
    让 render 保持零依赖（它要能在没有 llm 模块的场合单独跑）。
    """
    out = []
    for b in hb.get("blocks") or []:
        if b.get("meta", {}).get("skip"):
            continue
        if (b.get("type") or "") in ("code", "figure", "table"):
            continue
        if not _visible(b.get("text")):
            continue
        out.append(b)
    return out


def _has_zh(tr: dict | None) -> bool:
    """
    这条译文记录里**是否真的有一个字**。

    不能用 `if tr` 判断：极端情况下会留下 `{"zh": "", "sentences": []}`
    这样的空壳记录，它存在但渲染不出任何绿框 —— 按「记录条数」算覆盖率
    就会高报，页眉显示「4/4 段」而页面上一个译文都没有。
    """
    if not tr:
        return False
    if _visible(tr.get("zh")):
        return True
    return any(_visible(s.get("zh")) for s in tr.get("sentences") or [])


def render_handbook(hb: dict, title: str = "英语精读手账") -> str:
    c = hb["counters"]
    trans = hb.get("translations") or {}
    mode = hb.get("trans_mode") or "off"
    if not trans:
        mode = "off"                 # 没有译文就不能声称有

    text_blocks = _text_blocks(hb)
    n_text = len(text_blocks)
    # 覆盖率按「真的渲染出译文的段」算，不是「translations 里有几条记录」：
    # 空壳记录（{"zh":"","sentences":[]}）存在但渲染不出任何绿框，
    # 按记录条数算会高报成「4/4 段」，而页面上一个译文都没有。
    n_have = sum(1 for b in text_blocks if _has_zh(trans.get(b["id"])))

    # 段覆盖率之外**还要**看句覆盖率：一段里丢 2 句、剩下 1 句译出来了，
    # 段覆盖率照样是 100%，用户却在读一段缺了三分之二译文的文章。
    # 只看段的话这种「每段都缺一点」的整页降级永远不会触发告警。
    n_sent = n_sent_zh = 0
    for b in text_blocks:
        spans = split_spans(b.get("text") or "")
        if not spans:
            continue
        zs = {s["start"] for s in ((trans.get(b["id"]) or {}).get("sentences") or [])
              if _visible(s.get("zh"))}
        n_sent += len(spans)
        n_sent_zh += sum(1 for s, _e, _t in spans if s in zs)

    short_sent = bool(mode != "off" and n_sent and n_sent_zh < n_sent)
    short_block = bool(mode != "off" and n_text and n_have < n_text)
    short = short_sent or short_block

    trans_note_raw = (hb.get("trans_note") or "").strip()
    llm_note_raw = (hb.get("llm_note") or "").strip()
    # 一段都没成时 trans_mode 会退回 "off"，short 恒为 False ——
    # 必须另外认出来，否则「整篇翻译失败」反而是唯一不显示任何提示的情形。
    failed_all = any(k in trans_note_raw for k in
                     ("未能生成中文译文", "中文译文生成失败", "需要大模型"))
    llm_bad = ("失败" in llm_note_raw) or ("降级" in llm_note_raw)

    trans_chip = ""
    if mode != "off":
        label = "逐句对照" if mode == "sentence" else "整段附译"
        if mode == "sentence" and n_sent:
            # 逐句模式下**始终**按句报数：这是该模式真实的粒度，
            # 也是用户判断「这页是不是没翻出来」唯一看得懂的指标。
            cov = f"{n_sent_zh}/{n_sent} 句"
        elif n_text:
            cov = f"{n_have}/{n_text} 段"
        else:
            cov = f"{n_have} 段"
        # 覆盖不全时把 chip 也染成告警色：只写在正文里容易被划过去
        cls = "chip warn" if short else "chip k"
        trans_chip = f'<span class="{cls}">中文译文 {cov} · {label}</span>'

    # ---- 译文降级提示 ----
    # `trans_note` / `llm_note` 以前只挂在 hb 上、**从未渲染**：翻译失败时
    # 用户只看到满页空绿框，拿不到任何解释，比留白本身更让人困惑。
    # 顺利时不显示，保持页面干净；出问题时必须说清「为什么」和「怎么办」。
    note_bits: list[str] = []
    if short_sent:
        note_bits.append(
            f"<b>中文译文只覆盖 {n_sent_zh}/{n_sent} 句</b>：未取到译文的句子按原文显示，"
            f"不再留空框。可点「重新生成」重试。")
    elif short_block:
        note_bits.append(
            f"<b>中文译文只覆盖 {n_have}/{n_text} 段</b>：其余段落按原文显示，"
            f"不再留空框。可点「重新生成」重试。")
    if (short or failed_all) and trans_note_raw:
        note_bits.append(_esc(trans_note_raw))
    if llm_bad and llm_note_raw != trans_note_raw:
        note_bits.append(_esc(llm_note_raw))
    note_html = ('<div class="hb-note">' + "<br>".join(note_bits) + "</div>") if note_bits else ""

    head = f"""
<div class="hb-head">
  <h1 class="hb-title">{_esc(title)}</h1>
  <div class="hb-sub">
    <span class="chip lv">目标水平：{_esc(hb['level_name'])}</span>
    <span class="chip k">词汇基准 {_esc(hb['vocab_note'])}</span>
    <span class="chip">全文 {hb['word_count']} 词</span>
    <span class="chip">标注 {c['word_highlight']+c['word_circle']+c['word_rare']} 词</span>
    <span class="chip">语法 {c['grammar']} 处</span>
    <span class="chip">加分句型 {c['patterns']} 个</span>
    {trans_chip}
  </div>
</div>"""

    body: list[str] = []
    for b in hb["blocks"]:
        if b.get("meta", {}).get("skip"):
            continue
        # 用 _visible 而不是 .strip()：PDF 文字层里常有「整块只有零宽字符」的伪区块，
        # str.strip() 删不掉它们，会渲染成一堆有框无字的空白。
        if not _visible(b.get("text")):
            continue
        tr = trans.get(b["id"])
        if mode == "sentence" and tr:
            body.append(_render_block_sentence(b, tr))
        else:
            body.append(_render_block_paragraph(b, tr if mode != "off" else None))
        body.append(_render_side(b))

    vocab = hb.get("vocab") or []
    vocab_html = ""
    if vocab:
        rows = []
        for v in vocab:
            color = {"overflow": "#E02424", "rare": "#0284C7",
                     "beyond": "#0284C7", "target": "#D97706"}.get(v["kind"], "#999")
            label = {"overflow": "超纲常见", "rare": "超纲生僻",
                     "beyond": "六档之外", "target": "本级考纲"}.get(v["kind"], "")
            rows.append(
                f'<tr><td class="en"><span class="dot" style="background:{color}"></span>{_esc(v["surface"])}</td>'
                f'<td class="ph">{_esc(v["phonetic"])}</td>'
                f'<td>{_esc(v["pos"])}</td>'
                f'<td>{_vocab_gloss(v)}</td>'
                f'<td>{label}</td>'
                f'<td style="color:#777;font-size:12.5px">{_esc(v["example"])}</td></tr>'
            )
        vocab_html = (
            '<div class="section"><h2>生词表（{n} 个）</h2><table>'
            "<thead><tr><th>单词</th><th>音标</th><th>词性</th><th>释义</th><th>来源</th><th>例句</th></tr></thead>"
            "<tbody>{r}</tbody></table></div>"
        ).format(n=len(vocab), r="".join(rows))

    pats = hb.get("patterns") or []
    pat_html = ""
    if pats:
        rows = []
        for p in pats:
            rows.append(
                f'<tr><td class="en">{_esc(p["name"])}</td>'
                f'<td>{_esc("、".join(p["usage"]))}</td>'
                f'<td style="font-style:italic">{_esc(p["imitation"])}</td></tr>'
            )
        pat_html = (
            '<div class="section"><h2>作文加分句型（{n} 个）</h2><table>'
            "<thead><tr><th>句型</th><th>适用场景</th><th>仿写示例</th></tr></thead>"
            "<tbody>{r}</tbody></table></div>"
        ).format(n=len(pats), r="".join(rows))

    foot_bits = [f'按「{_esc(hb["level_name"])}」水平自动标注',
                 _esc(hb["level_tagline"])]
    if mode != "off":
        foot_bits.append("中文译文由大模型生成，供理解参考")
    foot_bits.append(f'共 {hb["word_count"]} 词')
    foot = f'<div class="foot">{" · ".join(foot_bits)}</div>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(title)} · {_esc(hb['level_name'])}</title>
<style>{CSS}</style></head>
<body>
<div class="sheet">
{head}
{note_html}
{_legend(c)}
{''.join(body)}
{vocab_html}
{pat_html}
{foot}
</div>
<div id="tip"></div>
<script>{JS}</script>
</body></html>"""
