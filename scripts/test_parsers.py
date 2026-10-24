"""
解析器验证：文字层 PDF（含双栏）→ pypdfium2；扫描件 / 图片 → OCR。
"""
import sys
from pathlib import Path

ROOT = Path(r"F:\英语学习应用")
sys.path.insert(0, str(ROOT / "backend"))

from app import ocr, parsers  # noqa: E402

out = []


def show(tag: str, path: Path) -> None:
    data = path.read_bytes()
    try:
        blocks, info = parsers.parse(path.name, data)
    except Exception as e:  # noqa: BLE001
        out.append(f"===== {tag} :: {path.name} =====\n  ERROR: {type(e).__name__}: {e}")
        return
    out.append(f"===== {tag} :: {path.name} ({len(data)} bytes) =====")
    out.append(f"  info = {info}")
    out.append(f"  blocks = {len(blocks)}")
    for b in blocks:
        head = f"  [{b.order:02d}] {b.type:<9} p{b.page} lv={b.level} bbox={b.bbox}"
        out.append(head)
        out.append(f"       {b.text[:150]}")


info = ocr.engine_info()
out.append(f"OCR engine: {info}")
out.append("")

show("文字层PDF", ROOT / "samples" / "test_text.pdf")
out.append("")
show("扫描件PDF", ROOT / "samples" / "test_scanned.pdf")
out.append("")
show("图片", ROOT / "samples" / "test_scan.png")
out.append("")
show("Markdown", ROOT / "samples" / "sample_article.md")

(ROOT / "out" / "_parsers.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out[:12]))
