#!/usr/bin/env python3
"""Record training results, summarize progress, back up, or reset study state."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
import zipfile
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = Path(
    os.environ.get(
        "KAOYAN_ENGLISH_ONE_DATA_DIR",
        Path.home() / ".codex" / "user-data" / "kaoyan-english-one-sentence-trainer",
    )
)
DEFAULT_CORPUS = SKILL_ROOT / "data" / "corpus.jsonl"
STATE_FILES = (
    "active_session.json",
    "progress.json",
    "vocabulary.json",
    "grammar_profile.json",
    "session_history.jsonl",
    "pending_update.json",
    "pending_selection.json",
    "pending_restore.json",
)
PENDING_STATE_FILES = {"pending_update.json", "pending_selection.json", "pending_restore.json"}
RESTORABLE_STATE_FILES = tuple(name for name in STATE_FILES if name not in PENDING_STATE_FILES)
SCORE_LIMITS = {
    "main_structure": 25,
    "grammar": 25,
    "word_meaning": 20,
    "completeness": 20,
    "chinese_expression": 10,
}


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


def atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with temp.open("wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    temp = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with temp.open("w", encoding="utf-8", newline="\n") as handle:
            if existing:
                handle.write(existing)
                if not existing.endswith("\n"):
                    handle.write("\n")
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


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
        "score_total": 0,
        "average_score": 0,
        "recent_scores": [],
        "recent_results": [],
        "sentence_scores": {},
        "error_counts": {},
        "last_error_tags": [],
    }


def load_corpus_index(data_dir: Path, corpus_path: Path | None = None) -> dict[str, dict[str, Any]]:
    local_corpus = data_dir / "corpus.jsonl"
    path = (corpus_path or (local_corpus if local_corpus.exists() else DEFAULT_CORPUS)).resolve()
    if not path.exists():
        raise SystemExit(f"corpus not found: {path}")
    result = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"invalid corpus JSON at line {line_number}: {exc}") from exc
            result[record["id"]] = record
    return result


def history_contains(path: Path, attempt_id: str) -> bool:
    if not path.exists():
        return False
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                if json.loads(line).get("attempt_id") == attempt_id:
                    return True
            except json.JSONDecodeError:
                continue
    return False


def _validate_pending_transaction(transaction: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, Any], str]:
    if transaction.get("version") != 1 or not isinstance(transaction.get("event"), dict):
        raise SystemExit("invalid pending study-state transaction")
    states = transaction.get("states")
    if not isinstance(states, dict):
        raise SystemExit("invalid pending study-state transaction states")
    allowed = {"progress.json", "vocabulary.json", "grammar_profile.json", "active_session.json"}
    if not set(states).issubset(allowed):
        raise SystemExit("pending transaction contains an unexpected state file")
    if any(not isinstance(payload, dict) for payload in states.values()):
        raise SystemExit("pending transaction state payloads must be JSON objects")
    event = transaction["event"]
    attempt_id = str(event.get("attempt_id", ""))
    if not attempt_id:
        raise SystemExit("pending transaction has no attempt ID")
    return states, event, attempt_id


def _commit_pending_transaction(data_dir: Path, transaction: dict[str, Any]) -> None:
    states, event, attempt_id = _validate_pending_transaction(transaction)
    for name, payload in states.items():
        atomic_json(data_dir / name, payload)
    history_path = data_dir / "session_history.jsonl"
    if not history_contains(history_path, attempt_id):
        append_jsonl(history_path, event)
    (data_dir / "pending_update.json").unlink(missing_ok=True)


def recover_pending_transaction(data_dir: Path) -> str | None:
    pending_path = data_dir / "pending_update.json"
    if not pending_path.exists():
        return None
    transaction = load_json(pending_path, {})
    _commit_pending_transaction(data_dir, transaction)
    return str(transaction["event"]["attempt_id"])


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


def _validate_pending_selection(transaction: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if transaction.get("version") != 1:
        raise SystemExit("invalid pending sentence-selection transaction")
    progress = transaction.get("progress")
    active = transaction.get("active")
    if not isinstance(progress, dict) or not isinstance(active, dict):
        raise SystemExit("invalid pending sentence-selection state")
    return progress, active


def _validated_restore_payloads(transaction: dict[str, Any]) -> dict[str, bytes]:
    if transaction.get("version") != 1:
        raise SystemExit("invalid pending restore transaction")
    payloads = transaction.get("payloads")
    if not isinstance(payloads, dict) or not set(payloads).issubset(RESTORABLE_STATE_FILES):
        raise SystemExit("invalid pending restore payloads")
    encoded: dict[str, bytes] = {}
    for name, text in payloads.items():
        if not isinstance(text, str):
            raise SystemExit(f"invalid pending restore data for {name}")
        try:
            if name.endswith(".jsonl"):
                for line in text.splitlines():
                    if line.strip():
                        json.loads(line)
            else:
                json.loads(text)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid pending restore data for {name}") from exc
        encoded[name] = text.encode("utf-8")
    return encoded


def _commit_pending_restore(data_dir: Path, transaction: dict[str, Any]) -> None:
    encoded = _validated_restore_payloads(transaction)
    for name in RESTORABLE_STATE_FILES:
        path = data_dir / name
        if name not in encoded and path.exists():
            path.unlink()
    for name, payload in encoded.items():
        atomic_bytes(data_dir / name, payload)
    (data_dir / "pending_restore.json").unlink(missing_ok=True)


def recover_pending_restore(data_dir: Path) -> None:
    pending_path = data_dir / "pending_restore.json"
    if not pending_path.exists():
        return
    _commit_pending_restore(data_dir, load_json(pending_path, {}))


def _transaction_sort_key(path: Path, payload: dict[str, Any]) -> tuple[int, int, str]:
    raw_order = payload.get("transaction_order")
    if isinstance(raw_order, int) and raw_order >= 0:
        logical_time = raw_order
    else:
        created_at = payload.get("created_at")
        if not isinstance(created_at, str) or not created_at:
            raise SystemExit(f"pending transaction has no valid order or created_at: {path.name}")
        try:
            parsed = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError("timezone is required")
            logical_time = int(parsed.timestamp() * 1_000_000_000)
        except ValueError as exc:
            raise SystemExit(f"pending transaction has invalid created_at: {path.name}") from exc
    return logical_time, path.stat().st_mtime_ns, path.name


def recover_state_transactions(data_dir: Path) -> str | None:
    recovered_attempt: str | None = None
    handlers = {
        "pending_update.json": _commit_pending_transaction,
        "pending_selection.json": lambda root, payload: _commit_pending_selection_payload(root, payload),
        "pending_restore.json": _commit_pending_restore,
    }
    while True:
        pending: list[tuple[tuple[int, int, str], str, dict[str, Any]]] = []
        for name in handlers:
            path = data_dir / name
            if path.exists():
                try:
                    payload = load_json(path, {})
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"invalid pending transaction JSON: {name}") from exc
                if name == "pending_update.json":
                    _validate_pending_transaction(payload)
                elif name == "pending_selection.json":
                    _validate_pending_selection(payload)
                else:
                    _validated_restore_payloads(payload)
                pending.append((_transaction_sort_key(path, payload), name, payload))
        if not pending:
            return recovered_attempt
        ordered = sorted(pending, key=lambda item: item[0])
        for previous, current in zip(ordered, ordered[1:]):
            if previous[0][:2] == current[0][:2]:
                raise SystemExit("pending transactions have an ambiguous identical order")
        _sort_key, name, payload = ordered[0]
        handlers[name](data_dir, payload)
        if name == "pending_update.json":
            recovered_attempt = str(payload.get("event", {}).get("attempt_id", "")) or recovered_attempt


def _commit_pending_selection_payload(data_dir: Path, transaction: dict[str, Any]) -> None:
    progress, active = _validate_pending_selection(transaction)
    atomic_json(data_dir / "progress.json", progress)
    atomic_json(data_dir / "active_session.json", active)
    (data_dir / "pending_selection.json").unlink(missing_ok=True)


def commit_transaction(data_dir: Path, states: dict[str, Any], event: dict[str, Any]) -> None:
    transaction = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "transaction_order": time.time_ns(),
        "states": states,
        "event": event,
    }
    atomic_json(data_dir / "pending_update.json", transaction)
    _commit_pending_transaction(data_dir, transaction)


def parse_pair(value: str, separator: str = "=") -> tuple[str, str]:
    if separator not in value:
        raise argparse.ArgumentTypeError(f"expected NAME{separator}VALUE, got: {value}")
    left, right = value.split(separator, 1)
    if not left.strip() or not right.strip():
        raise argparse.ArgumentTypeError(f"expected non-empty NAME{separator}VALUE")
    return left.strip(), right.strip()


def parse_word(value: str) -> tuple[str, str | None]:
    if "|" in value:
        word, meaning = value.split("|", 1)
        return word.strip(), meaning.strip() or None
    return value.strip(), None


def _vocab_status(entry: dict[str, Any], outcome: str) -> str:
    if outcome == "confused":
        return "confused"
    if outcome == "wrong":
        return "weak"
    if entry.get("correct_streak", 0) >= 3 and entry.get("wrong_count", 0) <= entry.get("correct_count", 0):
        return "mastered"
    if entry.get("encounters", 0) <= 1:
        return "new"
    return "learning"


def _review_days(status: str, correct_streak: int = 0) -> int:
    if status in {"weak", "confused"}:
        return 1
    if status == "mastered":
        return 30 if correct_streak >= 5 else 14
    return 3 if correct_streak <= 1 else 7


def update_vocabulary(
    vocabulary: dict[str, Any],
    items: list[tuple[str, str | None, str]],
    sentence_id: str,
    today: date,
) -> None:
    for raw_word, meaning, outcome in items:
        key = raw_word.lower().replace("’", "'").strip()
        if not key:
            continue
        entry = vocabulary.setdefault(
            key,
            {
                "word": raw_word,
                "status": "new",
                "encounters": 0,
                "wrong_count": 0,
                "correct_count": 0,
                "correct_streak": 0,
                "meanings_seen": [],
                "source_sentence_ids": [],
            },
        )
        entry["encounters"] = int(entry.get("encounters", 0)) + 1
        if outcome in {"wrong", "confused"}:
            entry["wrong_count"] = int(entry.get("wrong_count", 0)) + 1
            entry["correct_streak"] = 0
        else:
            entry["correct_count"] = int(entry.get("correct_count", 0)) + 1
            entry["correct_streak"] = int(entry.get("correct_streak", 0)) + 1
        if meaning and meaning not in entry.setdefault("meanings_seen", []):
            entry["meanings_seen"].append(meaning)
        if sentence_id not in entry.setdefault("source_sentence_ids", []):
            entry["source_sentence_ids"].append(sentence_id)
        entry["status"] = _vocab_status(entry, outcome)
        entry["last_seen"] = today.isoformat()
        entry["next_review"] = (today + timedelta(days=_review_days(entry["status"], entry["correct_streak"]))).isoformat()


def update_grammar(
    grammar_profile: dict[str, Any],
    outcomes: list[tuple[str, str]],
    today: date,
) -> None:
    for tag, outcome in outcomes:
        normalized = outcome.lower()
        if normalized not in {"correct", "right", "wrong", "incorrect"}:
            raise SystemExit(f"grammar outcome must be correct or wrong: {tag}={outcome}")
        entry = grammar_profile.setdefault(
            tag,
            {"attempts": 0, "wrong": 0, "correct_streak": 0, "level": "new"},
        )
        entry["attempts"] = int(entry.get("attempts", 0)) + 1
        if normalized in {"wrong", "incorrect"}:
            entry["wrong"] = int(entry.get("wrong", 0)) + 1
            entry["correct_streak"] = 0
        else:
            entry["correct_streak"] = int(entry.get("correct_streak", 0)) + 1
        attempts = entry["attempts"]
        wrong = entry["wrong"]
        if attempts < 2:
            level = "new"
        elif wrong / attempts >= 0.5:
            level = "weak"
        elif wrong / attempts >= 0.25 or entry["correct_streak"] < 3:
            level = "learning"
        else:
            level = "stable"
        entry["level"] = level
        entry["last_seen"] = today.isoformat()
        entry["next_review"] = (today + timedelta(days=1 if level == "weak" else 3 if level == "learning" else 7)).isoformat()


def adjust_difficulty(progress: dict[str, Any]) -> None:
    recent = progress.get("recent_results", [])[-3:]
    current = max(1, min(5, int(progress.get("current_difficulty", 3))))
    session_count = int(progress.get("session_count", 0))
    last_change = int(progress.get("last_level_change_session", 0))
    if session_count - last_change < 2:
        return
    if len(recent) >= 2 and all(item["total"] < 60 for item in recent[-2:]):
        progress["current_difficulty"] = max(1, current - 1)
        progress["last_level_change_session"] = session_count
        progress["last_level_change_reason"] = "two_scores_below_60"
        return
    if len(recent) >= 2 and all("predicate_identification" in item.get("errors", []) for item in recent[-2:]):
        progress["current_difficulty"] = max(1, current - 1)
        progress["last_level_change_session"] = session_count
        progress["last_level_change_reason"] = "repeated_predicate_error"
        return
    if len(recent) == 3 and all(item["total"] >= 75 and item["main_structure"] >= 18 for item in recent):
        progress["current_difficulty"] = min(5, current + 1)
        progress["last_level_change_session"] = session_count
        progress["last_level_change_reason"] = "three_stable_scores_at_or_above_75"


def record_result(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = args.data_dir.resolve()
    recover_state_transactions(data_dir)
    corpus = load_corpus_index(data_dir, getattr(args, "corpus", None))
    active_path = data_dir / "active_session.json"
    active = load_json(active_path, {})
    sentence_id = args.sentence_id or active.get("sentence_id")
    if not sentence_id:
        raise SystemExit("--sentence-id is required when there is no active session")
    if sentence_id not in corpus:
        raise SystemExit(f"sentence ID is not in corpus: {sentence_id}")
    attempt_id = args.attempt_id or active.get("session_id") or hashlib.sha256(
        f"{sentence_id}|{datetime.now(timezone.utc).isoformat()}".encode()
    ).hexdigest()[:20]
    history_path = data_dir / "session_history.jsonl"
    if not args.allow_nonactive:
        if (
            active.get("stage") == "completed"
            and active.get("sentence_id") == sentence_id
            and history_contains(history_path, attempt_id)
        ):
            return {"status": "duplicate_ignored", "attempt_id": attempt_id, "sentence_id": sentence_id}
        if active.get("stage") != "awaiting_answer":
            raise SystemExit("record requires an active awaiting-answer session; use --allow-nonactive explicitly")
        if active.get("sentence_id") != sentence_id:
            raise SystemExit("sentence ID does not match the active awaiting-answer session")

    scores = {
        "main_structure": args.main_structure,
        "grammar": args.grammar_score,
        "word_meaning": args.word_meaning,
        "completeness": args.completeness,
        "chinese_expression": args.chinese_expression,
    }
    for key, maximum in SCORE_LIMITS.items():
        value = scores[key]
        if value < 0 or value > maximum:
            raise SystemExit(f"{key} score must be between 0 and {maximum}")
    total = sum(scores.values())
    if history_contains(history_path, attempt_id):
        return {"status": "duplicate_ignored", "attempt_id": attempt_id, "sentence_id": sentence_id}

    today = date.today()
    progress_path = data_dir / "progress.json"
    vocabulary_path = data_dir / "vocabulary.json"
    grammar_path = data_dir / "grammar_profile.json"
    progress = load_json(progress_path, default_progress())
    vocabulary = load_json(vocabulary_path, {})
    grammar_profile = load_json(grammar_path, {})

    error_pairs = [parse_pair(value, ":") if ":" in value else (value, "") for value in args.error]
    error_codes = [code for code, _detail in error_pairs]
    grammar_outcomes = [parse_pair(value) for value in args.grammar]
    vocab_items = [(word, meaning, "wrong") for word, meaning in map(parse_word, args.wrong_word)]
    vocab_items += [(word, meaning, "correct") for word, meaning in map(parse_word, args.correct_word)]
    vocab_items += [(word, meaning, "confused") for word, meaning in map(parse_word, args.confused_word)]

    update_vocabulary(vocabulary, vocab_items, sentence_id, today)
    update_grammar(grammar_profile, grammar_outcomes, today)

    trained = list(progress.get("trained_sentence_ids", []))
    if sentence_id not in trained:
        trained.append(sentence_id)
    progress["trained_sentence_ids"] = trained
    progress["last_sentence_id"] = sentence_id
    progress["session_count"] = int(progress.get("session_count", 0)) + 1
    progress["score_total"] = int(progress.get("score_total", 0)) + total
    progress["average_score"] = round(progress["score_total"] / progress["session_count"], 2)
    recent_scores = list(progress.get("recent_scores", [])) + [total]
    progress["recent_scores"] = recent_scores[-20:]
    recent_results = list(progress.get("recent_results", [])) + [
        {"total": total, "main_structure": scores["main_structure"], "errors": error_codes, "date": today.isoformat()}
    ]
    progress["recent_results"] = recent_results[-20:]
    progress["last_error_tags"] = sorted({tag for tag, outcome in grammar_outcomes if outcome.lower() in {"wrong", "incorrect"}})
    for code in error_codes:
        counts = progress.setdefault("error_counts", {})
        counts[code] = int(counts.get(code, 0)) + 1

    sentence_state = progress.setdefault("sentence_scores", {}).setdefault(
        sentence_id, {"attempts": 0, "best_total": 0, "correct_streak": 0}
    )
    sentence_state["attempts"] = int(sentence_state.get("attempts", 0)) + 1
    sentence_state["last_total"] = total
    sentence_state["best_total"] = max(int(sentence_state.get("best_total", 0)), total)
    sentence_state["last_seen"] = today.isoformat()
    if total >= 75:
        sentence_state["correct_streak"] = int(sentence_state.get("correct_streak", 0)) + 1
    else:
        sentence_state["correct_streak"] = 0
    if total < 60:
        review_days = 1
    elif total < 75:
        review_days = 3
    else:
        review_days = min(30, 7 * max(1, sentence_state["correct_streak"]))
    sentence_state["next_review"] = (today + timedelta(days=review_days)).isoformat()

    progress["profile_revision"] = int(progress.get("profile_revision", 0)) + 1
    adjust_difficulty(progress)

    event = {
        "version": 1,
        "event": "graded",
        "attempt_id": attempt_id,
        "sentence_id": sentence_id,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "rubric": {key: {"score": value, "max": SCORE_LIMITS[key]} for key, value in scores.items()},
        "total": total,
        "errors": [{"code": code, "detail": detail} for code, detail in error_pairs],
        "grammar_outcomes": dict(grammar_outcomes),
        "wrong_words": [word for word, _meaning in map(parse_word, args.wrong_word)],
        "note": args.note,
    }
    active.update(
        {
            "sentence_id": sentence_id,
            "stage": "completed",
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "attempt_id": attempt_id,
            "total": total,
        }
    )
    commit_transaction(
        data_dir,
        {
            "progress.json": progress,
            "vocabulary.json": vocabulary,
            "grammar_profile.json": grammar_profile,
            "active_session.json": active,
        },
        event,
    )
    return {
        "status": "recorded",
        "attempt_id": attempt_id,
        "sentence_id": sentence_id,
        "total": total,
        "average_score": progress["average_score"],
        "current_difficulty": progress["current_difficulty"],
    }


def skip_active(args: argparse.Namespace) -> dict[str, Any]:
    data_dir = args.data_dir.resolve()
    recover_state_transactions(data_dir)
    active_path = data_dir / "active_session.json"
    active = load_json(active_path, {})
    corpus = load_corpus_index(data_dir, getattr(args, "corpus", None))
    sentence_id = args.sentence_id or active.get("sentence_id")
    if not sentence_id:
        raise SystemExit("there is no active sentence to skip")
    if sentence_id not in corpus:
        raise SystemExit(f"sentence ID is not in corpus: {sentence_id}")
    if active.get("stage") != "awaiting_answer":
        raise SystemExit("skip requires an active awaiting-answer session")
    if active.get("sentence_id") != sentence_id:
        raise SystemExit("sentence ID does not match the active awaiting-answer session")
    attempt_id = args.attempt_id or active.get("session_id") or hashlib.sha256(
        f"skip|{sentence_id}|{datetime.now(timezone.utc).isoformat()}".encode()
    ).hexdigest()[:20]
    history_path = data_dir / "session_history.jsonl"
    if history_contains(history_path, attempt_id):
        return {"status": "duplicate_ignored", "attempt_id": attempt_id, "sentence_id": sentence_id}
    event = {
        "version": 1,
        "event": "skipped",
        "attempt_id": attempt_id,
        "sentence_id": sentence_id,
        "reason": args.reason,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }
    active.update({"stage": "skipped", "skipped_at": event["recorded_at"], "reason": args.reason})
    commit_transaction(data_dir, {"active_session.json": active}, event)
    return {"status": "skipped", "sentence_id": sentence_id, "attempt_id": attempt_id}


def summarize(data_dir: Path) -> dict[str, Any]:
    progress = load_json(data_dir / "progress.json", default_progress())
    vocabulary = load_json(data_dir / "vocabulary.json", {})
    grammar = load_json(data_dir / "grammar_profile.json", {})

    weak_grammar = sorted(
        (
            {
                "tag": tag,
                "level": entry.get("level", "new"),
                "attempts": int(entry.get("attempts", 0)),
                "wrong": int(entry.get("wrong", 0)),
                "error_rate": round(int(entry.get("wrong", 0)) / max(1, int(entry.get("attempts", 0))), 3),
            }
            for tag, entry in grammar.items()
        ),
        key=lambda item: (item["level"] == "weak", item["error_rate"], item["attempts"]),
        reverse=True,
    )[:3]
    weak_words = sorted(
        (
            {
                "word": entry.get("word", key),
                "status": entry.get("status", "new"),
                "wrong_count": int(entry.get("wrong_count", 0)),
                "next_review": entry.get("next_review"),
            }
            for key, entry in vocabulary.items()
            if entry.get("status") in {"weak", "confused", "learning"}
        ),
        key=lambda item: (item["status"] in {"weak", "confused"}, item["wrong_count"]),
        reverse=True,
    )[:10]
    recent = progress.get("recent_scores", [])[-7:]
    if not recent:
        recommendation = "先从2—3级真题句开始，建立主干识别基线。"
    elif len(recent) >= 2 and all(score < 60 for score in recent[-2:]):
        recommendation = "降低一级并专项复习谓语、从句边界和基础词义。"
    elif sum(recent) / len(recent) >= 75:
        recommendation = "保持当前难度，优先攻克错误率最高的语法标签。"
    else:
        recommendation = "继续当前难度，先稳定主干和主要逻辑，再增加嵌套层次。"
    return {
        "trained_sentences": len(progress.get("trained_sentence_ids", [])),
        "session_count": int(progress.get("session_count", 0)),
        "average_score": progress.get("average_score", 0),
        "current_difficulty": int(progress.get("current_difficulty", 3)),
        "weakest_grammar": weak_grammar,
        "weakest_words": weak_words,
        "recent_7_scores": recent,
        "recommendation": recommendation,
    }


def backup_state(data_dir: Path, output: Path | None = None) -> Path:
    recover_state_transactions(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    output = output or data_dir / "backups" / f"study-state-{stamp}.zip"
    output = output.resolve()
    state_paths = {(data_dir / name).resolve() for name in STATE_FILES}
    if output in state_paths:
        raise SystemExit("backup output cannot overwrite a study-state file")
    if output.exists():
        raise SystemExit(f"backup output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    files = [data_dir / name for name in STATE_FILES if (data_dir / name).exists()]
    manifest = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files
        },
    }
    temp = output.with_name(f".{output.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        with zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, arcname=path.name)
            archive.writestr("backup_manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        with zipfile.ZipFile(temp) as archive:
            if archive.testzip() is not None:
                raise SystemExit("backup verification failed: damaged ZIP member")
            stored = json.loads(archive.read("backup_manifest.json"))
            for name, expected in stored.get("files", {}).items():
                actual = hashlib.sha256(archive.read(name)).hexdigest()
                if actual != expected:
                    raise SystemExit(f"backup verification failed for {name}")
        os.replace(temp, output)
    finally:
        temp.unlink(missing_ok=True)
    return output


def reset_state(args: argparse.Namespace) -> dict[str, Any]:
    if args.confirm != "RESET":
        raise SystemExit("reset refused: pass --confirm RESET exactly")
    data_dir = args.data_dir.resolve()
    recover_state_transactions(data_dir)
    backup = backup_state(data_dir)
    removed = []
    for name in STATE_FILES:
        path = data_dir / name
        if path.exists():
            path.unlink()
            removed.append(name)
    return {"status": "reset", "backup": str(backup), "removed": removed}


def restore_state(args: argparse.Namespace) -> dict[str, Any]:
    if args.confirm != "RESTORE":
        raise SystemExit("restore refused: pass --confirm RESTORE exactly")
    data_dir = args.data_dir.resolve()
    recover_state_transactions(data_dir)
    archive_path = args.archive.resolve()
    if not archive_path.is_file():
        raise SystemExit(f"backup archive not found: {archive_path}")

    restorable = set(RESTORABLE_STATE_FILES)
    restored_payloads: dict[str, bytes] = {}
    with zipfile.ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            raise SystemExit("restore refused: backup ZIP is damaged")
        if "backup_manifest.json" not in archive.namelist():
            raise SystemExit("restore refused: backup manifest is missing")
        manifest = json.loads(archive.read("backup_manifest.json"))
        files = manifest.get("files")
        if not isinstance(files, dict):
            raise SystemExit("restore refused: invalid backup manifest")
        for name, expected in files.items():
            if name not in restorable:
                raise SystemExit(f"restore refused: unexpected state file {name}")
            if name not in archive.namelist():
                raise SystemExit(f"restore refused: missing archive member {name}")
            payload = archive.read(name)
            if hashlib.sha256(payload).hexdigest() != expected:
                raise SystemExit(f"restore refused: checksum mismatch for {name}")
            try:
                text = payload.decode("utf-8")
                if name.endswith(".jsonl"):
                    for line in text.splitlines():
                        if line.strip():
                            json.loads(line)
                else:
                    json.loads(text)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise SystemExit(f"restore refused: invalid state data in {name}") from exc
            restored_payloads[name] = payload

    safety_backup = backup_state(data_dir)
    transaction = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "transaction_order": time.time_ns(),
        "archive": str(archive_path),
        "safety_backup": str(safety_backup),
        "payloads": {name: payload.decode("utf-8") for name, payload in restored_payloads.items()},
    }
    atomic_json(data_dir / "pending_restore.json", transaction)
    _commit_pending_restore(data_dir, transaction)
    return {
        "status": "restored",
        "archive": str(archive_path),
        "safety_backup": str(safety_backup),
        "restored": sorted(restored_payloads),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--corpus", type=Path, help="corpus path; defaults to the installed Skill corpus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    record = subparsers.add_parser("record", help="record one completed, graded attempt")
    record.add_argument("--sentence-id")
    record.add_argument("--attempt-id", help="idempotency key; defaults to active session ID")
    record.add_argument("--main-structure", type=int, required=True)
    record.add_argument("--grammar-score", type=int, required=True)
    record.add_argument("--word-meaning", type=int, required=True)
    record.add_argument("--completeness", type=int, required=True)
    record.add_argument("--chinese-expression", type=int, required=True)
    record.add_argument("--grammar", action="append", default=[], metavar="TAG=correct|wrong")
    record.add_argument("--wrong-word", action="append", default=[], metavar="WORD|MEANING")
    record.add_argument("--correct-word", action="append", default=[], metavar="WORD|MEANING")
    record.add_argument("--confused-word", action="append", default=[], metavar="WORD|MEANING")
    record.add_argument("--error", action="append", default=[], metavar="CODE:DETAIL")
    record.add_argument("--note")
    record.add_argument("--allow-nonactive", action="store_true")

    skip = subparsers.add_parser("skip", help="mark the active sentence skipped without scoring it")
    skip.add_argument("--sentence-id")
    skip.add_argument("--attempt-id")
    skip.add_argument("--reason", default="user_requested_direct_explanation")

    summary = subparsers.add_parser("summary", help="show current learning progress")
    summary.add_argument("--format", choices=("json", "human"), default="human")

    backup = subparsers.add_parser("backup", help="create a ZIP backup of study state only")
    backup.add_argument("--output", type=Path)

    reset = subparsers.add_parser("reset", help="back up and remove study state; keep corpus and source files")
    reset.add_argument("--confirm", required=True)

    restore = subparsers.add_parser("restore", help="verify and restore a study-state ZIP; back up current state first")
    restore.add_argument("--archive", type=Path, required=True)
    restore.add_argument("--confirm", required=True)
    return parser


def _run(args: argparse.Namespace) -> int:
    if args.command in {"summary", "backup", "reset", "restore"}:
        recover_state_transactions(args.data_dir.resolve())
    if args.command == "record":
        payload = record_result(args)
    elif args.command == "skip":
        payload = skip_active(args)
    elif args.command == "summary":
        payload = summarize(args.data_dir.resolve())
        if args.format == "human":
            print(f"已训练句子：{payload['trained_sentences']}")
            print(f"平均分：{payload['average_score']}")
            print(f"当前难度：{payload['current_difficulty']}")
            print("最弱语法：" + ("、".join(item["tag"] for item in payload["weakest_grammar"]) or "暂无"))
            print("易忘词：" + ("、".join(item["word"] for item in payload["weakest_words"]) or "暂无"))
            print("最近7次：" + ("、".join(map(str, payload["recent_7_scores"])) or "暂无"))
            print("建议：" + payload["recommendation"])
            return 0
    elif args.command == "backup":
        payload = {"status": "backed_up", "path": str(backup_state(args.data_dir.resolve(), args.output))}
    elif args.command == "reset":
        payload = reset_state(args)
    else:
        payload = restore_state(args)
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
