"""命令行入口。

子命令一览::

    python -m npee_vocab extract     PDF -> raw/*.txt
    python -m npee_vocab stats       主统计 -> stats.json + 报告 + 高频内容词表
    python -m npee_vocab coverage    token 覆盖率曲线（不依赖词表）
    python -m npee_vocab reading     阅读生词密度
    python -m npee_vocab tiers       分层复习清单（T0–T4）
    python -m npee_vocab a-list      A 类词表（按功能分组）
    python -m npee_vocab ab          A / B 类词假设检验
    python -m npee_vocab all         全部产出写入 reports/
    python -m npee_vocab compare-modes  量化两条清洗路径 / 两种切词口径的差异

**所有路径都是命令行参数，没有任何硬编码**——这也是这个仓库存在的理由之一。
"""

from __future__ import annotations

import argparse
import pathlib
import sys

from .analysis import (
    a_group_total,
    compute_a_groups,
    compute_ab,
    compute_coverage_curve,
    compute_reading,
    compute_stats,
    compute_tiers,
    compute_yearly,
    load_corpus,
)
from .corpus import year_files
from .wordlist import load_wordlist

# 仓库根目录：src/npee_vocab/cli.py -> src/npee_vocab -> src -> <root>
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_WORDLIST = REPO_ROOT / "data" / "kaoyan_syllabus_verified.txt"
DEFAULT_CORPUS = REPO_ROOT / "raw"
DEFAULT_PDFS = REPO_ROOT / "pdfs"
DEFAULT_REPORTS = REPO_ROOT / "reports"


def _corpus_info(corpus) -> str:
    return (
        f"[管线] 清洗={corpus.mode}  切词={corpus.token_mode}  "
        f"年份={len(corpus.years)}  词元={corpus.total_tokens:,}  "
        f"不同词形={corpus.distinct:,}"
    )


def _load(args, token_mode: str):
    corpus_dir = pathlib.Path(args.corpus_dir)
    if not year_files(corpus_dir):
        sys.exit(
            f"错误：{corpus_dir} 下没有找到任何 <年份>.txt。\n"
            "先跑 `python -m npee_vocab extract --pdf-dir <真题PDF目录>`，\n"
            "或用 `--corpus-dir examples/sample_corpus` 跑合成样例。"
        )
    return load_corpus(corpus_dir, mode=args.clean_mode, token_mode=token_mode)


def _token_mode(args, default: str) -> str:
    """子命令各自的默认切词口径，可被 ``--token-mode`` 覆盖。"""
    return args.token_mode or default


def _wordlist(args):
    path = pathlib.Path(args.wordlist)
    wl = load_wordlist(path)
    if not wl.words:
        sys.exit(f"错误：词表 {path} 不存在或为空。")
    return wl


def _write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"  已写入 {path}")


def _report_dir(args) -> pathlib.Path:
    return pathlib.Path(args.output_dir)


# --------------------------------------------------------------------------
# 子命令
# --------------------------------------------------------------------------


def cmd_extract(args) -> int:
    """PDF -> raw/*.txt。需要 pymupdf。"""
    try:
        import pymupdf
    except ImportError:
        sys.exit("错误：extract 需要 pymupdf。pip install pymupdf")

    pdf_dir = pathlib.Path(args.pdf_dir)
    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"错误：{pdf_dir} 下没有 PDF。")

    out = pathlib.Path(args.corpus_dir)
    out.mkdir(parents=True, exist_ok=True)
    for pdf in pdfs:
        doc = pymupdf.open(pdf)
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        _write(out / f"{pdf.stem}.txt", text)
    print(f"共抽取 {len(pdfs)} 份试卷 -> {out}")
    return 0


def cmd_stats(args) -> int:
    corpus = _load(args, _token_mode(args, "lemma"))
    wl = _wordlist(args)
    stats = compute_stats(corpus, wl)
    yearly = compute_yearly(corpus)
    curve = compute_coverage_curve(corpus)

    from .render import render_content_words, render_report, render_stats_json

    out = _report_dir(args)
    _write(out / "stats.json", render_stats_json(stats))
    _write(out / "高频内容词表.md", render_content_words(stats, wl))
    _write(out / "统计报告.md", render_report(stats, yearly, curve, wl))

    print()
    print(f"  不同词口径覆盖率  {stats.mean_coverage_distinct:.1%}")
    print(f"  次数加权覆盖率    {stats.mean_coverage_weighted:.1%}")
    print(f"  恒定词            {len(stats.always)} 个")
    print(f"  高频内容词        {len(stats.content_words)} 个")
    print(f"  相邻年份 Jaccard  {yearly.mean_jaccard:.1%}"
          f"  重合系数 {yearly.mean_overlap_coefficient:.1%}")
    return 0


def cmd_coverage(args) -> int:
    corpus = _load(args, _token_mode(args, "lemma"))
    from .render import render_coverage

    print(render_coverage(compute_coverage_curve(corpus), _corpus_info(corpus)))
    return 0


def cmd_reading(args) -> int:
    corpus = _load(args, _token_mode(args, "lemma"))
    from .render import render_reading

    print(render_reading(compute_reading(corpus), _corpus_info(corpus)))
    return 0


def cmd_tiers(args) -> int:
    corpus = _load(args, _token_mode(args, "lemma"))
    wl = _wordlist(args)
    stats = compute_stats(corpus, wl)
    tiers = compute_tiers(stats)
    from .render import render_tiers

    _write(_report_dir(args) / "分层复习清单.md", render_tiers(tiers, stats))
    for tier in tiers.all():
        print(f"  {tier.key} {tier.label:<22}{len(tier.words):>5} 个")
    print(f"  合计{tiers.total:>28} 个")
    return 0


def cmd_a_list(args) -> int:
    # A 类词表**必须**用 surface 口径：它要区分 argue / argues / argued 的
    # 不同识别难度，还原成 argue 会把这个信息抹掉。
    corpus = _load(args, _token_mode(args, "surface"))
    wl = _wordlist(args)
    stats = compute_stats(corpus, wl)
    # 「出现年份」也取 surface 自身的年份数，与 freq 同源，避免跨口径混用。
    groups = compute_a_groups(corpus)
    ab = compute_ab(corpus)
    from .render import render_a_list

    _write(
        _report_dir(args) / "A类-逻辑与抽象词表.md",
        render_a_list(groups, stats, ab.a_per_article_distinct),
    )
    print(f"  分组覆盖 A 类词 {a_group_total(groups)} 个")
    for g in groups:
        print(f"    {g.name:<20}{len(g.words):>4} 个")
    return 0


def cmd_ab(args) -> int:
    corpus = _load(args, _token_mode(args, "surface"))
    from .render import render_ab

    print(render_ab(compute_ab(corpus), _corpus_info(corpus)))
    return 0


def cmd_all(args) -> int:
    for fn in (cmd_stats, cmd_tiers, cmd_a_list):
        rc = fn(args)
        if rc:
            return rc
    if args.also_stdout:
        for fn in (cmd_coverage, cmd_reading, cmd_ab):
            fn(args)
    return 0


def cmd_compare_modes(args) -> int:
    """量化「两条清洗路径 × 两种切词口径」的差异。

    这是本仓库的一个诚实性检查：上游项目里这些差异是隐式的，
    同一份报告的不同数字其实来自不同管线。
    """
    wl = _wordlist(args)
    corpus_dir = pathlib.Path(args.corpus_dir)
    if not year_files(corpus_dir):
        sys.exit(f"错误：{corpus_dir} 下没有语料。")

    header = (
        f"{'清洗':<8}{'切词':<9}{'词元':>9}{'不同词形':>10}"
        f"{'覆盖率(不同)':>14}{'覆盖率(加权)':>14}{'恒定词':>8}{'高频词':>8}"
    )
    print("=" * len(header))
    print("管线口径对比")
    print("=" * len(header))
    print(header)
    print("-" * len(header))
    for clean in ("blocks", "flat"):
        for tok in ("lemma", "surface"):
            corpus = load_corpus(corpus_dir, mode=clean, token_mode=tok)
            stats = compute_stats(corpus, wl)
            print(
                f"{clean:<8}{tok:<9}{stats.tokens_total:>9,}{stats.distinct_total:>10,}"
                f"{stats.mean_coverage_distinct:>13.2%}{stats.mean_coverage_weighted:>14.2%}"
                f"{len(stats.always):>8}{len(stats.content_words):>8}"
            )
    print()
    print("说明：")
    print("  blocks  先切连续散文块（>=3 行且 >=40 词），块内丢 Directions 续行。")
    print("  flat    逐行过滤，不做块级筛选。会留下题干与选项行。")
    print("  lemma   词形还原后统计（was->be）。counting 类分析的默认口径。")
    print("  surface 不做还原。区分 argue/argues/argued，A 类词表用这条。")
    return 0


# --------------------------------------------------------------------------
# 参数解析
# --------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="npee-vocab",
        description="考研英语（一）真题词汇统计",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--version", action="version", version="npee-vocab 1.0.0")

    sub = ap.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument(
            "--corpus-dir",
            default=str(DEFAULT_CORPUS),
            help="存放 <年份>.txt 的目录（默认 ./raw）",
        )
        p.add_argument(
            "--wordlist",
            default=str(DEFAULT_WORDLIST),
            help="大纲词表（默认 data/kaoyan_syllabus_verified.txt）",
        )
        p.add_argument(
            "--output-dir",
            default=str(DEFAULT_REPORTS),
            help="报告输出目录（默认 ./reports）",
        )
        p.add_argument(
            "--clean-mode",
            choices=("blocks", "flat"),
            default="blocks",
            help="语料清洗路径（默认 blocks，唯一符合「已剔除题干与选项」声明的口径）",
        )
        p.add_argument(
            "--token-mode",
            choices=("lemma", "surface"),
            default=None,
            help=(
                "切词口径。默认按子命令取：stats/coverage/reading/tiers 用 lemma"
                "（was->be，计数类分析的正确单位）；a-list/ab 用 surface"
                "（区分 argue/argues/argued）"
            ),
        )

    p = sub.add_parser("extract", help="PDF -> raw/*.txt")
    p.add_argument("--pdf-dir", default=str(DEFAULT_PDFS))
    p.add_argument("--corpus-dir", default=str(DEFAULT_CORPUS))
    p.set_defaults(func=cmd_extract)

    for name, func, help_text in [
        ("stats", cmd_stats, "主统计 -> stats.json + 报告 + 高频内容词表"),
        ("coverage", cmd_coverage, "token 覆盖率曲线（不依赖词表）"),
        ("reading", cmd_reading, "阅读生词密度"),
        ("tiers", cmd_tiers, "分层复习清单（T0–T4）"),
        ("a-list", cmd_a_list, "A 类词表（按功能分组）"),
        ("ab", cmd_ab, "A / B 类词假设检验"),
        ("compare-modes", cmd_compare_modes, "量化管线口径差异"),
    ]:
        sp = sub.add_parser(name, help=help_text)
        add_common(sp)
        sp.set_defaults(func=func)

    sp = sub.add_parser("all", help="全部产出写入 reports/")
    add_common(sp)
    sp.add_argument("--also-stdout", action="store_true", help="额外打印分析型子命令的输出")
    sp.set_defaults(func=cmd_all)

    return ap


def main(argv: list[str] | None = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    return args.func(args)
