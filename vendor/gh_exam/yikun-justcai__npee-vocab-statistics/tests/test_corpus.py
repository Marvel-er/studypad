"""语料清洗的回归测试。

这些用例锁住的是**「什么样的行算正文」**这条判断——
一旦改动 ``is_usable`` / ``prose_blocks``，这里必须同步反映。
"""

from __future__ import annotations

import pathlib
import re

import pytest

from npee_vocab.corpus import (
    WATERMARK,
    TRUNCATE,
    get_lines,
    is_usable,
    kept_lines,
    prose_blocks,
    strip_directions,
    surface_tokens,
    year_files,
)

PROSE = (
    "For most of the past century, urban planners treated traffic as a problem to be solved by "
    "building more roads, and the assumption seemed reasonable enough at the time."
)


class TestIsUsable:
    def test_plain_prose_is_usable(self):
        assert is_usable(PROSE)

    def test_blank_line_rejected(self):
        assert not is_usable("   ")

    @pytest.mark.parametrize(
        "line",
        [
            "Directions:",
            "Section II Reading Comprehension",
            "Part A",
            "Text 1",
            "[A] The engineers were mistaken about the causes of congestion.",
            "21. The author mentions Gilles Duranton in order to ______.",
            "51",
            "--- 12 ---",
        ],
    )
    def test_structural_lines_rejected(self, line):
        assert not is_usable(line), line

    @pytest.mark.parametrize("mark", WATERMARK)
    def test_watermark_rejected(self, mark):
        assert not is_usable(f"some prose here about reading {mark} and more words to pass")

    def test_chinese_explanation_rejected(self):
        assert not is_usable("本题考查的是转折关系，答案为 B。此处应该注意上下文。")

    def test_too_few_words_rejected(self):
        assert not is_usable("Short line here")

    def test_short_line_with_struct_word_rejected(self):
        # "numbered" 来自 Directions 的 "numbered blank"
        assert not is_usable("choose the best word for each numbered blank")

    def test_long_line_with_struct_word_kept(self):
        # 长句里出现 blank 是正常英文，不该被误杀
        line = (
            "The screen went blank for a moment, and then the image returned, which the "
            "technicians regarded as evidence that the cable had merely come loose."
        )
        assert is_usable(line)


class TestProseBlocks:
    def test_short_block_dropped(self):
        # 2 行 + 不足 40 词的碎块应被丢弃
        lines = ["A short sentence here.", "Another short one."]
        assert prose_blocks(lines) == []

    def test_long_block_kept(self):
        block = [PROSE] * 4
        assert len(prose_blocks(block)) == 1

    def test_blocks_split_by_junk(self):
        lines = [PROSE] * 4 + ["Directions:"] + [PROSE] * 4
        blocks = prose_blocks(lines)
        assert len(blocks) == 2


class TestStripDirections:
    def test_directions_line_plus_two_following_dropped(self):
        """Directions 行 + 其后 2 行 = **共 3 行**被丢弃。

        上游脚本的注释写的是「其后 3 行」，但计数器在遇到 Directions 行的
        当次迭代就先减了 1（该行本身也被丢掉），实际是共 3 行。
        """
        block = [
            "kept before",
            "Directions:",
            "drop 1",
            "drop 2",
            "kept after",
        ]
        assert strip_directions(block) == ["kept before", "kept after"]

    def test_directly_following_line_after_budget_is_kept(self):
        block = ["Directions:", "d1", "d2", "kept"]
        assert strip_directions(block) == ["kept"]


class TestKeptLines:
    def test_sample_2019_keeps_prose_drops_junk(self, sample_corpus_dir: pathlib.Path):
        kept = kept_lines(sample_corpus_dir, "2019", mode="blocks")
        text = " ".join(kept)
        assert "induced demand" in text, "正文应当保留"
        assert "ANSWER SHEET" not in text, "指令行应被剔除"
        assert "冰柠" not in text, "水印行应被剔除"
        assert "in order to" not in text, "题干行应被剔除"
        assert "The engineers were mistaken" not in text, "选项行应被剔除"

    def test_blocks_is_subset_of_flat(self, sample_corpus_dir: pathlib.Path):
        """blocks 是 flat 的子集——块级筛选只会**减少**内容，不会引入新行。"""
        from collections import Counter

        for year in year_files(sample_corpus_dir):
            flat = Counter(kept_lines(sample_corpus_dir, year, "flat"))
            blocks = Counter(kept_lines(sample_corpus_dir, year, "blocks"))
            assert not (blocks - flat), f"{year}: blocks 出现了 flat 没有的行"

    def test_flat_leaks_realistic_option_line(self, sample_corpus_dir: pathlib.Path):
        """反向锁定已知缺陷：flat 会漏进**真实排版**的选项行。

        真题 PDF 抽出的选项常是 ``[ C]`` 这种带空格的形态，
        结构行正则 ``\\[[A-D]\\]`` 匹配不到，于是被当成正文收了进来。
        `blocks` 则因为这个残块太短而整块丢弃。

        这正是本项目把 `blocks` 定为默认口径的原因——
        文档声称「已剔除题干与选项」，而只有 `blocks` 真的做到了。
        """
        flat = " ".join(kept_lines(sample_corpus_dir, "2019", mode="flat"))
        blocks = " ".join(kept_lines(sample_corpus_dir, "2019", mode="blocks"))
        assert "[ C] In consequence" in flat
        assert "[ C] In consequence" not in blocks

    def test_flat_also_leaks_directions_continuation(self, sample_corpus_dir: pathlib.Path):
        """flat 会漏进指令行的续行。

        这里有一个不显眼的机制：``Directions:`` 这一行**先被 STRUCT_LINE 拦下**
        （正则里就有 ``Directions`` 这个分支），于是 ``is_usable`` 返回 False，
        而 flat 的跳过计数器只在 ``is_usable`` 为真时才推进——
        也就是说 flat 里那套 ``DIRECTIONS`` / skip 逻辑对真正的 Directions 行
        **根本不会触发**，纯粹是死代码，续行照样漏进来。

        `blocks` 则靠「残块不足 3 行就丢弃」把它挡在外面。
        """
        flat = " ".join(kept_lines(sample_corpus_dir, "2019", mode="flat"))
        blocks = " ".join(kept_lines(sample_corpus_dir, "2019", mode="blocks"))
        assert "Read the following four texts" in flat, "flat 漏进了指令续行"
        assert "Read the following four texts" not in blocks

    def test_inline_directions_word_triggers_skip(self, tmp_path: pathlib.Path):
        """正文里出现（非行首的）Directions 会误触发跳过，连丢 3 行。

        这是从上游继承的行为，本项目原样保留并在此锁定：
        修它需要先确认真题语料里到底有没有这种句子，否则改了反而偏离已发布结果。

        注意跳过计数器**只在可用行上推进**——不可用的短行穿过时不计数。
        """
        prose1 = "This sentence contains a long and clear description that survives every filter."
        trigger = "She ignored the Directions given by the committee entirely."
        prose2 = "Another perfectly ordinary sentence about weather and the changing of the seasons."
        prose3 = "A third sentence that should be swallowed by the skip counter for no good reason."
        prose4 = "The fourth sentence reappears once the counter has finally run out."
        prose5 = "And the fifth sentence is kept as well, as one would expect."

        f = tmp_path / "2019.txt"
        f.write_text("\n".join([prose1, trigger, prose2, prose3, prose4, prose5]), encoding="utf-8")
        kept = kept_lines(tmp_path, "2019", mode="flat")
        assert kept == [prose1, prose4, prose5]

    def test_short_unusable_lines_do_not_advance_the_skip_counter(self, tmp_path: pathlib.Path):
        """短行穿过时不计入跳过的 3 行额度。"""
        trigger = "She ignored the Directions given by the committee entirely."
        prose = "A perfectly ordinary sentence that ought to be kept after the counter runs out."
        f = tmp_path / "2019.txt"
        f.write_text("\n".join([trigger, "x", "y", prose]), encoding="utf-8")
        # trigger 丢掉自己（skip 3->2），x/y 不可用不计数，prose 仍被 skip=2 吃掉
        assert kept_lines(tmp_path, "2019", mode="flat") == []


class TestSurfaceTokens:
    def test_lowercases_and_splits(self):
        assert surface_tokens("The Cats, sat!") == ["the", "cats", "sat"]

    def test_drops_single_letters(self):
        assert surface_tokens("a I b cd") == ["cd"]

    def test_no_lemmatization(self):
        assert surface_tokens("was children better") == ["was", "children", "better"]


class TestYearFiles:
    def test_lists_sample_years_sorted(self, sample_corpus_dir: pathlib.Path):
        assert year_files(sample_corpus_dir) == ["2019", "2020", "2021", "2022"]


class TestTruncate:
    def test_2022_is_truncated_convention(self):
        # 常量本身是「2022 是合订本」这条知识的载体
        assert TRUNCATE == {"2022": 678}

    def test_truncation_applied(self, tmp_path: pathlib.Path):
        f = tmp_path / "2022.txt"
        f.write_text("\n".join(f"line {i} {PROSE}" for i in range(700)), encoding="utf-8")
        assert len(get_lines(tmp_path, "2022")) == 678

    def test_short_file_not_padded_or_truncated(self, tmp_path: pathlib.Path):
        f = tmp_path / "2022.txt"
        f.write_text("\n".join(f"line {i}" for i in range(10)), encoding="utf-8")
        assert len(get_lines(tmp_path, "2022")) == 10

    def test_missing_year_raises(self, tmp_path: pathlib.Path):
        """缺年份文件应当报错，而不是静默返回空——静默会把统计悄悄算小。"""
        with pytest.raises(FileNotFoundError):
            get_lines(tmp_path, "2021")
