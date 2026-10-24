"""
六档能力画像（Level Profile）。

设计要点：切换等级 = 换一份参数，不改任何代码。
参数驱动四件事：标记什么、标多少、讲多深、用什么语言讲。
"""
from __future__ import annotations

# bit 位序（与 scripts/build_wordlists.py 一致）
LEVELS: list[dict] = [
    {
        "id": "high_school",
        "name": "高中",
        "en": "Senior High",
        "bit": 1,
        "vocab_note": "课标 3500",
        "tagline": "基础打牢，每个语法点都讲透",
        # 词频地板：比这个 rank 更常见的词视为已掌握，不标（避免划满等于没划）
        "min_freq_rank": 2000,
        # --- 词汇标记策略 ---
        "highlight_per_1000": 26,   # 本级考纲词：荧光笔上限
        "circle_per_1000": 16,      # 超纲常见词：红圈上限
        "deep_per_1000": 10,        # 超纲生僻词：天蓝虚线上限
        # --- 语法标注策略 ---
        "grammar_density": 0.75,    # 每句被语法标注的概率上限系数
        "grammar_max_per_para": 8,
        "sentence_split_min_words": 34,
        # --- 讲解 ---
        "explain": "zh",
        "explain_depth": 4,         # 1 最简 → 4 最详
        "show_translation": True,
        # --- 句型 ---
        "pattern_level": ["basic", "cet"],
    },
    {
        "id": "cet4",
        "name": "大学英语四级",
        "en": "CET-4",
        "bit": 2,
        "vocab_note": "大纲 4500",
        "tagline": "只圈你真的可能不认识的词",
        "min_freq_rank": 3000,
        "highlight_per_1000": 18,
        "circle_per_1000": 12,
        "deep_per_1000": 8,
        "grammar_density": 0.6,
        "grammar_max_per_para": 6,
        "sentence_split_min_words": 32,
        "explain": "zh",
        "explain_depth": 3,
        "show_translation": True,
        "pattern_level": ["basic", "cet"],
    },
    {
        "id": "cet6",
        "name": "大学英语六级",
        "en": "CET-6",
        "bit": 4,
        "vocab_note": "大纲 6000",
        "tagline": "标注变少，但每个都值得记",
        "min_freq_rank": 3800,
        "highlight_per_1000": 13,
        "circle_per_1000": 9,
        "deep_per_1000": 6,
        "grammar_density": 0.45,
        "grammar_max_per_para": 5,
        "sentence_split_min_words": 32,
        "explain": "zh",
        "explain_depth": 2,
        "show_translation": False,
        "pattern_level": ["cet", "advanced"],
    },
    {
        "id": "kaoyan",
        "name": "考研英语",
        "en": "Postgraduate",
        "bit": 8,
        "vocab_note": "大纲 5500",
        "tagline": "长难句是主战场",
        "min_freq_rank": 4200,
        "highlight_per_1000": 11,
        "circle_per_1000": 8,
        "deep_per_1000": 5,
        "grammar_density": 0.4,
        "grammar_max_per_para": 4,
        "sentence_split_min_words": 30,
        "explain": "zh",
        "explain_depth": 2,
        "show_translation": False,
        "pattern_level": ["cet", "advanced"],
    },
    {
        "id": "ielts",
        "name": "雅思",
        "en": "IELTS",
        "bit": 16,
        "vocab_note": "8000（含学术词表）",
        "tagline": "学术表达 + 写作加分句型",
        "min_freq_rank": 4800,
        "highlight_per_1000": 8,
        "circle_per_1000": 6,
        "deep_per_1000": 4,
        "grammar_density": 0.3,
        "grammar_max_per_para": 3,
        "sentence_split_min_words": 30,
        "explain": "bi",
        "explain_depth": 2,
        "show_translation": False,
        "pattern_level": ["advanced", "academic"],
    },
    {
        "id": "toefl",
        "name": "托福",
        "en": "TOEFL",
        "bit": 32,
        "vocab_note": "10000（含学术词表）",
        "tagline": "只留最精要的标记",
        "min_freq_rank": 5500,
        "highlight_per_1000": 5,
        "circle_per_1000": 4,
        "deep_per_1000": 3,
        "grammar_density": 0.2,
        "grammar_max_per_para": 2,
        "sentence_split_min_words": 28,
        "explain": "en",
        "explain_depth": 1,
        "show_translation": False,
        "pattern_level": ["academic"],
    },
]

BY_ID: dict[str, dict] = {lv["id"]: lv for lv in LEVELS}
ORDER: list[str] = [lv["id"] for lv in LEVELS]


def get(level_id: str) -> dict:
    return BY_ID.get(level_id, BY_ID["cet4"])


def known_mask(level_id: str) -> int:
    """返回该等级「已掌握词」的累积掩码：本级及以下所有档位的并集。"""
    idx = ORDER.index(level_id) if level_id in ORDER else 1
    return (1 << (idx + 1)) - 1


def own_mask(level_id: str) -> int:
    """返回该等级「本级考纲词」的掩码。"""
    return BY_ID[level_id]["bit"] if level_id in BY_ID else BY_ID["cet4"]["bit"]


def lower_mask(level_id: str) -> int:
    """返回严格低于该等级的所有档位掩码（用于识别「本级新增词」）。"""
    idx = ORDER.index(level_id) if level_id in ORDER else 1
    return (1 << idx) - 1
