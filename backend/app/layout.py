"""
版面重建：把「文本行」聚类成「区块 + 阅读顺序」。

这是文字层 PDF 与 OCR 共用的同一套逻辑 —— 两个通道产出同样的 Line 列表，
再走同一个 build_blocks，保证「统一中间表示」不是一句空话。

输入 Line 的坐标系统一为：**左上角原点**，y 向下增长，单位点数或像素。
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Line:
    text: str
    x0: float
    y0: float          # 上边
    x1: float
    y1: float          # 下边
    size: float = 10.0  # 仅供调试：文字层=字符框高 p90，OCR=检测框高×0.72

    @property
    def height(self) -> float:
        return max(self.y1 - self.y0, 1.0)

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def width(self) -> float:
        return max(self.x1 - self.x0, 0.0)

    @property
    def units(self) -> int:
        """等效字符数：全角字符按 2 计，避免中英混排把行宽算胖。"""
        t = self.text.strip()
        if not t:
            return 1
        return max(sum(2 if ord(ch) > 0x2E80 else 1 for ch in t), 1)

    @property
    def avg_width(self) -> float:
        """
        平均字符宽度 —— 本项目的**字号代理**。

        为什么不用字符框高度：
          · 文字层：pypdfium2 的 get_charbox 是字形包围盒，
            x-height 行与 ascender 行能差 50%；
          · OCR：RapidOCR 的检测框高度被引擎统一 padding 过 ——
            同一份文档的 title 与 heading 框高只差 2.6%（16.55 vs 16.13），
            而它们的真实字号差 40%。
        行宽只跟字宽有关、与升降部无关，且**跨通道一致**：
        实测 title/正文 = 2.07（文字层） vs 2.16（OCR），
        heading/正文 = 1.43 vs 1.63 —— 都能被同一个阈值分开。
        """
        return self.width / self.units


@dataclass
class BlockSpec:
    type: str
    text: str
    page: int | None = None
    level: int | None = None
    bbox: tuple[float, float, float, float] | None = None
    meta: dict = field(default_factory=dict)


# ---------------------------------------------------------------- 栏切分

def _largest_gutter(lines: list[Line], page_w: float) -> float | None:
    """
    找一条竖直空白带，把行分成互不交叉的左右两组。
    返回切分位置 x；找不到合适的中缝则返回 None。

    两个坑（都是实测踩出来的）：

    1. **候选位置不能取「行的 x0/x1 去掉重」**。OCR 的框带小数，
       左栏最右 x1=214.04，round 成 214.0 后判断 `x1 <= g` 为假，
       这条行既不算左也不算右 → cross=1>0 → 整条中缝被否决，
       返回 None，于是双栏被当成一栏、左右两栏按 y 拼成同一行。
       改为在 [lo, hi] 区间内均匀扫描。

    2. **允许极少数行跨界**。栏宽不等、行末标点越界、
       OCR 检测框抖动都会让个别行同时压在中缝上；一刀切要求 cross==0
       太脆。这里按 cross 最小优先、左右行数均衡次优来选。
    """
    if page_w <= 0 or len(lines) < 6:
        return None
    lo, hi = page_w * 0.24, page_w * 0.76
    if hi <= lo:
        return None

    steps = 64
    best_g: float | None = None
    best_cross: int | None = None
    best_balance = 0
    for k in range(steps + 1):
        g = lo + (hi - lo) * k / steps
        left = sum(1 for ln in lines if ln.x1 <= g)
        right = sum(1 for ln in lines if ln.x0 >= g)
        if left < 3 or right < 3:
            continue
        cross = len(lines) - left - right
        balance = min(left, right)
        if (best_cross is None or cross < best_cross
                or (cross == best_cross and balance > best_balance)):
            best_g, best_cross, best_balance = g, cross, balance

    if best_g is None or best_cross is None:
        return None
    if best_cross > max(1, int(len(lines) * 0.10)):
        return None
    return best_g


def split_columns(lines: list[Line], page_w: float, depth: int = 0) -> list[list[Line]]:
    """递归切栏，返回按阅读顺序排列的若干栏（每栏内部尚未排序）。"""
    if depth >= 2 or len(lines) < 6:
        return [lines]
    g = _largest_gutter(lines, page_w)
    if g is None:
        return [lines]
    # 按行中心归属，保证跨界行不会丢失
    left = [ln for ln in lines if ln.cx <= g]
    right = [ln for ln in lines if ln.cx > g]
    if len(left) < 3 or len(right) < 3:
        return [lines]
    return split_columns(left, page_w, depth + 1) + split_columns(right, page_w, depth + 1)


# ---------------------------------------------------------------- 行 → 块

_HYPHEN_END = re.compile(r"[A-Za-z]-$")

_VOWELS = frozenset("aeiouyAEIOUY")
_WORD_RE = re.compile(r"[A-Za-z]+")


def is_garbled(text: str) -> bool:
    """
    OCR 失败行的启发式判定。

    RapidOCR 偶尔把一整行识别成碎片（实测：'difft n d ty sin tion'，
    原文是 'different. Organizations that strip away every unnecessary…'）。
    这类行字符数少、检测框却仍撑满整行宽，avg_width 被抬到正文的 2.9 倍，
    于是抢了 title 的位置。

    判据用「无元音词占比」：英文里无元音的真词几乎都带 y
    （by / my / why / try），所以无元音短词成串出现就是识别失败，
    而不是生僻词。真实英文行的这个比例是 0。
    """
    words = _WORD_RE.findall(text)
    if len(words) < 4:
        return False
    novowel = sum(1 for w in words if not (_VOWELS & set(w)))
    return novowel >= 2 and novowel / len(words) >= 0.30


def _join_lines(chunk: list[Line]) -> str:
    """把同一段落的多行拼成一句，处理行尾连字符断词。"""
    out = ""
    for i, ln in enumerate(chunk):
        t = ln.text.strip()
        if not t:
            continue
        if out and _HYPHEN_END.search(out) and t[:1].islower():
            out = out[:-1] + t                 # metho- + dology → methodology
        elif out:
            out += " " + t
        else:
            out = t
    return re.sub(r"\s+", " ", out).strip()


def _body_size(lines: list[Line]) -> float:
    """
    正文基准字号：按字符数加权的 avg_width **中位数**。

    中位数而不是众数 —— avg_width 是连续量，众数会退化；
    也不剔除标题行 —— 标题通常只占少数，中位数天然抗离群，
    比「先猜哪些是标题再统计」稳得多。
    """
    pairs = [(ln.avg_width, ln.units) for ln in lines if ln.text.strip()]
    pairs = [(w, n) for w, n in pairs if w > 0]
    if not pairs:
        return 10.0
    pairs.sort(key=lambda p: p[0])
    total = sum(n for _, n in pairs)
    acc = 0
    for w, n in pairs:
        acc += n
        if acc * 2 >= total:
            return w
    return pairs[-1][0]


def _classify(size: float, body: float, text: str) -> tuple[str, int | None]:
    """
    按「字号相对正文的倍数」定标题层级。size 传的是 avg_width。

    阈值 1.75 是两条通道的实测交集：
        文字层 title/正文 2.07 · heading/正文 1.43
        OCR    title/正文 2.16 · heading/正文 1.63
    四个比值全部落在 1.75 的两侧，最小余量 0.12。
    """
    if body <= 0:
        return "paragraph", None
    ratio = size / body
    if ratio >= 1.75 and len(text) < 120:
        return "title", 1
    if ratio >= 1.15 and len(text) < 140:
        return "heading", 2
    if re.match(r"^\s*([-•*·]|\d+[.)])\s+", text):
        return "list", None
    return "paragraph", None


def build_blocks(lines: list[Line], page_w: float, page_no: int | None = None,
                 page_h: float | None = None) -> list[BlockSpec]:
    """行列表 → 区块列表（含阅读顺序、标题层级、bbox）。"""
    if not lines:
        return []
    lines = [ln for ln in lines if ln.text.strip()]
    if not lines:
        return []

    body = _body_size(lines)
    blocks: list[BlockSpec] = []

    for column in split_columns(lines, page_w):
        col = sorted(column, key=lambda ln: (round(ln.y0, 1), ln.x0))
        if not col:
            continue

        # 本栏的行距基准：段间距通常 ≥ 1 行距，用中位行距来区分「换行」与「换段」
        pitches = [b.y0 - a.y0 for a, b in zip(col, col[1:]) if b.y0 - a.y0 > 0.5]
        pitch = sorted(pitches)[len(pitches) // 2] if pitches else 0.0

        chunk: list[Line] = [col[0]]

        def flush() -> None:
            if not chunk:
                return
            text = _join_lines(chunk)
            if not text:
                chunk.clear()
                return
            avg_size = sum(c.avg_width for c in chunk) / len(chunk)
            btype, lvl = _classify(avg_size, body, text)
            x0 = min(c.x0 for c in chunk)
            x1 = max(c.x1 for c in chunk)
            y0 = min(c.y0 for c in chunk)
            y1 = max(c.y1 for c in chunk)
            blocks.append(BlockSpec(
                type=btype, text=text, page=page_no, level=lvl,
                bbox=(round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)),
                meta={"avg_width": round(avg_size, 3)},
            ))
            chunk.clear()

        for prev, cur in zip(col, col[1:]):
            gap = cur.y0 - prev.y1
            taller = max(prev.height, cur.height)
            size_shift = abs(cur.avg_width - prev.avg_width) / max(body, 1e-6)
            indent_shift = abs(cur.x0 - prev.x0)

            # 换行 vs 换段：正常行距内合并，明显超出（段间距）就断开
            gap_limit = max(taller * 0.85, pitch * 0.62) if pitch else taller * 0.85
            cur_is_head = _classify(cur.avg_width, body, cur.text)[0] in ("title", "heading")
            prev_is_head = _classify(prev.avg_width, body, prev.text)[0] in ("title", "heading")

            same_block = (
                gap <= gap_limit
                and size_shift <= 0.18
                and indent_shift <= max(body * 2.2, 18)
                and not cur_is_head
                and not prev_is_head
            )
            if same_block:
                chunk.append(cur)
            else:
                flush()
                chunk.append(cur)
        flush()

    # 归一化 bbox 到 0~1
    if page_w and page_h:
        for b in blocks:
            if b.bbox:
                x0, y0, x1, y1 = b.bbox
                b.bbox = (round(x0 / page_w, 4), round(y0 / page_h, 4),
                          round(x1 / page_w, 4), round(y1 / page_h, 4))
    return blocks


def merge_fragments(blocks: list[BlockSpec]) -> list[BlockSpec]:
    """把 OCR 常见的碎片行合并：连续短行若字号一致且属于同类，并成一段。"""
    if not blocks:
        return blocks
    out: list[BlockSpec] = []
    for b in blocks:
        if (out and b.type == "paragraph" and out[-1].type == "paragraph"
                and b.page == out[-1].page
                and not out[-1].text.endswith((".", "!", "?", ":", ";"))
                and len(out[-1].text) < 90):
            out[-1].text = (out[-1].text + " " + b.text).strip()
        else:
            out.append(b)
    return out
