"""探针：OCR 检测框高度能否区分标题与正文。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import pypdfium2 as pdfium  # noqa: E402

from app import ocr, parsers  # noqa: E402

TEE = open(ROOT / "out" / "_probe_ocr.txt", "w", encoding="utf-8")


def log(*a):
    TEE.write(" ".join(str(x) for x in a) + "\n")


data = (ROOT / "samples" / "test_scanned.pdf").read_bytes()
pdf = pdfium.PdfDocument(data)
for pno in range(len(pdf)):
    page = pdf[pno]
    pw, ph = page.get_width(), page.get_height()
    pil, scale = parsers._render_page(page, parsers.OCR_SCALE)
    lines = ocr.image_to_lines(pil, scale=scale, page_w=pw, page_h=ph)
    log(f"===== page {pno + 1}  page={pw:.1f}x{ph:.1f}  scale={scale:.3f}  n={len(lines)}")
    for ln in sorted(lines, key=lambda x: (round(x.y0, 1), x.x0)):
        log(f"  x0={ln.x0:7.2f} x1={ln.x1:7.2f} y0={ln.y0:7.2f} "
            f"h={ln.height:6.2f} size={ln.size:5.2f} ratio_h={ln.height / (ln.size / 0.72):5.2f}"
            f" | {ln.text!r}")
    log("")

TEE.close()
