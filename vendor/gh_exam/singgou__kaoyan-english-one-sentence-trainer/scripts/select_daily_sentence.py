#!/usr/bin/env python3
"""Select a difficulty-aware authentic sentence without exposing its answer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from contextlib import contextmanager
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = Path(
    os.environ.get(
        "KAOYAN_ENGLISH_ONE_DATA_DIR",
        Path.home() / ".codex" / "user-data" / "kaoyan-english-one-sentence-trainer",
    )
)
DEFAULT_CORPUS = SKILL_ROOT / "data" / "corpus.jsonl"
BUCKET_SCHEDULE = ("weak", "weak", "weak", "weak", "weak", "normal", "normal", "normal", "similar", "similar")


@contextmanager
def state_lock(data_dir: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    lock_path = data_dir / ".state.lock"
    with lock_path.open("a+b") as handle:
        if lock_path.stat().st_size == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with temp.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def recover_pending_selection(data_dir: Path) -> None:
    pending_path = data_dir / "pending_selection.json"
    if not pending_path.exists():
        return
    transaction = load_json(pending_path, {})
    if transaction.get("version") != 1:
        raise SystemExit("invalid pending sentence-selection transaction")
    progress = transaction.get("progress")
    active = transaction.get("active")
    if not isinstance(progress, dict) or not isinstance(active, dict):
        raise SystemExit("invalid pending sentence-selection state")
    atomic_json(data_dir / "progress.json", progress)
    atomic_json(data_dir / "active_session.json", active)
    pending_path.unlink(missing_ok=True)


def commit_selection(data_dir: Path, progress: dict[str, Any], active: dict[str, Any]) -> None:
    transaction = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "transaction_order": time.time_ns(),
        "progress": progress,
        "active": active,
    }
    atomic_json(data_dir / "pending_selection.json", transaction)
    recover_pending_selection(data_dir)


def load_corpus(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"corpus not found: {path}; run scripts/build_corpus.py first")
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid corpus JSON at line {line_number}: {exc}") from exc
    if not records:
        raise SystemExit("corpus is empty; rebuild it from the user-provided exam files")
    return records


def default_progress() -> dict[str, Any]:
    return {
        "version": 1,
        "current_difficulty": 3,
        "trained_sentence_ids": [],
        "recent_sentence_ids": [],
        "assigned_sentence_ids": [],
        "recent_years": [],
        "session_count": 0,
        "new_selection_count": 0,
        "profile_revision": 0,
        "sentence_scores": {},
        "last_error_tags": [],
    }


def _is_selectable(record: dict[str, Any], allow_unreviewed: bool) -> bool:
    # Completeness is an independent safety boundary: a cleanly extracted
    # sentence from an article with known missing paragraphs must never enter
    # daily training, even when the surviving sentence itself looks reliable.
    if record.get("safe_for_training") is not True:
        return False
    if record.get("source_status") != "user_provided_question_file":
        return False
    if record.get("provenance_status") not in {"source_unverified", "source_verified", "official_verified"}:
        return False
    source_name = Path(record.get("source_file", "")).name
    if "答案" in source_name or "解析" in source_name:
        return False
    text_status = str(record.get("text_status", ""))
    extraction_method = str(record.get("extraction_method", "")).lower()
    extraction_origin = str(record.get("extraction_origin", "")).lower()
    locator_kind = str(record.get("source_locator", {}).get("kind", "")).lower()
    ocr_tokens = ("ocr", "tesseract", "paddle", "easyocr", "rapidocr", "image_text", "scanned", "vision")
    extraction_signature = " ".join((source_name.lower(), extraction_method, locator_kind))
    has_ocr_signal = (
        text_status == "ocr_unverified"
        or extraction_origin == "ocr"
        or any(token in extraction_signature for token in ocr_tokens)
    )
    if has_ocr_signal and (text_status != "human_verified" or record.get("needs_manual_review", True)):
        return False
    if allow_unreviewed:
        if has_ocr_signal:
            return text_status == "human_verified" and not record.get("needs_manual_review", True)
        known_non_ocr_methods = {"pdfplumber", "python-docx", "raw-ooxml", "legacy-word-converter", "plain-text"}
        if extraction_origin and extraction_origin not in {"embedded_text", "document_text", "plain_text"}:
            return False
        if not extraction_origin and extraction_method not in known_non_ocr_methods:
            return False
        return text_status != "corrupt"
    return text_status in {"cross_checked", "human_verified"} and not record.get("needs_manual_review", True)


def safe_pending(active: dict[str, Any], by_id: dict[str, dict[str, Any]], allow_unreviewed: bool) -> dict[str, Any] | None:
    if active.get("stage") != "awaiting_answer":
        return None
    pending = by_id.get(active.get("sentence_id"))
    if pending is None or not _is_selectable(pending, allow_unreviewed):
        return None
    return pending


def _weak_tags(grammar: dict[str, Any]) -> set[str]:
    result = set()
    for tag, profile in grammar.items():
        attempts = int(profile.get("attempts", 0))
        wrong = int(profile.get("wrong", 0))
        if profile.get("level") in {"weak", "confused"} or (attempts >= 2 and wrong / attempts >= 0.4):
            result.add(tag)
    return result


def _stable_jitter(seed: str, sentence_id: str) -> float:
    digest = hashlib.sha256(f"{seed}|{sentence_id}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF * 0.05


def _candidate_score(
    record: dict[str, Any],
    current_difficulty: int,
    weak_tags: set[str],
    recent_years: list[int],
    similar_tags: set[str],
    bucket: str,
    seed: str,
) -> float:
    tags = set(record.get("grammar_tags", []))
    weak_match = len(tags & weak_tags) / max(1, len(weak_tags))
    similar_match = len(tags & similar_tags) / max(1, len(similar_tags))
    difficulty_fit = 1.0 - min(1.0, abs(int(record.get("difficulty", 3)) - current_difficulty) / 2)
    year_diversity = 0.0 if record.get("year") in recent_years[-2:] else 1.0
    structure = min(1.0, len(tags) / 5)
    if bucket == "weak":
        bucket_value = weak_match
    elif bucket == "similar":
        bucket_value = similar_match
    else:
        bucket_value = 0.5 * year_diversity + 0.5 * structure
    return (
        0.50 * bucket_value
        + 0.25 * difficulty_fit
        + 0.15 * year_diversity
        + 0.10 * structure
        + _stable_jitter(seed, record["id"])
    )


def choose_new(
    corpus: list[dict[str, Any]],
    progress: dict[str, Any],
    grammar: dict[str, Any],
    allow_unreviewed: bool,
    seed: str,
) -> tuple[dict[str, Any], str, str | None]:
    trained = set(progress.get("trained_sentence_ids", []))
    recent = set(progress.get("recent_sentence_ids", [])[-15:])
    current = max(1, min(5, int(progress.get("current_difficulty", 3))))
    weak = _weak_tags(grammar)
    similar = set(progress.get("last_error_tags", []))
    bucket = BUCKET_SCHEDULE[int(progress.get("new_selection_count", 0)) % len(BUCKET_SCHEDULE)]
    fallback: str | None = None
    if bucket == "weak" and not weak:
        bucket = "normal"
        fallback = "no_weak_profile_yet"
    elif bucket == "similar" and not similar:
        bucket = "normal"
        fallback = "no_recent_error_tags"

    base = [
        record for record in corpus
        if _is_selectable(record, allow_unreviewed)
        and record["id"] not in trained
        and record["id"] not in recent
        and int(record.get("word_count", 0)) >= 15
        and int(record.get("difficulty", 1)) >= 2
        and abs(int(record.get("difficulty", 3)) - current) <= 1
    ]
    if not base:
        base = [
            record for record in corpus
            if _is_selectable(record, allow_unreviewed)
            and record["id"] not in trained
            and record["id"] not in recent
            and int(record.get("word_count", 0)) >= 15
            and int(record.get("difficulty", 1)) >= 2
        ]
    if not base:
        raise SystemExit("no eligible new sentence remains; review old sentences or manually verify more corpus records")

    if bucket == "weak" and weak:
        bucket_candidates = [record for record in base if set(record.get("grammar_tags", [])) & weak]
    elif bucket == "similar" and similar:
        bucket_candidates = [record for record in base if set(record.get("grammar_tags", [])) & similar]
    else:
        bucket_candidates = base
    if not bucket_candidates:
        bucket_candidates = base
        fallback = f"{bucket}_bucket_empty"

    recent_years = [int(year) for year in progress.get("recent_years", [])]
    selected = max(
        bucket_candidates,
        key=lambda record: _candidate_score(record, current, weak, recent_years, similar, bucket, seed),
    )
    return selected, bucket, fallback


def choose_review(
    corpus: list[dict[str, Any]],
    progress: dict[str, Any],
    allow_unreviewed: bool,
    exclude_ids: Iterable[str] = (),
) -> dict[str, Any] | None:
    by_id = {record["id"]: record for record in corpus}
    excluded = set(exclude_ids)
    scores = progress.get("sentence_scores", {})
    candidates = []
    today = date.today().isoformat()
    for sentence_id in progress.get("trained_sentence_ids", []):
        record = by_id.get(sentence_id)
        if record is None or sentence_id in excluded or not _is_selectable(record, allow_unreviewed):
            continue
        state = scores.get(sentence_id, {})
        due = state.get("next_review")
        due_priority = 1 if due and due <= today else 0
        total = float(state.get("last_total", 100))
        candidates.append((due_priority, -total, record))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1], item[2]["id"]), reverse=True)
    return candidates[0][2]


def public_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return only stage-A-safe fields."""
    return {
        "id": record["id"],
        "original": record["original"],
        "year": record["year"],
        "section": record["section"],
        "article": record["article"],
    }


def prompt_for(new_record: dict[str, Any] | None, review_record: dict[str, Any] | None = None) -> str:
    sections: list[str] = []
    if new_record is not None:
        sections.append(
            "### 今日长难句\n\n"
            f"> {new_record['original']}\n\n"
            f"来源：{new_record['year']} · {new_record['section']} · {new_record['article']}\n\n"
            "请先独立完成：\n"
            "1. 写出中文翻译；\n"
            "2. 找出主语和谓语；\n"
            "3. 写出句子主干；\n"
            "4. 判断从句或非谓语；\n"
            "5. 列出不认识或不确定的词。"
        )
    if review_record is not None:
        sections.append(
            "### 旧错句快速复习\n\n"
            f"> {review_record['original']}\n\n"
            f"来源：{review_record['year']} · {review_record['section']} · {review_record['article']}\n\n"
            "先重新翻译并写出主干，不查看上次讲解。"
        )
    return "\n\n".join(sections)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--corpus", type=Path, help="override corpus path")
    parser.add_argument("--mode", choices=("new", "review", "daily"), default="new")
    parser.add_argument("--format", choices=("prompt", "json"), default="prompt")
    parser.add_argument("--commit", action="store_true", help="persist the pending session and anti-repeat state")
    parser.add_argument("--force-new", action="store_true", help="replace an existing awaiting-answer session")
    parser.add_argument("--allow-unreviewed", action="store_true", help="allow single-source or fuzzy-matched text; never allows unverified OCR")
    parser.add_argument("--seed", help="stable tie-break seed for tests; defaults to study date and profile revision")
    return parser


def _run(args: argparse.Namespace) -> int:
    data_dir = args.data_dir.resolve()
    from update_progress import recover_state_transactions

    recover_state_transactions(data_dir)
    corpus = load_corpus((args.corpus or DEFAULT_CORPUS).resolve())
    by_id = {record["id"]: record for record in corpus}
    progress_path = data_dir / "progress.json"
    active_path = data_dir / "active_session.json"
    progress = load_json(progress_path, default_progress())
    grammar = load_json(data_dir / "grammar_profile.json", {})
    active = load_json(active_path, {})

    if not args.force_new:
        pending = safe_pending(active, by_id, args.allow_unreviewed)
        if pending is not None:
            payload = {"stage": "awaiting_answer", "reused_pending": True, "new": public_record(pending), "review": None}
            print(prompt_for(pending) if args.format == "prompt" else json.dumps(payload, ensure_ascii=False, indent=2))
            return 0

    seed = args.seed or f"{date.today().isoformat()}|{progress.get('profile_revision', 0)}"
    new_record: dict[str, Any] | None = None
    review_record: dict[str, Any] | None = None
    bucket: str | None = None
    fallback: str | None = None
    if args.mode in {"new", "daily"}:
        new_record, bucket, fallback = choose_new(corpus, progress, grammar, args.allow_unreviewed, seed)
    if args.mode in {"review", "daily"}:
        review_record = choose_review(corpus, progress, args.allow_unreviewed, [new_record["id"]] if new_record else [])
        if args.mode == "review" and review_record is None:
            raise SystemExit("no completed sentence is available for review")

    if args.commit:
        issued = new_record or review_record
        assert issued is not None
        recent = list(progress.get("recent_sentence_ids", []))
        recent.append(issued["id"])
        progress["recent_sentence_ids"] = recent[-20:]
        assigned = list(progress.get("assigned_sentence_ids", []))
        if issued["id"] not in assigned:
            assigned.append(issued["id"])
        progress["assigned_sentence_ids"] = assigned
        recent_years = list(progress.get("recent_years", []))
        recent_years.append(int(issued["year"]))
        progress["recent_years"] = recent_years[-10:]
        if new_record is not None:
            progress["new_selection_count"] = int(progress.get("new_selection_count", 0)) + 1
        active = {
            "version": 1,
            "session_id": hashlib.sha256(f"{issued['id']}|{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16],
            "sentence_id": issued["id"],
            "review_sentence_id": review_record["id"] if review_record and new_record else None,
            "stage": "awaiting_answer",
            "mode": args.mode,
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "selection_bucket": bucket,
            "fallback_reason": fallback,
        }
        commit_selection(data_dir, progress, active)

    payload = {
        "stage": "awaiting_answer",
        "reused_pending": False,
        "new": public_record(new_record) if new_record else None,
        "review": public_record(review_record) if review_record else None,
        "selection_bucket": bucket,
        "fallback_reason": fallback,
    }
    if args.format == "prompt":
        print(prompt_for(new_record, review_record))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    with state_lock(args.data_dir.resolve()):
        return _run(args)


if __name__ == "__main__":
    raise SystemExit(main())
