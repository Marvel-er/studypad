"""调试：双栏页的行明细（文字层 vs OCR）。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from app import layout, ocr, parsers  # noqa: E402

OUT = []
TEE = open(ROOT / "out" / "_dbg2.txt", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    TEE.write(s + "\n")
    TEE.flush()


import pypdfium2 as pdfium  # noqa: E402


def dump_lines(tag, lines, page_w):
    log(f"--- {tag}: {len(lines)} lines, page_w={page_w:.1f}")
    g = layout._largest_gutter(lines, page_w)
    log(f"    gutter = {g}")
    for i, ln in enumerate(lines):
        log(f"  [{i:02d}] x0={ln.x0:7.2f} x1={ln.x1:7.2f} y0={ln.y0:7.2f} "
            f"y1={ln.y1:7.2f} h={ln.height:6.2f} size={ln.size:5.2f} | {ln.text[:70]!r}")
    # 模拟 build_blocks 的逐行判定
    body = layout._body_size(lines)
    log(f"    body_size = {body}")
    cols = layout.split_columns(lines, page_w)
    log(f"    columns = {[len(c) for c in cols]}")
    for ci, column in enumerate(cols):
        col = sorted(column, key=lambda x: (round(x.y0, 1), x.x0))
        pitches = [b.y0 - a.y0 for a, b in zip(col, col[1:]) if b.y0 - a.y0 > 0.5]
        pitch = sorted(pitches)[len(pitches) // 2] if pitches else 0.0
        log(f"    col{ci} pitch={pitch:.2f} n={len(col)}")
        for prev, cur in zip(col, col[1:]):
            gap = cur.y0 - prev.y1
            taller = max(prev.height, cur.height)
            shift = abs(cur.size - prev.size) / max(body, 1e-6)
            cls_c = layout._classify(cur.size, body, cur.text)[0]
            cls_p = layout._classify(prev.size, body, prev.text)[0]
            log(f"      gap={gap:6.2f} taller*0.85={taller*0.85:6.2f} "
                f"pitch*0.62={pitch*0.62:6.2f} size_shift={shift:5.3f} "
                f"prev={cls_p:9s} cur={cls_c:9s} | {cur.text[:36]!r}")


# ---------- 1. 文字层 PDF page 2
data = (ROOT / "samples" / "test_text.pdf").read_bytes()
pdf = pdfium.PdfDocument(data)
log(f"### test_text.pdf pages={len(pdf)}")
page = pdf[1]
pw, ph = page.get_width(), page.get_height()
tp = page.get_textpage()
lines = parsers._extract_lines(tp, ph)
dump_lines("TEXT-PDF p2", lines, pw)

# ---------- 2. OCR 扫描件 page 2
log("")
data2 = (ROOT / "samples" / "test_scanned.pdf").read_bytes()
pdf2 = pdfium.PdfDocument(data2)
log(f"### test_scanned.pdf pages={len(pdf2)}")
p2 = pdf2[1]
pw2, ph2 = p2.get_width(), p2.get_height()
pil, scale = parsers._render_page(p2, parsers.OCR_SCALE)
log(f"    render scale={scale:.3f} img={pil.size}")
ok, msg = ocr.load()
log(f"    ocr load ok={ok} msg={msg}")
olines = ocr.image_to_lines(pil, scale=scale, page_w=pw2, page_h=ph2)
dump_lines("OCR p2", olines, pw2)

TEE.close()
