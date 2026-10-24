"""共用测试夹具。

测试**全部基于 `examples/sample_corpus/` 里的合成语料**，不使用任何真题文本。
那份样例是刻意构造的：里面混着 Directions 指令行、题干、选项、盗版水印和
中文解析行，因此它同时是清洗逻辑的回归夹具。
"""

from __future__ import annotations

import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SAMPLE_CORPUS = REPO_ROOT / "examples" / "sample_corpus"
SYLLABUS = REPO_ROOT / "data" / "kaoyan_syllabus_verified.txt"


@pytest.fixture(scope="session")
def sample_corpus_dir() -> pathlib.Path:
    assert SAMPLE_CORPUS.is_dir(), f"样例语料缺失：{SAMPLE_CORPUS}"
    return SAMPLE_CORPUS


@pytest.fixture(scope="session")
def syllabus_path() -> pathlib.Path:
    assert SYLLABUS.is_file(), f"词表缺失：{SYLLABUS}"
    return SYLLABUS


def _nltk_ready() -> bool:
    """真实调用一次词形还原来判断 nltk 数据是否就位。

    不要用 ``nltk.data.find("corpora/wordnet")``：数据以 zip 形式存放时
    （``wordnet.zip``）它会误报缺失，而实际调用完全正常。
    """
    try:
        from npee_vocab.lemmatize import lemmatize

        return lemmatize("the children were making better progress") == [
            "the",
            "child",
            "be",
            "make",
            "better",
            "progress",
        ]
    except Exception:
        return False


NLTK_READY = _nltk_ready()

requires_nltk = pytest.mark.skipif(
    not NLTK_READY,
    reason="需要 nltk 数据（python -c \"import nltk; nltk.download('wordnet')\"）",
)
