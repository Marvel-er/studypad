"""
轻量规则词形还原。

不引入 NLTK / spaCy 那样的大依赖：本项目的目标是把文章中出现的屈折形式
（submissions / reviewed / running）映射回词表里的原形，规则枚举足够准。

⚠ 2026-10-15 补过一次大窟窿：用户导入《A Piece of Red Calico》后反馈
「生词表有的行音标/词性/释义全空」。追下来发现 IRREGULAR 漏了 56 个常用
不规则形式（got / became / broke / threw / sang / rang / froze / stole …），
而它们的原形**全都在六档词表里** —— 于是这些词一律被判成「六档之外」，
生词表里留下三列全空的一行。同期还漏了撇号形式（girl's / don't）与
`-ier → -y`（prettier → pretty）。三类都在下面补上，回归见 probe_irregular.py。
"""
from __future__ import annotations

import re

# ⚠ 2026-10-15 第二次补窟窿（与上面那次症状一模一样：「生词表有的行音标/词性/释义全空」）。
#
# 用户导入《A Mystery of Heroism》后，生词表里出现一行词头写着
# `anticipation--anticipation`、四列全空。真因是**这个正则允许任意连续的连字符**：
# `[A-Za-z][A-Za-z'\-]*` 会把 `anticipation--anticipation` 整个吃成一个 token。
#
# 而 `--` 在 Gutenberg 这类纯文本里是 **em dash（破折号）的 ASCII 写法**，
# 它是**分隔符**，不是构词连字符 —— 那句话原文是
# `…white with anticipation--anticipation of a blow…`，本来就是「预料 / 预料」的重复强调。
# 后果是连锁的三重，且都不报错：
#   1. 这个 token 谁都不认 → 判成「六档之外」（其实 anticipation 在 ielts 词表里，有音标有例句）；
#   2. 三层补充词典按整串查也查不到 → 音标/词性/释义/例句四列**全空**；
#   3. 词头原样显示成 `anticipation--anticipation`，看着像数据坏了。
#
# 正解：只允许「**单**连字符/撇号 + 字母」的构词形式，连续连字符与尾随连字符在那里断开。
#   · 保留：death-wound / swift-boiling / black-bearded（复合词，补充词典里有词条）
#   · 保留：don't / girl's / brother-in-law's
#   · 断开：anticipation--anticipation → anticipation + anticipation
#   · 顺手修掉：`lad--"don't` 里的 `lad--`、行尾的 `well-` 这类带尾连字符的假词
# 真正的 em dash 字符 `—` 本来就断得开（不在字符类里），这次只治 ASCII 的 `--`。
# 回归见 `scripts/probe_dash_token.py`。
_WORD_RE = re.compile(r"[A-Za-z]+(?:['\-][A-Za-z]+)*")

IRREGULAR = {
    "was": "be", "were": "be", "is": "be", "are": "be", "am": "be", "been": "be", "being": "be",
    "has": "have", "had": "have", "having": "have",
    "does": "do", "did": "do", "done": "do", "doing": "do",
    "went": "go", "gone": "go", "goes": "go",
    "said": "say", "says": "say",
    "made": "make", "making": "make",
    "took": "take", "taken": "take",
    "gave": "give", "given": "give",
    "found": "find", "felt": "feel", "kept": "keep", "left": "leave",
    "meant": "mean", "met": "meet", "paid": "pay", "ran": "run",
    "saw": "see", "seen": "see", "sold": "sell", "sent": "send",
    "spent": "spend", "stood": "stand", "taught": "teach", "told": "tell",
    "thought": "think", "understood": "understand", "wrote": "write", "written": "write",
    "brought": "bring", "bought": "buy", "built": "build", "caught": "catch",
    "chose": "choose", "chosen": "choose", "came": "come", "cost": "cost",
    "cut": "cut", "drew": "draw", "drawn": "draw", "drove": "drive", "driven": "drive",
    "ate": "eat", "eaten": "eat", "fell": "fall", "fallen": "fall",
    "grew": "grow", "grown": "grow", "heard": "hear", "held": "hold",
    "knew": "know", "known": "know", "led": "lead", "lost": "lose",
    "read": "read", "rose": "rise", "risen": "rise", "sat": "sit",
    "slept": "sleep", "spoke": "speak", "spoken": "speak", "swam": "swim",
    "wore": "wear", "worn": "wear", "won": "win", "began": "begin", "begun": "begin",
    "better": "good", "best": "good", "worse": "bad", "worst": "bad",
    "children": "child", "men": "man", "women": "woman", "people": "people",
    "feet": "foot", "teeth": "tooth", "mice": "mouse", "data": "datum",
    "criteria": "criterion", "analyses": "analysis", "theses": "thesis",
    "hypotheses": "hypothesis", "phenomena": "phenomenon", "media": "medium",
    "indices": "index", "appendices": "appendix",
    # ---- 2026-10-15 补：常用不规则动词（原形都在六档词表里，漏了会被误判成「六档之外」）----
    "got": "get", "gotten": "get", "forgot": "forget", "forgotten": "forget",
    "became": "become",
    "threw": "throw", "thrown": "throw",
    "rang": "ring", "rung": "ring",
    "sang": "sing", "sung": "sing",
    "sank": "sink", "sunk": "sink",
    "shrank": "shrink", "shrunk": "shrink",
    "sprang": "spring", "sprung": "spring",
    "swore": "swear", "sworn": "swear",
    "tore": "tear", "torn": "tear",
    "broke": "break", "broken": "break",
    "shook": "shake", "shaken": "shake",
    "froze": "freeze", "frozen": "freeze",
    "stole": "steal", "stolen": "steal",
    "forbade": "forbid", "forbidden": "forbid",
    "undertook": "undertake", "undertaken": "undertake",
    "withdrew": "withdraw", "withdrawn": "withdraw",
    "overcame": "overcome",
    "arose": "arise", "arisen": "arise",
    "rode": "ride", "ridden": "ride",
    "woke": "wake", "woken": "wake",
    "lain": "lie", "lay": "lie", "laid": "lay",
    "hung": "hang",
    "struck": "strike",
    "strove": "strive", "thriven": "thrive",
    "wove": "weave", "woven": "weave",
    "dug": "dig",
    "spun": "spin",
    "shone": "shine",
    "slain": "slay",
    "smote": "smite",
    # ---- 2026-10-15 再补一批：书面语 / 文学文本里高频的过去式与过去分词 ----
    # 判据与上一批完全相同（跑 probe_irregular.py 的同款检查扫出来的）：
    # **当前认不出** 且 **原形确实在六档词表里**，两条同时成立才收，共 31 个。
    # 漏了它们的后果也一样：本该命中某个档位，却被判成「六档之外」，
    # 生词表里那一行只剩一个来源标签 —— 补充词典恰好收了的词还有内容，
    # 没收的词就是音标/词性/释义/例句**四列全空**。
    # 触发本次补漏的是《A Mystery of Heroism》里的 `smitten`（原形 smite 在六档内）。
    "swept": "sweep", "wept": "weep", "crept": "creep", "leapt": "leap", "sped": "speed",
    "dealt": "deal", "lent": "lend", "burnt": "burn", "spilt": "spill", "spoilt": "spoil",
    "knelt": "kneel", "dwelt": "dwell", "fled": "flee",
    "clung": "cling", "flung": "fling", "stung": "sting", "swung": "swing", "wrung": "wring",
    "stricken": "strike", "trod": "tread", "trodden": "tread",
    "smitten": "smite", "slew": "slay", "forsook": "forsake", "forsaken": "forsake",
    "striven": "strive", "swollen": "swell", "shaven": "shave", "sown": "sow",
    "mown": "mow", "sawn": "saw", "graven": "grave",
}

# 缩略形式整体算功能词，不该进生词表（don't / girl's 这类以前会留下三列全空的一行）。
# 放在这里而不是 analyzer.STOPWORDS：它是**词形还原**该管的事，
# 而 analyzer 那份是「哪些词不值得标」的语义名单。
CONTRACTION_STOP = frozenset("""
i'm you're we're they're he's she's it's that's there's here's what's who's let's
i've you've we've they've
i'll you'll he'll she'll we'll they'll
i'd you'd he'd she'd we'd they'd
isn't aren't wasn't weren't don't doesn't didn't
haven't hasn't hadn't won't wouldn't can't couldn't
shouldn't shan't mustn't needn't oughtn't
""".split())

# 少数缩略不走规则，只能查表（won't → will、can't → can、shan't → shall）
_IRREGULAR_CONTRACTION = {
    "won't": "will", "can't": "can", "shan't": "shall", "ain't": "be",
}

_VOWELS = set("aeiou")


def _restore_e(stem: str) -> str:
    """running → run(无需 e)；making → make（补回 e）。"""
    return stem


def lemma_candidates(word: str) -> list[str]:
    """
    返回一个词可能的原形候选（含自身，按可信度从高到低）。
    用于在词表里做宽松匹配。

    ⚠ 候选顺序即安全边界：**原词自身永远排第一**，派生形式全部排在后面。
    这样即使某条派生规则生成了同形真词（promise → promize），
    只要原词本身能命中，就不会走到那里。
    """
    w = word.strip().lower().strip("'-")
    if not w:
        return []
    out: list[str] = [w]
    seen = {w}

    def add(x: str) -> None:
        if x and x not in seen and len(x) >= 2:
            seen.add(x)
            out.append(x)

    # ---- 撇号形式：所有格与缩略 ----
    # 词典只收原形，不收 girl's / don't。不处理的话这些形式会被判成「六档之外」，
    # 生词表里留下三列全空的一行（2026-10-15 用户导入《A Piece of Red Calico》时反馈）。
    # 拆成两类：
    #   · 所有格 girl's → girls / girl —— 是真词，要能还原回去；
    #   · 缩略 don't → do —— 是功能词，由 CONTRACTION_STOP 在 analyzer 里拦掉，
    #     这里仍然给出原形候选，免得换个调用方又漏。
    if "'" in w:
        plain = w.replace("'", "")
        if plain:
            add(plain)                                    # girls / dont / its
        for suf in ("ll", "ve", "re", "d", "m", "s", "t"):
            if w.endswith("'" + suf):
                base = w[: -(len(suf) + 1)]
                if base:
                    add(base)                             # girl / you / it / don
        if w in _IRREGULAR_CONTRACTION:
            add(_IRREGULAR_CONTRACTION[w])                # won't → will
        elif w.endswith("n't"):
            add(w[:-3])                                   # don't → do, haven't → have
            stem = w[:-3]
            if stem in IRREGULAR:
                add(IRREGULAR[stem])                      # didn't → did → do

    if w in IRREGULAR:
        add(IRREGULAR[w])

    # 复数 / 三单
    if w.endswith("ies") and len(w) > 4:
        add(w[:-3] + "y")
    # 不规则复数：`-men` → `-man`（cabmen → cabman、tradesmen、policemen…）。
    # 这两个词形**同音**，所以音标与释义都能直接借用原形；而 `-s` 规则对它是无效的
    #（cabmen 减 s 得 cabmen，候选表里还是只有它自己）。
    # 只加候选、不做判断 —— 目标词不存在时自然没人命中，与其它规则一个套路。
    if w.endswith("men") and len(w) > 4:
        add(w[:-3] + "man")
    if w.endswith(("ses", "xes", "zes", "ches", "shes")) and len(w) > 4:
        add(w[:-2])
    if w.endswith("es") and len(w) > 3:
        add(w[:-2])
        add(w[:-1])
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        add(w[:-1])

    # 过去式 / 过去分词
    if w.endswith("ied") and len(w) > 4:
        add(w[:-3] + "y")
    if w.endswith("ed") and len(w) > 3:
        add(w[:-2])
        add(w[:-1])
        # 双写辅音：stopped → stop
        if len(w) > 4 and w[-3] == w[-4] and w[-3] not in _VOWELS:
            add(w[:-3])
        # hoped → hope
        add(w[:-2] + "e")

    # 现在分词 / 动名词
    if w.endswith("ing") and len(w) > 4:
        base = w[:-3]
        add(base)
        add(base + "e")
        if len(base) > 2 and base[-1] == base[-2] and base[-1] not in _VOWELS:
            add(base[:-1])

    # 副词 / 形容词
    if w.endswith("ly") and len(w) > 4:
        add(w[:-2])
        if w.endswith("ily"):
            add(w[:-3] + "y")
        if w.endswith("ally"):
            add(w[:-4] + "al")
            add(w[:-4])
    # 比较级 -ier / 最高级 -iest → -y：prettier → pretty、happiest → happy。
    # 漏了这条的话 prettier 只能生成 pretti / prettie，照样查不到词
    # （2026-10-15 在《A Piece of Red Calico》里抓到）。
    if w.endswith("ier") and len(w) > 4:
        add(w[:-3] + "y")
    if w.endswith("iest") and len(w) > 5:
        add(w[:-4] + "y")
    if w.endswith("er") and len(w) > 4:
        add(w[:-2])
        add(w[:-1])
    if w.endswith("est") and len(w) > 5:
        add(w[:-3])
        add(w[:-2])

    # 常见派生后缀
    for suf, repl in (("ness", ""), ("ment", ""), ("tion", "te"), ("sion", ""),
                      ("able", ""), ("ible", ""), ("ful", ""), ("less", ""),
                      ("ous", ""), ("ive", ""), ("ity", ""), ("ance", ""),
                      ("ence", ""), ("ency", "ent"), ("ancy", "ant")):
        if w.endswith(suf) and len(w) > len(suf) + 2:
            add(w[: -len(suf)])
            if repl:
                add(w[: -len(suf)] + repl)

    # 形容词 -ive ↔ 名词 -ion：convulsive → convulsion / decisive → decision。
    # 这是**同一词根的两种词性**，词典里往往只收名词那一形 ——
    # 不收这条的话，文章里出现的形容词就会被判成「六档之外」，
    # 生词表里音标和释义全空（用户反馈过的问题）。
    if w.endswith("ive") and len(w) > 4:
        stem = w[:-3]
        add(stem + "ion")
        add(stem + "e")
        add(stem + "ity")

    # 英式拼写 → 美式（词库以美式为主）。**必须放在候选表最后**：
    # 这些规则会误伤同形的真词（promise→promize、flour→flor、spare→spaer），
    # 但只要原词本身能命中，就不会走到这里 —— 顺序即安全边界。
    if w.endswith("ise") and len(w) > 4:
        add(w[:-3] + "ize")
    if w.endswith("isation") and len(w) > 8:
        add(w[:-7] + "ization")
    if w.endswith("yse") and len(w) > 4:
        add(w[:-3] + "yze")
    if w.endswith("our") and len(w) > 4:
        add(w[:-3] + "or")
    if w.endswith("re") and len(w) > 3:
        add(w[:-2] + "er")

    return out


def tokenize(text: str) -> list[tuple[str, int, int]]:
    """返回 [(单词, 起止偏移)]，只取纯英文词。"""
    return [(m.group(0), m.start(), m.end()) for m in _WORD_RE.finditer(text)]


def is_content_word(w: str) -> bool:
    """过滤掉纯数字、单字母、全大写缩写等不该标注的 token。"""
    if len(w) < 2:
        return False
    if w.isupper() and len(w) > 1:
        return False          # 全大写多半是缩写 / 机构名
    return True
