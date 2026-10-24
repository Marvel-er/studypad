"""纯计算层：吃语料，吐数据结构，不碰文件渲染。

设计约定：**这里不写任何 markdown、不 print、不读命令行**。
渲染在 ``render.py``，命令行在 ``cli.py``。这样每个统计口径都能被单元测试
直接断言，不需要去解析输出文本。
"""

from __future__ import annotations

import collections
import pathlib
from dataclasses import dataclass, field
from typing import Literal

from . import lexicon
from .corpus import Mode, prose_text, surface_tokens, year_files
from .lemmatize import lemmatize
from .wordlist import Wordlist, coverage

TokenMode = Literal["lemma", "surface"]

# 高频内容词的门槛：出现在多少年以上
CONTENT_MIN_YEARS = 10

# 分档门槛
T2_MIN_YEARS = 15
T3_MIN_YEARS = 10

# token 覆盖率曲线上的取样词汇量
COVERAGE_SIZES = (2000, 3000, 4000, 5000, 6000, 8000)

# 覆盖率目标点
COVERAGE_TARGETS = (0.80, 0.90, 0.95, 0.98, 0.99, 0.995)

# 阅读流畅的公认门槛
FLUENCY_TARGET = 0.98

# 切片大小：把语料切成「一篇」的粒度
ARTICLE_TOKENS = 400


def tokenize(text: str, token_mode: TokenMode = "lemma") -> list[str]:
    """按指定口径切词。"""
    if token_mode == "surface":
        return surface_tokens(text)
    if token_mode == "lemma":
        return lemmatize(text)
    raise ValueError(f"未知 token_mode: {token_mode!r}")


@dataclass
class Corpus:
    """切好词的语料。"""

    tokens_by_year: dict[str, list[str]]
    mode: Mode
    token_mode: TokenMode
    frequency: collections.Counter = field(init=False)
    yearcount: collections.Counter = field(init=False)

    def __post_init__(self) -> None:
        freq: collections.Counter = collections.Counter()
        yc: collections.Counter = collections.Counter()
        for tokens in self.tokens_by_year.values():
            freq.update(tokens)
            yc.update(set(tokens))
        self.frequency = freq
        self.yearcount = yc

    @property
    def years(self) -> list[str]:
        return sorted(self.tokens_by_year)

    @property
    def total_tokens(self) -> int:
        return sum(self.frequency.values())

    @property
    def distinct(self) -> int:
        return len(self.frequency)

    @property
    def chunks(self) -> list[list[str]]:
        """按固定大小切成的「伪文章」，用于算每篇生词量。

        注意这是**机械切片**，不是真实的 Text A/B/C 边界——
        真实边界需要解析试卷结构，本管线只清洗了正文行。
        """
        out: list[list[str]] = []
        for year in self.years:
            cur: list[str] = []
            for tok in self.tokens_by_year[year]:
                cur.append(tok)
                if len(cur) >= ARTICLE_TOKENS:
                    out.append(cur)
                    cur = []
            if cur:
                out.append(cur)
        return out


def load_corpus(
    raw_dir: pathlib.Path,
    mode: Mode = "blocks",
    token_mode: TokenMode = "lemma",
) -> Corpus:
    """读取并切词。"""
    raw_dir = pathlib.Path(raw_dir)
    return Corpus(
        tokens_by_year={
            y: tokenize(prose_text(raw_dir, y, mode), token_mode)
            for y in year_files(raw_dir)
        },
        mode=mode,
        token_mode=token_mode,
    )


@dataclass
class Stats:
    """主统计结果。序列化后即 ``stats.json``。"""

    years: list[str]
    vocab_per_year: dict[str, int]
    yearcount: dict[str, int]
    always: list[str]
    coverage_distinct: dict[str, float]
    coverage_weighted: dict[str, float]
    content_words: list[tuple[str, int]]
    tokens_total: int
    distinct_total: int
    dicts: dict[str, object] = field(default_factory=dict)

    @property
    def mean_coverage_distinct(self) -> float:
        vals = list(self.coverage_distinct.values())
        return sum(vals) / len(vals) if vals else 0.0

    @property
    def mean_coverage_weighted(self) -> float:
        vals = list(self.coverage_weighted.values())
        return sum(vals) / len(vals) if vals else 0.0

    def to_json(self) -> dict:
        return {
            "years": self.years,
            "vocab_per_year": self.vocab_per_year,
            "yearcount": self.yearcount,
            "always": self.always,
            "coverage_distinct": self.coverage_distinct,
            "coverage_weighted": self.coverage_weighted,
            "content_words": self.content_words,
            "tokens_total": self.tokens_total,
            "distinct_total": self.distinct_total,
            "dicts": self.dicts,
        }


def content_words(
    yearcount: collections.Counter, min_years: int = CONTENT_MIN_YEARS
) -> list[tuple[str, int]]:
    """高频**内容**词：跨年份稳定、非功能词、非切分残留。

    判分口径是「出现年份数」而非原始词频——它衡量的是**跨年份稳定性**，
    更贴近「这个词是不是考研恒定用词」。
    """
    words = [
        (w, c)
        for w, c in yearcount.items()
        if c >= min_years
        and w not in lexicon.FUNCTION
        and w not in lexicon.CONTRACTION
        and len(w) >= 3
    ]
    words.sort(key=lambda t: (-t[1], t[0]))
    return words


def compute_stats(corpus: Corpus, wordlist: Wordlist) -> Stats:
    """算主统计。"""
    years = corpus.years
    lemmas_by_year = {y: set(t) for y, t in corpus.tokens_by_year.items()}
    tokens_by_year = {y: collections.Counter(t) for y, t in corpus.tokens_by_year.items()}

    vol = {y: len(lemmas_by_year[y]) for y in years}
    yc: collections.Counter = collections.Counter()
    for y in years:
        for w in lemmas_by_year[y]:
            yc[w] += 1

    cov_a, cov_b = {}, {}
    for y in years:
        d, w = coverage(lemmas_by_year[y], tokens_by_year[y], wordlist)
        cov_a[y] = round(d, 4)
        cov_b[y] = round(w, 4)

    return Stats(
        years=years,
        vocab_per_year=vol,
        yearcount=dict(yc),
        always=sorted(w for w, c in yc.items() if c == len(years)),
        coverage_distinct=cov_a,
        coverage_weighted=cov_b,
        content_words=content_words(yc),
        tokens_total=corpus.total_tokens,
        distinct_total=corpus.distinct,
        dicts={
            "clean_mode": corpus.mode,
            "token_mode": corpus.token_mode,
            "wordlist": str(wordlist.path) if wordlist.path else None,
            "wordlist_size": len(wordlist),
        },
    )


# --------------------------------------------------------------------------
# 分档：T0–T4
# --------------------------------------------------------------------------


@dataclass
class Tier:
    key: str
    label: str
    meaning: str
    advice: str
    words: list[tuple[str, int]]
    intro: str = ""


@dataclass
class Tiers:
    t0: Tier
    t1: Tier
    t2: Tier
    t3: Tier
    t4: Tier

    def all(self) -> list[Tier]:
        return [self.t0, self.t1, self.t2, self.t3, self.t4]

    @property
    def total(self) -> int:
        return sum(len(t.words) for t in self.all())


def compute_tiers(stats: Stats) -> Tiers:
    """分层复习清单。

    分档依据**全部来自实测数据**（出现年份数 + 是否功能词 + 是否专名/派生），
    不含主观难度判断。
    """
    years_n = len(stats.years)
    yc = stats.yearcount
    always = set(stats.always)
    content = [tuple(t) for t in stats.content_words]

    t0_words = sorted((w, yc[w]) for w in always if w in lexicon.FUNCTION)
    t1_words = sorted((w, yc[w]) for w in always if w not in lexicon.FUNCTION)
    t1_set = {w for w, _ in t1_words}

    t2_words = [
        (w, c)
        for w, c in content
        if T2_MIN_YEARS <= c < years_n
        and w not in t1_set
        and w not in lexicon.SPECIAL
    ]
    t3_words = [
        (w, c) for w, c in content if T3_MIN_YEARS <= c < T2_MIN_YEARS and w not in lexicon.SPECIAL
    ]
    t4_words = [(w, c) for w, c in content if w in lexicon.SPECIAL]

    return Tiers(
        t0=Tier(
            key="T0",
            label="恒定功能词",
            meaning=f"{years_n} 年每年都出现，且属功能词",
            advice="读句子自然掌握，**关键是逻辑功能**",
            words=t0_words,
            intro=(
                f"{years_n} 年真题每年都出现。这类词的价值不在词义，而在**逻辑关系**——\n"
                "它们标记转折、因果、指代，做长难句分析时比实词更关键。\n\n"
                "**不建议孤立背词义。** 要能立刻说出每个词的逻辑功能。"
            ),
        ),
        t1=Tier(
            key="T1",
            label="核心内容词",
            meaning=f"{years_n} 年每年都出现",
            advice="**最优先**。必须能主动用出来",
            words=t1_words,
            intro=(
                "同样每年都出现，但是实词。这些词出现在**任何**一年真题的正文里，\n"
                "是考研英语的骨架动词 / 名词。写作和翻译要能主动调用。"
            ),
        ),
        t2=Tier(
            key="T2",
            label="高频内容词",
            meaning=f"出现 {T2_MIN_YEARS}–{years_n - 1} 年",
            advice="**次优先**。必须认得",
            words=t2_words,
            intro=(
                f"出现在 {T2_MIN_YEARS}–{years_n - 1} 个年份。目标是**一眼认得**，不要求拼写。\n"
                "按出现年数从高到低排列，年数越高越该先拿下。"
            ),
        ),
        t3=Tier(
            key="T3",
            label="常考内容词",
            meaning=f"出现 {T3_MIN_YEARS}–{T2_MIN_YEARS - 1} 年",
            advice="认得即可，靠精读自然覆盖",
            words=t3_words,
            intro=(
                f"出现在 {T3_MIN_YEARS}–{T2_MIN_YEARS - 1} 个年份。这些词的收益不需要靠背单词书获取——\n"
                "**把真题精读懂，它们会自然覆盖。** 遇到就标记，不要列表式背诵。"
            ),
        ),
        t4=Tier(
            key="T4",
            label="专名 / 派生词 / 残留",
            meaning="高频但属人名地名或可拆解的派生词",
            advice="**基本不用背**，见档内说明",
            words=sorted(t4_words, key=lambda t: -t[1]),
            intro=(
                "高频词里的「难词」几乎都是专有名词或可拆解的派生词。\n"
                "**你要练的是词根词缀意识，不是去搜罗冷僻词表。**"
            ),
        ),
    )


# --------------------------------------------------------------------------
# token 覆盖率曲线：不依赖任何词表
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# 年度趋势：相邻年份重合率、首次出现的新词、高频词 TOP N
# --------------------------------------------------------------------------


@dataclass
class YearlyTrend:
    """逐年走势。"""

    jaccard: dict[str, float]
    """相邻年份的词形集合 Jaccard 相似度 ``|A∩B| / |A∪B|``。"""

    overlap_coefficient: dict[str, float]
    """相邻年份的重合系数 ``|A∩B| / min(|A|,|B|)``。"""

    first_seen: dict[str, int]
    """该年首次出现的词形数。"""

    first_seen_words: dict[str, list[str]]
    """该年首次出现的词形。"""

    top_words: list[tuple[str, int]]
    """全语料最高频词形。"""

    @property
    def mean_jaccard(self) -> float:
        vals = list(self.jaccard.values())
        return sum(vals) / len(vals) if vals else 0.0

    @property
    def mean_overlap_coefficient(self) -> float:
        vals = list(self.overlap_coefficient.values())
        return sum(vals) / len(vals) if vals else 0.0


def compute_yearly(corpus: Corpus, top_n: int = 40) -> YearlyTrend:
    """相邻年份重合率 + 逐年新增词 + 高频词榜。"""
    years = corpus.years
    sets = {y: set(t) for y, t in corpus.tokens_by_year.items()}

    jac, ovl = {}, {}
    for prev, cur in zip(years, years[1:]):
        a, b = sets[prev], sets[cur]
        inter = len(a & b)
        union = len(a | b)
        jac[cur] = inter / union if union else 0.0
        ovl[cur] = inter / min(len(a), len(b)) if a and b else 0.0

    seen: set[str] = set()
    first_seen, first_seen_words = {}, {}
    for y in years:
        new = sets[y] - seen
        first_seen[y] = len(new)
        first_seen_words[y] = sorted(new)
        seen |= sets[y]

    return YearlyTrend(
        jaccard=jac,
        overlap_coefficient=ovl,
        first_seen=first_seen,
        first_seen_words=first_seen_words,
        top_words=corpus.frequency.most_common(top_n),
    )


@dataclass
class CoveragePoint:
    size: int
    coverage: float
    unknown_distinct_per_article: float
    unknown_tokens_per_article: float


@dataclass
class CoverageCurve:
    articles: int
    total_tokens: int
    distinct: int
    targets: list[tuple[float, int]]  # (目标覆盖率, 需要词汇量)
    points: list[CoveragePoint]
    bands: list[tuple[str, int, float, float]]  # (标签, 词形数, 占词形, 占词次)


def compute_coverage_curve(corpus: Corpus) -> CoverageCurve:
    """要掌握多少词，才能覆盖多少词次；以及每篇还剩多少生词。

    这个口径**不依赖任何大纲词表**，因此不受词表争议影响，始终可信。
    """
    freq = corpus.frequency
    chunks = corpus.chunks
    total = corpus.total_tokens
    ordered = freq.most_common()

    need: dict[float, int] = {}
    cum = 0
    for i, (_w, c) in enumerate(ordered, 1):
        cum += c
        for tg in COVERAGE_TARGETS:
            if tg not in need and cum / total >= tg:
                need[tg] = i

    points = []
    for n in COVERAGE_SIZES:
        known = {w for w, _ in ordered[:n]}
        cov = sum(c for w, c in ordered[:n]) / total
        d_list, t_list = [], []
        for chunk in chunks:
            unk = [w for w in chunk if w not in known]
            d_list.append(len(set(unk)))
            t_list.append(len(unk))
        points.append(
            CoveragePoint(
                size=n,
                coverage=cov,
                unknown_distinct_per_article=sum(d_list) / len(d_list),
                unknown_tokens_per_article=sum(t_list) / len(t_list),
            )
        )

    bands = []
    for lo, hi, label in [
        (1, 1, f"出现 1 次"),
        (2, 2, "2 次"),
        (3, 5, "3-5 次"),
        (6, 10, "6-10 次"),
        (11, 50, "11-50 次"),
        (51, 10**9, "50 次以上"),
    ]:
        ws = [(w, c) for w, c in freq.items() if lo <= c <= hi]
        nf = len(ws)
        nt = sum(c for _, c in ws)
        bands.append((label, nf, nf / len(freq), nt / total))

    return CoverageCurve(
        articles=len(chunks),
        total_tokens=total,
        distinct=len(freq),
        targets=[(t, need[t]) for t in COVERAGE_TARGETS if t in need],
        points=points,
        bands=bands,
    )


# --------------------------------------------------------------------------
# A / B 类词假设检验
# --------------------------------------------------------------------------


@dataclass
class ABAnalysis:
    candidates: int
    present: list[tuple[str, int, int]]  # (词, 次数, 年份数)
    a_tokens: int
    a_token_share: float
    reuse_buckets: list[tuple[str, int, float]]
    b_distinct: int
    b_share_distinct: float
    b_tokens: int
    b_token_share: float
    articles: int
    a_per_article_distinct: float
    a_per_article_tokens: float
    b_per_article_distinct: float


def compute_ab(corpus: Corpus) -> ABAnalysis:
    """检验「A 类词是封闭集合」这个假设。"""
    freq = corpus.frequency
    yc = corpus.yearcount
    total = corpus.total_tokens
    a_all = lexicon.A_CANDIDATES

    present = sorted(
        ((w, freq[w], yc.get(w, 0)) for w in a_all if freq[w] > 0),
        key=lambda t: -t[1],
    )
    a_tokens = sum(t[1] for t in present)

    buckets = []
    for lo, hi, label in [(1, 1, "只出现1次"), (2, 5, "2-5次"), (6, 20, "6-20次"), (21, 10**9, "20次以上")]:
        n = sum(1 for _, c, _ in present if lo <= c <= hi)
        buckets.append((label, n, n / len(present) if present else 0.0))

    low = [(w, c) for w, c in freq.items() if c <= 2]
    low_tokens = sum(c for _, c in low)

    chunks = corpus.chunks
    a_distinct, a_token, b_distinct = [], [], []
    for chunk in chunks:
        ua = {w for w in chunk if w in a_all}
        ub = {
            w
            for w in chunk
            if w not in a_all
            and freq[w] <= lexicon.B_MAX_YEARCOUNT
            and len(w) >= lexicon.B_MIN_LEN
        }
        a_distinct.append(len(ua))
        a_token.append(sum(1 for w in chunk if w in a_all))
        b_distinct.append(len(ub))

    n = len(chunks)
    return ABAnalysis(
        candidates=len(a_all),
        present=present,
        a_tokens=a_tokens,
        a_token_share=a_tokens / total,
        reuse_buckets=buckets,
        b_distinct=len(low),
        b_share_distinct=len(low) / corpus.distinct,
        b_tokens=low_tokens,
        b_token_share=low_tokens / total,
        articles=n,
        a_per_article_distinct=sum(a_distinct) / n,
        a_per_article_tokens=sum(a_token) / n,
        b_per_article_distinct=sum(b_distinct) / n,
    )


# --------------------------------------------------------------------------
# A 类词表（按功能分组）
# --------------------------------------------------------------------------


@dataclass
class AGroupResult:
    name: str
    hint: str
    words: list[tuple[str, int, int]]  # (词, 次数, 年份数)


def compute_a_groups(corpus: Corpus, yearcount: dict[str, int] | None = None) -> list[AGroupResult]:
    """按功能分组产出 A 类词表。

    只保留**在语料中真实出现过**的词，并按出现次数降序——
    分组本身是人工的，但组内排序是数据的。
    """
    freq = corpus.frequency
    yc = yearcount if yearcount is not None else dict(corpus.yearcount)
    out = []
    for name, hint, words in lexicon.A_GROUPS:
        ws = sorted(
            lexicon.clean_a_words(words) & set(freq), key=lambda w: (-freq[w], w)
        )
        if not ws:
            continue
        out.append(
            AGroupResult(
                name=name,
                hint=hint,
                words=[(w, freq[w], yc.get(w, 0)) for w in ws],
            )
        )
    return out


def a_group_total(groups: list[AGroupResult]) -> int:
    seen: set[str] = set()
    for g in groups:
        seen |= {w for w, _, _ in g.words}
    return len(seen)


# --------------------------------------------------------------------------
# 阅读生词密度
# --------------------------------------------------------------------------


@dataclass
class ReadingPoint:
    vocab_size: int
    coverage: float
    unknown_tokens: float
    unknown_distinct: float


@dataclass
class ReadingAnalysis:
    articles: int
    total_tokens: int
    hf10: int
    hf5: int
    distribution: list[tuple[str, int, float, float]]
    points: list[ReadingPoint]


def compute_reading(corpus: Corpus) -> ReadingAnalysis:
    """阅读时「一篇里有多少生词」，以及其中多少是高频词。"""
    yc = corpus.yearcount
    freq = corpus.frequency
    total = corpus.total_tokens
    chunks = corpus.chunks

    hf10 = {w for w, c in yc.items() if c >= 10}
    hf5 = {w for w, c in yc.items() if c >= 5}

    dist = []
    cum = 0
    for lo, hi in [(25, 25), (20, 24), (15, 19), (10, 14), (5, 9), (3, 4), (2, 2), (1, 1)]:
        n = sum(1 for c in yc.values() if lo <= c <= hi)
        cum += n
        label = f"{lo}" if lo == hi else f"{lo}-{hi}"
        dist.append((label, n, n / len(yc), cum / len(yc)))

    ordered = freq.most_common()
    points = []
    for n in COVERAGE_SIZES:
        known = {w for w, _ in ordered[:n]}
        cov = sum(c for w, c in ordered[:n]) / total
        d_list, t_list = [], []
        for chunk in chunks:
            unk = [w for w in chunk if w not in known]
            d_list.append(len(set(unk)))
            t_list.append(len(unk))
        points.append(
            ReadingPoint(
                vocab_size=n,
                coverage=cov,
                unknown_tokens=sum(t_list) / len(t_list),
                unknown_distinct=sum(d_list) / len(d_list),
            )
        )

    return ReadingAnalysis(
        articles=len(chunks),
        total_tokens=total,
        hf10=len(hf10),
        hf5=len(hf5),
        distribution=dist,
        points=points,
    )
