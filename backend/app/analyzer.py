"""
语言分析层：分句 → 词元分类 → 难度打分 → 候选筛选。

本地完成、零 API 成本。只有 annotation_value 高的句子才会被送去 LLM。
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from . import wordlist
from .lemmatize import CONTRACTION_STOP, is_content_word, lemma_candidates, tokenize
from .levels import get as get_level, known_mask, lower_mask, own_mask
from .wordlist import popcount

_SENT_END = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")
_ABBR = re.compile(r"\b(?:Mr|Mrs|Ms|Dr|Prof|St|Fig|No|vs|etc|e\.g|i\.e|U\.S|U\.K|approx)\.$", re.I)

# URL / 邮箱：其中的 token（https / en / wikisource / org / index / php / oldid）
# **不是英文单词**。PDF 文字层经常把出处信息（"From Wikisource:
# https://en.wikisource.org/w/index.php?oldid=123"）一起抽出来，
# 不排除的话它们会整串出现在生词表里，每行三列全空。
_URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.I)

# 功能词与超高频词：任何等级都不该标（标了等于噪音）
STOPWORDS = set("""
a an the and or but nor so yet for of in on at to from by with without within into onto
about above across after against along among around as before behind below beneath beside
between beyond during except inside near off out outside over past since through throughout
till toward under until up upon via
i you he she it we they me him her us them my your his its our their mine yours hers ours theirs
this that these those which who whom whose what whatever whichever where when why how
is are was were be been being am do does did done doing have has had having
will would shall should can could may might must ought need dare
not no nor none nothing nobody nowhere never neither
there here then than thus hence therefore however moreover furthermore nevertheless
also too very much many more most less least little few fewer
all any both each either every some such same other another others
if unless whether while whilst although though because since as until when whenever
one two three first second next last
mr mrs ms dr prof st
""".split())

# 缩略形式（don't / girl's …）整体算功能词，不进生词表。
# 单独一份而不是塞进上面那个集合：那份是「语义上不值得标的词」，
# 这份是「压根不是独立词汇的词形」—— 混在一起以后想改口径就分不清了。
STOPWORDS |= set(CONTRACTION_STOP)


def _url_spans(text: str) -> list[tuple[int, int]]:
    """文本里所有 URL / 邮箱的区间，用于把其中的 token 排除掉。"""
    return [(m.start(), m.end()) for m in _URL_RE.finditer(text)]


@dataclass
class Token:
    surface: str
    start: int
    end: int
    lemma: str | None = None
    mask: int = 0                 # 该词出现在哪几档词表
    kind: str = "known"           # known | target | overflow | rare | beyond | skip
    new_at_level: bool = False    # 是否属于「本级新增词」（更低档都没收录）
    info: dict = field(default_factory=dict)


def split_sentences(text: str) -> list[tuple[str, int]]:
    """返回 [(句子, 起始偏移)]。处理常见缩写不误切。"""
    out: list[tuple[str, int]] = []
    pos = 0
    for part in _SENT_END.split(text):
        if not part:
            continue
        # 如果上一段以缩写结尾，合并回去
        if out and _ABBR.search(out[-1][0]):
            prev, pstart = out.pop()
            part = prev + " " + part
            pos = pstart
        else:
            pos = text.find(part, pos)
        out.append((part.strip(), pos if pos >= 0 else 0))
        pos += len(part)
    if not out:
        out = [(text.strip(), 0)]
    return out


def split_spans(text: str) -> list[tuple[int, int, str]]:
    """
    Span 精确版分句，返回 `[(start, end, 句子)]`，可直接用来切原文。

    为什么不能直接用 `split_sentences`：它返回的 `start` 是**未 strip** 片段的位置，
    而句子文本是 strip 过的，于是 `text[start:start+len(sent)]` 会带上前导空格，
    逐句渲染时每句都会多缩进一点。更关键的是**译文对齐依赖这个 span 精确** ——
    一旦错位，译文会挂到错误的句子上，那比不翻译更糟。

    `end - start == len(句子)`，且相邻 span 单调不重叠。
    """
    out: list[tuple[int, int, str]] = []
    for sent, start in split_sentences(text):
        if not sent:
            continue
        i = text.find(sent, max(0, start))
        if i < 0:                       # 兜底：找不到就退回原起点
            i = max(0, start)
        end = min(i + len(sent), len(text))
        if out and i < out[-1][1]:      # 保证单调不重叠
            i = out[-1][1]
            end = min(i + len(sent), len(text))
        if end <= i:
            continue
        out.append((i, end, text[i:end]))
    return out


def is_proper_noun(surface: str, text: str, start: int) -> bool:
    """句首大写的普通词不算专有名词；其余位置首字母大写视为专有名词。"""
    if not surface[:1].isupper():
        return False
    if surface.isupper():
        return True
    # 往前看：前面是否只有空白 / 句末标点 → 说明是句首
    k = start - 1
    while k >= 0 and text[k] in " \t\n\"'([":
        k -= 1
    return not (k < 0 or text[k] in ".!?:;")


def classify_word(surface: str, level_id: str, text: str = "", start: int = 0) -> Token:
    """
    把一个词分类为：
      target   本级考纲词        → 荧光笔（需巩固）
      overflow 超纲常见词        → 红圈（最该背）
      rare     超纲生僻词        → 蓝色虚线（认识即可）
      beyond   六档之外（不在任何词表）→ 蓝色虚线，标记「六档之外」
      known    已掌握            → 不标
      skip     功能词/专有名词    → 不标
    """
    lv = get_level(level_id)
    kmask = known_mask(level_id)
    omask = own_mask(level_id)

    lemma, mask = wordlist.lookup(surface)

    if not is_content_word(surface):
        return Token(surface, start, start + len(surface), lemma=lemma, mask=mask, kind="skip")

    key = (lemma or surface).lower()
    if key in STOPWORDS or surface.lower() in STOPWORDS:
        return Token(surface, start, start + len(surface), lemma=lemma, mask=mask, kind="skip")

    if mask == 0:
        # 不在任何一档词表里：专有名词/缩写排除后，就是真正的「六档之外」
        if is_proper_noun(surface, text, start):
            return Token(surface, start, start + len(surface), lemma=None, mask=0, kind="skip")
        if len(surface) < 5:
            return Token(surface, start, start + len(surface), lemma=None, mask=0, kind="skip")
        # 六档之外也必须取词条：补充词典里有音标/词性/释义/例句。
        # 不取的话，生词表里这些词就是「只有一个小圆点 + 一个来源标签」的空白行
        # —— 而这恰恰是用户最需要查的词，留白比标错更没用。
        hit = wordlist.lookup_entry(surface, level_id)
        info, lemma = (hit[1], hit[0]) if hit else ({}, surface.lower())
        return Token(surface, start, start + len(surface), lemma=lemma, mask=0,
                     kind="beyond", info=info)

    info = wordlist.entry(surface, level_id) or {}
    lmask = lower_mask(level_id)
    is_new = not (mask & lmask)          # 更低档全都没收 → 本级才出现的词

    if mask & kmask:
        kind = "target" if (mask & omask) else "known"
        # 词频地板：过于基础的词（如 different / probably）不该被标记，
        # 这是「划满等于没划」的最主要来源。
        if kind == "target" and wordlist.freq_rank(surface) < lv["min_freq_rank"]:
            kind = "known"
    else:
        kind = "overflow" if popcount(mask) >= 2 else "rare"

    return Token(surface, start, start + len(surface), lemma=lemma, mask=mask,
                 kind=kind, new_at_level=is_new, info=info)


def word_score(kind: str, mask: int, surface: str, new_at_level: bool = False) -> float:
    """
    决定「同类型标注里谁先被保留」。

    两个信号叠加：
      1) 通用词频 —— 越靠词频尾部越生僻（different 排 421 绝不标；endurance 排 14627 必须标）
      2) 是否本级新增词 —— 更低档词表都没收它，说明正是本级要学的（kitchen 高中就学过，降权）
    """
    r = wordlist.freq_rank(surface)
    rarity = min(r, wordlist.UNKNOWN_RANK) / wordlist.UNKNOWN_RANK   # 0 常用 → 1 罕见
    if kind == "target":
        return (0.30 + 0.70 * rarity) * (1.0 if new_at_level else 0.45)
    if kind == "overflow":
        return 0.50 + 0.50 * (1.0 - rarity)
    if kind == "rare":
        return 0.25 + 0.35 * rarity
    if kind == "beyond":
        return 0.45 + 0.35 * rarity
    return 0.0


def analyze_text(text: str, level_id: str) -> dict:
    """对一段文本做词元级分析。"""
    toks: list[Token] = []
    # URL 里的 token 不是英文单词（Wikisource 出处信息整串会被 PDF 文字层抽出来）
    spans = _url_spans(text)

    def in_url(s: int, e: int) -> bool:
        return any(a <= s and e <= b for a, b in spans)

    for surface, s, e in tokenize(text):
        if in_url(s, e):
            continue
        t = classify_word(surface, level_id, text, s)
        t.start, t.end = s, e
        toks.append(t)

    counters = {"target": 0, "overflow": 0, "rare": 0, "beyond": 0, "known": 0, "skip": 0}
    for t in toks:
        counters[t.kind] = counters.get(t.kind, 0) + 1

    total = sum(counters.values())
    hard = counters["overflow"] + counters["rare"] + counters["beyond"]
    return {
        "tokens": toks,
        "word_count": total,
        "counters": counters,
        "overflow_ratio": hard / total if total else 0.0,
    }


def annotation_value(sentence: str, toks: list[Token], grammar_hits: list[dict],
                     pattern_hits: list[dict], level_id: str) -> float:
    """
    计算一个句子的「值得标注度」，0~1。
    对应开发文档 6.3.3 的公式，权重按等级可调。
    """
    words = [t for t in toks if t.kind != "skip"]
    if not words:
        return 0.0

    overflow = sum(1 for t in words if t.kind in ("overflow", "rare"))
    overflow_ratio = overflow / len(words)

    n = len(words)
    length_score = min(math.log(max(n, 1)) / math.log(60), 1.0)

    grammar_score = min(len(grammar_hits) / 2.0, 1.0)

    # 句型命中直接给高权重（产品价值最高的标注）
    pattern_score = 1.0 if pattern_hits else 0.0

    # 主题句启发式：首句且较短
    topic_bonus = 0.15 if n >= 8 else 0.0

    value = (0.34 * overflow_ratio
             + 0.24 * length_score
             + 0.20 * grammar_score
             + 0.22 * pattern_score
             + topic_bonus)
    return min(value, 1.0)


def threshold_for(level_id: str) -> float:
    """
    低等级 → 阈值更低（需要更多标注）；高等级 → 阈值更高（标记更精）。
    """
    table = {
        "high_school": 0.20,
        "cet4": 0.26,
        "cet6": 0.32,
        "kaoyan": 0.36,
        "ielts": 0.42,
        "toefl": 0.48,
    }
    return table.get(level_id, 0.30)


def normalize_surface(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()
