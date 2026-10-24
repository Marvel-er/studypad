"""
分页留白检测：把长文手账导出 PDF，逐页量「正文结束后还剩多少空白」。

为什么必须查 PDF：用户的反馈是「这一页是翻译失败的一页，可能留白分页了」。
留白分页不是 HTML 层面的问题，是**打印分页**的产物：
`.block{break-inside:avoid}` 会把一个整块推到下一页，前页尾部就空出一大片。
所以只有在真分页（PDF）里量，才验得到。

判据（每页）：
  · 内容底边 last_y / 页高  → 内容只占了上面多少
  · 最长连续空白 max_blank  → 尾部空白高度
「留白页」定义为：**非末页**里，内容底边不到页高的 60%。
（末页天然填不满，必须豁免 —— 否则每篇文档都会被判成有留白页。）

用法：python scripts/run_selftest.py scripts/probe_pagination.py out/_pagination.txt
前置：先跑 make_long_article.py + make_trans_fail_demo.py long_article.md，再用 Chrome 导出 PDF
      （本脚本自己调 Chrome，无需手动）
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / "out" / "visual"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
DARK = 150


def to_pdf(html: Path) -> Path:
    pdf = html.with_suffix(".pdf")
    if pdf.exists():
        pdf.unlink()
    subprocess.run(
        [str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
         "--no-pdf-header-footer", f"--print-to-pdf={pdf}", html.as_uri()],
        check=True, capture_output=True, timeout=180,
    )
    return pdf


def page_metrics(page) -> dict:
    img = page.render(scale=1.5).to_pil().convert("RGB")
    w, h = img.size
    px = img.load()
    x0, x1 = int(w * 0.08), int(w * 0.94)
    rows = []
    for y in range(h):
        rows.append(any(px[x, y][0] < DARK and px[x, y][1] < DARK and px[x, y][2] < DARK
                        for x in range(x0, x1, 2)))
    last = max((y for y, d in enumerate(rows) if d), default=0)
    best = cur = 0
    for d in rows:
        cur = 0 if d else cur + 1
        best = max(best, cur)
    text = page.get_textpage().get_text_range() or ""
    return {"w": w, "h": h, "last": last, "blank": best,
            "chars": len(text.strip()), "tail": h - last}


def analyse(pdf: Path) -> list[dict]:
    doc = pdfium.PdfDocument(str(pdf))
    try:
        return [page_metrics(doc[i]) for i in range(len(doc))]
    finally:
        doc.close()


def bad_pages(ms: list[dict]) -> list[int]:
    """非末页里正文没填到 60% 页高的页。"""
    last_i = len(ms)
    return [i + 1 for i, m in enumerate(ms)
            if i + 1 < last_i and m["last"] / m["h"] < 0.60]


print("=" * 96)
print("分页留白检测（真 PDF 分页）")
print("=" * 96)

results: dict[str, list[dict]] = {}
for tag in ("long_article_before", "long_article_after"):
    html = V / f"{tag}.html"
    if not html.exists():
        print(f"  {tag}.html 不存在，先跑 make_trans_fail_demo.py long_article.md")
        sys.exit(2)
    pdf = to_pdf(html)
    ms = analyse(pdf)
    results[tag] = ms
    print(f"--- {tag}.pdf  {len(ms)} 页 ---")
    last_i = len(ms)
    for i, m in enumerate(ms, 1):
        pct = m["last"] / m["h"] * 100
        flag = ""
        if i < last_i and pct < 60:
            flag = "   <== 留白页（非末页，正文没填到 60%）"
        elif i == last_i:
            flag = "   （末页，填不满是正常的）"
        print(f"  p{i}: {m['w']}x{m['h']}px  内容到 y={m['last']:>4}"
              f"（{pct:>5.1f}% 页高）最长空白 {m['blank']:>4}px"
              f"（{m['blank'] / m['h'] * 100:>4.1f}%）尾部空白 {m['tail']:>4}px"
              f" 文字 {m['chars']:>5} 字{flag}")
    print(f"  → 留白页 {len(bad_pages(ms))}/{len(ms)} 页（末页已豁免）；"
          f"最大尾部空白 {max(m['tail'] for m in ms)}px")


b, a = results["long_article_before"], results["long_article_after"]
print()
print("断言：")
ok = True
checks = [
    (len(b) >= 2 and len(a) >= 2, f"两版都真的跨页了（{len(b)} 页 / {len(a)} 页）"),
    (len(bad_pages(b)) > 0,
     f"复现：修复前存在留白页（第 {'、'.join(map(str, bad_pages(b)))} 页）"),
    (len(bad_pages(a)) == 0, "修复后：没有任何一页是留白页"),
    (max(m["tail"] for m in a) < max(m["tail"] for m in b),
     f"最大尾部空白变短：{max(m['tail'] for m in b)}px → {max(m['tail'] for m in a)}px"),
]
for cond, label in checks:
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    ok = ok and cond

sys.exit(0 if ok else 1)
