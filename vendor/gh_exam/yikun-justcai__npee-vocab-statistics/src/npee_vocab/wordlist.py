"""大纲词表的读取与合并。

当前使用的词表是 ``data/kaoyan_syllabus_verified.txt``（5,501 条，utf-8，
制表符分隔：``词<TAB>释义``）。它的来历和修订依据见
``reports/methodology/wordlist-revision.md``，一句话版本：

* 主体沿用旧表 ``5495大纲词汇.txt``（5,490 条，gb18030）；
* 并入第二份考纲词表 NPEE_Wordlist 中确认旧表缺失的部分；
* 手工补 6 条有**外部依据**的词（``an`` 与 5 个英美拼写变体）。

**方法论红线**：不允许把语料里挖出来的词补进词表来抬高覆盖率。
覆盖率只有在词表独立于语料时才有意义，否则等于把答案抄进考卷。
"""

from __future__ import annotations

import pathlib
from typing import NamedTuple


class Wordlist(NamedTuple):
    """一份大纲词表。"""

    words: frozenset[str]
    """词形集合（小写，词形还原后的形态）。"""

    definitions: dict[str, str]
    """词 -> 释义。词表不带释义时为空。"""

    path: pathlib.Path | None
    """来源文件。"""

    def __len__(self) -> int:
        return len(self.words)

    def __contains__(self, word: str) -> bool:
        return word in self.words

    def definition(self, word: str) -> str:
        return self.definitions.get(word, "—")


def read_any(path: pathlib.Path) -> str:
    """编码自适应读取：先 utf-8，失败再 gb18030。

    历史词表是 gb18030，verified 词表是 utf-8，两者都要能读。
    """
    data = pathlib.Path(path).read_bytes()
    for enc in ("utf-8", "gb18030"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def load_wordlist(path: pathlib.Path) -> Wordlist:
    """读取词表。支持 ``词<TAB>释义`` 与纯词表（每行一词/一词一空格）两种格式。"""
    path = pathlib.Path(path)
    words: set[str] = set()
    defs: dict[str, str] = {}

    if not path.exists():
        return Wordlist(frozenset(), {}, path)

    for line in read_any(path).splitlines():
        if "\t" in line:
            key, value = line.split("\t", 1)
        else:
            stripped = line.strip()
            if not stripped:
                continue
            # 纯词表：取每行第一个空白分隔的字段
            key, _, value = stripped.partition(" ")
        key = key.strip().lower()
        if not key:
            continue
        words.add(key)
        if value.strip():
            defs[key] = value.strip()

    return Wordlist(frozenset(words), defs, path)


def coverage(distinct: set[str], token_counts, wordlist: Wordlist) -> tuple[float, float]:
    """两种口径的大纲覆盖率。

    ``distinct``
        该年的不同词元集合。
    ``token_counts``
        该年的 ``Counter``（词元 -> 次数）。

    返回 ``(不同词口径, 次数加权口径)``。

    **次数加权口径才是贴近实感的那个**：它问的是「你实际读到的词次里，
    有多少在大纲内」。出现次数最多的那批词（the/of/and/be…）几乎全在大纲内，
    真正「超纲」的是偶尔露面的低频词——所以不同词口径明显更低。
    """
    cov_distinct = len(distinct & wordlist.words) / len(distinct) if distinct else 0.0
    total = sum(token_counts.values())
    in_list = sum(c for w, c in token_counts.items() if w in wordlist.words)
    cov_weighted = in_list / total if total else 0.0
    return cov_distinct, cov_weighted
