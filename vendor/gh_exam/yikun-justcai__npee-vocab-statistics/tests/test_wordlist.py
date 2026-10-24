"""词表读取与覆盖率口径的测试。"""

from __future__ import annotations

import collections
import pathlib

from npee_vocab.wordlist import Wordlist, coverage, load_wordlist, read_any


class TestReadAny:
    def test_utf8(self, tmp_path: pathlib.Path):
        f = tmp_path / "a.txt"
        f.write_bytes("中文 utf-8".encode("utf-8"))
        assert read_any(f) == "中文 utf-8"

    def test_gb18030_fallback(self, tmp_path: pathlib.Path):
        """历史词表是 gb18030，必须能读。"""
        f = tmp_path / "b.txt"
        f.write_bytes("解释".encode("gb18030"))
        assert read_any(f) == "解释"


class TestLoadWordlist:
    def test_tab_separated_with_definitions(self, tmp_path: pathlib.Path):
        f = tmp_path / "w.txt"
        f.write_text("abandon\tvt.放弃\nzoo\tn.动物园\n", encoding="utf-8")
        wl = load_wordlist(f)
        assert len(wl) == 2
        assert "abandon" in wl
        assert wl.definition("abandon") == "vt.放弃"
        assert wl.definition("missing") == "—"

    def test_lowercases_keys(self, tmp_path: pathlib.Path):
        f = tmp_path / "w.txt"
        f.write_text("Abandon\tvt.放弃\n", encoding="utf-8")
        assert "abandon" in load_wordlist(f)

    def test_plain_wordlist_without_definitions(self, tmp_path: pathlib.Path):
        """纯词表（每行一词）也要能读——旧表就是这种格式。"""
        f = tmp_path / "w.txt"
        f.write_text("abandon\nzoo\n", encoding="utf-8")
        wl = load_wordlist(f)
        assert len(wl) == 2
        assert wl.definitions == {}

    def test_plain_wordlist_with_phonetics(self, tmp_path: pathlib.Path):
        """NPEE 词表是 ``word [phonetic] 释义`` 格式，取第一个字段。"""
        f = tmp_path / "w.txt"
        f.write_text("abandon [əˈbændən] vt.离弃\n", encoding="utf-8")
        wl = load_wordlist(f)
        assert "abandon" in wl
        assert "abandon" not in wl.definitions or wl.definition("abandon") != "—"

    def test_missing_file_is_empty_not_crash(self, tmp_path: pathlib.Path):
        wl = load_wordlist(tmp_path / "nope.txt")
        assert len(wl) == 0
        assert wl.words == frozenset()

    def test_real_syllabus_is_5501(self, syllabus_path: pathlib.Path):
        """锁住已发布结果所依赖的词表规模。

        这个数字一旦变化，README 里的覆盖率结论就必须一并重算。
        """
        wl = load_wordlist(syllabus_path)
        assert len(wl) == 5501
        assert len(wl.definitions) == 5501

    def test_real_syllabus_has_the_6_patches(self, syllabus_path: pathlib.Path):
        """6 条手工补丁必须在表里——它们是有外部依据的缺口修复。"""
        wl = load_wordlist(syllabus_path)
        for word in ["an", "program", "center", "analyze", "realize", "judgment"]:
            assert word in wl, word


class TestCoverage:
    def test_distinct_and_weighted(self):
        wl = Wordlist(frozenset({"the", "be"}), {}, None)
        tokens = collections.Counter({"the": 8, "be": 1, "zzz": 1})
        distinct, weighted = coverage({"the", "be", "zzz"}, tokens, wl)
        assert distinct == 2 / 3
        assert weighted == 9 / 10

    def test_weighted_is_higher_when_unknown_words_are_rare(self):
        """次数加权口径应当高于不同词口径——这是报告里反复出现的现象。"""
        wl = Wordlist(frozenset({"the"}), {}, None)
        tokens = collections.Counter({"the": 90, "rare1": 1, "rare2": 1, "rare3": 1})
        distinct, weighted = coverage(set(tokens), tokens, wl)
        assert weighted > distinct

    def test_empty_inputs_do_not_divide_by_zero(self):
        wl = Wordlist(frozenset({"a"}), {}, None)
        assert coverage(set(), collections.Counter(), wl) == (0.0, 0.0)
