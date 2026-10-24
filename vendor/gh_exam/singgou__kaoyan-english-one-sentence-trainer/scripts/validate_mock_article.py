#!/usr/bin/env python3
"""Validate an original English-I-style reading article before presentation."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = SKILL_ROOT / "data" / "corpus.jsonl"
WORD_RE = re.compile(r"[A-Za-z]+(?:[’'-][A-Za-z]+)*")
CHINESE_RE = re.compile(r"[\u3400-\u9fff]")
MARKDOWN_LINE_RE = re.compile(r"^\s*(?:#{1,6}\s|[-*+]\s|```|>\s)", re.MULTILINE)
LOGIC_MARKERS = (
    "although",
    "because",
    "by contrast",
    "consequently",
    "despite",
    "however",
    "instead",
    "moreover",
    "nevertheless",
    "rather than",
    "therefore",
    "thus",
    "whereas",
    "while",
    "yet",
)


def words(text: str) -> list[str]:
    return [token.lower().replace("’", "'") for token in WORD_RE.findall(text)]


def paragraphs(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"\r?\n\s*\r?\n", text.strip()) if part.strip()]


def sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.strip())
    parts = re.split(r"(?<=[.!?])(?:[”’\"])?\s+(?=[A-Z“\"])", normalized)
    return [part.strip() for part in parts if part.strip()]


def ngrams(tokens: list[str], size: int) -> Iterable[tuple[str, ...]]:
    for index in range(max(0, len(tokens) - size + 1)):
        yield tuple(tokens[index : index + size])


def load_corpus_ngrams(path: Path, size: int) -> dict[tuple[str, ...], str]:
    index: dict[tuple[str, ...], str] = {}
    if not path.exists():
        return index
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid corpus JSON at {path}:{line_number}: {exc}") from exc
            record_id = str(record.get("id", f"line-{line_number}"))
            source_text = record.get("text") or record.get("original") or ""
            for gram in ngrams(words(str(source_text)), size):
                index.setdefault(gram, record_id)
    return index


def validate(
    text: str,
    *,
    corpus_path: Path | None = DEFAULT_CORPUS,
    min_words: int = 388,
    max_words: int = 452,
    ngram_size: int = 12,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    token_list = words(text)
    paragraph_list = paragraphs(text)
    sentence_list = sentences(text)
    sentence_lengths = [len(words(sentence)) for sentence in sentence_list]
    long_sentence_count = sum(length >= 30 for length in sentence_lengths)
    average_sentence_words = (
        round(sum(sentence_lengths) / len(sentence_lengths), 2) if sentence_lengths else 0.0
    )
    lower = text.lower()
    logic_markers = sorted(marker for marker in LOGIC_MARKERS if marker in lower)

    if not text.strip():
        errors.append("article is empty")
    if not min_words <= len(token_list) <= max_words:
        errors.append(
            f"word count {len(token_list)} is outside the required range {min_words}-{max_words}"
        )
    if not 4 <= len(paragraph_list) <= 10:
        errors.append(
            f"paragraph count {len(paragraph_list)} is outside the supported range 4-10"
        )
    elif not 5 <= len(paragraph_list) <= 8:
        warnings.append(
            f"paragraph count {len(paragraph_list)} is valid but outside the high-confidence target 5-8"
        )
    if CHINESE_RE.search(text):
        errors.append("article body contains Chinese characters")
    if MARKDOWN_LINE_RE.search(text):
        errors.append("article body contains a Markdown heading, list, quote, or code fence")
    if len(sentence_list) < 14 or len(sentence_list) > 26:
        warnings.append(
            f"sentence count {len(sentence_list)} is outside the corpus-centered target 14-26"
        )
    if average_sentence_words and not 18 <= average_sentence_words <= 30:
        warnings.append(
            f"average sentence length {average_sentence_words} is outside the target 18-30 words"
        )
    if long_sentence_count < 3:
        warnings.append("fewer than three sentences contain at least 30 words")
    elif long_sentence_count > 6:
        warnings.append("more than six sentences contain at least 30 words")
    if len(logic_markers) < 3:
        warnings.append("fewer than three distinct discourse markers were detected")

    shared_ngram: dict[str, Any] | None = None
    if corpus_path is not None:
        if not corpus_path.exists():
            errors.append(f"comparison corpus does not exist: {corpus_path}")
        else:
            corpus_index = load_corpus_ngrams(corpus_path, ngram_size)
            for gram in ngrams(token_list, ngram_size):
                source_id = corpus_index.get(gram)
                if source_id:
                    shared_ngram = {
                        "size": ngram_size,
                        "text": " ".join(gram),
                        "source_id": source_id,
                    }
                    errors.append(
                        f"article repeats a {ngram_size}-word sequence from {source_id}"
                    )
                    break

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "word_count": len(token_list),
            "paragraph_count": len(paragraph_list),
            "sentence_count": len(sentence_list),
            "average_sentence_words": average_sentence_words,
            "long_sentence_count_30_plus": long_sentence_count,
            "logic_markers": logic_markers,
            "shared_corpus_ngram": shared_ngram,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("article", type=Path, help="UTF-8 text file containing body paragraphs only")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--min-words", type=int, default=388)
    parser.add_argument("--max-words", type=int, default=452)
    parser.add_argument("--ngram-size", type=int, default=12)
    parser.add_argument("--strict", action="store_true", help="also fail when style warnings remain")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    if args.min_words <= 0 or args.max_words < args.min_words:
        raise SystemExit("invalid word-count range")
    if args.ngram_size < 8:
        raise SystemExit("ngram size must be at least 8")
    if not args.article.exists():
        raise SystemExit(f"article does not exist: {args.article}")
    report = validate(
        args.article.read_text(encoding="utf-8"),
        corpus_path=args.corpus,
        min_words=args.min_words,
        max_words=args.max_words,
        ngram_size=args.ngram_size,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["valid"]:
        return 1
    if args.strict and report["warnings"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
