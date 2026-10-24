"""
把考点知识库导出一份自包含 HTML 报告。

为什么要有这个：
知识库本体是给 agent 用的（Python 数据结构 + API），但「有据可查」这件事
必须让人能亲眼看到 —— 用户要能翻到某一条考点、点开它的来源链接。
所以这里做一份纯静态、可打印、无外部依赖的单文件报告。

数据全部从 `app.exam_points` 读，不在这里写死任何内容。
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app import exam_points as ep  # noqa: E402

OUT = ROOT / "out" / "考点知识库.html"

TIER_LABEL = {"official": "官方", "semi_official": "教研转述",
              "secondary": "第三方", "oss": "开源"}

CSS = """
:root{--bg:#f6f7f9;--card:#fff;--border:#e3e6ea;--ink:#1f2328;--ink2:#5b6370;
--accent:#c0392b;--accent-soft:#fdf2f0}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-size:14.5px;line-height:1.75;
font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
header{background:#fff;border-bottom:1px solid var(--border);padding:26px 34px 22px}
header h1{margin:0;font-size:24px;letter-spacing:-.02em}
header .sub{color:var(--ink2);font-size:13px;margin-top:6px}
.wrap{max-width:1060px;margin:0 auto;padding:24px 34px 100px}
.stats{display:flex;gap:10px;flex-wrap:wrap;margin:18px 0 8px}
.stat{background:#fff;border:1px solid var(--border);border-radius:10px;padding:10px 16px;min-width:110px}
.stat u{display:block;text-decoration:none;font-size:21px;font-weight:700;line-height:1.25;color:var(--accent)}
.stat s{display:block;text-decoration:none;font-size:11.5px;color:var(--ink2);margin-top:2px}
.toc{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0 26px}
.toc a{display:block;background:#fff;border:1px solid var(--border);border-radius:9px;
padding:8px 14px;font-size:13px;color:var(--ink);text-decoration:none}
.toc a:hover{border-color:var(--accent);color:var(--accent)}
.lv{background:var(--card);border:1px solid var(--border);border-radius:12px;
padding:22px 26px;margin-bottom:22px;scroll-margin-top:16px}
.lv > h2{margin:0 0 4px;font-size:19px;display:flex;align-items:center;gap:9px}
.lv > h2 i{width:4px;height:18px;background:var(--accent);border-radius:2px;display:inline-block}
.lv .en{color:var(--ink2);font-size:12.5px;margin-bottom:14px}
h3{font-size:14.5px;margin:22px 0 9px;padding-bottom:6px;border-bottom:1px dashed var(--border);
font-weight:650;color:var(--ink)}
h3:first-of-type{margin-top:16px}
.chips{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:12px}
.chip{background:#fff;border:1px solid var(--border);border-radius:7px;padding:4px 11px;
font-size:12px;color:var(--ink2)}
.chip b{color:var(--ink);font-weight:650}
.note{background:#fbfcfd;border-left:3px solid #cfd5dd;padding:8px 13px;font-size:12.5px;
color:var(--ink2);margin:8px 0 12px;border-radius:0 6px 6px 0}
.warn{background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:9px 13px;
font-size:12.5px;color:#7c5a00;margin:8px 0 12px}
.row{padding:9px 0;border-top:1px dashed var(--border)}
.row:first-child{border-top:none}
.row > b{font-size:13.5px;font-weight:650}
.row p{margin:3px 0 0;color:var(--ink2);font-size:12.8px}
.row ul{margin:4px 0 0;padding-left:18px;color:var(--ink2);font-size:12.8px}
.mono{font-weight:600;color:var(--ink);font-size:12.5px}
.sb{display:inline-block;margin-left:6px;font-size:10.5px;padding:1px 7px;border-radius:5px;
background:#eef2f7;color:#4b5563;vertical-align:1.5px;white-space:nowrap}
.sb.official{background:#e3f5ec;color:#0f6e56}
.sb.semi_official{background:#fef4e3;color:#916107}
.sb.secondary{background:#f1f0f6;color:#5b5b7a}
.tag{display:inline-block;margin-left:6px;font-size:10.5px;padding:1px 7px;border-radius:5px;
background:#f3f4f6;color:#6b7280;vertical-align:1.5px}
table{width:100%;border-collapse:collapse;font-size:12.8px;margin-top:4px}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--border);vertical-align:top}
th{background:#fafbfc;font-weight:650;font-size:12.3px;color:var(--ink2)}
td.num{white-space:nowrap;color:var(--ink);font-weight:600}
.srcline{display:flex;gap:10px;padding:9px 0;border-top:1px dashed var(--border);font-size:12.8px}
.srcline:first-child{border-top:none}
.srcline .t{flex:1}
.srcline b{font-size:13px}
.srcline .m{color:var(--ink2);font-size:12px;margin-top:2px}
a{color:#2563eb}
footer{color:var(--ink2);font-size:12px;text-align:center;padding:30px 0}
code{background:#f1f3f6;padding:1px 5px;border-radius:4px;font-size:12.5px}
@media print{body{background:#fff}.lv{break-inside:avoid;border-color:#ccc}}
"""


def e(x) -> str:
    return html.escape(str(x if x is not None else ""))


def badge(ids: list[str] | None, srcmap: dict) -> str:
    if not ids:
        return ""
    out = []
    for sid in ids:
        s = srcmap.get(sid)
        if not s:
            out.append(f'<span class="sb">{e(sid)}</span>')
            continue
        title = f"{s['title']} —— {s['publisher']}（访问 {s['accessed']}）"
        out.append(f'<span class="sb {e(s["tier"])}" title="{e(title)}">{e(s["short"])}</span>')
    return "".join(out)


def render_level(lid: str) -> str:
    d = ep.require(lid)
    srcs = ep.sources_of(lid)
    srcmap = {s["id"]: s for s in srcs}
    prof = d.get("profile", {})
    v = d.get("vocabulary", {})
    g = d.get("grammar", {})
    q = d.get("question_types", {})
    h: list[str] = []

    h.append(f'<section class="lv" id="{e(lid)}">')
    h.append(f'<h2><i></i>{e(d["label"])}</h2>')
    h.append(f'<div class="en">{e(d["en"])}</div>')

    chips = []
    if prof.get("score_scale"):
        chips.append(f'<span class="chip">满分 <b>{e(prof["score_scale"])}</b></span>')
    if prof.get("duration"):
        chips.append(f'<span class="chip">时长 <b>{e(prof["duration"])}</b></span>')
    if prof.get("paper_count"):
        chips.append(f'<span class="chip">题量 <b>{e(prof["paper_count"])}</b></span>')
    chips.append(f'<span class="chip">词汇目标 <b>{e(v.get("target"))}</b> 词</span>')
    chips.append(f'<span class="chip">来源 <b>{len(srcs)}</b> 条</span>')
    h.append('<div class="chips">' + "".join(chips) + "</div>")
    if prof.get("note"):
        h.append(f'<div class="warn">{e(prof["note"])}</div>')

    # 词汇
    h.append("<h3>一、词汇</h3>")
    h.append(f'<div class="note">目标约 <b>{e(v.get("target"))}</b> 词。{e(v.get("basis"))}'
             f'{badge(v.get("src"), srcmap)}</div>')
    for t in v.get("tiers", []):
        h.append(f'<div class="row"><b>{e(t["name"])}</b><p>{e(t["detail"])}</p></div>')
    if v.get("focus"):
        h.append('<div class="row"><b>考查侧重</b><ul>'
                 + "".join(f"<li>{e(x)}</li>" for x in v["focus"]) + "</ul></div>")

    # 语法
    h.append("<h3>二、语法</h3>")
    if g.get("note"):
        h.append(f'<div class="note">{e(g["note"])}</div>')
    for it in g.get("items", []):
        h.append(f'<div class="row"><b>{e(it["name"])}</b>{badge(it.get("src"), srcmap)}'
                 f'<p>{e(it["detail"])}</p></div>')
    if g.get("cross_check"):
        h.append('<div class="note">结构交叉校验：'
                 + e("、".join(g["cross_check"]))
                 + "（仅用于比对知识点是否遗漏，未引用原文）</div>")

    # 题型
    h.append("<h3>三、题型与分值</h3>")
    if q.get("note"):
        h.append(f'<div class="note">{e(q["note"])}</div>')
    rows = []
    for it in q.get("items", []):
        legacy = (f'<span class="tag">已于 {e(it["effective_until"])} 起失效</span>'
                  if it.get("effective_until") else "")
        rows.append(
            "<tr>"
            f'<td class="num">{e(it["section"])}</td>'
            f"<td>{e(it['name'])}{badge(it.get('src'), srcmap)}{legacy}"
            + (f'<div class="m" style="color:#5b6370;font-size:12px;margin-top:3px">'
               f'{e(it["detail"])}</div>' if it.get("detail") else "")
            + "</td>"
            f'<td class="num">{e(it.get("items", "—"))}</td>'
            f'<td class="num">{e(it.get("score", "—"))}</td>'
            f'<td class="num">{e(it.get("time", "—"))}</td>'
            "</tr>")
    h.append("<table><thead><tr><th>板块</th><th>题型</th><th>题量</th>"
             "<th>分值</th><th>时长</th></tr></thead><tbody>"
             + "".join(rows) + "</tbody></table>")

    # 高频考点
    h.append("<h3>四、高频考点</h3>")
    for t in d.get("high_frequency", []):
        h.append(f'<div class="row"><b>{e(t["topic"])}</b>{badge(t.get("src"), srcmap)}<ul>'
                 + "".join(f"<li>{e(x)}</li>" for x in t.get("points", []))
                 + "</ul></div>")

    # 考查重点
    h.append("<h3>五、考查重点</h3>")
    for f in d.get("focus", []):
        h.append(f'<div class="row"><b>{e(f["title"])}</b>{badge(f.get("src"), srcmap)}'
                 f'<p>{e(f["detail"])}</p></div>')

    # 来源
    h.append("<h3>六、本档来源依据</h3>")
    for s in srcs:
        h.append(
            '<div class="srcline"><div class="t">'
            f'<b>{e(s["title"])}</b>'
            f'<span class="sb {e(s["tier"])}">{e(TIER_LABEL.get(s["tier"], s["tier"]))}</span>'
            f'<div class="m">{e(s["publisher"])}　·　访问日期 {e(s["accessed"])}</div>'
            f'<div class="m">可查证：{e(s["establishes"])}</div>'
            + (f'<div class="m">注：{e(s["note"])}</div>' if s.get("note") else "")
            + f'<div class="m"><a href="{e(s["url"])}" target="_blank" rel="noopener">'
              f'{e(s["url"])}</a></div>'
            "</div></div>")

    h.append("</section>")
    return "\n".join(h)


def main() -> None:
    st = ep.stats()
    n_official = sum(1 for v in ep.SOURCES.values() if v["tier"] == "official")
    parts: list[str] = []
    parts.append("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>"
                 "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                 "<title>六档英语考点知识库</title>"
                 f"<style>{CSS}</style></head><body>")
    parts.append(
        "<header><h1>六档英语考点知识库</h1>"
        "<div class='sub'>高中 · 大学英语四级 · 大学英语六级 · 考研 · 雅思 · 托福"
        "　—— 覆盖词汇 / 语法 / 题型 / 高频考点 / 考查重点，逐条标注来源</div>"
        "<div class='stats'>"
        f"<div class='stat'><u>{st['levels']}</u><s>考试阶段</s></div>"
        f"<div class='stat'><u>{st['sources']}</u><s>来源条目</s></div>"
        f"<div class='stat'><u>{n_official}</u><s>官方来源</s></div>"
        f"<div class='stat'><u>{st['grammar_items']}</u><s>语法考点块</s></div>"
        f"<div class='stat'><u>{st['question_types']}</u><s>题型条目</s></div>"
        f"<div class='stat'><u>{st['high_frequency_topics']}</u><s>高频考点主题</s></div>"
        f"<div class='stat'><u>{st['focus_items']}</u><s>考查重点</s></div>"
        "</div></header><div class='wrap'>")

    parts.append("<div class='toc'>" + "".join(
        f'<a href="#{e(lid)}">{e(ep.require(lid)["label"])}</a>' for lid in ep.ORDER
    ) + "</div>")

    parts.append(
        "<div class='note'>可信度分级：<span class='sb official'>官方</span>"
        "考试主办方或教育主管部门原文／官方页面；"
        "<span class='sb semi_official'>教研转述</span>权威教研机构对官方口径的复述；"
        "<span class='sb secondary'>第三方</span>第三方整理，仅作旁证。"
        "失效的旧制条目会明确标注失效日期，不与现行口径混在一起。</div>")

    for lid in ep.ORDER:
        parts.append(render_level(lid))

    # 附录：来源总表 + 开源交叉校验
    parts.append("<section class='lv' id='appendix'><h2><i></i>附录 · 全部来源</h2>")
    parts.append("<h3>来源登记表</h3>")
    for sid, s in ep.SOURCES.items():
        parts.append(
            '<div class="srcline"><div class="t">'
            f'<b>{e(s["title"])}</b>'
            f'<span class="sb {e(s["tier"])}">{e(TIER_LABEL.get(s["tier"], s["tier"]))}</span>'
            f'<div class="m">id = <code>{e(sid)}</code>　·　{e(s["publisher"])}'
            f'　·　访问日期 {e(s["accessed"])}</div>'
            f'<div class="m">可查证：{e(s["establishes"])}</div>'
            + (f'<div class="m">注：{e(s["note"])}</div>' if s.get("note") else "")
            + (f'<div class="m">失效日期：{e(s["effective_until"])}</div>'
               if s.get("effective_until") else "")
            + f'<div class="m"><a href="{e(s["url"])}" target="_blank" rel="noopener">'
              f'{e(s["url"])}</a></div></div></div>')

    parts.append("<h3>开源仓库（仅结构交叉校验，未引用原文）</h3>")
    for name, o in ep.OSS_SOURCES.items():
        parts.append(
            '<div class="srcline"><div class="t">'
            f'<b>{e(name)}</b><span class="sb oss">开源</span>'
            f'<div class="m">许可证：{e(o["license"])}　·　用途：{e(o["usage"])}</div>'
            f'<div class="m">覆盖：{e(o["covers"])}</div>'
            f'<div class="m">说明：{e(o["note"])}</div></div></div>')
    parts.append("</section>")

    parts.append("<footer>数据源：<code>backend/app/exam_points.py</code>　·　"
                 "接口：<code>GET /api/exam-points/&lt;level_id&gt;</code>　·　"
                 "本页可离线打印</footer>")
    parts.append("</div></body></html>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"written: {OUT}  {OUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
