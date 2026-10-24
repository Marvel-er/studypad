"""计算层测试。

大部分用例直接构造 ``Corpus`` / ``Stats`` 对象，**不需要 nltk 数据**，
因此在 CI 里跑得很快；只有端到端用例才依赖词形还原。
"""

from __future__ import annotations

import collections
import pathlib

import pytest

from conftest import requires_nltk
from npee_vocab import lexicon
from npee_vocab.analysis import (
    ARTICLE_TOKENS,
    Corpus,
    Stats,
    a_group_total,
    compute_a_groups,
    compute_ab,
    compute_coverage_curve,
    compute_stats,
    compute_tiers,
    compute_yearly,
    content_words,
    load_corpus,
)
from npee_vocab.wordlist import load_wordlist


def make_corpus(tokens_by_year: dict[str, list[str]]) -> Corpus:
    return Corpus(tokens_by_year=tokens_by_year, mode="blocks", token_mode="lemma")


class TestCorpusObject:
    def test_frequency_and_yearcount(self):
        c = make_corpus({"2019": ["a", "a", "b"], "2020": ["a", "c"]})
        assert c.frequency == collections.Counter({"a": 3, "b": 1, "c": 1})
        assert c.yearcount == collections.Counter({"a": 2, "b": 1, "c": 1})
        assert c.total_tokens == 5
        assert c.distinct == 3

    def test_chunks_are_400_tokens(self):
        c = make_corpus({"2019": ["w"] * (ARTICLE_TOKENS * 2 + 10)})
        chunks = c.chunks
        assert [len(x) for x in chunks] == [ARTICLE_TOKENS, ARTICLE_TOKENS, 10]

    def test_chunks_do_not_cross_years(self):
        c = make_corpus({"2019": ["w"] * 300, "2020": ["w"] * 300})
        assert [len(x) for x in c.chunks] == [300, 300]


class TestContentWords:
    def test_excludes_function_words(self):
        yc = collections.Counter({"the": 25, "analysis": 25})
        assert content_words(yc) == [("analysis", 25)]

    def test_excludes_contraction_fragments(self):
        yc = collections.Counter({"don": 25, "analysis": 25})
        assert content_words(yc) == [("analysis", 25)]

    def test_excludes_short_words(self):
        yc = collections.Counter({"ab": 25, "analysis": 25})
        assert content_words(yc) == [("analysis", 25)]

    def test_applies_year_threshold(self):
        yc = collections.Counter({"analysis": 9, "research": 10})
        assert content_words(yc) == [("research", 10)]

    def test_sorted_by_yearcount_desc_then_alpha(self):
        yc = collections.Counter({"beta": 12, "alpha": 12, "gamma": 20})
        assert content_words(yc) == [("gamma", 20), ("alpha", 12), ("beta", 12)]


class TestYearly:
    def test_jaccard_and_overlap_coefficient(self):
        c = make_corpus({"2019": ["a", "b", "c", "d"], "2020": ["a", "b", "x", "y"]})
        y = compute_yearly(c)
        # |A∩B| = 2, |A∪B| = 6
        assert y.jaccard["2020"] == pytest.approx(2 / 6)
        # |A∩B| / min(4,4) = 0.5
        assert y.overlap_coefficient["2020"] == pytest.approx(0.5)

    def test_first_seen_is_cumulative_and_disjoint(self):
        c = make_corpus({"2019": ["a", "b"], "2020": ["b", "c"], "2021": ["c", "d"]})
        y = compute_yearly(c)
        assert y.first_seen == {"2019": 2, "2020": 1, "2021": 1}

    def test_first_seen_words_recorded(self):
        c = make_corpus({"2019": ["a"], "2020": ["a", "z"]})
        assert compute_yearly(c).first_seen_words["2020"] == ["z"]

    def test_single_year_has_no_transition(self):
        y = compute_yearly(make_corpus({"2019": ["a"]}))
        assert y.jaccard == {}
        assert y.mean_jaccard == 0.0


class TestTiers:
    def _stats(self) -> Stats:
        years = [str(y) for y in range(2002, 2027)]  # 25 年
        yc = {
            "the": 25,          # T0 功能词
            "research": 25,     # T1 核心内容词
            "climate": 20,      # T2
            "monetary": 12,     # T3
            "washington": 15,   # T4 专名
            "numbered": 11,     # T4 残留
        }
        return Stats(
            years=years,
            vocab_per_year={y: 100 for y in years},
            yearcount=yc,
            always=["the", "research"],
            coverage_distinct={y: 0.5 for y in years},
            coverage_weighted={y: 0.6 for y in years},
            content_words=content_words(collections.Counter(yc)),
            tokens_total=1000,
            distinct_total=len(yc),
        )

    def test_tiers_partition_the_expected_words(self):
        t = compute_tiers(self._stats())
        assert [w for w, _ in t.t0.words] == ["the"]
        assert [w for w, _ in t.t1.words] == ["research"]
        assert [w for w, _ in t.t2.words] == ["climate"]
        assert [w for w, _ in t.t3.words] == ["monetary"]
        assert {w for w, _ in t.t4.words} == {"washington", "numbered"}

    def test_t4_excludes_words_already_in_t1(self):
        """t2 显式排除 t1；t4 只收 SPECIAL 集合内的词。"""
        t = compute_tiers(self._stats())
        assert not ({w for w, _ in t.t1.words} & {w for w, _ in t.t2.words})

    def test_total_matches_sum_of_tiers(self):
        t = compute_tiers(self._stats())
        assert t.total == sum(len(x.words) for x in t.all())


class TestCoverageCurve:
    def test_coverage_is_monotonic_in_vocab_size(self):
        c = make_corpus({"2019": [f"w{i}" for i in range(3000)]})
        curve = compute_coverage_curve(c)
        covs = [p.coverage for p in curve.points]
        assert covs == sorted(covs)

    def test_unknown_words_shrink_as_vocabulary_grows(self):
        c = make_corpus({"2019": [f"w{i}" for i in range(3000)]})
        curve = compute_coverage_curve(c)
        unknowns = [p.unknown_tokens_per_article for p in curve.points]
        assert unknowns == sorted(unknowns, reverse=True)

    def test_bands_share_of_distinct_sums_to_one(self):
        c = make_corpus({"2019": [f"w{i}" for i in range(1000)]})
        curve = compute_coverage_curve(c)
        assert sum(fs for _, _, fs, _ in curve.bands) == pytest.approx(1.0)
        assert sum(ts for _, _, _, ts in curve.bands) == pytest.approx(1.0)


class TestAB:
    def test_a_class_detected_in_corpus(self):
        c = make_corpus({"2019": ["however", "however", "argue", "research"]})
        ab = compute_ab(c)
        assert ab.a_tokens == 3  # however x2 + argue
        present = {w for w, _, _ in ab.present}
        assert {"however", "argue"} <= present

    def test_reuse_buckets_cover_all_present_candidates(self):
        c = make_corpus({"2019": ["however", "argue", "however"]})
        ab = compute_ab(c)
        assert sum(n for _, n, _ in ab.reuse_buckets) == len(ab.present)


class TestAGroups:
    def test_only_words_present_in_corpus_are_returned(self):
        c = make_corpus({"2019": ["however", "zzz"]})
        groups = compute_a_groups(c)
        words = {w for g in groups for w, _, _ in g.words}
        assert "however" in words
        assert "nevertheless" not in words, "未在语料出现的词不该进表"

    def test_groups_are_disjoint_in_total_count(self):
        c = make_corpus({"2019": ["however", "because", "moreover"]})
        groups = compute_a_groups(c)
        assert a_group_total(groups) == 3

    def test_phrases_are_stripped_before_matching(self):
        """`in spite of` 会被切分成 in/spite/of，必须靠 A_STOP 滤掉功能词。"""
        c = make_corpus({"2019": ["in", "spite", "of", "however"]})
        groups = compute_a_groups(c)
        words = {w for g in groups for w, _, _ in g.words}
        assert "in" not in words and "of" not in words


class TestCleanAWords:
    def test_removes_stopwords_and_short_fragments(self):
        assert lexicon.clean_a_words({"however", "in", "of", "as", "by"}) == {"however"}

    def test_keeps_content_words(self):
        assert lexicon.clean_a_words({"nevertheless", "assumption"}) == {
            "nevertheless",
            "assumption",
        }


class TestAStopIsConsistent:
    def test_a_stop_contains_all_two_letter_phrase_fragments(self):
        """A 类组里出现过的多词短语碎片，必须都在 A_STOP 里，否则会污染词表。"""
        fragments = set()
        for _name, _hint, words in lexicon.A_GROUPS:
            for w in words:
                if len(w) < lexicon.A_MIN_LEN:
                    fragments.add(w)
        assert fragments <= lexicon.A_STOP


@requires_nltk
class TestEndToEndOnSample:
    def test_pipeline_runs_on_sample_corpus(self, sample_corpus_dir: pathlib.Path, syllabus_path: pathlib.Path):
        corpus = load_corpus(sample_corpus_dir, mode="blocks", token_mode="lemma")
        wl = load_wordlist(syllabus_path)
        stats = compute_stats(corpus, wl)

        assert len(stats.years) == 4
        assert stats.tokens_total > 0
        assert 0.0 < stats.mean_coverage_distinct <= 1.0
        assert 0.0 < stats.mean_coverage_weighted <= 1.0
        # 次数加权口径应当高于不同词口径
        assert stats.mean_coverage_weighted > stats.mean_coverage_distinct
        assert stats.dicts["wordlist_size"] == 5501

    def test_lemmatization_actually_merges_inflections(self, sample_corpus_dir: pathlib.Path):
        """样例里同时有 was / is / been，还原后应当只剩 be。"""
        corpus = load_corpus(sample_corpus_dir, mode="blocks", token_mode="lemma")
        assert "be" in corpus.frequency
        assert "was" not in corpus.frequency
        assert "been" not in corpus.frequency

    def test_surface_mode_keeps_inflections(self, sample_corpus_dir: pathlib.Path):
        surface = load_corpus(sample_corpus_dir, mode="blocks", token_mode="surface")
        lemma = load_corpus(sample_corpus_dir, mode="blocks", token_mode="lemma")

        # 表层形态保留为独立的键
        for form in ("was", "is", "been"):
            assert form in surface.frequency, form
        # 还原后它们全都并入 be，因此 lemma 口径的 is/was/been 应当消失
        for form in ("was", "been"):
            assert form not in lemma.frequency, form
        # 同一份语料，还原后词形数必定更少
        assert surface.distinct > lemma.distinct
