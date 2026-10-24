"""项目里所有**人工归纳**的词表。

这一层和 ``corpus.py`` 的区别很重要：语料清洗是**算法**，可以复现；
下面这些集合是**人的判断**，改一个词就会改变产出报告。

上游项目把这些常量散在 6 个脚本里，同一个 ``FUNCTION`` 集合抄了两份，
``A 类词`` 在 ``make_A_list.py`` 和 ``diagnose_AB.py`` 里各有一份且**并不相同**。
集中到这里之后，每一份的口径和用途都写在名字旁边，改动能被 review。
"""

from __future__ import annotations

# --------------------------------------------------------------------------
# 纯功能词：统计「高频【内容】词」时排除
# --------------------------------------------------------------------------
FUNCTION = frozenset(
    """a an the and or but if because so than that this these those there their them they
we you your it its his her he she i me my our us of to in on at by for from with without into out up
over under about as not no nor only very more most much many some any all both each every few other
another such same own can could may might must shall should will would do does did done be been being
am is are was were have has had having what when where which who whom whose how why whether while
also then thus hence therefore however moreover furthermore nevertheless nonetheless still yet even
just ever never always often sometimes usually rather quite too enough again once here now already""".split()
)

# --------------------------------------------------------------------------
# 撇号切分残留：don't -> don+t、we're -> we+re，不是真实单词
# --------------------------------------------------------------------------
CONTRACTION = frozenset(
    """don doesn didn isn aren wasn weren won wouldn couldn shouldn hasn haven hadn ain
re ve ll th u s t d m n""".split()
)

# --------------------------------------------------------------------------
# T4 档：高频但**不需要专门背**的词
# --------------------------------------------------------------------------

# 专有名词。真题中首字母大写的实体，无法从统计推出，只能人工归纳。
PROPER = frozenset(
    {"american", "america", "europe", "european", "britain", "john", "washington"}
)

# 派生 / 比较级：给出可拆解的原形
DERIVED: dict[str, str] = {
    "researcher": "research",
    "development": "develop",
    "higher": "high",
    "longer": "long",
    "greater": "great",
    "particularly": "particular",
    "generally": "general",
    "recently": "recent",
    "others": "other",
    "cannot": "can + not",
    "non": "前缀 non-",
    "online": "on + line（现代复合词）",
    "program": "programme 的美式拼写",
}

# 统计残留：来自 Directions 的 "numbered blank"，不是词汇
ARTIFACT = frozenset({"numbered"})

SPECIAL = PROPER | frozenset(DERIVED) | ARTIFACT

# --------------------------------------------------------------------------
# A 类词：逻辑 / 抽象词，按【功能】分组
#
# 为什么分组而不按字母序：A 类词的价值在逻辑信号，不在词义。
# 练「看到 nevertheless 就知道要转折」比练「nevertheless = 然而」有用。
# 同一组的词在句子里的作用相同，一起记效率更高。
# --------------------------------------------------------------------------

A_GROUPS: list[tuple[str, str, tuple[str, ...]]] = [
    (
        "转折 / 让步",
        "读到就该警觉：前后意思相反",
        tuple(
            """however nevertheless nonetheless notwithstanding but yet although though even if
     while whereas despite in spite of admittedly granted""".split()
        ),
    ),
    (
        "因果 / 推断",
        "标记论据与结论的连接",
        tuple(
            """because since therefore thus hence consequently accordingly so for as a result
     due to owing to thereby""".split()
        ),
    ),
    (
        "递进 / 并列",
        "标记论证的推进方向",
        tuple(
            """moreover furthermore besides additionally also likewise similarly in addition
     not only as well as moreover""".split()
        ),
    ),
    (
        "对比 / 替代",
        "标记两个选项的对立",
        tuple(
            """instead rather otherwise alternatively conversely on the contrary by contrast
     meanwhile whereas""".split()
        ),
    ),
    (
        "条件 / 限定",
        "标记结论成立的边界，常是出题点",
        tuple(
            """unless until provided if whether in case as long as only if subject to""".split()
        ),
    ),
    (
        "立场动词：主张",
        "标记作者 / 研究者持什么态度",
        tuple(
            """argue argues argued claim claims claimed contend contends contended maintain
     maintains maintained assert asserts asserted insist insists insisted""".split()
        ),
    ),
    (
        "立场动词：暗示",
        "弱断言，常是推理题的关键",
        tuple(
            """suggest suggests suggested imply implies implied indicate indicates indicated
     hint hints hinted speculate speculates speculated presume presumes presumed""".split()
        ),
    ),
    (
        "立场动词：举证",
        "标记证据的呈现",
        tuple(
            """show shows showed shown demonstrate demonstrates demonstrated reveal reveals
     revealed observe observes observed note notes noted report reports reported
     find finds found document documents documented""".split()
        ),
    ),
    (
        "立场动词：质疑",
        "反方立场，转折题的信号",
        tuple(
            """doubt doubts doubted question questions questioned challenge challenges challenged
     dispute disputes disputed deny denies denied reject rejects rejected""".split()
        ),
    ),
    (
        "立场动词：承认",
        "让步后必有转折",
        tuple(
            """acknowledge acknowledges acknowledged admit admits admitted concede concedes
     conceded recognize recognizes recognized""".split()
        ),
    ),
    (
        "抽象名词：论证构件",
        "读不懂这些，段落的骨架就抓不住",
        tuple(
            """assumption assumptions hypothesis hypotheses premise premises inference inferences
     implication implications notion notions proposition propositions assertion assertions
     argument arguments claim claims conclusion conclusions""".split()
        ),
    ),
    (
        "抽象名词：评价维度",
        "选项里高频出现，决定能否排除干扰项",
        tuple(
            """significance relevance validity reliability credibility plausibility
     distinction distinctions correlation causality consequence consequences
     tendency norm norms principle principles criterion criteria""".split()
        ),
    ),
    (
        "抽象名词：张力概念",
        "文章主题层面的常见词",
        tuple(
            """paradox dilemma contradiction ambiguity consensus controversy phenomenon phenomena
     perspective perspectives framework frameworks rationale justification""".split()
        ),
    ),
]

# A 类词表在统计前的黑名单：多词短语（in spite of / as a result）会被
# 空白切分拆成 of/in/as/for 这类功能词，必须剔除，否则污染 A 类表。
A_STOP = frozenset(
    """a an the and or but if of to in on at by for from with as so not no nor
is are was were be been being do does did have has had will would shall should can could
may might must this that these those it its they them their we you your he she his her
one two three all any some each every both few more most other another such same own
than then there here when where which who whom whose what how why while whether
result spite due owing addition case long only just very too also well""".split()
)

# 最短长度：2 字母的碎片基本是切分噪声
A_MIN_LEN = 3


def clean_a_words(words) -> set[str]:
    """A 类候选词清洗：去功能词 / 短语碎片，去 2 字母碎片。"""
    return {w for w in words if w not in A_STOP and len(w) >= A_MIN_LEN}


# --------------------------------------------------------------------------
# A 类词的**候选池**（假设检验用）
#
# 和上面的 A_GROUPS 不是一回事：A_GROUPS 是最终交付的分组词表，
# 这里是用于检验「A 类是不是封闭集合」的更大候选池（含未在语料中出现的词）。
# 上游项目把这两份混在同一个概念下，容易误读。
# --------------------------------------------------------------------------

A_CONNECT = tuple(
    """however nevertheless nonetheless notwithstanding whereas while although though
despite despite therefore thus hence consequently accordingly moreover furthermore besides
instead rather otherwise meanwhile likewise similarly conversely alternatively
because since unless until provided whether albeit""".split()
)

A_STANCE = tuple(
    """suggest suggests suggested argue argues argued claim claims claimed
indicate indicates indicated imply implies implied assume assumes assumed presume
contend contends contend maintain maintains maintained assert asserts asserted
note notes noted observe observes observed report reports reported find finds found
reveal reveals revealed demonstrate demonstrates demonstrated show shows showed
conclude concludes concluded propose proposes proposed recommend recommends recommended
acknowledge acknowledges acknowledged admit admits admitted concede concedes conceded
insist insists insisted doubt doubts doubted question questions questioned
estimate estimates estimated predict predicts predicted speculate speculates speculated""".split()
)

A_ABSTRACT = tuple(
    """implication implications assumption assumptions hypothesis hypotheses
premise premises inference inferences interpretation interpretations notion notions
concept concepts perspective perspectives framework frameworks approach approaches
tendency tendency assumption rationale justification justification criterion criteria
phenomenon phenomena paradox dilemma contradiction ambiguity consensus controversy
norm norms principle principles proposition propositions assertion assertion
distinction distinctions correlation correlation causality consequence consequences
significance significance relevance validity reliability credibility plausibility
evidence argument arguments reasoning judgment judgments bias biases incentive incentives""".split()
)

A_CANDIDATES = frozenset(A_CONNECT) | frozenset(A_STANCE) | frozenset(A_ABSTRACT)

# --------------------------------------------------------------------------
# 长尾实词（B 类）的近似判定
# --------------------------------------------------------------------------

# B 类近似：出现总次数 <= 该阈值、非 A 类、长度 >= 该值的词
B_MAX_YEARCOUNT = 5
B_MIN_LEN = 4
