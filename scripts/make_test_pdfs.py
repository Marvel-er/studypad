"""
生成测试用 PDF（不依赖任何第三方库，直接写 PDF 字节）。

产出：
  samples/test_text.pdf     有真实文字层的 2 页 PDF
                            第 1 页单栏（含 18pt 标题 / 13pt 小标题 / 10.5pt 正文）
                            第 2 页双栏（用于验证栏重排）
  samples/test_multipage.docx  由 make_docx 生成（可选）
"""
from pathlib import Path

ROOT = Path(r"F:\英语学习应用")
OUT = ROOT / "samples"

PAGE_W, PAGE_H = 595.0, 842.0


def esc(s: str) -> str:
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def line(x: float, y: float, text: str) -> str:
    return f"1 0 0 1 {x:.1f} {y:.1f} Tm\n({esc(text)}) Tj"


def build_content_page1() -> str:
    """单栏：大标题 + 小标题 + 正文，字号分层用于验证标题识别。"""
    ops = ["BT"]
    ops.append("/F1 18 Tf")
    ops.append(line(60, 780, "The Cost of Convenience"))
    ops.append("/F1 13 Tf")
    ops.append(line(60, 752, "Why Efficiency Is Not Enough"))
    ops.append("/F2 10.5 Tf")
    body = [
        "Economists have long assumed that productivity could be improved",
        "simply by removing friction. Yet the evidence, which has accumulated",
        "over two decades of workplace research, suggests something rather",
        "different. Organizations that strip away every unnecessary interaction",
        "frequently find that they have also stripped away the very exchanges",
        "from which innovation emerges. What matters most is not the speed of a",
        "process but the density of the connections that surround it.",
        "",
        "There is no denying that remote work has reshaped how firms measure",
        "output. Although a digital order takes seconds to place, the warehouse",
        "worker who fulfils it may be evaluated by an algorithm that never",
        "pauses. Given that these systems are designed to optimise throughput",
        "rather than for human endurance, it is hardly surprising that turnover",
        "in such roles has risen sharply.",
        "",
        "Hardly had the first automated scheduling tools been deployed when",
        "complaints began to mount. Not only did they ignore the preferences of",
        "staff, but they also made it impossible to plan a week in advance.",
        "Far from resolving the problem, the software deepened it.",
    ]
    y = 720.0
    for ln in body:
        if ln:
            ops.append(line(60, y, ln))
        y -= 17.0

    ops.append("ET")
    return "\n".join(ops)


def build_content_page2() -> str:
    """双栏：左栏读完再读右栏，用于验证栏重排。"""
    left = [
        "Policymakers should invest in",
        "prevention rather than remediation.",
        "The more transparent a system of",
        "scheduling becomes, the more likely",
        "workers are to accept it. It goes",
        "without saying that technology itself",
        "is not the enemy; the difficulty lies",
        "in deciding who gets to set its",
        "objectives, and how that choice is",
        "reviewed over time. A system that",
        "nobody can inspect is a system that",
        "nobody can improve.",
    ]
    right = [
        "Some scholars argue that the second",
        "half of this century will be defined",
        "not by the invention of new machines",
        "but by the negotiation of new limits.",
        "Only when we treat those limits as a",
        "design question rather than an",
        "afterthought can we begin to build",
        "workplaces that are both efficient",
        "and humane. That is a conclusion the",
        "evidence has supported for years,",
        "even if practice has been slow to",
        "catch up with it.",
    ]
    ops = ["BT", "/F2 10.5 Tf"]
    y = 760.0
    for ln in left:
        ops.append(line(58, y, ln))
        y -= 17.0
    y = 760.0
    for ln in right:
        ops.append(line(308, y, ln))
        y -= 17.0
    ops.append("ET")
    return "\n".join(ops)


def build_pdf(pages: list[str]) -> bytes:
    objs: list[bytes] = []

    def add(b: bytes) -> int:
        objs.append(b)
        return len(objs)          # 1-based object number

    # 预留：1=Catalog, 2=Pages, 3/5=Page, 4/6=Contents, 7/8=Fonts
    objs.append(b"")   # 1
    objs.append(b"")   # 2
    n_pages = len(pages)
    page_ids, content_ids = [], []
    for i in range(n_pages):
        content_ids.append(len(objs) + 1)
        objs.append(b"")
        page_ids.append(len(objs) + 1)
        objs.append(b"")

    font1 = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    font2 = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Times-Roman /Encoding /WinAnsiEncoding >>")

    for idx, content in enumerate(pages):
        data = content.encode("latin-1", "replace")
        objs[content_ids[idx] - 1] = (
            f"<< /Length {len(data)} >>\nstream\n".encode() + data + b"\nendstream"
        )
        objs[page_ids[idx] - 1] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W:.0f} {PAGE_H:.0f}] "
            f"/Resources << /Font << /F1 {font1} 0 R /F2 {font2} 0 R >> >> "
            f"/Contents {content_ids[idx]} 0 R >>"
        ).encode()

    objs[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objs[1] = f"<< /Type /Pages /Kids [{kids}] /Count {n_pages} >>".encode()

    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"

    xref_pos = len(out)
    n = len(objs) + 1
    out += f"xref\n0 {n}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {n} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n").encode()
    return bytes(out)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    pages = [build_content_page1(), build_content_page2()]
    pdf = build_pdf(pages)
    dst = OUT / "test_text.pdf"
    dst.write_bytes(pdf)
    print(f"[OK] {dst}  {len(pdf)} bytes  pages={len(pages)}")


if __name__ == "__main__":
    main()
