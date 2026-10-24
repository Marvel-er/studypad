"""
对照两张手账截图的像素：译文带的条数 / 带内有没有字 / 空带总高度。

这一项验的是「HTML 断言验不到的东西」：断言能保证产物里没有空框，
但保证不了**用户肉眼看到的绿框里真的有字**。所以必须真渲染、真量像素。

**踩过的坑（第一版探针为什么会误报）**：
一开始按 `.tr-zh` 的底色 (238,242,234) 找绿框，容差 6。
但纸面背景每 32px 有一条横线，它会**透过半透明绿底**：叠出来的颜色是
(220,228,228)，与底色差 18/14/6 —— 直接判定为「不是绿框」。
于是一条 40px 高的译文带被横线切成「28px 有字 + 12px 没字」两片，
每次都多报 5~6 条假空带（而且 before/after 位置完全相同，纯属纹理伪影）。
**正解**：认 `.tr-zh` 那条**不透明**的青色左边框 `#9dc7bd = (157,199,189)`。
它是实色、只有译文框才有；`.block.tr-sent` 的半透明同色边框叠出来是
(200,222,213)（差 43），不会被误认。

另一件必须记住的事：**占位框里是有字的**（「（本句未译出）」本身是文字），
所以「文字像素为 0」这一条**区分不了**新旧实现 —— 能区分的是
「译文带总条数」与「空带总高」，前者由 `make_trans_fail_demo.py` 断言，
后者由 `probe_pagination.py` 在真 PDF 分页里量。

用法（由 run_all.py 的视觉链自动调用）：
    python scripts/run_selftest.py scripts/probe_pixels.py out/_pixels.txt [stem]
默认 stem = sample_article，对应 out/visual/<stem>_{before,after}.html
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / "out" / "visual"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

TEAL = (157, 199, 189)      # .tr-zh 的 border-left（**绿色译文框**），不透明
GOLD = (232, 201, 121)      # .tr-zh.partial 的 border-left（**黄色占位框**）
TOL = 10
DARK = 140                  # 深色像素阈值（字）
X_SCAN = (140, 240)         # 扫左边框的横向范围
X_TEXT = (170, 960)         # 数文字像素的横向范围
WINDOW_H = 12000


def shoot(html: Path) -> Path:
    png = html.with_suffix(".png")
    subprocess.run(
        [str(CHROME), "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--no-sandbox", f"--screenshot={png}",
         f"--window-size=1100,{WINDOW_H}", html.as_uri()],
        check=True, capture_output=True, timeout=180,
    )
    return png


def _border_rows(px, w: int, h: int, color: tuple[int, int, int]) -> list[int | None]:
    """逐行找指定颜色的左边框，返回该行边框的 x（没找到为 None）。"""
    out: list[int | None] = []
    for y in range(h):
        found, run = None, 0
        for x in range(X_SCAN[0], X_SCAN[1]):
            r, g, b = px[x, y]
            if abs(r - color[0]) <= TOL and abs(g - color[1]) <= TOL and abs(b - color[2]) <= TOL:
                run += 1
                if run >= 2:            # 连续 2px 才算边框，避开抗锯齿噪点
                    found = x - run + 1
                    break
            else:
                run = 0
        out.append(found)
    return out


def _text_pixels(px, y0: int, y1: int) -> int:
    n = 0
    for y in range(y0, y1):
        for x in range(X_TEXT[0], X_TEXT[1]):
            r, g, b = px[x, y]
            if r < DARK and g < DARK and b < DARK:
                n += 1
    return n


def _bands(rows: list[int | None], h: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    start = None
    for y, v in enumerate(rows):
        if v is not None and start is None:
            start = y
        elif v is None and start is not None:
            if y - start >= 6:
                out.append((start, y))
            start = None
    if start is not None:
        out.append((start, h))
    return out


def analyse(path: Path) -> dict:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()

    res: dict = {"size": im.size}
    for name, color in (("green", TEAL), ("gold", GOLD)):
        bs = _bands(_border_rows(px, w, h, color), h)
        detail = [(y0, y1, y1 - y0, _text_pixels(px, y0, y1)) for y0, y1 in bs]
        res[name] = {
            "bands": len(bs),
            "empty": sum(1 for *_x, tp in detail if tp == 0),
            "detail": detail,
        }
    return res


STEM = sys.argv[1] if len(sys.argv) > 1 else "sample_article"
hb_html = V / f"{STEM}_before.html"
ha_html = V / f"{STEM}_after.html"

out = []
out.append("=" * 96)
out.append(f"像素对照 · {STEM}：译文带里到底有没有字（认不透明青色左边框 #9dc7bd）")
out.append("=" * 96)

if not CHROME.exists():
    out.append(f"  跳过：找不到 Chrome（{CHROME}）")
    print("\n".join(out))
    sys.exit(0)
if not (hb_html.exists() and ha_html.exists()):
    out.append(f"  跳过：缺少 {hb_html.name} / {ha_html.name}（先跑 make_trans_fail_demo.py）")
    print("\n".join(out))
    sys.exit(0)

a = analyse(shoot(hb_html))
b = analyse(shoot(ha_html))
out = []
out.append("=" * 96)
out.append(f"像素对照 · {STEM}：绿框（真译文）与黄框（占位）各多少")
out.append("=" * 96)
for name, s in (("修复前", a), ("修复后", b)):
    out.append(f"--- {name} {s['size']} ---")
    for key, label in (("green", "绿框 .tr-zh（真译文）"),
                       ("gold", "黄框 .tr-zh.partial（「（本句未译出）」占位）")):
        d = s[key]
        out.append(f"  {label}：{d['bands']} 条；带内无字的 {d['empty']} 条")
        for y0, y1, hh, tp in d["detail"]:
            flag = "   <== 空带" if tp == 0 else ""
            out.append(f"      y {y0:>4}-{y1:<4} 高 {hh:>3}px  文字像素 {tp:>5}{flag}")

out.append("")
out.append("断言：")
ok = True
checks = [
    (a["gold"]["bands"] > 0,
     f"复现：修复前有 {a['gold']['bands']} 条黄色占位框（旧实现逐句产出）"),
    (b["gold"]["bands"] == 0, "修复后：黄色占位框 0 条"),
    (b["green"]["bands"] == a["green"]["bands"],
     f"真译文一条不少：绿框 {a['green']['bands']} → {b['green']['bands']}"),
    (b["green"]["empty"] == 0, "修复后：绿框里没有一条是空的"),
    (a["green"]["empty"] == 0,
     "修复前绿框里也都有字（⇒ 用户看到的「绿框无字」不是占位框造成的，"
     "而是译文内容本身是零宽/空白字符 —— 那条路径已由 _visible + 解析层清理修掉）"),
]
for cond, label in checks:
    out.append(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    ok = ok and cond

print("\n".join(out))
sys.exit(0 if ok else 1)
