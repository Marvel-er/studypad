"""把 probe_missing_words 量出的缺口词落成 gaps.json，供下载后验证。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import wordlist  # noqa: E402

WORDS = open(ROOT / "scripts" / "probe_missing_words.py", encoding="utf-8").read()
start = WORDS.index('WORDS = """') + len('WORDS = """')
end = WORDS.index('"""', start)
words = WORDS[start:end].split()

gaps = []
for w in sorted(set(words)):
    _lm, mask = wordlist.lookup(w)
    if mask:
        continue
    if wordlist.lookup_entry(w, "cet6"):
        continue
    gaps.append(w)

out = ROOT / "out" / "_gh_collins" / "gaps.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(gaps, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"缺口词 {len(gaps)} 个 → {out}")
print(" ".join(gaps))
