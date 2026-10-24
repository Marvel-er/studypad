"""真题语料的加载与清洗。

一份试卷 PDF 抽出的纯文本里混着大量非正文内容（指令行、题干、选项、页码、
中文解析、盗版水印）。统计之前必须先剔掉，否则词频会被严重污染——
原项目参考的 YSMull/words-statistics 最大的问题就是没剔 ``Directions`` 指令行。

本模块把「清洗」分成两个层次，并用 ``mode`` 显式区分：

``blocks``
    先按连续可用行切块，丢掉 <3 行或 <40 词的碎块，再在块内丢弃
    ``Directions`` 及其续行。原 ``vocab_stats.py`` 走这条。
    块级筛选能滤掉散落的残留行，口径更干净。

``flat``
    逐行过滤，不做块级筛选。原 ``diagnose_coverage.py`` / ``diagnose_AB.py``
    / ``diagnose_reading.py`` / ``make_A_list.py`` 走这条。

两条路径产出的语料**并不相同**（``flat`` 会多留下一些短碎块）。上游项目里
这个差异是隐式的：同一份报告里不同脚本的数字其实来自略微不同的语料。
这里把它参数化，是为了让差异可见、可测、可选——而不是藏在一个循环里。
``python -m npee_vocab compare-modes`` 可以量化两者的差距。
"""

from __future__ import annotations

import pathlib
import re
from typing import Iterator, Literal

Mode = Literal["blocks", "flat"]

# 盗版水印 / 转载标记
WATERMARK = ("mbadic", "考研资料", "公众号", "冰柠")

DIRECTIONS = re.compile(r"Directions", re.IGNORECASE)

# 试卷结构行：出现即判定为非正文
STRUCT_LINE = re.compile(
    r"^\s*(Section\s+[IVX]+|Part\s+[ABC]\b|Text\s+\d|"
    r"\d{1,2}\s*[\.\、\)]\s|\[[A-D]\]|Directions|"
    r"[-—]\s*\d+\s*[-—]|\d{1,3}\s*$)",
    re.IGNORECASE,
)

STRUCT_WORDS = {"sheet", "points", "marked", "mark", "numbered", "blank", "blanks"}

# 词形：至少 2 个字母
TOKEN_RE = re.compile(r"^[A-Za-z]{2,}$")

# 合订本年份：试卷正文在第几行截止。
# 2022 年那份 PDF 是「试卷 + 34 页中文解析」合订本（48 页、19.7% 汉字），
# 第 678 行是试卷末、679 行是第二份中文标题「试题解析」。
TRUNCATE: dict[str, int] = {"2022": 678}

# 判定为「中文行」的汉字占比阈值
HAN_RATIO = 0.15

# 块级筛选阈值
MIN_BLOCK_LINES = 3
MIN_BLOCK_WORDS = 40

# Directions 指令块被丢弃的**总行数**（含 Directions 行本身）
DIRECTIONS_SKIP = 3


def year_files(raw_dir: pathlib.Path) -> list[str]:
    """列出 ``raw/`` 下所有年份，升序。"""
    return sorted(p.stem for p in pathlib.Path(raw_dir).glob("*.txt"))


def get_lines(raw_dir: pathlib.Path, year: str) -> list[str]:
    """读取某年的抽取文本，按需截断合订本。"""
    text = (pathlib.Path(raw_dir) / f"{year}.txt").read_text(
        encoding="utf-8", errors="replace"
    )
    lines = text.splitlines()
    if year in TRUNCATE:
        return lines[: TRUNCATE[year]]
    return lines


def is_usable(line: str) -> bool:
    """这一行像正文散文吗？"""
    s = line.strip()
    if not s or any(w in s for w in WATERMARK) or STRUCT_LINE.match(s):
        return False
    han = len(re.findall(r"[\u4e00-\u9fff]", s))
    if han and han / max(len(s), 1) > HAN_RATIO:
        return False
    words = re.findall(r"[A-Za-z]{2,}", s)
    if len(words) < 4:
        return False
    if len(words) <= 12 and ({w.lower() for w in words} & STRUCT_WORDS):
        return False
    return True


def prose_blocks(lines: list[str]) -> list[list[str]]:
    """把可用行切成连续块，只保留足够长的块。

    正文是长连续散文，散落的短行基本是题干/选项/残留。
    """
    blocks: list[list[str]] = []
    cur: list[str] = []
    for line in lines:
        if is_usable(line):
            cur.append(line)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    return [
        b
        for b in blocks
        if len(b) >= MIN_BLOCK_LINES
        and sum(len(re.findall(r"[A-Za-z]{2,}", line)) for line in b) >= MIN_BLOCK_WORDS
    ]


def strip_directions(block: list[str]) -> list[str]:
    """块内残留的 Directions 行及其后 **2** 行（指令续行）一并丢弃。

    注意是连同 Directions 行**共 3 行**被丢弃，不是「其后 3 行」——
    ``DIRECTIONS_SKIP = 3`` 数的是被丢的总行数，而计数器在遇到
    Directions 行的当次迭代就已经减 1（该行本身也被 continue 掉）。
    上游脚本的注释写的是「其后 3 行」，与实际行为不符；这里按实际行为说明。
    """
    out: list[str] = []
    skip = 0
    for line in block:
        if DIRECTIONS.search(line):
            skip = DIRECTIONS_SKIP
        if skip > 0:
            skip -= 1
            continue
        out.append(line)
    return out


def _flat_kept(lines: list[str]) -> Iterator[str]:
    """逐行过滤，Directions 行及其续行丢弃（共 3 行）。"""
    skip = 0
    for line in lines:
        if not is_usable(line):
            continue
        if DIRECTIONS.search(line):
            skip = DIRECTIONS_SKIP
        if skip > 0:
            skip -= 1
            continue
        yield line


def kept_lines(raw_dir: pathlib.Path, year: str, mode: Mode = "blocks") -> list[str]:
    """某一年保留下来的正文行。"""
    lines = get_lines(raw_dir, year)
    if mode == "flat":
        return list(_flat_kept(lines))
    if mode == "blocks":
        kept: list[str] = []
        for block in prose_blocks(lines):
            kept.extend(strip_directions(block))
        return kept
    raise ValueError(f"未知 mode: {mode!r}（可选 'blocks' / 'flat'）")


def prose_text(raw_dir: pathlib.Path, year: str, mode: Mode = "blocks") -> str:
    """某一年保留正文拼成的单行文本（空白已归一）。"""
    return re.sub(r"\s+", " ", "\n".join(kept_lines(raw_dir, year, mode)))


def surface_tokens(text: str) -> list[str]:
    """切词：只保留 2 个字母以上的词形，转小写，**不做**词形还原。

    ``make_A_list.py`` / ``diagnose_AB.py`` 用的是这个口径——
    它们要区分 argue/argues/argued 的不同识别难度。
    """
    return [w.lower() for w in re.split(r"[^A-Za-z]+", text) if TOKEN_RE.match(w)]


def load_corpus(raw_dir: pathlib.Path, mode: Mode = "blocks") -> dict[str, list[str]]:
    """按年份载入正文行。

    返回 ``{年份: [行, ...]}``。词形还原是单独一步（见 ``lemmatize.py``），
    因为还原需要 nltk 数据、也慢得多，不该和清洗绑在一起。
    """
    raw_dir = pathlib.Path(raw_dir)
    return {y: kept_lines(raw_dir, y, mode) for y in year_files(raw_dir)}
