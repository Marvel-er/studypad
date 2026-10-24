#!/usr/bin/env python3
"""Heuristically tag and rank English I long-sentence candidates.

The rules are deliberately conservative. They support retrieval and corpus
statistics; they are not a substitute for a full grammatical analysis.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


WORD_RE = re.compile(r"[A-Za-z]+(?:[’'-][A-Za-z]+)*")
TAG_RULE_VERSION = "2.0"

ACADEMIC_VERBS = {
    "address", "affect", "analyze", "analyse", "argue", "assess", "assume",
    "constitute", "demonstrate", "derive", "establish", "evaluate", "examine",
    "indicate", "interpret", "maintain", "observe", "propose", "reflect",
    "represent", "require", "reveal", "suggest", "undermine",
}

FAMILIAR_UNFAMILIAR = {
    "account", "address", "bear", "capital", "command", "discipline", "issue",
    "mean", "practice", "present", "render", "subject", "term", "value",
}

LOGICAL_CONNECTORS = {
    "accordingly", "although", "because", "consequently", "despite", "however",
    "instead", "moreover", "nevertheless", "otherwise", "therefore", "thus",
    "whereas", "while", "yet",
}

FIXED_COLLOCATIONS = (
    "account for", "as a result", "be subject to", "by contrast", "contribute to",
    "depend on", "give rise to", "in response to", "in terms of", "lead to",
    "rather than", "result in", "take into account",
)

ABSTRACT_SUBJECTS = {
    "ability", "assumption", "challenge", "change", "comparison", "concept",
    "development", "evidence", "fact", "failure", "growth", "idea", "impact",
    "importance", "possibility", "practice", "problem", "process", "question",
    "requirement", "result", "role", "tendency", "trend", "use", "value",
}

TO_BASE_VERBS = {
    "achieve", "address", "affect", "allow", "analyze", "analyse", "argue",
    "assess", "avoid", "be", "become", "believe", "build", "change", "choose",
    "claim", "combine", "compare", "consider", "continue", "control", "create",
    "deal", "decide", "define", "demonstrate", "develop", "do", "enable",
    "encourage", "establish", "evaluate", "examine", "explain", "find", "focus",
    "follow", "give", "have", "help", "identify", "improve", "increase",
    "interpret", "keep", "learn", "maintain", "make", "measure", "meet", "offer",
    "prevent", "produce", "protect", "provide", "reduce", "reflect", "remain",
    "represent", "require", "respond", "reveal", "show", "solve", "suggest",
    "support", "take", "treat", "understand", "use", "work",
}


def _non_finite_signal_count(text: str) -> int:
    """Count relatively strong non-finite signals, avoiding ordinary past tense."""
    lower = text.lower().replace("’", "'")
    base_pattern = "|".join(sorted(map(re.escape, TO_BASE_VERBS), key=len, reverse=True))
    patterns = (
        rf"\bto\s+(?:not\s+)?(?:{base_pattern})\b",
        r"\b(?:by|after|before|without|while|instead of)\s+[a-z]{4,}ing\b",
        r"\b(?:being|having)\s+(?:been\s+)?[a-z]+\b",
        r"(?:^|[,;:]\s+)(?:not\s+)?[a-z]{4,}ing\b",
        r"(?:^|[,;:]\s+)(?:not\s+)?[a-z]{3,}ed\b",
        r"\b(?:a|an|the|this|that|these|those|people|workers|systems|rules|methods|companies|researchers)\s+[a-z]{3,}ed\s+(?:by|in|to|with|for|from)\b",
    )
    return sum(len(re.findall(pattern, lower)) for pattern in patterns)


def words(text: str) -> list[str]:
    """Return normalized word tokens."""
    return [token.lower().replace("’", "'") for token in WORD_RE.findall(text)]


def _contains_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def grammar_tags(text: str) -> list[str]:
    """Return conservative grammar candidates in stable display order."""
    lower = text.lower().replace("’", "'")
    tokens = words(text)
    tags: set[str] = set()

    if _contains_any(
        lower,
        (
            r"\bwho(?:m|se)?\b", r"\bwhich\b", r"\bwhereby\b",
            r"\bwherein\b",
            r"\b(?:the|a|an|this|these|those|each|any|some|no)\s+"
            r"(?!(?:fact|idea|claim|evidence|possibility|question|argument|belief|assumption|view|notion|hope|news)\b)"
            r"(?:[a-z][a-z'-]*\s+){0,2}[a-z][a-z'-]*\s+that\s+"
            r"(?:(?:he|she|it|they|we|you|i|[a-z]+s?)\s+)?"
            r"(?:is|are|was|were|has|have|had|can|could|will|would|may|might|do|does|did|[a-z]+ed|[a-z]+s)\b",
        ),
    ):
        tags.add("relative_clause")

    if _contains_any(
        lower,
        (
            r"\b(?:whether|whatever|whoever|whichever)\b",
            r"\b(?:argue|assume|believe|claim|demonstrate|find|hold|indicate|maintain|mean|show|suggest|think)\w*\s+that\b",
            r"\b(?:fact|idea|assumption|claim|evidence|possibility|question)\s+that\b",
            r"^(?:what|why|how|whether)\b",
        ),
    ):
        tags.add("noun_clause")

    if _contains_any(
        lower,
        (
            r"\b(?:although|though|even though|whereas|while|because|since|unless|until|once|whenever|wherever)\b",
            r"\bif\b", r"\bso that\b", r"\bin order that\b", r"\bprovided that\b",
        ),
    ):
        tags.add("adverbial_clause")

    if _non_finite_signal_count(text):
        tags.add("non_finite")

    if re.search(
        r"\b(?:am|is|are|was|were|be|been|being|get|gets|got)\s+(?:\w+ly\s+)?(?:\w+ed|built|bought|caught|drawn|found|given|held|known|made|paid|seen|shown|taught|thought|written)\b",
        lower,
    ):
        tags.add("passive_voice")

    if any(mark in text for mark in ("—", "–", "--", "(", ")")):
        tags.add("parenthetical")

    if re.search(r",\s+(?:an?|the)\s+[A-Za-z][^,]{2,80},", text):
        tags.add("apposition")

    if _contains_any(
        lower,
        (r"\bmore\b.{0,50}\bthan\b", r"\bless\b.{0,50}\bthan\b", r"\bas\b.{1,50}\bas\b", r"\bthe\s+more\b", r"\bthan\s+(?:is|are|was|were|do|does|did)\b"),
    ):
        tags.add("comparison")

    if re.search(r"^(?:never|nor|neither|not only|only (?:then|when|after|by|in)|rarely|seldom|little)\b", lower):
        tags.add("inversion")

    conjunctions = len(re.findall(r"\b(?:and|but|or|nor|yet)\b", lower))
    if conjunctions >= 2 or re.search(r"\bnot only\b.+\bbut also\b", lower):
        tags.add("coordination")

    if len(re.findall(r"\b(?:of|for|in|on|with|by|from|about|between|among)\b", lower)) >= 3:
        tags.add("prepositional_postmodifier")

    if tokens and tokens[0] in ABSTRACT_SUBJECTS:
        tags.add("abstract_subject")
    elif len(tokens) >= 2 and tokens[0] in {"the", "this", "that"} and tokens[1] in ABSTRACT_SUBJECTS:
        tags.add("abstract_subject")

    if len(re.findall(r"\b(?:it|its|they|their|this|that|these|those|which)\b", lower)) >= 3:
        tags.add("complex_reference")

    if re.search(r"\b(?:do|does|did)\s+not\s+(?:think|believe|suppose|imagine|expect)\b", lower):
        tags.add("negation_transfer")

    order = [
        "relative_clause", "noun_clause", "adverbial_clause", "non_finite",
        "passive_voice", "parenthetical", "apposition", "comparison", "inversion",
        "coordination", "prepositional_postmodifier", "abstract_subject",
        "complex_reference", "negation_transfer",
    ]
    return [tag for tag in order if tag in tags]


def vocabulary_tags(text: str) -> list[str]:
    lower = text.lower().replace("’", "'")
    token_set = set(words(text))
    tags: list[str] = []
    if token_set & ACADEMIC_VERBS:
        tags.append("academic_verb")
    if token_set & FAMILIAR_UNFAMILIAR:
        tags.append("familiar_word_unfamiliar_meaning")
    if any(re.search(r"(?:tion|sion|ment|ness|ity|ism|ance|ence)$", token) for token in token_set):
        tags.append("abstract_noun")
    if token_set & LOGICAL_CONNECTORS:
        tags.append("logical_connector")
    if any(phrase in lower for phrase in FIXED_COLLOCATIONS):
        tags.append("fixed_collocation")
    return tags


def difficulty_features(text: str, tags: list[str] | None = None) -> dict[str, Any]:
    tags = tags if tags is not None else grammar_tags(text)
    count = len(words(text))
    clause_markers = len(
        re.findall(
            r"\b(?:that|which|who|whom|whose|where|when|whether|if|although|though|because|since|unless|while|whereas)\b",
            text,
            re.IGNORECASE,
        )
    )
    punctuation_layers = len(re.findall(r"[;:—–()]", text))
    non_finite_signals = _non_finite_signal_count(text)
    return {
        "word_count": count,
        "clause_markers": clause_markers,
        "non_finite_signals": non_finite_signals,
        "punctuation_layers": punctuation_layers,
        "tag_count": len(tags),
    }


def difficulty_level(text: str, tags: list[str] | None = None) -> tuple[int, dict[str, Any]]:
    tags = tags if tags is not None else grammar_tags(text)
    features = difficulty_features(text, tags)
    word_count = features["word_count"]

    score = 0.0
    if word_count >= 18:
        score += 0.6
    if word_count >= 28:
        score += 0.7
    if word_count >= 40:
        score += 0.7
    if word_count >= 55:
        score += 0.4

    structural = {
        "relative_clause", "noun_clause", "adverbial_clause", "non_finite",
        "passive_voice", "apposition", "comparison", "inversion",
        "prepositional_postmodifier", "abstract_subject", "complex_reference",
    }
    score += min(2.2, 0.42 * len(set(tags) & structural))
    score += min(0.8, 0.2 * features["clause_markers"])
    score += min(0.6, 0.15 * features["punctuation_layers"])
    if len(set(tags) & {"relative_clause", "noun_clause", "adverbial_clause"}) >= 2:
        score += 0.5
    if "parenthetical" in tags and len(tags) >= 3:
        score += 0.35

    if score < 0.8:
        level = 1
    elif score < 1.8:
        level = 2
    elif score < 3.0:
        level = 3
    elif score < 4.4:
        level = 4
    else:
        level = 5
    features["difficulty_score"] = round(score, 2)
    return level, features


def classify(text: str) -> dict[str, Any]:
    g_tags = grammar_tags(text)
    level, features = difficulty_level(text, g_tags)
    return {
        "word_count": len(words(text)),
        "difficulty": level,
        "difficulty_features": features,
        "grammar_tags": g_tags,
        "vocabulary_tags": vocabulary_tags(text),
        "tag_confidence": None,
        "tag_review_status": "heuristic_unreviewed",
        "tag_rule_version": TAG_RULE_VERSION,
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return records


def _write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="classify one sentence")
    source.add_argument("--input", type=Path, help="annotate a JSONL corpus in place or to --output")
    parser.add_argument("--output", type=Path, help="output JSONL path; defaults to replacing --input")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    if args.text is not None:
        print(json.dumps(classify(args.text), ensure_ascii=False, indent=2))
        return 0

    records = _read_jsonl(args.input)
    for record in records:
        record.update(classify(record["original"]))
    _write_jsonl(args.output or args.input, records)
    print(f"classified {len(records)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
