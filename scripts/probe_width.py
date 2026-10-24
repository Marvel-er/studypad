"""探针：平均字符宽度 vs 字符框高度，哪个是更稳的字号代理。

avg_w = (行 x1 - 行 x0) / 字符数
  · 只跟字体的字宽有关，不受 ascender/descender 影响
  · 与字号成正比（同一字族内）
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import pypdfium2 as pdfium  # noqa: E402

from app import ocr, parsers  # noqa: E402

TEE = open(ROOT / "out" / "_probe_width.txt", "w", encoding="utf-8")


def log(*a):
    TEE.write(" ".join(str(x) for x in a) + "\n")


def p90(vals):
    v = sorted(vals)
    return v[min(len(v) - 1, int(len(v) * 0.90))] if v else 0.0


log("################ 文字层 test_text.pdf")
data = (ROOT / "samples" / "test_text.pdf").read_bytes()
pdf = pdfium.PdfDocument(data)
for pno in range(len(pdf)):
    page = pdf[pno]
    ph = page.get_height()
    tp = page.get_textpage()
    n = tp.count_chars()
    rows, buf = [], []
    for i in range(n):
        ch = tp.get_text_range(i, 1)
        if ch in ("\r", "\n"):
            if buf:
                rows.append(buf)
                buf = []
            continue
        if ch:
            buf.append((ch, tuple(tp.get_charbox(i))))
    if buf:
        rows.append(buf)

    log(f"===== page {pno + 1}")
    log(f"{'#':>3} {'len':>4} {'avgw':>7} {'hp90':>6} {'h*0.694':>7}  text")
    wlist = []
    for i, b in enumerate(rows):
        txt = "".join(c for c, _ in b).strip()
        if len(txt) < 6:
            continue
        x0 = min(bx[0] for _, bx in b)
        x1 = max(bx[2] for _, bx in b)
        avgw = (x1 - x0) / len(txt)
        hp90 = p90([abs(bx[3] - bx[1]) for _, bx in b if abs(bx[3] - bx[1]) > 0.15])
        wlist.append(avgw)
        log(f"{i:>3} {len(txt):>4} {avgw:>7.3f} {hp90:>6.2f} {hp90 / 0.694:>7.2f}  {txt[:44]!r}")

    # 只用正文行长（长度>=25）算稳定性
    body_w = [w for i, w in enumerate(wlist) if w < 0.65 * max(wlist)]
    if body_w:
        m = statistics.mean(body_w)
        log(f"    正文 avg_w: mean={m:.3f} rsd={statistics.pstdev(body_w) / m * 100:.2f}%  n={len(body_w)}")
    log("")

log("################ OCR test_scanned.pdf")
data2 = (ROOT / "samples" / "test_scanned.pdf").read_bytes()
pdf2 = pdfium.PdfDocument(data2)
for pno in range(len(pdf2)):
    page = pdf2[pno]
    pw, ph = page.get_width(), page.get_height()
    pil, scale = parsers._render_page(page, parsers.OCR_SCALE)
    lines = ocr.image_to_lines(pil, scale=scale, page_w=pw, page_h=ph)
    log(f"===== page {pno + 1}")
    log(f"{'len':>4} {'avgw':>7} {'h':>6} {'h*0.72':>7}  text")
    wlist = []
    for ln in sorted(lines, key=lambda x: (round(x.y0, 1), x.x0)):
        t = ln.text.strip()
        if len(t) < 6:
            continue
        avgw = (ln.x1 - ln.x0) / len(t)
        wlist.append(avgw)
        log(f"{len(t):>4} {avgw:>7.3f} {ln.height:>6.2f} {ln.size:>7.2f}  {t[:44]!r}")
    body_w = [w for w in wlist if w < 0.65 * max(wlist)]
    if body_w:
        m = statistics.mean(body_w)
        log(f"    正文 avg_w: mean={m:.3f} rsd={statistics.pstdev(body_w) / m * 100:.2f}%  n={len(body_w)}")
    log("")

TEE.close()
