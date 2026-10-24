"""探针：常用不规则形式在 IRREGULAR 表里的覆盖情况。"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.lemmatize import IRREGULAR, lemma_candidates  # noqa: E402
from app import wordlist  # noqa: E402

# 常用不规则形式 → 期望原形
CASES = {
    "got": "get", "gotten": "get", "gets": "get", "getting": "get",
    "became": "become", "becomes": "become", "becoming": "become",
    "threw": "throw", "thrown": "throw",
    "rang": "ring", "rung": "ring",
    "sang": "sing", "sung": "sing",
    "sank": "sink", "sunk": "sink",
    "shrank": "shrink", "shrunk": "shrink",
    "sprang": "spring", "sprung": "spring",
    "swore": "swear", "sworn": "swear",
    "tore": "tear", "torn": "tear",
    "broke": "break", "broken": "break",
    "shook": "shake", "shaken": "shake",
    "froze": "freeze", "frozen": "freeze",
    "stole": "steal", "stolen": "steal",
    "forbade": "forbid", "forbidden": "forbid",
    "undertook": "undertake", "undertaken": "undertake",
    "withdrew": "withdraw", "withdrawn": "withdraw",
    "overcame": "overcome",
    "forgot": "forget", "forgotten": "forget",
    "arose": "arise", "arisen": "arise",
    "arose": "arise",
    "ate": "eat",
    "rode": "ride", "ridden": "ride",
    "woke": "wake", "woken": "wake",
    "lay": "lie", "lain": "lie",
    "laid": "lay",
    "hung": "hang",
    "struck": "strike",
    "strove": "strive",
    "wove": "weave", "woven": "weave",
    "dug": "dig",
    "spun": "spin",
    "won": "win",
    "shone": "shine",
    "slain": "slay",
    "smote": "smite",
    "thriven": "thrive",
}

out: list[str] = []
missing: list[str] = []
for w, want in sorted(CASES.items()):
    cands = lemma_candidates(w)
    hit = want in cands
    # 原形本身在不在六档里（在的话说明这个词确实该被识别）
    _lm, mask = wordlist.lookup(want)
    in_wl = bool(mask)
    tag = "OK" if hit else "缺候选"
    if not hit:
        missing.append(w)
    out.append(f"  {w:<12}→ 期望 {want:<10}{tag:<8}候选={cands[:4]}"
               f"{'（原形在六档内）' if in_wl else ''}")

out.append("")
out.append(f"IRREGULAR 表现有 {len(IRREGULAR)} 条；缺候选的形式 {len(missing)} 个：{missing}")
print("\n".join(out))
sys.exit(1 if missing else 0)
