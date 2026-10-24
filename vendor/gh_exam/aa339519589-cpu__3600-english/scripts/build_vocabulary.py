#!/usr/bin/env python3
"""Build the committed 3,600-word vocabulary dataset.

The source list is MIT-licensed and downloaded to work/gaozhong.txt. Difficulty
tiers use English usage frequency so the progression is independent of the
source list's alphabetical order.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from wordfreq import zipf_frequency


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work" / "gaozhong.txt"
OUTPUT = ROOT / "src" / "data" / "vocabulary.json"


SUPPLEMENTS = [
    ("analogy", "/əˈnælədʒi/", "n.", "类比；相似之处"),
    ("anticipate", "/ænˈtɪsɪpeɪt/", "v.", "预期；预料"),
    ("bewilder", "/bɪˈwɪldə(r)/", "v.", "使困惑"),
    ("coherent", "/kəʊˈhɪərənt/", "adj.", "连贯的；条理清楚的"),
    ("coincide", "/ˌkəʊɪnˈsaɪd/", "v.", "同时发生；一致"),
    ("collaborate", "/kəˈlæbəreɪt/", "v.", "合作；协作"),
    ("compelling", "/kəmˈpelɪŋ/", "adj.", "令人信服的；引人入胜的"),
    ("consecutive", "/kənˈsekjətɪv/", "adj.", "连续的"),
    ("contemplate", "/ˈkɒntəmpleɪt/", "v.", "深思；考虑"),
    ("controversy", "/ˈkɒntrəvɜːsi/", "n.", "争议；争论"),
    ("criterion", "/kraɪˈtɪəriən/", "n.", "标准；准则"),
    ("cumulative", "/ˈkjuːmjələtɪv/", "adj.", "累积的"),
    ("deliberate", "/dɪˈlɪbərət/", "adj./v.", "深思熟虑的；仔细考虑"),
    ("diminish", "/dɪˈmɪnɪʃ/", "v.", "减少；削弱"),
    ("discriminate", "/dɪˈskrɪmɪneɪt/", "v.", "区分；区别对待"),
    ("elaborate", "/ɪˈlæbərət/", "adj./v.", "精心制作的；详述"),
    ("empirical", "/ɪmˈpɪrɪkl/", "adj.", "以观察或实验为依据的"),
    ("encounter", "/ɪnˈkaʊntə(r)/", "v./n.", "遇到；邂逅"),
    ("endeavor", "/ɪnˈdevə(r)/", "v./n.", "努力；尽力"),
    ("equivalent", "/ɪˈkwɪvələnt/", "adj./n.", "相等的；等同物"),
    ("ethical", "/ˈeθɪkl/", "adj.", "道德的；合乎伦理的"),
    ("facilitate", "/fəˈsɪlɪteɪt/", "v.", "促进；使便利"),
    ("fluctuate", "/ˈflʌktʃueɪt/", "v.", "波动；起伏"),
    ("formulate", "/ˈfɔːmjuleɪt/", "v.", "制定；系统表达"),
    ("hypothesis", "/haɪˈpɒθəsɪs/", "n.", "假说；假设"),
    ("inevitable", "/ɪnˈevɪtəbl/", "adj.", "不可避免的"),
    ("infer", "/ɪnˈfɜː(r)/", "v.", "推断；推知"),
    ("integrate", "/ˈɪntɪɡreɪt/", "v.", "整合；融入"),
    ("interpret", "/ɪnˈtɜːprɪt/", "v.", "解释；理解"),
    ("intrinsic", "/ɪnˈtrɪnsɪk/", "adj.", "内在的；固有的"),
    ("justify", "/ˈdʒʌstɪfaɪ/", "v.", "证明……有道理"),
    ("manipulate", "/məˈnɪpjuleɪt/", "v.", "操控；熟练处理"),
    ("metaphor", "/ˈmetəfə(r)/", "n.", "隐喻；暗喻"),
    ("mutual", "/ˈmjuːtʃuəl/", "adj.", "相互的；共同的"),
    ("objective", "/əbˈdʒektɪv/", "adj./n.", "客观的；目标"),
    ("paradox", "/ˈpærədɒks/", "n.", "悖论；看似矛盾的事"),
    ("perceive", "/pəˈsiːv/", "v.", "察觉；理解"),
    ("perspective", "/pəˈspektɪv/", "n.", "视角；观点"),
    ("plausible", "/ˈplɔːzəbl/", "adj.", "看似合理的"),
    ("preliminary", "/prɪˈlɪmɪnəri/", "adj.", "初步的；预备的"),
    ("profound", "/prəˈfaʊnd/", "adj.", "深刻的；意义深远的"),
    ("reinforce", "/ˌriːɪnˈfɔːs/", "v.", "加强；巩固"),
    ("reluctant", "/rɪˈlʌktənt/", "adj.", "不情愿的；勉强的"),
    ("resilient", "/rɪˈzɪliənt/", "adj.", "有复原力的；坚韧的"),
    ("respective", "/rɪˈspektɪv/", "adj.", "各自的；分别的"),
    ("sustainable", "/səˈsteɪnəbl/", "adj.", "可持续的"),
    ("tentative", "/ˈtentətɪv/", "adj.", "试探性的；暂定的"),
    ("underlying", "/ˌʌndəˈlaɪɪŋ/", "adj.", "潜在的；根本的"),
    ("alter", "/ˈɔːltə(r)/", "v.", "改变；更改"),
    ("bias", "/ˈbaɪəs/", "n./v.", "偏见；使有偏向"),
    ("comprise", "/kəmˈpraɪz/", "v.", "由……组成；包含"),
    ("conceive", "/kənˈsiːv/", "v.", "构想；设想"),
    ("denote", "/dɪˈnəʊt/", "v.", "表示；指示"),
    ("derive", "/dɪˈraɪv/", "v.", "获得；起源于"),
    ("deviate", "/ˈdiːvieɪt/", "v.", "偏离；背离"),
    ("emerge", "/ɪˈmɜːdʒ/", "v.", "出现；显露"),
    ("enhance", "/ɪnˈhɑːns/", "v.", "提高；增强"),
    ("exceed", "/ɪkˈsiːd/", "v.", "超过；超出"),
    ("exclude", "/ɪkˈskluːd/", "v.", "排除；不包括"),
    ("imply", "/ɪmˈplaɪ/", "v.", "暗示；意味着"),
    ("incentive", "/ɪnˈsentɪv/", "n.", "激励；动机"),
    ("inhibit", "/ɪnˈhɪbɪt/", "v.", "抑制；阻碍"),
    ("innovate", "/ˈɪnəveɪt/", "v.", "创新；革新"),
    ("insight", "/ˈɪnsaɪt/", "n.", "洞察；深刻理解"),
    ("invoke", "/ɪnˈvəʊk/", "v.", "援引；唤起"),
    ("isolate", "/ˈaɪsəleɪt/", "v.", "使隔离；单独考虑"),
    ("maintain", "/meɪnˈteɪn/", "v.", "维持；坚持认为"),
    ("mediate", "/ˈmiːdieɪt/", "v.", "调解；促成"),
    ("modify", "/ˈmɒdɪfaɪ/", "v.", "修改；调整"),
    ("notion", "/ˈnəʊʃn/", "n.", "观念；想法"),
    ("orient", "/ˈɔːrient/", "v.", "使适应；确定方向"),
    ("persist", "/pəˈsɪst/", "v.", "坚持；持续存在"),
    ("phenomenon", "/fəˈnɒmɪnən/", "n.", "现象"),
    ("rational", "/ˈræʃnəl/", "adj.", "理性的；合理的"),
    ("refine", "/rɪˈfaɪn/", "v.", "改进；提炼"),
    ("regulate", "/ˈreɡjuleɪt/", "v.", "调节；管理"),
    ("relevant", "/ˈreləvənt/", "adj.", "相关的；切题的"),
    ("retain", "/rɪˈteɪn/", "v.", "保留；保持"),
    ("signify", "/ˈsɪɡnɪfaɪ/", "v.", "表示；意味着"),
    ("simulate", "/ˈsɪmjuleɪt/", "v.", "模拟；模仿"),
    ("subsequent", "/ˈsʌbsɪkwənt/", "adj.", "随后的；后来的"),
    ("undergo", "/ˌʌndəˈɡəʊ/", "v.", "经历；经受"),
    ("verify", "/ˈverɪfaɪ/", "v.", "核实；验证"),
    ("adaptation", "/ˌædæpˈteɪʃn/", "n.", "适应；改编"),
    ("adjacent", "/əˈdʒeɪsnt/", "adj.", "相邻的；邻近的"),
    ("aggregate", "/ˈæɡrɪɡət/", "n./v.", "总计；合计"),
    ("albeit", "/ˌɔːlˈbiːɪt/", "conj.", "尽管；即使"),
    ("analogous", "/əˈnæləɡəs/", "adj.", "相似的；可类比的"),
    ("attribute", "/əˈtrɪbjuːt/", "n./v.", "属性；把……归因于"),
    ("capacity", "/kəˈpæsəti/", "n.", "能力；容量"),
    ("compatible", "/kəmˈpætəbl/", "adj.", "兼容的；相容的"),
    ("constitute", "/ˈkɒnstɪtjuːt/", "v.", "构成；组成"),
    ("constraint", "/kənˈstreɪnt/", "n.", "限制；约束"),
]


# A handful of source rows are split across lines or omit delimiters. Keeping
# these corrections here makes the generated dataset deterministic and clean.
SKIP_INDICES = {1373, 1421, 1860, 2671, 2675, 2794, 2813, 2819}
MANUAL_OVERRIDES = {
    139: ("a.m.", "/ˌeɪ ˈem/", "abbr.", "上午；午前"),
    153: ("analyze", "/ˈænəlaɪz/", "v.", "分析"),
    246: ("assure", "/əˈʃʊə(r)/", "v.", "向……保证；使确信"),
    329: ("BC", "/ˌbiː ˈsiː/", "abbr.", "公元前"),
    353: ("behaviour", "/bɪˈheɪvjə(r)/", "n.", "行为；举止"),
    415: ("bored", "/bɔːd/", "adj.", "感到无聊的"),
    416: ("boring", "/ˈbɔːrɪŋ/", "adj.", "乏味的；无聊的"),
    422: ("bother", "/ˈbɒðə(r)/", "v.", "打扰；费心"),
    563: ("centre", "/ˈsentə(r)/", "n.", "中心；中央"),
    647: ("client", "/ˈklaɪənt/", "n.", "客户；委托人"),
    706: ("complain", "/kəmˈpleɪn/", "v.", "抱怨；投诉"),
    707: ("complaint", "/kəmˈpleɪnt/", "n.", "抱怨；投诉；疾病"),
    739: ("conscious", "/ˈkɒnʃəs/", "adj.", "有意识的；清醒的"),
    762: ("context", "/ˈkɒntekst/", "n.", "上下文；语境"),
    897: ("define", "/dɪˈfaɪn/", "v.", "给……下定义；明确"),
    898: ("definite", "/ˈdefɪnət/", "adj.", "明确的；肯定的"),
    899: ("definition", "/ˌdefɪˈnɪʃn/", "n.", "定义；释义"),
    909: ("demanding", "/dɪˈmɑːndɪŋ/", "adj.", "要求高的；费力的"),
    916: ("depression", "/dɪˈpreʃn/", "n.", "抑郁；萧条；凹陷"),
    927: ("despite", "/dɪˈspaɪt/", "prep.", "尽管；即使"),
    1022: ("Dr", "/ˈdɒktə(r)/", "abbr.", "博士；医生"),
    1133: ("equate", "/ɪˈkweɪt/", "v.", "等同；使相等"),
    1515: ("hell", "/hel/", "n.", "地狱；苦境"),
    1582: ("hurrah", "/həˈrɑː/", "interj.", "好哇；万岁"),
    1816: ("limited", "/ˈlɪmɪtɪd/", "adj.", "有限的；受限制的"),
    2067: ("number", "/ˈnʌmbə(r)/", "n./v.", "数字；号码；给……编号"),
    2131: ("Olympic", "/əˈlɪmpɪk/", "adj.", "奥林匹克运动会的"),
    2159: ("organise", "/ˈɔːɡənaɪz/", "v.", "组织；安排"),
    2180: ("outward", "/ˈaʊtwəd/", "adj./adv.", "向外的；向外"),
    2195: ("ox", "/ɒks/", "n.", "公牛；阉牛"),
    2245: ("pay", "/peɪ/", "v./n.", "支付；工资"),
    2246: ("PC", "/ˌpiː ˈsiː/", "abbr.", "个人计算机"),
    2247: ("PE", "/ˌpiː ˈiː/", "abbr.", "体育课"),
    2305: ("ping-pong", "/ˈpɪŋ pɒŋ/", "n.", "乒乓球"),
    2316: ("planet", "/ˈplænɪt/", "n.", "行星"),
    2325: ("pleased", "/pliːzd/", "adj.", "高兴的；满意的"),
    2331: ("p.m.", "/ˌpiː ˈem/", "abbr.", "下午；午后"),
    2384: ("practise", "/ˈpræktɪs/", "v.", "练习；实践"),
    2428: ("programme", "/ˈprəʊɡræm/", "n./v.", "节目；计划；编排"),
    2439: ("propose", "/prəˈpəʊz/", "v.", "提议；打算"),
    2501: ("rate", "/reɪt/", "n./v.", "比率；速度；评价"),
    2635: ("room", "/ruːm/", "n.", "房间；空间"),
    2914: ("southeast", "/ˌsaʊθˈiːst/", "n./adj.", "东南；东南的"),
    2939: ("spoil", "/spɔɪl/", "v.", "破坏；宠坏"),
    3005: ("stretch", "/stretʃ/", "v./n.", "伸展；延伸；一段"),
    3090: ("tablet", "/ˈtæblət/", "n.", "药片；平板电脑"),
    3354: ("VCD", "/ˌviː siː ˈdiː/", "abbr.", "影碟光盘"),
}


def normalize_word(label: str) -> str:
    word = re.sub(r"\s*[（(].*$", "", label).strip()
    word = re.sub(r"\s+", " ", word)
    return word.strip(" ,;：:")


def split_definition(text: str) -> tuple[str, str]:
    text = text.strip().replace("", "")
    match = re.match(
        r"^((?:(?:art|adj|adv|aux|modal|interj|int|prep|pron|conj|num|vt|vi|v|n|a|ad)\.?"
        r"(?:\s*&\s*|\s*/\s*|\s+and\s+|\s+)?){1,5})\s*(.*)$",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return "", text
    return match.group(1).strip(), match.group(2).strip()


def parse_source() -> list[dict]:
    entries: dict[str, dict] = {}
    for line in SOURCE.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^\s*(\d+)\.\s*(.+?)\s*$", line)
        if not match:
            continue
        source_index = int(match.group(1))
        if source_index in SKIP_INDICES:
            continue
        content = match.group(2)
        if source_index in MANUAL_OVERRIDES:
            word, phonetic, part_of_speech, gloss = MANUAL_OVERRIDES[source_index]
        else:
            phonetic_match = re.search(r"\[([^\]]+)\]", content)
            is_phonetic = bool(
                phonetic_match
                and phonetic_match.start() <= 50
                and not re.search(r"[\u3400-\u9fff]", phonetic_match.group(1))
            )
            if is_phonetic and phonetic_match:
                label = content[: phonetic_match.start()].strip()
                phonetic = f"/{phonetic_match.group(1).strip().strip('/')} /".replace(" /", "/")
                definition = content[phonetic_match.end() :].strip()
            else:
                label_match = re.match(
                    r"^([A-Za-z][A-Za-z'./ -]{0,47}?)\s+"
                    r"((?:art|adj|adv|aux|modal|interj|int|prep|pron|conj|num|vt|vi|v|n|a|ad)\.?)"
                    r"\s*(.*)$",
                    content,
                    flags=re.IGNORECASE,
                )
                if label_match:
                    label = label_match.group(1)
                    definition = f"{label_match.group(2)} {label_match.group(3)}"
                else:
                    label, definition = content, ""
                phonetic = ""

            word = normalize_word(label)
            part_of_speech, gloss = split_definition(definition)
            if not gloss:
                gloss = definition or "释义待补充"
        if not word or len(word) > 48:
            continue
        key = word.casefold()
        if key in entries:
            existing = entries[key]
            if gloss not in existing["gloss"]:
                existing["gloss"] = f'{existing["gloss"]}；{gloss}'
            if not existing["phonetic"] and phonetic:
                existing["phonetic"] = phonetic
            continue
        entries[key] = {
            "word": word,
            "phonetic": phonetic,
            "partOfSpeech": part_of_speech,
            "gloss": gloss,
            "sourceIndex": source_index,
        }
    return list(entries.values())


def build() -> list[dict]:
    entries = parse_source()
    known = {entry["word"].casefold() for entry in entries}
    next_index = max(entry["sourceIndex"] for entry in entries) + 1
    for word, phonetic, part_of_speech, gloss in SUPPLEMENTS:
        if len(entries) >= 3600:
            break
        if word.casefold() in known:
            continue
        entries.append(
            {
                "word": word,
                "phonetic": phonetic,
                "partOfSpeech": part_of_speech,
                "gloss": gloss,
                "sourceIndex": next_index,
            }
        )
        known.add(word.casefold())
        next_index += 1

    if len(entries) != 3600:
        raise RuntimeError(f"Expected 3,600 unique words, got {len(entries)}")

    ranked = sorted(
        entries,
        key=lambda item: (
            -zipf_frequency(re.sub(r"[^A-Za-z' -]", "", item["word"]), "en"),
            len(item["word"]),
            item["sourceIndex"],
        ),
    )
    for rank, entry in enumerate(ranked):
        entry["level"] = "basic" if rank < 1200 else "middle" if rank < 2400 else "advanced"

    entries.sort(key=lambda item: item["sourceIndex"])
    for position, entry in enumerate(entries, start=1):
        entry["id"] = f"w{position:04d}"

    assert len({entry["word"].casefold() for entry in entries}) == 3600
    assert {level: sum(entry["level"] == level for entry in entries) for level in ("basic", "middle", "advanced")} == {
        "basic": 1200,
        "middle": 1200,
        "advanced": 1200,
    }
    return entries


if __name__ == "__main__":
    vocabulary = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(vocabulary, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {len(vocabulary)} words to {OUTPUT.relative_to(ROOT)}")
