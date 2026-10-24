"""
词表数据层：加载六档词表索引，做「词 → 等级归属」判定。

数据来源：KyleBing/english-vocabulary (MIT)，见 scripts/build_wordlists.py
补充词典（六档之外的词）：同仓库的完整词条，见 scripts/build_general_dict.py
"""
from __future__ import annotations

import json
import re
import sqlite3
import threading
from functools import lru_cache
from pathlib import Path

from .lemmatize import lemma_candidates

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "wordlists"
GENERAL_PATH = DATA_DIR.parent / "dict" / "general.json"
# 手写补充词典：六档与 general.json 都漏收的常用词（calico 这类）。
# 每一条都是手写的、来历见文件里的 _meta。
EXTRA_PATH = DATA_DIR.parent / "dict" / "extra.json"
# ECDICT 兜底层：skywind3000/ECDICT (MIT) 的 ecdict.csv 过滤而来，8673 条。
# **优先级最低**，且带上游来历 caveat（见 build_ecdict_supplement.py 与文件 _meta）。
ECDICT_PATH = DATA_DIR.parent / "dict" / "ecdict.json"

# 全量兜底词典（data/dict/lexicon.sqlite，约 37 万条）。见 scripts/build_lexicon.py。
#
# 上面那四层全是**预先筛过的小子集**，`ecdict.json` 更是拿 BNC 排名当「太生僻没人查」的闸门，
# 于是文学/旧文本里最需要的词反被丢掉：`caisson` 在 ECDICT 源里音标、中文释义俱全，
# 只因 `bnc=0` 就被筛了 —— 生词表那一行只剩「六档之外」标签，四列全空。
# 这一层改用全量（只留「有中文释义的纯英文单词」），并叠加 CMUdict 的音标
# 与 Open English WordNet 的英释/例句。
LEXICON_PATH = DATA_DIR.parent / "dict" / "lexicon.sqlite"


@lru_cache(maxsize=1)
def _index() -> dict[str, int]:
    """{word: bitmask}。word 已小写；bit 表示该词出现在哪几档词表里。"""
    p = DATA_DIR / "_index.json"
    if not p.exists():
        raise FileNotFoundError(
            f"词表索引缺失：{p}\n请先运行：python scripts/build_wordlists.py"
        )
    return json.loads(p.read_text(encoding="utf-8"))


@lru_cache(maxsize=8)
def _detail(level_id: str) -> dict[str, dict]:
    p = DATA_DIR / f"{level_id}.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


UNKNOWN_RANK = 20001


@lru_cache(maxsize=1)
def _general() -> dict[str, dict]:
    """
    六档之外的补充词典：word → {p 音标, pos 词性, t 释义, e 英释, s 例句}。

    为什么需要：一篇文章里出现的「超纲词」有相当一部分根本不在六档词表里，
    没有它的话生词表那一行的音标/词性/释义就是空的 —— 用户看到一行白。
    文件缺失时返回空表，功能降级但不报错（用户可能还没跑构建脚本）。
    """
    p = GENERAL_PATH
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return d if isinstance(d, dict) else {}


def has_general_dict() -> bool:
    """补充词典是否已构建（前端/自检用来区分「没有这个词」和「没建词典」）。"""
    return bool(_general())


@lru_cache(maxsize=1)
def _extra() -> dict[str, dict]:
    """
    手写补充词典（见 extra.json 里的 `_meta`）。

    为什么单独一份而不是并进 `general.json`：`general.json` 是由
    `build_general_dict.py` 从上游词库**生成**的，可以被随时重建覆盖；
    手写的条目不能掺在里面，否则下次重建就丢了，也没法说清来历。

    文件缺失时返回空表，功能降级但不报错。
    """
    p = EXTRA_PATH
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(d, dict):
        return {}
    # `_meta` 是说明性字段，不是词条
    return {k: v for k, v in d.items()
            if isinstance(v, dict) and not k.startswith("_")}


def has_extra_dict() -> bool:
    """手写补充词典是否存在（`/api/levels` 与自检用）。"""
    return bool(_extra())


@lru_cache(maxsize=1)
def _ecdict() -> dict[str, dict]:
    """
    ECDICT 兜底层（见 `ecdict.json` 里的 `_meta`）。

    为什么放在最后：它的上游来历没有逐一明确的许可（作者自多处汇编：
    网友的 EDictAZ.txt、爬虫抓取的音标、Linux cdict、WordNet），
    而仓库本身是 MIT。所以只作**最后兜底** —— 前面三层都查不到才用它。
    不接受这个 caveat 的话，删掉 `data/dict/ecdict.json` 即可，这里静默降级。
    """
    p = ECDICT_PATH
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(d, dict):
        return {}
    return {k: v for k, v in d.items()
            if isinstance(v, dict) and not k.startswith("_")}


def has_ecdict_dict() -> bool:
    """ECDICT 兜底层是否已构建（`/api/levels` 与自检用）。"""
    return bool(_ecdict())


@lru_cache(maxsize=1)
def _freq() -> dict[str, int]:
    """通用英语词频索引：word → rank（越小越常用）。"""
    p = DATA_DIR / "_freq.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def freq_rank(word: str) -> int:
    """
    词的通用词频序（1 = the）。未收录返回 UNKNOWN_RANK。
    这是判断「这个词到底常不常见」的唯一可靠信号 —— 比词表归属可靠得多。
    """
    f = _freq()
    if not f:
        return UNKNOWN_RANK
    for cand in lemma_candidates(word):
        r = f.get(cand)
        if r:
            return r
    return UNKNOWN_RANK


@lru_cache(maxsize=1)
def stats() -> dict:
    idx = _index()
    return {"unique_words": len(idx)}


def popcount(n: int) -> int:
    return bin(n).count("1")


def _cands(word: str) -> list[str]:
    """
    词形候选，**带一层回溯展开**。

    为什么需要（2026-10-15 用户反馈「生词表有的行四列全空」）：
    `lemma_candidates` 是**单层**的 —— `hootings` 只会被拆成 `hooting`（复数→单数），
    而 `hooting` 自己还能再拆出 `hoot`（-ing 还原）。只查一层的话，
    `hootings` 在六档与三层补充词典里全都查不到，生词表那一行就只剩一个
    「六档之外」标签，音标/词性/释义/例句**四列全空** ——
    而它的原形 `hoot` 明明有完整词条。

    实现要点：把第二轮候选**追加在后面**，绝不插到前面。
    候选顺序就是命中优先级，第二轮的可信度更低（多绕了一层），
    插到前面会让 `staring` 这类词被拆出的次级候选抢在正确候选之前命中。
    """
    first = lemma_candidates(word)
    if not first:
        return first
    seen = set(first)
    out = list(first)
    for c in first:
        for d in lemma_candidates(c):
            if d not in seen:
                seen.add(d)
                out.append(d)
    return out


def lookup(word: str) -> tuple[str | None, int]:
    """
    查一个词（可以是任意词形）。
    返回 (命中的原形, bitmask)；都没命中则返回 (None, 0)。

    ⚠ 必须用 `_cands`（带回溯），不能直接用 `lemma_candidates`：
    分类用的 bitmask 与取词条走的候选链必须是**同一条**，
    否则会出现「分类说它是六档之外、词条却来自六档词表」这种自相矛盾的行。
    """
    idx = _index()
    for cand in _cands(word):
        m = idx.get(cand)
        if m:
            return cand, m
    return None, 0


def _search_order(level_id: str) -> list[str]:
    """
    词条搜索的档位顺序：本级 → 更低档（由高到低）→ 更高档（由低到高）。

    为什么要横跨**全部**档位：一个 cet4 用户文章里的「超纲词」，
    恰恰多半就是六级 / 考研 / 雅思 / 托福词表里的词 —— 它们有完整词条
    （音标、词性、释义、例句），原实现只往低档回退，于是一个都取不到，
    生词表里那一行只剩一个「超纲常见」标签，其余列全空。
    """
    from .levels import ORDER

    if level_id not in ORDER:
        return list(ORDER)
    i = ORDER.index(level_id)
    return [level_id] + list(reversed(ORDER[:i])) + list(ORDER[i + 1:])


# 词条里可以「就地补全」的字段。`r`（本级序号）不补 —— 它是档位专属的。
_FILL_KEYS = ("p", "pos", "t", "s", "e")


def _fill(lemma: str, base: dict, details: list[tuple[str, dict]],
          g: dict) -> dict:
    """
    词条字段级补全。

    为什么需要：六档词表里有大量条目**有释义、没音标**（如 cet6 的 `deepen`
    是 `"p": ""`），而同一个词在别的档位（toefl）里音标是齐的。
    用户明确要求「补全每个单词的意思和词性以及音标」，只做整条命中是不够的 ——
    命中了一条缺音标的记录，音标那一列照样是空的。

    规则：**只填空字段，绝不覆盖已有值**。已有的 `t` 是该档位首选义项，
    自带档位语义（cet6 的 deepen 收的是「加浓」而不是通用义），不能被别档盖掉。
    """
    miss = [k for k in _FILL_KEYS if not base.get(k)]
    if not miss:
        return base
    srcs = [d.get(lemma) or {} for _lid, d in details]
    if g:
        srcs.append(g.get(lemma) or {})
    x = _extra()
    if x:
        srcs.append(x.get(lemma) or {})
    ec = _ecdict()
    if ec:
        srcs.append(ec.get(lemma) or {})
    out: dict | None = None
    for s in srcs:
        for k in miss:
            if s.get(k):
                if out is None:
                    out = dict(base)
                out[k] = s[k]
    return out or base


def _lookup_plain_raw(word: str, level_id: str = "") -> tuple[str, dict] | None:
    """
    查一条词条（词形候选 × 各层词典），不做复合词拆分。**音标不在这里修** ——
    音标由外面的 `_lookup_plain` 统一收口（见 `pronunciation` 的说明）。

    顺序是**层优先**：先拿所有候选词形问完六档，再问补充词典，再问手写，再问 ecdict，
    最后才是兜底全量库。这是项目的既有规约 —— 生词表按**原形归并**
    （`convulsive` 用 `convulsion` 的词条解释、且并进同一行），
    免得一个词族的不同词形各占一行预算（`probe_compound` 守着这条）。

    曾试过改成「候选在外、层在内」（让直接命中压过派生命中），
    好处是 `stolidity` 能拿到自己的词条、不用 `stolid`（形容词）的释义；
    但那等于把档位与补充词典之间的优先级也一起改了（`convulsive` 会从
    「用 cet4 档的 convulsion」变成「用 general 里它自己那条」），
    动的是全站每个派生词的解析结果，收益不抵风险，故保持层优先。
    """
    cands = _cands(word)          # 带回溯，见 _cands 的说明（hootings → hooting → hoot）
    if not cands:
        return None

    details = [(_lid, _detail(_lid)) for _lid in _search_order(level_id)]
    g, x, ec = _general(), _extra(), _ecdict()
    con = _lexicon()

    def from_lexicon(cand: str) -> dict | None:
        """兜底全量库是 SQLite 不是内存字典，单条查询；库不在就整层跳过。"""
        if con is None:
            return None
        row = con.execute(
            "SELECT phonetic, pos, zh, en, ex FROM lex WHERE word = ?", (cand,)
        ).fetchone()
        if not row:
            return None
        return {"p": row[0], "pos": row[1], "t": row[2], "e": row[3], "s": row[4]}

    # 档位：对所有候选词形问一遍六档
    for cand in cands:
        for _lid, d in details:
            e = d.get(cand)
            if e:
                return cand, _fill(cand, e, details, g)

    # 补充词典：**每层各自把所有候选问一遍**（层在内、候选在外会变成另一回事：
    # ecdict 里的 `convulsive` 会抢在 general 的 `convulsion` 前面，把「按原形归并」翻掉）
    for src in (g, x, ec):
        if not src:
            continue
        for cand in cands:
            e = src.get(cand)
            if e:
                return cand, _fill(cand, e, details, g)

    # 最后一层：全量兜底库（35 万条，含 CMUdict 音标、WordNet 英释与例句）。
    # 上面四层是**预先筛过的小子集**，文学/旧文本里最需要的词反被它们丢掉
    #（`caisson` 在 ECDICT 源里音标、中文释义俱全，只因 bnc=0 被筛），
    # 所以这一层用全量兜住：质量参差，但**有内容永远好过空白单元格**。
    if con is not None:
        for cand in cands:
            e = from_lexicon(cand)
            if e:
                return cand, _fill(cand, e, details, g)
    return None


# SQLite 连接按线程懒开：FastAPI 的同步端点跑在线程池里，一个连接跨线程用会炸
# （`check_same_thread` 默认就拦），而每次查询都新开连接又白白付一遍打开开销。
_LEX_LOCAL = threading.local()


def _lexicon():
    """本线程的全量词典连接；库文件不在就返回 None（整套降级，不报错）。"""
    if not hasattr(_LEX_LOCAL, "con"):
        if LEXICON_PATH.exists():
            con = sqlite3.connect(LEXICON_PATH)
            con.execute("PRAGMA query_only=ON")
            _LEX_LOCAL.con = con
        else:
            # 记下「没有」这个结论，避免每次查词都 stat 一遍磁盘
            _LEX_LOCAL.con = None
    return _LEX_LOCAL.con


def _first_sense(t: str) -> str:
    """
    取释义的首个义项。

    源数据里义项分隔符既有「；」也有「，」—— 只切「；」会把
    `policy` 的「政策， 保险单」整段当成一个义项，拼出来的合成释义
    就成了「政策，保险单 + 制造者」，看着像坏数据。
    """
    return re.split(r"[；;，,]", (t or "").strip())[0].strip()


def _join_phon(a: str, b: str) -> str:
    """
    合成词的音标：两个词的音标连写（复合词按一个词读）。

    必须先把各自的斜杠脱掉 —— 有的词条写 `/kən'vʌlʃən/`、有的写 `'dipən`，
    不脱就接出 `/a//b/` 这种双斜杠，比没有音标还像坏数据。
    """
    a = (a or "").strip().strip("/").strip()
    b = (b or "").strip().strip("/").strip()
    if a and b:
        return f"/{a}{b}/"
    if a or b:
        return f"/{a or b}/"
    return ""


def _compound_entry(word: str, level_id: str = "") -> tuple[str, dict] | None:
    """
    复合词兜底：`policymaker` 词典里没有，但 `policy` + `maker` 都有。

    **只在其他所有查法都失败之后**才走这条路，且要求两半都是 ≥4 字母的实词 ——
    否则 `there` 会被拆成 `the` + `re`，返回一个荒谬的释义。

    合成词条的释义写成「A + B」（并在 `e` 里注明是合成，标 `c=1`），
    不假装它是词典里的原词条。宁可让用户自己把两半拼出语义，
    也不直接编一个「政策制定者」出来 —— 编出来的释义没有出处，错了没人发现。
    """
    w = (word or "").lower()
    if not (8 <= len(w) <= 20):
        return None
    for i in range(len(w) - 4, 3, -1):
        a, b = w[:i], w[i:]
        ha, hb = _lookup_plain(a, level_id), _lookup_plain(b, level_id)
        if not ha or not hb:
            continue
        ea, eb = ha[1], hb[1]
        ta = _first_sense(ea.get("t"))
        tb = _first_sense(eb.get("t"))
        if not (ta and tb):
            continue
        return w, {
            "p": _join_phon(ea.get("p", ""), eb.get("p", "")),
            "pos": eb.get("pos") or ea.get("pos") or "",
            "t": f"{ta} + {tb}",
            "e": f"复合词，由 {a} + {b} 合成",
            "s": eb.get("s") or ea.get("s") or "",
            "c": 1,
        }
    return None


@lru_cache(maxsize=8192)
def pronunciation(word: str) -> str:
    """
    取**这个词形本身**的 IPA 音标；查不到返回空串。

    为什么单独开一个口子（2026-10-15 用户反馈「有的音标给的不完整」）：
    音标列的语义是「**显示出来的这个词**怎么读」，而词条是按**原形归并**的 ——
    `flapping` 的词条来自 `flap`（释义「拍打」没问题），音标若跟着用 `flæp`，
    读起来就像 -ing 被吞了；`beads` → `bid`、`dragged` → `dræg` 同理。
    实测那篇手账 85 行里 **36 行**是这么来的。

    发音表是 CMUdict 全量（12.6 万词，**含各种屈折形**），专门解决这一件事：
    它按词形收录，`beads`/`dragged`/`flapping` 都有自己的读音。

    取不到就返回空串，调用方保留词条自带的音标 —— 宁可用原形的，也不要瞎拼一个。
    """
    con = _lexicon()
    if con is None:
        return ""
    w = word.strip().lower()

    def query(key: str) -> str:
        try:
            row = con.execute("SELECT ipa FROM pron WHERE word = ?", (key,)).fetchone()
        except sqlite3.OperationalError:
            return ""      # 旧版库没有 pron 表：整层降级，不影响释义与渲染
        return row[0] if row else ""

    ipa = query(w)
    if not ipa and "-" in w:
        # 连字符写法在发音词典里常常是**连写**的（`arm-chairs` ↔ `armchairs`）：
        # 实测拿掉连字符再查，多救回 3751 个词（`arm-chairs` 因此才有复数 /z/，
        # 否则只剩 `chair` 那个单数读音，看着就是「少了一截」）。
        ipa = query(w.replace("-", ""))
    return ipa


def _lookup_plain(word: str, level_id: str = "") -> tuple[str, dict] | None:
    """
    查词条，并把音标**收口到显示的那个词形**上。

    只做两件事：调 `_lookup_plain_raw` 取词条 → 若发音词典里有 `word` 本身的读音，
    就替换掉词条自带的那个。为什么必须替换而不是「缺了才填」：
    词条自带的音标属于**另一个词形**（原形），它不是缺，是错位 ——
    看着像被截断（`flapping` → `flæp`）。
    顺带这也统一了记法：来源五花八门（六档词表不带斜杠、general/ecdict 带斜杠、
    ECDICT 有个词条甚至一格塞了两套读音），换成发音词典后整列一致。
    """
    hit = _lookup_plain_raw(word, level_id)
    if not hit:
        return None
    cand, e = hit
    p = pronunciation(word)
    if not p:
        cands = _cands(word)      # 与 _lookup_plain_raw 用的是同一份候选表
        # 表面词形不在发音词典里，就沿候选表找**第一个有读音的词形**：
        # `tradesman's` → tradesman、`hesitatingly` → hesitating、`cabmen` → cabman。
        # 后者尤其说明问题：它在兜底库里**有自己的词条**（释义是对的），只是 ECDICT
        # 那一行没给音标，于是 `cand` 等于它自己、退不到原形 —— 所以这里不能只看 `cand`，
        # 要按候选表逐个试。
        # 拿到的都是发音词典里的真值、记法一致，不是拼出来的。合成后缀音素试过：
        # 留出验证命中率只有 2.6%~62%（词干选错 + 两套记法混在里面），错得没规律，故不做。
        for c in cands:
            p = pronunciation(c)
            if p:
                break
    if p and p != e.get("p"):
        e = {**e, "p": p}
    return cand, e


def lookup_entry(word: str, level_id: str = "") -> tuple[str, dict] | None:
    """
    返回 `(命中的原形, 词条)` —— 比 `entry()` 多告诉调用方「命中的是哪个词形」。

    这个信息很重要：`convulsive` 的词条实际来自 `convulsion`，
    生词表要显示前者（文章里的词形）、用后者的音标与释义。
    """
    hit = _lookup_plain(word, level_id)
    if hit:
        return _topup_missing_fields(word, hit, level_id)
    return _compound_entry(word, level_id)


def _topup_missing_fields(word: str, hit: tuple[str, dict],
                          level_id: str) -> tuple[str, dict]:
    """
    字段补全：词条缺音标 / 词性 / 例句时，用「复合词拆分」那套从两半借一份。

    为什么需要：`verify_render_api.py` 断言生词表**每行都有例句**，而兜底全量库里
    大量词条只有释义（ECDICT 没有例句列，WordNet 也只覆盖一部分）。`policymakers`
    就是这种：以前它不在任何词典里，靠 `_compound_entry` 拆成 `policy + makers`，
    例句从 `makers` 借来；现在兜底库有 `policymaker` 词条（释义「政策制定者」更准），
    命中之后就不再走拆分那条路，例句列于是空了 —— 修的是「查得准」带来的副作用。

    **只填空字段，已有的一律不动**：词条自己的音标/例句永远比借来的可信。
    """
    lem, e = hit
    if e.get("p") and e.get("pos") and e.get("s"):
        return hit
    ce = _compound_entry(word.lower(), level_id)
    if not ce:
        return hit
    filled = dict(e)
    for k in ("p", "pos", "s"):
        if not filled.get(k) and ce[1].get(k):
            filled[k] = ce[1][k]
    return lem, filled


def entry(word: str, level_id: str = "") -> dict | None:
    """
    取词条详情（音标 / 词性 / 释义 / 例句）。

    搜索策略是**候选词形优先、档位次之**：
    对每个原形候选（`lemma_candidates` 已按可信度排好序）依次问六档，
    最后落到补充词典，再不行才尝试复合词拆分。反过来（先档位后候选）
    会在 high_school 档里拿 `caption` 的词条去解释 `captive` —— 词形差得离谱却先命中。

    返回 None 表示「这个词真的没有任何词条」，调用方应把留空如实呈现，
    不要编一个出来。
    """
    hit = lookup_entry(word, level_id)
    return hit[1] if hit else None




def tail_rank(word: str, level_id: str) -> int:
    """词在本级词表里的序号（越小越常见）。不在本级则返回 99999。"""
    d = _detail(level_id)
    e = d.get(word)
    return e.get("r", 99999) if e else 99999
