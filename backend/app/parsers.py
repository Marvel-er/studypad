"""
文档解析层：任意格式 → 统一中间表示 Block[]。

三条通道，产出同一个 IR：
  · 文字层 PDF / DOCX / MD / TXT  → 直接抽取
  · 扫描件 PDF                     → pypdfium2 渲染成图 → RapidOCR
  · 图片                            → RapidOCR

PDF 引擎用 **pypdfium2**（Apache-2.0 / BSD-3），
替换掉原先的 PyMuPDF（AGPL-3.0），消除商业化的许可传染风险。

版面重建（行聚类 / 双栏重排 / 标题识别）统一在 layout.py，
因此文字层与 OCR 通道的行为完全一致。
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

from . import layout

SUPPORTED = {".txt", ".md", ".markdown", ".pdf", ".docx", ".doc"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

# 扫描件判定：平均每页字符数低于此值 → 走 OCR
SCANNED_CHAR_THRESHOLD = 100
# OCR 渲染倍率（点数 → 像素）
OCR_SCALE = 2.5
OCR_MAX_SIDE = 2600


@dataclass
class Block:
    id: str
    type: str                 # title | heading | paragraph | list | quote | code | table | figure
    order: int
    text: str
    page: int | None = None
    level: int | None = None
    bbox: tuple[float, float, float, float] | None = None
    meta: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


# 零宽 / 不可见字符：PDF 文字层与 OCR 引擎都会产出
# （U+200B 零宽空格、U+FEFF BOM 残留、U+200C/200D 连接符、U+2060 word joiner）。
#
# 危害很隐蔽：它们**能通过 `str.strip()`**，于是「整块只有零宽字符」的伪文本块
# 会被一路当成有内容，最后在页面上渲染出一个有背景、没文字的框 ——
# 用户看到的就是一片莫名其妙的留白（截图反馈过）。
# 所以在解析层就清掉，这是所有下游判空的前提。
_ZERO_WIDTH = dict.fromkeys(
    [0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0x00AD, 0x180E]
    + [c for c in range(0x00, 0x20) if c not in (0x09, 0x0A)]      # 控制字符（留 \t \n）
    + [0x7F] + list(range(0x80, 0xA0)),                            # DEL 与 C1
    None,
)


def clean_text(s: str) -> str:
    """
    去掉零宽字符与其它不可见字符。**解析层的统一文本出口**，下游不要再各写各的 strip()。

    只删不可见字符，不动换行与空格 —— 代码块、表格的对齐依赖它们。
    PDF 文字层里常有 C0 控制字符（尤其是 \x00 与 \x0c），它们同样骗得过
    `str.strip()`，会在页面上留下「有框无字」的空块，所以一并清掉。
    """
    return (s or "").translate(_ZERO_WIDTH)


def _mk(btype: str, order: int, text: str, **kw) -> Block:
    return Block(id=f"b{order:04d}", type=btype, order=order,
                 text=clean_text(text).strip(), **kw)


def _from_specs(specs: list[layout.BlockSpec], start_order: int) -> list[Block]:
    out: list[Block] = []
    order = start_order
    for s in specs:
        out.append(Block(
            id=f"b{order:04d}", type=s.type, order=order, text=clean_text(s.text),
            page=s.page, level=s.level, bbox=s.bbox, meta=dict(s.meta or {}),
        ))
        order += 1
    return out


# ---------------------------------------------------------------- TXT / MD

def parse_text(raw: str) -> list[Block]:
    blocks: list[Block] = []
    order = 0
    para: list[str] = []

    def flush() -> None:
        nonlocal order, para
        if para:
            txt = " ".join(para).strip()
            if txt:
                blocks.append(_mk("paragraph", order, txt))
                order += 1
            para = []

    for line in raw.splitlines():
        s = line.strip()
        if not s:
            flush()
            continue
        if re.match(r"^#{1,6}\s+", s):
            flush()
            lvl = len(s) - len(s.lstrip("#"))
            title = re.sub(r"^#{1,6}\s+", "", s)
            blocks.append(_mk("title" if lvl == 1 else "heading", order, title, level=lvl))
            order += 1
            continue
        if re.match(r"^([-*+]|\d+[.)])\s+", s):
            flush()
            blocks.append(_mk("list", order, re.sub(r"^([-*+]|\d+[.)])\s+", "", s)))
            order += 1
            continue
        if s.startswith(">"):
            flush()
            blocks.append(_mk("quote", order, s.lstrip("> ").strip()))
            order += 1
            continue
        para.append(s)

    flush()
    return blocks


def _strip_inline_md(s: str) -> str:
    """剥掉行内的 Markdown 语法（行级结构由 parse_text 处理）。"""
    s = re.sub(r"`([^`]*)`", r"\1", s)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"\*\*([^*]*)\*\*", r"\1", s)
    s = re.sub(r"\*([^*]*)\*", r"\1", s)
    s = re.sub(r"^\s*\|.*\|\s*$", "", s, flags=re.M)
    return s


def parse_markdown(raw: str) -> list[Block]:
    """
    剥掉 Markdown 语法后按纯文本切块（表格与代码块单独成块）。

    ⚠ 这里曾有一个**把阅读顺序整个打乱**的 bug（2026-10-14 修）：
    早先实现分两趟 —— 先用一个 while 循环把表格 / 代码块按文档顺序收进来
    （`order` 从 0 开始），再把「剩下的正文」整批交给 `parse_text`，
    块号接着往下排，最后按 `order` 排序。于是**只要文档里出现一个表格或
    代码块，它就会被搬到全文最前面** —— 连标题都排到它后面。
    用户看到的是：手账第一页是一张表，然后才是文章标题。

    现在改成**单趟**：按行推进，遇到表格 / 代码块就地成块，
    其余行攒成一批交给 `parse_text`，顺序天然就是文档顺序。
    """
    blocks: list[Block] = []
    order = 0
    lines = raw.splitlines()
    i = 0
    pending: list[str] = []

    def flush_pending() -> None:
        """把攒着的普通行交给 parse_text，并就地分配块号。"""
        nonlocal order, pending
        if not pending:
            return
        for b in parse_text(_strip_inline_md("\n".join(pending))):
            b.order = order
            b.id = f"b{order:04d}"
            order += 1
            blocks.append(b)
        pending = []

    while i < len(lines):
        s = lines[i].strip()

        # --- 表格：表头行 + 分隔行 + 后续所有 | 行 ---
        if s.startswith("|") and i + 1 < len(lines) \
                and re.match(r"^\|[\s:\-|]+\|$", lines[i + 1].strip()):
            tbl = [s]
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                tbl.append(lines[j].strip())
                j += 1
            flush_pending()
            text = "\n".join(
                " | ".join(c.strip() for c in r.strip("|").split("|"))
                for r in tbl if not re.match(r"^\|[\s:\-|]+\|$", r)
            )
            blocks.append(_mk("table", order, text))
            order += 1
            i = j
            continue

        # --- 代码块：``` 围栏（内容不参与语言分析） ---
        if s.startswith("```"):
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(lines[j])
                j += 1
            flush_pending()
            blocks.append(_mk("code", order, "\n".join(buf), meta={"skip": True}))
            order += 1
            i = j + 1
            continue

        pending.append(lines[i])
        i += 1

    flush_pending()
    return blocks


# ---------------------------------------------------------------- PDF

def _extract_lines(textpage, page_h: float) -> list[layout.Line]:
    """
    从 pypdfium2 的文字层逐字符抽取，聚成行。

    字号不用 pypdfium2 的 get_fontsize —— 实测它返回的是缩放过的值
    （18pt 报 12.0、10.5pt 报 8.6），比例不稳定，会把标题降级、把段落误切。
    改用**行内字符框高度的 90 分位**（见 _line_size 的说明）。
    """
    try:
        n = textpage.count_chars()
    except Exception:  # noqa: BLE001
        return []

    if not hasattr(textpage, "get_charbox"):
        return []

    lines: list[layout.Line] = []
    buf: list[tuple[str, tuple[float, float, float, float]]] = []

    def flush() -> None:
        if not buf:
            return
        text = "".join(c for c, _ in buf)
        if text.strip():
            xs0 = [b[0] for _, b in buf]
            ys0 = [b[1] for _, b in buf]
            xs1 = [b[2] for _, b in buf]
            ys1 = [b[3] for _, b in buf]
            size = _line_size(buf, ys0, ys1)
            lines.append(layout.Line(
                text=text,
                x0=min(xs0), x1=max(xs1),
                y0=page_h - max(ys1),      # PDF 原点在左下，翻转成左上原点
                y1=page_h - min(ys0),
                size=size,
            ))
        buf.clear()

    for i in range(n):
        try:
            ch = textpage.get_text_range(i, 1)
        except Exception:  # noqa: BLE001
            continue
        if not ch:
            continue
        if ch in ("\r", "\n"):
            flush()
            continue
        try:
            box = tuple(textpage.get_charbox(i))       # (l, b, r, t)
        except Exception:  # noqa: BLE001
            continue
        buf.append((ch, box))
    flush()
    return lines


def _line_size(buf, ys0, ys1) -> float:
    """
    行字号代理：字符框高度的 **90 分位**。

    pypdfium2 的 get_charbox 返回的是**字形包围盒**，不是字号，
    所以「众数」会被 x-height 字母（o/a/e/n/r…）带偏：
        'prevention rather than remediation.'      → 众数 4.80
        'without saying that technology itself'    → 众数 7.30
    同一段落被判成两种字号，触发 size_shift 断块 + 误判标题。

    scripts/probe_size.py 实测四种统计量的行间相对标准差：
        mode 19.6%   median 11.7%   max 5.8%   **p90 1.1%**
    p90 既能稳定贴近字体 ascender，又能滤掉偶发的异常框
    （如 'objectives, and how that choice is' 里那个 9.55 的离群框，
      max 会被它骗成 heading，p90 不会）。
    """
    heights = [round(abs(b[3] - b[1]), 2) for _, b in buf if abs(b[3] - b[1]) > 0.15]
    if not heights:
        return float(max(max(ys1) - min(ys0), 1.0) * 0.7)
    heights.sort()
    n = len(heights)
    return float(heights[min(n - 1, int(n * 0.90))])


def _render_page(page, scale: float):
    """渲染整页为 PIL 图，自动限制最长边，避免 OCR 过慢。"""
    w, h = page.get_width(), page.get_height()
    s = scale
    longest = max(w, h) * s
    if longest > OCR_MAX_SIDE:
        s = OCR_MAX_SIDE / max(w, h)
    return page.render(scale=s).to_pil(), s


def _note(on_progress, done: int, total: int, msg: str) -> None:
    """进度上报的安全包装：解析绝不能因为上报出错而失败。"""
    if not on_progress:
        return
    try:
        on_progress(done, total, msg)
    except Exception:  # noqa: BLE001
        pass


def parse_pdf(data: bytes, on_progress=None) -> tuple[list[Block], dict]:
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(data)
    n = len(pdf)
    info: dict = {"page_count": n, "engine": "pypdfium2", "scanned": False}

    _note(on_progress, 0, 0, "读取 PDF 文字层")
    pages: list[tuple[int, float, float, list[layout.Line]]] = []
    total_chars = 0
    for i in range(n):
        page = pdf[i]
        pw, ph = page.get_width(), page.get_height()
        try:
            tp = page.get_textpage()
            lines = _extract_lines(tp, ph)
        except Exception:  # noqa: BLE001
            lines = []
        total_chars += sum(len(ln.text) for ln in lines)
        pages.append((i + 1, pw, ph, lines))
        _note(on_progress, i + 1, n, f"读取文字层 {i + 1}/{n} 页")

    if n and total_chars / n < SCANNED_CHAR_THRESHOLD:
        info["scanned"] = True
        blocks = _parse_scanned_pdf(pdf, info, on_progress=on_progress)
        pdf.close()
        return blocks, info

    blocks: list[Block] = []
    order = 0
    _note(on_progress, 0, 0, "重建版面")
    for pno, pw, ph, lines in pages:
        specs = layout.build_blocks(lines, pw, pno, ph)
        new = _from_specs(specs, order)
        order += len(new)
        blocks.extend(new)

    pdf.close()
    return blocks, info


def _parse_scanned_pdf(pdf, info: dict, on_progress=None) -> list[Block]:
    """扫描件：逐页渲染 → OCR → 同一个 layout 重建版面。"""
    from . import ocr

    ok, msg = ocr.load()
    if not ok:
        raise RuntimeError(
            "这是扫描件（没有文字层），需要 OCR 才能解析，"
            f"但 OCR 引擎不可用：{msg}"
        )

    n = len(pdf)
    blocks: list[Block] = []
    order = 0
    dropped = 0
    for i in range(n):
        # OCR 是这条链路里最慢的一步，逐页上报，让用户看得见它在往前走
        _note(on_progress, i, n, f"OCR 识别第 {i + 1}/{n} 页")
        page = pdf[i]
        pw, ph = page.get_width(), page.get_height()
        pil, scale = _render_page(page, OCR_SCALE)
        lines = ocr.image_to_lines(pil, scale=scale, page_w=pw, page_h=ph)
        # 丢掉 OCR 整行识别失败的碎片，否则它们会挤掉真正的标题
        kept = [ln for ln in lines if not layout.is_garbled(ln.text)]
        dropped += len(lines) - len(kept)
        specs = layout.merge_fragments(layout.build_blocks(kept, pw, i + 1, ph))
        new = _from_specs(specs, order)
        order += len(new)
        blocks.extend(new)
        _note(on_progress, i + 1, n, f"OCR 识别 {i + 1}/{n} 页")

    info["engine"] = "pypdfium2+rapidocr"
    info["ocr"] = True
    info["ocr_dropped_lines"] = dropped
    return blocks


# ---------------------------------------------------------------- 图片

def parse_image(data: bytes, on_progress=None) -> tuple[list[Block], dict]:
    from PIL import Image

    from . import ocr

    ok, msg = ocr.load()
    if not ok:
        raise RuntimeError(f"图片需要 OCR 才能解析，但 OCR 引擎不可用：{msg}")

    img = Image.open(io.BytesIO(data))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    w, h = img.size

    _note(on_progress, 0, 1, "OCR 识别图片")
    lines = ocr.image_to_lines(img, scale=1.0, page_w=float(w), page_h=float(h))
    kept = [ln for ln in lines if not layout.is_garbled(ln.text)]
    specs = layout.merge_fragments(layout.build_blocks(kept, float(w), 1, float(h)))
    _note(on_progress, 1, 1, "OCR 识别完成")
    return _from_specs(specs, 0), {
        "page_count": 1, "engine": "rapidocr", "ocr": True,
        "image_size": [w, h], "ocr_dropped_lines": len(lines) - len(kept),
    }


# ---------------------------------------------------------------- DOCX

def parse_docx(data: bytes) -> tuple[list[Block], dict]:
    import docx

    d = docx.Document(io.BytesIO(data))
    blocks: list[Block] = []
    order = 0
    for p in d.paragraphs:
        text = (p.text or "").strip()
        if not text:
            continue
        style = (p.style.name or "").lower()
        btype, lvl = "paragraph", None
        if "title" in style:
            btype, lvl = "title", 1
        elif "heading" in style:
            btype = "heading"
            m = re.search(r"(\d+)", style)
            lvl = int(m.group(1)) if m else 2
        elif "list" in style:
            btype = "list"
        elif "quote" in style:
            btype = "quote"
        blocks.append(_mk(btype, order, text, level=lvl))
        order += 1

    for t in d.tables:
        rows = [" | ".join(c.text.strip() for c in r.cells) for r in t.rows]
        if rows:
            blocks.append(_mk("table", order, "\n".join(rows)))
            order += 1

    return blocks, {"engine": "python-docx"}


# ---------------------------------------------------------------- 入口

def parse(filename: str, data: bytes, on_progress=None) -> tuple[list[Block], dict]:
    """
    `on_progress(done, total, note)` 可选，用来说明「解析到哪儿了」。

    为什么需要：OCR 是整条链路里除等模型之外最慢的一步（秒级/页），
    没有它的话进度条会在解析阶段一直停在 0%，看起来就像卡住 ——
    而这恰恰是最容易被误判成「程序死了」的阶段。
    约定 `total = 0` 表示「分母未知，只是一句说明」，此时进度不动、只更新文案。
    """
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return parse_pdf(data, on_progress=on_progress)
    if ext == ".docx":
        return parse_docx(data)
    if ext in (".md", ".markdown"):
        return parse_markdown(data.decode("utf-8", errors="replace")), {"engine": "markdown-it"}
    if ext in (".txt", ".doc"):
        return parse_text(data.decode("utf-8", errors="replace")), {"engine": "plain-text"}
    if ext in IMAGE_EXT:
        return parse_image(data, on_progress=on_progress)
    raise ValueError(f"不支持的文件类型：{ext}")


def supported_extensions() -> list[str]:
    return sorted(SUPPORTED | IMAGE_EXT)
