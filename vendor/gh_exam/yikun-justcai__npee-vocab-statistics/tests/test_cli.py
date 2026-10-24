"""命令行冒烟测试。

这些用例锁住「CLI 能跑通、参数真的生效、默认口径不会静默走错」。
最后一个类是回归测试：A 类词表曾经因为默认拿到 lemma 口径而少算 46 个词。
"""

from __future__ import annotations

import json
import pathlib

import pytest

from conftest import requires_nltk
from npee_vocab.cli import main


@pytest.fixture
def sample_args(sample_corpus_dir: pathlib.Path, tmp_path: pathlib.Path) -> list[str]:
    return [
        "--corpus-dir",
        str(sample_corpus_dir),
        "--output-dir",
        str(tmp_path / "reports"),
    ]


class TestParser:
    def test_all_subcommands_registered(self):
        from npee_vocab.cli import build_parser

        ap = build_parser()
        actions = [a for a in ap._actions if hasattr(a, "choices") and a.choices]
        names = set()
        for a in actions:
            if a.dest == "command":
                names = set(a.choices)
        assert {
            "extract",
            "stats",
            "coverage",
            "reading",
            "tiers",
            "a-list",
            "ab",
            "all",
            "compare-modes",
        } <= names

    def test_missing_corpus_dir_exits_with_helpful_message(self, tmp_path: pathlib.Path, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["stats", "--corpus-dir", str(tmp_path / "nope")])
        assert "extract" in str(exc.value), "错误信息应当指路"

    def test_compare_modes_runs_without_corpus_option_conflicts(
        self, sample_corpus_dir: pathlib.Path, capsys
    ):
        rc = main(["compare-modes", "--corpus-dir", str(sample_corpus_dir)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "blocks" in out and "flat" in out
        assert "lemma" in out and "surface" in out


@requires_nltk
class TestSampleCorpusCommands:
    def test_stats_writes_expected_files(self, sample_args, capsys):
        rc = main(["stats", *sample_args])
        assert rc == 0
        out = pathlib.Path(sample_args[sample_args.index("--output-dir") + 1])
        for name in ("stats.json", "高频内容词表.md", "统计报告.md"):
            assert (out / name).is_file(), name

    def test_stats_json_is_wellformed(self, sample_args):
        main(["stats", *sample_args])
        out = pathlib.Path(sample_args[sample_args.index("--output-dir") + 1])
        data = json.loads((out / "stats.json").read_text(encoding="utf-8"))
        assert data["years"] == ["2019", "2020", "2021", "2022"]
        assert data["tokens_total"] > 0
        assert data["dicts"]["clean_mode"] == "blocks"
        assert data["dicts"]["token_mode"] == "lemma"

    def test_coverage_prints_curve(self, sample_args, capsys):
        assert main(["coverage", *sample_args]) == 0
        assert "覆盖率目标" in capsys.readouterr().out

    def test_reading_prints_distribution(self, sample_args, capsys):
        assert main(["reading", *sample_args]) == 0
        assert "出现年份数" in capsys.readouterr().out

    def test_tiers_writes_report(self, sample_args, capsys):
        assert main(["tiers", *sample_args]) == 0
        out = pathlib.Path(sample_args[sample_args.index("--output-dir") + 1])
        assert (out / "分层复习清单.md").is_file()

    def test_all_writes_every_report(self, sample_args):
        assert main(["all", *sample_args]) == 0
        out = pathlib.Path(sample_args[sample_args.index("--output-dir") + 1])
        for name in (
            "stats.json",
            "统计报告.md",
            "高频内容词表.md",
            "分层复习清单.md",
            "A类-逻辑与抽象词表.md",
        ):
            assert (out / name).is_file(), name


class TestTokenModeOverride:
    """默认口径必须按子命令走，且能被显式覆盖。"""

    def _recorded_mode(self, argv, sample_corpus_dir, tmp_path) -> str:
        out = tmp_path / "r"
        main(
            [
                *argv,
                "--corpus-dir",
                str(sample_corpus_dir),
                "--output-dir",
                str(out),
            ]
        )
        return json.loads((out / "stats.json").read_text(encoding="utf-8"))["dicts"]["token_mode"]

    @requires_nltk
    def test_stats_defaults_to_lemma(self, sample_corpus_dir, tmp_path):
        assert self._recorded_mode(["stats"], sample_corpus_dir, tmp_path) == "lemma"

    def test_explicit_override_wins(self, sample_corpus_dir, tmp_path):
        mode = self._recorded_mode(
            ["stats", "--token-mode", "surface"], sample_corpus_dir, tmp_path
        )
        assert mode == "surface"


@requires_nltk
class TestAListRegression:
    def test_a_list_does_not_use_lemma_by_default(self, sample_corpus_dir, tmp_path, capsys):
        """回归：A 类词表必须走 surface 口径。

        曾经因为子命令共用 lemma 默认值，A 类词从 140 个缩到 94 个。
        样例语料里 ``argues`` 只以变形出现，若被还原成 ``argue`` 就会换组，
        因此这里直接断言字形仍在表内。
        """
        assert main(
            [
                "a-list",
                "--corpus-dir",
                str(sample_corpus_dir),
                "--output-dir",
                str(tmp_path / "r"),
            ]
        ) == 0
        text = (tmp_path / "r" / "A类-逻辑与抽象词表.md").read_text(encoding="utf-8")
        assert "| however |" in text, "however 应出现在 A 类表中"
