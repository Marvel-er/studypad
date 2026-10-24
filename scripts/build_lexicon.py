"""
构建 `data/dict/lexicon.sqlite` —— 生词表的「兜底词典」，目标是让「未收录」不再出现。

## 为什么需要它

项目原有四层词典（六档考纲 → general.json → extra.json → ecdict.json 精选 8673 条），
但它们全是**预先筛过的小子集**：`ecdict.json` 用 BNC 排名当「太生僻没人查」的闸门
（`bnc` 为空就丢），结果恰恰丢掉文学/旧文本里最需要的那批词 ——
`caisson` 在 ECDICT 源里数据完整（音标 + 中文释义），只因为 `bnc=0` 就被筛掉了。

本脚本改用**全量**：ECDICT 里凡是「有中文释义的纯英文单词」都收，
另外叠加两个免费权威源补项目缺的两项（音标、例句）：
· CMUdict（卡内基梅隆发音词典，BSD-2）→ 补音标
· Open English WordNet（CC BY 4.0）→ 补英释 / 词性 / 例句

## 许可（重要）

· ECDICT — MIT。注意它是对多个来源的**聚合**，其条目来源不完全可追溯；
  本项目此前已在用（`data/dict/ecdict.json` 就是它筛出来的），这里只是放宽筛选。
· CMUdict — BSD-2-Clause，可商用。
· Open English WordNet — CC BY 4.0，可商用，需署名。
· **不含柯林斯（Collins）**：Collins COBUILD / Collins English Dictionary 是
  HarperCollins 的商业版权产品，没有免费许可，网络上流传的 MDX/StarDict 版本
  均为未授权转载，不引入。
  （ECDICT 里那个 `collins` 列是**柯林斯星级**——只有常用词的 1~5 星难度标记，
  本项目把它当难度标签用，不是柯林斯词典的释义内容。）

## 用法

    python scripts/build_lexicon.py              # 全量构建（WordNet 数据在就一起并进去）
    python scripts/build_lexicon.py --no-wordnet # 只用 ECDICT + CMUdict

WordNet 数据的获取（网络慢，建议后台跑）：

    mkdir -p .cache/wn
    curl -L -o .cache/wn/oewn-2024.xml.gz https://en-word.net/static/english-wordnet-2024.xml.gz
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
csv.field_size_limit(10 ** 7)

ECDICT_CSV = ROOT / "vendor" / "ecdict" / "ECDICT-master" / "ecdict.csv"
OUT_SQLITE = ROOT / "data" / "dict" / "lexicon.sqlite"

# 一个「纯英文单词」的定义：字母开头，允许内部连字符/撇号（death-wound、don't）。
# 数字、空格、括号（那些是短语/缩写/化学式）一律不要 —— 生词表里放不做词的东西没意义。
WORD_RE = re.compile(r"^[A-Za-z][A-Za-z'\-]*$")

# ECDICT 的释义长这样：`n. 预期, 预料\n[医] 提前出现(如遗传病)`。
# 逐行剥掉行首的词性标记，词性单独进 pos 列（原来这一列在所有 ECDICT 词条上都是空的）。
POS_RE = re.compile(
    r"^(n|v|vt|vi|adj|adv|prep|conj|pron|num|art|int|interj|aux|abbr|a|ad|pl|"
    r"vt&vi|v&n|adj&adv)\.\s*",
    re.I,
)
# ECDICT 里有一批**纯屈折说明**条目（`smite的过去分词`、`(hooting 的复数) v. 喊叫…`）。
# 这类条目的中文格子里写的是「它是谁的什么形式」，不是释义本身 ——
# 词形还原（含 _cands 回溯）已经能把 hootings 归到 hoot，真正的释义在那边，
# 所以这里直接不收：留着反而会把「直接命中」喂成一句元信息。
INFLECTION_ONLY = re.compile(
    r"^[（(]?[A-Za-z\-']{0,20}[）)]?\s*的?\s*"
    r"(复数|过去式|过去分词|现在分词|第三人称单数|比较级|最高级|ing形式|动名词)"
)
# 同一种说明吊在释义**尾部**的形态：`v. 喊叫；鸣响（hoot的ing形式）`。
# 这时前半截是真释义，只把尾巴掐掉、整条留用（与上面那种「整条只有元信息」不同）。
TRAILING_NOTE = re.compile(
    r"[（(][^）)]{0,30}?的\s*"
    r"(复数|过去式|过去分词|现在分词|第三人称单数|比较级|最高级|ing形式|动名词)[）)]\s*$"
)

# 词频排名：bnc / frq 哪个有就用哪个，取小的那个（0 = 都没有）。
MAX_ZH = 64      # 释义列的宽度上限，超了截断（生词表那一列本来就放不下长释义）
MAX_EN = 110     # 英释上限
MAX_EX = 96      # 例句上限

# CMUdict 的 ARPAbet → IPA。词尾的重音数字单独处理：`1` = 主重音（前面插 `'`）。
ARPABET_IPA = {
    "AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ", "AY": "aɪ", "B": "b",
    "CH": "tʃ", "D": "d", "DH": "ð", "EH": "e", "ER": "ɜːr", "EY": "eɪ", "F": "f",
    "G": "ɡ", "HH": "h", "IH": "ɪ", "IY": "iː", "JH": "dʒ", "K": "k", "L": "l",
    "M": "m", "N": "n", "NG": "ŋ", "OW": "oʊ", "OY": "ɔɪ", "P": "p", "R": "r",
    "S": "s", "SH": "ʃ", "T": "t", "TH": "θ", "UH": "ʊ", "UW": "uː", "V": "v",
    "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ",
}


def arpabet_to_ipa(phones: list[str]) -> str:
    """
    把 CMUdict 的 ARPAbet 音素串转成 IPA，**沿用项目里既有音标的写法**：
    重音用 `'` 前缀、schwa 用 `ә`(U+04D9) —— 和六档词表/ECDICT 那一列保持一致，
    否则同一列里两套记法，看起来像数据坏了。

    三条规则值得单独说清（都是踩出来的）：

    1. **重音标在「音节首」，不是「元音前」**：`streak` 要写 `/'striːk/` 而不是 `str'iːk`。
       所以遇到带 stress=1 的元音，把 `'` 单独插到它前面那串辅音之前
       （CMUdict 只标在元音上，没有音节信息，这里按「前导辅音串属于本音节」近似）。
    2. **`r` 是前一个元音的一部分**：`artillery` 的 `r` 属于前面的 `ɑːr`，
       重音该落在 `t` 前（`/ɑːr'tɪlɜːriː/`）。所以往左找音节头时，遇到
       「前面是元音的 r」要停下 —— 否则会写成 `/ɑː'rtɪlɜːriː/`（重音跑到了 r 上）。
    3. **重读 ER 是 `ɜːr`、非重读 ER 是 `ər`**：`pursued` 是 `/pər'suːd/`，不是 `/pɜːr'suːd/`。
    4. 长元音带 `ː`：`bead` → `/biːd/`，和短音 `bid`（`/bɪd/`）区分开 ——
       上游词表把两者都写成 `bid`，学生根本分不出来。
    """
    out: list[tuple[str, bool]] = []      # (文本, 是不是元音)
    for ph in phones:
        stress = ""
        raw = ph
        if raw and raw[-1].isdigit():
            digit, raw = raw[-1], raw[:-1]
            if digit == "1":
                stress = "'"
        if raw == "AH" and not stress:
            out.append(("ә", True))
            continue
        if raw == "ER" and not stress:
            out.append(("ər", True))
            continue
        ipa = ARPABET_IPA.get(raw)
        if ipa is None:
            return ""            # 遇到不认识的音素就别硬凑，宁可不给音标
        if stress:
            # 往左回退跳过本音节的前导辅音（但「前面是元音的 r」属于上一音节，要停）
            j = len(out) - 1
            while j >= 0 and not out[j][1]:
                if out[j][0] == "r" and j > 0 and out[j - 1][1]:
                    break
                j -= 1
            out.insert(j + 1, ("'", False))
        out.append((ipa, raw in _ARPABET_VOWELS))
    return "/" + "".join(t for t, _ in out) + "/"


# ARPAbet 的元音音素（判断「这一格是不是元音」用；辅音一律 False）
_ARPABET_VOWELS = {"AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY",
                   "IH", "IY", "OW", "OY", "UH", "UW"}


def _norm_phon(ph: str) -> str:
    """
    ECDICT 的 `phonetic` → 与本列其它来源一致的写法。**只作 CMUdict 的兜底**。

    规格是按实测形态定的（抽样统计：第一套读音用 `;` 分隔、次要重音写 `,`、
    可选读法吊在 `,-kəl` 这种尾巴上、个别用 `ˈ/ˌ`）：

    1. 多套读音只取**第一套**（`ə'gleɪ; ə'gliː` → `ə'gleɪ`）；
    2. 砍掉「可选读法」尾巴（`'tɔrik,-kəl` → `'tɔrik`）；
    3. 斜杠与空格一律去掉；`ˈ`→`'`、`ˌ`→`,`；长度符 `:`→`ː`（与 CMUdict 那套统一）；
    4. **太长（>32）直接放弃**：截断的音标正是这次要修的病，宁可退回原形的。

    取样里那些 `(ə)`（可选音）保留原样 —— 词典也这么写，不算坏数据。
    """
    s = (ph or "").split(";")[0]
    for sep in (",-", " -", "/ -"):
        if sep in s:
            s = s.split(sep)[0]
    s = (s.replace("/", "").replace(" ", "").replace("ˈ", "'")
          .replace("ˌ", ",").replace(":", "ː").strip())
    if not s or len(s) > 32:
        return ""
    return f"/{s}/"


def _clean_zh(s: str) -> str:
    """ECDICT 释义 → 生词表那一格要的样子：剥词性前缀、剥尾部屈折说明、最多两条义项、限宽。"""
    lines = [ln.strip() for ln in s.replace("\\n", "\n").split("\n") if ln.strip()]
    senses: list[str] = []
    for ln in lines:
        ln = POS_RE.sub("", ln).strip()
        # ECDICT 有些条目把屈折说明吊在释义**尾部**：
        # `v. 喊叫；鸣响；摄制（hoot的ing形式）`。前半截是真释义、后半截是元信息，
        # 生词表那一格放不下两样，把尾巴掐掉。
        ln = TRAILING_NOTE.sub("", ln).strip()
        ln = ln.rstrip("；,，;")
        if not ln:
            continue
        senses.append(ln)
        if len(senses) >= 2:
            break
    txt = "；".join(senses)
    return txt[:MAX_ZH].rstrip("；,，")


def _parse_pos(s: str) -> str:
    """从释义里解析词性（ECDICT 没有独立的 pos 列，词性是写在释义开头的）。"""
    seen: list[str] = []
    for ln in s.replace("\\n", "\n").split("\n"):
        m = POS_RE.match(ln.strip())
        if m:
            t = m.group(1).lower()
            t = {"ad": "adv", "a": "adj", "interj": "int"}.get(t, t)
            if t not in seen:
                seen.append(t)
    return ",".join(seen[:3])


def _lemma_from_exchange(ex: str) -> str:
    """ECDICT 的 `exchange` 字段形如 `0:smite/1:d`，`0:` 后面是原形。"""
    for part in (ex or "").split("/"):
        if part.startswith("0:"):
            return part[2:].strip()
    return ""


def known_heads() -> set[str]:
    """前四层已经覆盖的词头 —— 这些不用进兜底库，免得同一格出现两种说法。"""
    have: set[str] = set()
    for p in sorted((ROOT / "data" / "wordlists").glob("*.json")):
        if p.name.startswith("_"):
            continue
        have |= {k.lower() for k in json.loads(p.read_text(encoding="utf-8"))}
    for name in ("general", "extra", "ecdict"):
        p = ROOT / "data" / "dict" / f"{name}.json"
        if p.exists():
            have |= {k.lower() for k in json.loads(p.read_text(encoding="utf-8"))
                     if not k.startswith("_")}
    return have


def cmudict_ipa() -> dict[str, str]:
    """CMUdict → {词: IPA}，多个读音取第一个。装不上就返回空（音标少一列，其余照旧）。"""
    try:
        import cmudict  # noqa: PLC0415
    except ImportError:
        print("  [跳过] cmudict 未安装，音标仅用 ECDICT 自带的那部分")
        return {}
    d = cmudict.dict()
    out: dict[str, str] = {}
    for w, prons in d.items():
        ipa = arpabet_to_ipa(prons[0])
        if ipa:
            out[w] = ipa
    print(f"  CMUdict 音标 {len(out)} 条")
    return out


def wordnet_rows() -> dict[str, tuple[str, str, str]]:
    """
    Open English WordNet → {词: (词性, 英释, 例句)}。

    数据是 **WN-LMF 格式**（不是「Synset 里嵌 Lemma」那种直觉结构）：
    `Synset id=...` 装释义与例句，`LexicalEntry` 里 `Lemma writtenForm=...` 配
    `Sense synset=...` 指回去。两边靠 id 关联，且 LexicalEntry 排在 Synset 前面，
    所以必须**扫两遍**：第一遍收 synset，第二遍把词形接上。

    ⚠ 第一版按「Synset 里有 Members/Lemma」写，结果一条都没解出来却**不报错**
    （`findall` 找不到就返回空列表），只在日志里留了个「词条 0 条」。这类静默为空
    比抛异常难查，所以这里两个计数都会打出来。

    XML 在 `.cache/wn/` 就自己解，不依赖 `wn` 包的下载器 —— 后者超时重试很钝，
    且它的候选 URL 里 GitHub 那一份在本机网络下连不通。
    """
    gz = ROOT / ".cache" / "wn" / "oewn-2024.xml.gz"
    if not gz.exists():
        print("  [跳过] 没有 .cache/wn/oewn-2024.xml.gz，英释/例句这一层先空着")
        return {}
    import gzip
    import xml.etree.ElementTree as ET

    t0 = time.time()
    pos_map = {"n": "n", "v": "v", "a": "adj", "s": "adj", "r": "adv"}
    try:
        syns: dict[str, tuple[str, str, str]] = {}
        with gzip.open(gz, "rb") as fh:
            # iterparse 流式解：解压后 100MB+，一次性 parse 会吃掉大几百 MB 内存。
            #
            # ⚠ 只清 **Synset / LexicalEntry 这两个容器**，别清 Definition / Example！
            # `Element.clear()` 连 `text` 一起清（官方文档原话：sets text and tail to None）。
            # 曾经在每个元素的 end 事件里都 clear，于是 `Definition` 自己的 end 一到文本就被抹掉，
            # 等父节点 Synset 结束时再读只剩空串 —— 结果 120,630 个 Synset 一条都没解出来，
            # 而且**不报错**（找不到就跳过），只在日志里留个「Synset 0 条」。
            # 不清它们不会涨内存：它们随父节点 Synset 一起被清掉。
            for _, el in ET.iterparse(fh, events=("end",)):
                if el.tag != "Synset":
                    continue
                sid = el.get("id") or ""
                defn = ""
                ex = ""
                for c in el:
                    txt = (c.text or "").strip()
                    if c.tag == "Definition" and not defn:
                        defn = txt[:MAX_EN]
                    elif c.tag == "Example" and not ex and 20 <= len(txt) <= MAX_EX:
                        ex = txt
                if sid and defn:
                    syns[sid] = (pos_map.get(el.get("partOfSpeech", ""), ""), defn, ex)
                el.clear()
        print(f"  词网释义（Synset）{len(syns)} 条")
        if not syns:
            print("  [警告] 一个 Synset 都没解出来，XML 结构可能变了")

        out: dict[str, tuple[str, str, str]] = {}
        with gzip.open(gz, "rb") as fh:
            for _, el in ET.iterparse(fh, events=("end",)):
                if el.tag != "LexicalEntry":
                    continue
                lem = ""
                sid = ""
                for c in el:
                    if c.tag == "Lemma" and not lem:
                        lem = (c.get("writtenForm") or "").strip().lower()
                    elif c.tag == "Sense" and not sid:
                        sid = c.get("synset") or ""
                if lem and sid in syns and WORD_RE.match(lem) and lem not in out:
                    out[lem] = syns[sid]      # 一个词只留第一条义项，够用且省地方
                el.clear()
    except Exception as e:  # noqa: BLE001
        # 下载被网络掐断是常态（本机拉 en-word.net 就断过），半个 gz 直接 gzip 报错。
        # 这种情况**不能整个构建失败** —— ECDICT + CMUdict 那部分已经够用了，
        # 只把 WordNet 这一层留空，并说清是文件没下完。
        print(f"  [跳过] WordNet 数据读不了（{type(e).__name__}: {str(e)[:60]}）")
        print(f"         多半是 {gz.name} 没下完（现在 {gz.stat().st_size / 1e6:.1f} MB，约需 13 MB）")
        return {}
    print(f"  WordNet 词条 {len(out)} 条（{time.time() - t0:.0f}s）")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-wordnet", action="store_true", help="不并入 WordNet（只用本地源）")
    args = ap.parse_args()

    if not ECDICT_CSV.exists():
        print(f"缺 ECDICT 源文件：{ECDICT_CSV}")
        return 1

    print("1/5 检查目标文件能不能替换（服务在跑的话它会占着库）…")
    if OUT_SQLITE.exists():
        # Windows 上 SQLite 连接会**按住文件**：`os.remove` / rename 直接
        # PermissionError [WinError 32]（实测：只要有一条没关的连接就失败）。
        # 所以先**探一下**再扫 ECDICT —— 否则白扫 40 秒，最后在一个原始 traceback 上炸掉，
        # 而真正的原因只是「服务还开着」。
        probe = OUT_SQLITE.with_suffix(".sqlite.lockprobe")
        try:
            OUT_SQLITE.rename(probe)
            probe.rename(OUT_SQLITE)          # 立刻改回来，只是探测
        except (PermissionError, OSError):
            print(f"  ✗ 库文件被占用：{OUT_SQLITE.name}")
            print("    多半是 StudyPad 服务还在跑（它启动后按线程缓存了库连接）。")
            print("    先停掉服务再重建；改完库也要重启服务，进程内的连接不会自动切到新文件。")
            return 1
    print("  可替换 ✓")

    print("2/5 收集已有词头 …")
    have = known_heads()
    print(f"  前四层已覆盖 {len(have)} 个词头，兜底库不再重复收")

    print("3/5 音标 / 英释数据源 …")
    ipa = cmudict_ipa()
    wnrows = {} if args.no_wordnet else wordnet_rows()

    print("4/5 扫 ECDICT 全量 …")
    t0 = time.time()
    rows = []
    ecd_phon: dict[str, str] = {}     # 全量音标（含前四层已有的词），给 pron 表兜底用
    n_skip = n_junk = 0
    with open(ECDICT_CSV, encoding="utf-8", newline="") as fh:
        for d in csv.DictReader(fh):
            w = (d.get("word") or "").strip().lower()
            if not w or not WORD_RE.match(w):
                n_junk += 1
                continue
            # 音标先收：**不管这个词最后进不进 lex 表**都要收 ——
            # 音标要按「显示的词形」查，而六档词表里的词一律不进 lex（见 known_heads）。
            if w not in ecd_phon:
                ph = _norm_phon(d.get("phonetic") or "")
                if ph:
                    ecd_phon[w] = ph
            if w in have:
                n_skip += 1
                continue
            zh = _clean_zh(d.get("translation") or "")
            raw_tr = (d.get("translation") or "").strip()
            if len(raw_tr) <= 60 and INFLECTION_ONLY.match(raw_tr):
                n_junk += 1          # 纯屈折说明，释义交给词形还原后的原形条目
                continue
            wo = wnrows.get(w)
            if not zh and not wo:
                n_junk += 1          # 中文英文都没有 = 没东西可显示，别占地方
                continue
            ph = ipa.get(w, "") or _norm_phon(d.get("phonetic") or "")
            pos = _parse_pos(d.get("translation") or "") or (wo[0] if wo else "")
            band = []
            if (d.get("collins") or "").strip():
                band.append("柯林斯" + str(d["collins"]) + "星")
            if (d.get("oxford") or "").strip():
                band.append("牛津3000")
            if (d.get("tag") or "").strip():
                band.append(d["tag"].strip())
            try:
                rank = min([int(x) for x in (d.get("bnc"), d.get("frq")) if x and int(x) > 0] or [0])
            except ValueError:
                rank = 0
            rows.append((
                w, ph, pos, zh,
                (wo[1] if wo else "")[:MAX_EN],
                (wo[2] if wo else "")[:MAX_EX],
                _lemma_from_exchange(d.get("exchange") or ""),
                " ".join(band)[:40],
                rank,
            ))
    print(f"  ECDICT 采用 {len(rows)} 条（跳过已有 {n_skip}、非单词或空条 {n_junk}，"
          f"{time.time() - t0:.0f}s）")

    print("5/5 写 SQLite …")
    tmp = OUT_SQLITE.with_suffix(".sqlite.tmp")
    if tmp.exists():
        tmp.unlink()
    con = sqlite3.connect(tmp)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("""
        CREATE TABLE lex (
            word     TEXT PRIMARY KEY,
            phonetic TEXT NOT NULL DEFAULT '',
            pos      TEXT NOT NULL DEFAULT '',
            zh       TEXT NOT NULL DEFAULT '',
            en       TEXT NOT NULL DEFAULT '',
            ex       TEXT NOT NULL DEFAULT '',
            lemma    TEXT NOT NULL DEFAULT '',
            band     TEXT NOT NULL DEFAULT '',
            rank     INTEGER NOT NULL DEFAULT 0
        )""")
    con.executemany("INSERT OR IGNORE INTO lex VALUES (?,?,?,?,?,?,?,?,?)", rows)
    con.execute("CREATE INDEX idx_lex_lemma ON lex(lemma)")
    # 发音表：CMUdict **全量**（12.6 万词），不只是兜底库里那些。
    # 上面 `lex` 只收「前四层没有的词」，所以六档词表里的词在库里查不到 ——
    # 但音标列需要的是「**显示的这个词形**怎么读」，跟词条在不在库里无关：
    # `flapping` 的词条来自原形 `flap`（释义「拍打」没错），可音标不能跟着用 `flæp`，
    # 那看着就像 -ing 被吞了。CMUdict 覆盖屈折形，正好补这个缺口。
    con.execute("CREATE TABLE pron (word TEXT PRIMARY KEY, ipa TEXT NOT NULL)")
    pron_rows = [(w, ipa_) for w, ipa_ in ipa.items() if WORD_RE.match(w)]
    seen = {w for w, _ in pron_rows}
    # CMUdict 没有的词形，用 ECDICT 自己的音标兜（已归一化，见 _norm_phon）。
    # 实测 48 个常见屈折形里 CMUdict 覆盖 44，缺的那几个（tousled 这类文雅词）
    # ECDICT 有完整音标 —— 不兜的话那一行会退回**原形**的音标，看着像被截断。
    ecd_only = [(w, v) for w, v in ecd_phon.items() if w not in seen and v]
    pron_rows += ecd_only
    con.executemany("INSERT OR IGNORE INTO pron VALUES (?,?)", pron_rows)
    print(f"  发音表 {len(pron_rows)} 条（CMUdict {len(seen)} + ECDICT 兜底 {len(ecd_only)}）")
    con.commit()
    con.execute("VACUUM")
    con.close()
    if OUT_SQLITE.exists():
        OUT_SQLITE.unlink()
    tmp.rename(OUT_SQLITE)
    mb = OUT_SQLITE.stat().st_size / 1e6
    print(f"  写出 {OUT_SQLITE.name}：{mb:.1f} MB")
    print("完成。" + ("（注意：本次未并 WordNet，英释/例句列为空）" if args.no_wordnet or not wnrows else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
