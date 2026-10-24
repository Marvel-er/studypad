"""词形还原（lemmatization）。

``was -> be``、``children -> child``、``better -> well``、``making -> make``。

这一步是整个管线里**最容易被误读的一步**：还原之后再和大纲词表比对，
意味着语料里根本不会以 ``is`` / ``was`` / ``children`` 这些表层形态去查表，
查的是 ``be`` / ``child``。上游项目曾经因为忽略这一点，误判「大纲词表缺
is/are/was/children，所以不是完整考纲」——实际上那些词元表里全都有。
详见 ``reports/methodology/wordlist-revision.md``。
"""

from __future__ import annotations

import re

from .corpus import TOKEN_RE

# 首次使用需要下载的 nltk 数据
NLTK_PACKAGES = (
    "wordnet",
    "omw-1.4",
    "averaged_perceptron_tagger_eng",
    "punkt",
    "punkt_tab",
)

_wnl = None
_pos_tag = None


def ensure_nltk_data(quiet: bool = True):
    """按需下载 nltk 数据，并返回 ``(WordNetLemmatizer, pos_tag)``。

    ⚠️ **不能用 ``nltk.data.find("corpora/wordnet")`` 判断数据是否就位。**
    nltk 允许把语料以 **zip** 形式存放（``wordnet.zip``），此时
    ``find("corpora/wordnet")`` 会抛 LookupError，但真实调用完全正常。
    按 find 的结果去下载，会导致每次运行都白跑一遍下载流程。

    所以这里直接做一次真实调用，只有真的 LookupError 才下载。
    """
    global _wnl, _pos_tag
    if _wnl is not None and _pos_tag is not None:
        return _wnl, _pos_tag

    import nltk
    from nltk import pos_tag
    from nltk.stem import WordNetLemmatizer

    wnl, tagger = WordNetLemmatizer(), pos_tag

    def probe() -> None:
        tagger(["testing"])
        wnl.lemmatize("testing", "v")

    try:
        probe()
    except LookupError:
        for pkg in NLTK_PACKAGES:
            nltk.download(pkg, quiet=quiet)
        probe()

    _wnl, _pos_tag = wnl, tagger
    return _wnl, _pos_tag


def lemmatize(text: str) -> list[str]:
    """切词 + 词形还原。返回词元序列（保留重复，顺序不变）。

    POS 标注只用来决定还原成名词/动词/形容词/副词中的哪一类；
    标不出实义词性时按名词处理——与原脚本一致。
    """
    wnl, pos_tag = ensure_nltk_data()
    raw = [w for w in re.split(r"[^A-Za-z]+", text) if TOKEN_RE.match(w)]
    out = []
    for w, tag in pos_tag(raw):
        p = tag[0].lower()
        out.append(wnl.lemmatize(w.lower(), p if p in "nvar" else "n"))
    return out
