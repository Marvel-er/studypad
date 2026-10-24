"""渲染产物结构自检：标签闭合、残留占位符、内容完整性。"""
import re
import sys
from pathlib import Path

ROOT = Path(r"F:\英语学习应用")
sys.path.insert(0, str(ROOT / "backend"))

from app import annotator, markup, parsers, render  # noqa: E402
from app.analyzer import split_spans  # noqa: E402

out = []
blocks, _ = parsers.parse("sample_article.md", (ROOT / "samples" / "sample_article.md").read_bytes())

for lv in ["high_school", "cet4", "cet6", "ielts", "toefl"]:
    hb = markup.build(annotator.analyze_document([b.as_dict() for b in blocks], lv), lv)
    html = render.render_handbook(hb, "The Cost of Convenience")
    span_o = len(re.findall(r"<span\b", html))
    span_c = html.count("</span>")
    div_o = len(re.findall(r"<div\b", html))
    div_c = html.count("</div>")
    a_o = len(re.findall(r"<a\b", html)); a_c = html.count("</a>")
    checks = {
        "span": (span_o, span_c),
        "div": (div_o, div_c),
        "a": (a_o, a_c),
    }
    bad = [k for k, (o, c) in checks.items() if o != c]
    leftovers = len(re.findall(r"\{[a-z_]+\}", html))
    out.append(f"[{lv:12s}] span {span_o}/{span_c}  div {div_o}/{div_c}  "
               f"未闭合={bad or '无'}  残留占位符={leftovers}  size={len(html)}")

# 抽取 cet4 的一段正文看渲染结构
hb = markup.build(annotator.analyze_document([b.as_dict() for b in blocks], "cet4"), "cet4")
block = hb["blocks"][0]
out.append("\n--- 首块原文 ---")
out.append(block["text"][:220])
out.append("--- 首块标注 ---")
for a in block["annotations"][:8]:
    out.append(f'  {a["type"]:20s} [{a["start"]}:{a["end"]}] "{a["surface"][:40]}" prio={a["priority"]} conf={a["confidence"]}')

# ---------------------------------------------------------------- 留白回归
#
# 用户反馈「生词表上面有很长的留白」。逐像素看那份截图：那一屏只有一排
# **空的译文框**（`.tr-zh` 的背景色一个像素不差，但框内没有任何文字）。
# 三种「有框无字」的写法都会造成这种观感，这里各钉一条断言：
#   ① 整块只有零宽字符 ② 译文视觉为空 ③ 同一区块内重复的语法讲解
#
# 注意反向断言：**正常内容必须照旧渲染**。修「空白」最容易的错法是修成
# 「什么都不渲染」，那样测试全绿、页面全空。

FAILS: list[str] = []


def _check(cond: bool, label: str, detail: str = "") -> None:
    out.append(f"  [{'PASS' if cond else 'FAIL'}] {label}" + (f"  → {detail}" if detail else ""))
    if not cond:
        FAILS.append(label)


ZW = "\u200b"          # 零宽空格：`str.strip()` 删不掉它
ZW_TOTAL = "\u200b\u200c\u200d\u2060\ufeff"

hb2 = markup.build(annotator.analyze_document([b.as_dict() for b in blocks], "cet4"), "cet4")

# ① 零宽伪区块 + ② 视觉为空的译文
zombie = {"id": "bzombie", "type": "paragraph", "order": 990, "text": ZW * 4,
          "page": None, "level": None, "bbox": None, "meta": {}, "annotations": []}
hb2["blocks"] = list(hb2["blocks"]) + [zombie]
hb2["translations"] = dict(hb2.get("translations") or {})
hb2["translations"]["bzombie"] = {
    "zh": ZW, "partial": False,
    "sentences": [{"start": 0, "end": 1, "en": ZW, "zh": ZW}],
}
hb2["trans_mode"] = "sentence"
# 再放一条**真实**译文：用来做反向断言 —— 别把「去掉空框」修成「什么都不渲染」
real = hb2["blocks"][0]
REAL_ZH = "这是一段用于回归测试的中文译文。"
hb2["translations"][real["id"]] = {
    "zh": REAL_ZH, "partial": False,
    "sentences": [{"start": 0, "end": len(real["text"]), "en": real["text"], "zh": REAL_ZH}],
}
html2 = render.render_handbook(hb2, "留白回归")

out.append("\n--- 留白回归 ---")
_check(ZW not in html2, "零宽字符一个都不出现在产物里",
       f"命中 {html2.count(ZW)} 次" if ZW in html2 else "干净")
for ch in ZW_TOTAL:
    _check(ch not in html2, f"不可见字符 U+{ord(ch):04X} 已清除")

empty_zh = [m for m in re.findall(r'<div class="tr-zh[^"]*">(.*?)</div>', html2, re.S)
            if not re.sub(r"<[^>]+>", "", m).replace(ZW, "").strip()]
_check(not empty_zh, "没有「有框无字」的译文块", f"发现 {len(empty_zh)} 个空框")

texts = [re.sub(r"<[^>]+>", "", m).strip()
         for m in re.findall(r'<div class="text">(.*?)</div>', html2, re.S)]
empty_text = [t for t in texts if not t.replace(ZW, "").strip()]
_check(not empty_text, "没有「有框无字」的原文块", f"发现 {len(empty_text)} 个空框")

# 反向断言：真实内容不许被误伤
_check(len(texts) >= 10, "正常原文块照旧渲染", f"共 {len(texts)} 块")
_check(REAL_ZH in html2, "真实译文照旧渲染（不是把空白修成「什么都不渲染」）")

# ③ 同一区块内重复的语法讲解 → 只留一条
dup = {
    "id": "bdup", "type": "paragraph", "order": 0, "text": "placeholder",
    "annotations": [
        {"type": "grammar_underline", "start": 0, "end": 1, "surface": "a",
         "payload": {"label": "名词性从句", "explain": "that 只起连接作用，what 充当成分。"}},
        {"type": "grammar_underline", "start": 2, "end": 3, "surface": "b",
         "payload": {"label": "名词性从句", "explain": "that 只起连接作用，what 充当成分。"}},
        {"type": "grammar_underline", "start": 4, "end": 5, "surface": "c",
         "payload": {"label": "定语从句", "explain": "先找先行词，从句单独拿出来翻译。"}},
    ],
}
side = render._render_side(dup)
n_note = side.count('<div class="note gram">')
_check(n_note == 2, "同区块内重复的语法讲解被合并（2 条不同标签保留，重复的去掉）",
       f"渲染出 {n_note} 条")
_check("名词性从句" in side and "定语从句" in side, "去重后两类语法都还在")

out.append("")
out.append(f"留白回归：{'全部通过' if not FAILS else '失败 ' + '、'.join(FAILS)}")

# ---------------------------------------------------------------- 译文失败回归
#
# 用户第二次反馈时纠正了我第一次的误读：
#   「生词表上面留白 说的是绿色译文框没有翻译下文，这一页是翻译失败的一页，
#     可能留白分页了」
#
# 根因是 `translate_blocks` 与 `render` 的口径不一致：
#   · `translate_blocks` 第三趟只把**成功译出的句子**放进 `tr["sentences"]`
#     （并置 partial=True）；
#   · `render._render_block_sentence` 却是按**全部 span** 遍历的，
#     旧实现给「这句没有译文」的分支也产出一个 `.tr-zh.partial` 空绿框。
# 于是一页里几段部分失败 → 十几到几十个空绿框 → 打印时又被
# `.block{break-inside:avoid}` 整体推到下一页 = 「整页留白 + 分页」。
#
# 这里构造三种失败形态（全译 / 部分译 / 一句没译），各钉一组断言，
# 并且照例都要带反向断言：正常译文不许被误伤。

out.append("\n--- 译文失败回归 ---")

SENTS4 = ["Alpha beta gamma delta.", "Epsilon zeta eta theta.",
          "Iota kappa lambda mu.", "Nu xi omicron pi."]
FULL_TEXT = " ".join(SENTS4)
OK_TEXT = "Sigma tau upsilon phi."




def _mk(bid: str, text: str) -> dict:
    return {"id": bid, "type": "paragraph", "order": 0, "text": text,
            "page": None, "level": None, "bbox": None, "meta": {}, "annotations": []}


sp_full = split_spans(FULL_TEXT)
sp_ok = split_spans(OK_TEXT)
_check(len(sp_full) == 4, "夹具：测试段能切成 4 句", f"实际 {len(sp_full)}")
_check(len(sp_ok) == 1, "夹具：对照段能切成 1 句", f"实际 {len(sp_ok)}")

hb3 = markup.build(annotator.analyze_document([b.as_dict() for b in blocks], "cet4"), "cet4")
hb3["blocks"] = [_mk("bfull", FULL_TEXT), _mk("bpart", FULL_TEXT),
                 _mk("bnone", FULL_TEXT), _mk("bok", OK_TEXT)]
hb3["trans_mode"] = "sentence"
hb3["translations"] = {
    # ① 全部译出：4 个绿框都该在
    "bfull": {"partial": False, "zh": "四句合起来的一段译文。",
              "sentences": [{"start": s, "end": e, "en": t, "zh": f"译文{i + 1}"}
                            for i, (s, e, t) in enumerate(sp_full)]},
    # ② 部分译出：只有第 1、3 句有译文 —— 这正是生产里「一批失败」的样子
    "bpart": {"partial": True, "zh": "",
              "sentences": [{"start": sp_full[0][0], "end": sp_full[0][1],
                             "en": SENTS4[0], "zh": "第一句译文"},
                            {"start": sp_full[2][0], "end": sp_full[2][1],
                             "en": SENTS4[2], "zh": "第三句译文"}]},
    # ③ 空壳记录：记录在、但一个字都没有（最坏情况，也不能崩）
    "bnone": {"partial": True, "zh": "", "sentences": []},
    # ④ 正常对照
    "bok": {"partial": False, "zh": "正常译文",
            "sentences": [{"start": sp_ok[0][0], "end": sp_ok[0][1],
                           "en": sp_ok[0][2], "zh": "正常译文"}]},
}
html3 = render.render_handbook(hb3, "译文失败回归")

zh_boxes = re.findall(r'<div class="tr-zh[^"]*">(.*?)</div>', html3, re.S)
empty_boxes = [b for b in zh_boxes if not re.sub(r"<[^>]+>", "", b).strip()]
_check(not empty_boxes, "译文失败：没有任何空绿框", f"发现 {len(empty_boxes)} 个")
_check("（本句未译出）" not in html3,
       "译文失败：不再逐句输出「（本句未译出）」占位绿框")
# 期望：bfull 4 个 + bpart 2 个 + bnone 0 个 + bok 1 个 = 7
_check(len(zh_boxes) == 7,
       "译文失败：绿框数 = 真的译出来的句子数（4+2+0+1）", f"实际 {len(zh_boxes)}")

# 反向断言：译出来的必须照旧显示
for want in ("译文1", "译文4", "第一句译文", "第三句译文", "正常译文"):
    _check(want in html3, f"反向：已译出的「{want}」照旧渲染")

# 未译出的句子不配框，但**原文不能丢**
for s in SENTS4:
    _check(s in html3, f"反向：原文「{s[:18]}…」仍完整保留")

# 用一条灰色说明替代 N 个空框
n_miss = html3.count('class="tr-miss"')
_check(n_miss >= 1, "未译出的句子汇总成一条灰色说明", f"共 {n_miss} 条")
_check("本段另有 2 句未取到译文" in html3,
       "说明里给出了准确的缺句数（bpart 缺 2 句）")

# 覆盖率必须如实：按**句**算 7/13（bfull 4/4 + bpart 2/4 + bnone 0/4 + bok 1/1）。
# 只看段覆盖率会得出 3/4 —— 而「每段都缺一点」时段覆盖率照样很高，
# 用户却在读缺了三分之一译文的文章，所以必须暴露到句这一级。
_check("中文译文 7/13 句" in html3, "页眉覆盖率如实到句（7/13 句）")
_check('class="chip warn"' in html3, "覆盖率不足时 chip 转告警色")
_check('class="hb-note"' in html3, "顶部出现译文降级提示条")
_check("中文译文只覆盖 7/13 句" in html3,
       "提示条说清了缺多少句（而不是只报段数）")
hb3["trans_note"] = "中文译文 3/4 段，2 段未译"
html3b = render.render_handbook(hb3, "译文失败回归")
_check("2 段未译" in html3b, "把 trans_note 的原因也渲染出来（以前只挂在数据上）")

# 顺利时必须干净：不能给正常手账挂一条无意义的告警条
hbfine = markup.build(annotator.analyze_document([b.as_dict() for b in blocks], "cet4"), "cet4")
hbfine["trans_mode"] = "sentence"
hbfine["translations"] = {
    b["id"]: {"partial": False, "zh": "全段译文。",
              "sentences": [{"start": s, "end": e, "en": t, "zh": "全段译文。"}
                            for s, e, t in split_spans(b["text"])]}
    for b in hbfine["blocks"] if (b.get("text") or "").strip()
}
hbfine["trans_note"] = "中文译文 11/11 段"
htmlfine = render.render_handbook(hbfine, "顺利回归")
_check('class="hb-note"' not in htmlfine, "反向：顺利时不出告警条（保持页面干净）")
_check('class="chip warn"' not in htmlfine, "反向：顺利时 chip 不是告警色")

# 段覆盖满、句覆盖不足 —— 必须照样告警。
# 这正是「每段都缺两三句」的整页降级形状：段覆盖率恒为 100%，
# 只看段就会永远漏报，而用户读的是缺了三分之一译文的文章。
hbseg = markup.build(annotator.analyze_document([b.as_dict() for b in blocks], "cet4"), "cet4")
hbseg["trans_mode"] = "sentence"
hbseg["translations"] = {}
for b in hbseg["blocks"]:
    _sp = split_spans(b.get("text") or "")
    if not _sp:
        continue
    # 每隔一句丢掉一句（i=0 保留，所以每个段都「有」译文 → 段覆盖率 100%）
    hbseg["translations"][b["id"]] = {
        "partial": True, "zh": "",
        "sentences": [{"start": s, "end": e, "en": t, "zh": "半句译文"}
                      for i, (s, e, t) in enumerate(_sp) if i % 2 == 0],
    }
_ntext = len(render._text_blocks(hbseg))
_check(_ntext and len(hbseg["translations"]) >= _ntext,
       "夹具：段覆盖率看起来是满的", f"{len(hbseg['translations'])}/{_ntext}")
htmlseg = render.render_handbook(hbseg, "段满句缺")
_check('class="hb-note"' in htmlseg,
       "段覆盖满、句覆盖不足时仍然告警（只看段覆盖率会漏报）")
_check('class="chip warn"' in htmlseg, "同上：chip 也是告警色")
_check("中文译文只覆盖" in htmlseg and "句" in htmlseg, "同上：提示条按句报数")

out.append("")
out.append(f"译文失败回归：{'全部通过' if not FAILS else '失败 ' + '、'.join(FAILS)}")

# ---------------------------------------------------------------- 黑条回归
#
# 用户第三次反馈：「为什么会有黑色横杠」。截图里 `stripped` / `emerges`
# 两个词的下半部分各盖着一块**实心纯黑矩形**，文字在黑块里看不见（黑底黑字）。
#
# 逐像素定位到两块矩形的位置与 `.w-target` 的荧光笔几何**完全吻合**
# （`linear-gradient(180deg, … 52% … 92% …)` 正好是词的下半段）。
# 但同一条 HTML 在我这边渲染是**0 条纯黑、1700+ 像素荧光黄**，
# 说明问题不在产物内容，而在**这条 CSS 的两个脆弱点**：
#
#   ① `var(--hl)` —— 这种**通用变量名**会被宿主环境（预览面板 / 嵌入方的
#      主题样式表）重定义。旁证很硬：同一个 `:root` 里的 `--paper` 完全正常
#      （截图背景 `(252,250,243)` 就是我们的纸色），**只有 `--hl` 变黑**。
#      → 修法：变量全部加项目前缀 `--sp-`，且**荧光笔不再依赖变量**，直接写字面量。
#
#   ② `transparent` —— 它就是 `rgba(0,0,0,0)`，是**黑配零透明**。
#      任何一条丢掉 alpha 的渲染路径（打印导出、SVG 栅格化、某些合成器）
#      都会把它变成**不透明纯黑**。→ 修法：渐变里的透明端写成与色带同色族的
#      零透明 `rgba(255,224,102,0)`，丢掉 alpha 也只是看不见，不会变黑。
#
# 下面这组断言把两个脆弱点钉死。写成**可复用的审计函数**，是为了能做
# 反向验证 —— 一条永远不会失败的断言等于没写。

OPAQUE_BLACK = r"#000\b|#000000\b|rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*1\s*\)|\bblack\b"


def _audit_pen(text: str) -> list[tuple[str, bool, str]]:
    """审计「荧光笔会不会渲染成黑条」。返回 [(标签, 是否通过, 说明)]。"""
    res: list[tuple[str, bool, str]] = []
    m = re.search(r"<style>(.*?)</style>", text, re.S) or re.search(r"<style>(.*)", text, re.S)
    css = m.group(1) if m else ""
    if not css:
        return [("取到 <style> 块", False, "没有 style 块")]

    # ① 变量名撞车：通用名（--hl/--paper/--ink…）会被宿主主题重定义
    bad_use = sorted({n for n in re.findall(r"var\(\s*(--[A-Za-z0-9_-]+)", text)
                      if not n.startswith("--sp-")})
    res.append(("所有 var() 引用的变量都带 --sp- 前缀（防宿主重定义）",
                not bad_use, f"未加前缀：{bad_use}" if bad_use else "全部带前缀"))

    defs = {n for n in re.findall(r"(--[A-Za-z0-9_-]+)\s*:", text)}
    bad_def = sorted(n for n in defs if not n.startswith("--sp-"))
    res.append(("所有变量定义都带 --sp- 前缀",
                not bad_def, f"未加前缀：{bad_def}" if bad_def else "全部带前缀"))

    used = set(re.findall(r"var\(\s*(--sp-[A-Za-z0-9_-]+)\s*\)", text))
    miss = sorted(used - defs)
    res.append(("裸 var() 引用的变量都有定义",
                not miss, f"缺定义：{miss}" if miss else "全部有定义"))

    # ② 渐变里的 transparent 就是 rgba(0,0,0,0)，丢 alpha 会变成不透明纯黑
    grads = re.findall(r"(?:repeating-)?(?:linear|radial|conic)-gradient\([^;{}\"']*", css)
    res.append(("样式里有渐变（荧光笔 / 纸纹）", bool(grads), f"共 {len(grads)} 处"))
    for i, g in enumerate(grads):
        head = g.split("(")[0]
        has_t = re.search(r"\btransparent\b", g)
        res.append((f"渐变 #{i + 1}（{head}）的透明端不用 transparent（丢 alpha 会变纯黑）",
                    not has_t, g[:64] if has_t else ""))
        has_b = re.search(OPAQUE_BLACK, g)
        res.append((f"渐变 #{i + 1}（{head}）里没有不透明黑", not has_b, g[:64] if has_b else ""))

    # ③ 荧光笔本身必须写字面量，不依赖任何变量
    wt = re.search(r"\.w-target\{([^}]*)\}", css)
    if not wt:
        res.append(("定位到 .w-target 规则", False, "没找到 .w-target"))
    else:
        w = wt.group(1)
        res.append(("荧光笔颜色不依赖任何 CSS 变量（宿主改了也不变色）",
                    "var(" not in w, w[:64] if "var(" in w else ""))
        res.append(("荧光笔用的是荧光黄字面量",
                    "#FFE066" in w or "255,224,102" in w, w[:64]))
        res.append(("荧光笔的透明端是同色族零透明（丢 alpha 也只会看不见，不会变黑）",
                    "rgba(255,224,102,0)" in w, w[:64]))

    # ④ 兜底：任何 background 声明里都不许有纯黑
    black_bg = [d for d in re.findall(r"background(?:-color)?\s*:\s*([^;}\"']*)", css)
                if re.search(OPAQUE_BLACK, d)]
    res.append(("样式里没有任何纯黑填充", not black_bg, f"发现 {len(black_bg)} 处" if black_bg else "0 处"))
    return res


out.append("\n--- 黑条回归 ---")

for _label, _ok, _detail in _audit_pen(html):
    _check(_ok, _label, _detail)

# 反向验证：把旧实现贴回去，审计**必须**报警，否则上面那 14 条就是摆设。
_wt_new = re.search(r"\.w-target\{[^}]*\}", html).group(0)
_wt_old = (".w-target{background:linear-gradient(180deg,transparent 52%,var(--hl) 52%,"
           "var(--hl) 92%,transparent 92%);border-radius:2px}")
broken_old = html.replace(_wt_new, _wt_old).replace("--sp-", "--")
_bad_old = [l for l, ok, _ in _audit_pen(broken_old) if not ok]
_check(len(_bad_old) >= 4, "反向：贴回旧实现（transparent + var(--hl) + 无前缀）后审计确实报警",
       f"报出 {len(_bad_old)} 项：{'、'.join(_bad_old[:3])}…")
for _want in ("所有 var() 引用的变量都带 --sp- 前缀（防宿主重定义）",
              "所有变量定义都带 --sp- 前缀",
              "荧光笔颜色不依赖任何 CSS 变量（宿主改了也不变色）"):
    _check(_want in _bad_old, f"反向：旧实现命中「{_want}」")

# 反向验证 2：模拟「丢掉 alpha」这条路径 —— 透明端塌成不透明黑
broken_alpha = (html.replace("rgba(255,224,102,0)", "rgba(0,0,0,1)")
                    .replace("rgba(120,150,190,0)", "rgba(0,0,0,1)"))
_bad_alpha = [l for l, ok, _ in _audit_pen(broken_alpha) if not ok]
_check(len(_bad_alpha) >= 2, "反向：把零透明改成不透明黑后审计确实报警",
       f"报出 {len(_bad_alpha)} 项：{'、'.join(_bad_alpha)}")
_check("样式里没有任何纯黑填充" in _bad_alpha, "反向：纯黑填充这条真的会咬人")

out.append("")
out.append(f"黑条回归：{'全部通过' if not FAILS else '失败 ' + '、'.join(FAILS)}")

(ROOT / "out" / "_render_check.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
sys.exit(1 if FAILS else 0)
