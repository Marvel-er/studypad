"""
用 test_text.pdf 生成 OCR 测试样本：
  samples/test_scan.png      第 1 页的位图（模拟拍照/截图）
  samples/test_scanned.pdf   两页纯图片 PDF（模拟扫描件，无文字层）
"""
from pathlib import Path

ROOT = Path(r"F:\英语学习应用")
OUT = ROOT / "samples"

SCALE = 2.5           # 与 parsers.OCR_SCALE 保持一致
DPI = int(SCALE * 72)  # 让图片型 PDF 的页面尺寸回到原始点数


def main() -> None:
    import pypdfium2 as pdfium

    src = OUT / "test_text.pdf"
    pdf = pdfium.PdfDocument(src.read_bytes())

    images = []
    for i in range(len(pdf)):
        page = pdf[i]
        images.append(page.render(scale=SCALE).to_pil())

    png = OUT / "test_scan.png"
    images[0].save(png)

    scanned = OUT / "test_scanned.pdf"
    images[0].save(scanned, "PDF", save_all=True, append_images=images[1:],
                   resolution=DPI)

    pdf.close()
    print(f"[OK] {png}  {png.stat().st_size} bytes  size={images[0].size}")
    print(f"[OK] {scanned}  {scanned.stat().st_size} bytes  pages={len(images)}")


if __name__ == "__main__":
    main()
