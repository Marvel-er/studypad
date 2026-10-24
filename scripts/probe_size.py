"""探针：为「行字号代理」找一个稳定的统计量。

pypdfium2 的 get_charbox 返回**字形包围盒**（不是字号），
所以众数会被 x-height 字母带偏。这里对比几种统计量的行间稳定性。
"""
from __future__ import annotations

import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import pypdfium2 as pdfium  # noqa: E402

TEE = open(ROOT / "out" / "_probe_size.txt", "w", encoding="utf-8")


def log(*a):
    TEE.write(" ".join(str(x) for x in a) + "\n")


def stats_of(buf):
    hs = sorted(round(abs(b[3] - b[1]), 2) for _, b in buf if abs(b[3] - b[1]) > 0.15)
    if not hs:
        return None
    n = len(hs)

    def q(p):
        return hs[min(n - 1, int(n * p))]

    mode = Counter(hs).most_common(1)[0][0]
    return {
        "n": n, "max": hs[-1], "p90": q(0.90), "p75": q(0.75),
        "med": statistics.median(hs), "mode": mode,
    }


def rows_of(page):
    ph = page.get_height()
    tp = page.get_textpage()
    n = tp.count_chars()
    out, buf = [], []
    for i in range(n):
        ch = tp.get_text_range(i, 1)
        if ch in ("\r", "\n"):
            if buf:
                out.append(buf)
                buf = []
            continue
        if ch:
            buf.append((ch, tuple(tp.get_charbox(i))))
    if buf:
        out.append(buf)
    return out


data = (ROOT / "samples" / "test_text.pdf").read_bytes()
pdf = pdfium.PdfDocument(data)

for pno in (0, 1):
    log(f"===== page {pno + 1}")
    log(f"{'#':>3} {'n':>4} {'max':>6} {'p90':>6} {'p75':>6} {'med':>6} {'mode':>6}  text")
    for i, buf in enumerate(rows_of(pdf[pno])):
        s = stats_of(buf)
        if not s:
            continue
        txt = "".join(c for c, _ in buf)
        log(f"{i:>3} {s['n']:>4} {s['max']:>6.2f} {s['p90']:>6.2f} {s['p75']:>6.2f} "
            f"{s['med']:>6.2f} {s['mode']:>6.2f}  {txt[:56]!r}")
    log("")

# 稳定性：正文行的各统计量的相对标准差
log("===== 正文行稳定性（相对标准差，越小越稳）")
for pno in (0, 1):
    rows = [stats_of(b) for b in rows_of(pdf[pno])]
    rows = [r for r in rows if r and r["n"] >= 12]
    log(f"page {pno + 1}: {len(rows)} 行")
    for k in ("max", "p90", "p75", "med", "mode"):
        vals = [r[k] for r in rows]
        mean = statistics.mean(vals)
        sd = statistics.pstdev(vals)
        log(f"   {k:>5}: mean={mean:6.2f} sd={sd:5.3f} rsd={sd / mean * 100:5.2f}%")

TEE.close()
