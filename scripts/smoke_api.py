"""端到端接口冒烟测试（不依赖 shell 的引号处理）。

覆盖：等级/OCR 状态/LLM 预设 · 进度上报 · 文本标注三档 · 考点知识库 · 译文 ·
      文件上传（MD / 文字层 PDF / 扫描件 PDF / 图片）
"""
import sys
import uuid
from pathlib import Path

BASE = "http://127.0.0.1:8300"
ROOT = Path(r"F:\英语学习应用")

sys.path.insert(0, str(ROOT / "scripts"))
import _api  # noqa: E402

# 优先真服务；沙箱挡掉回环时退回进程内 ASGI（见 scripts/_api.py 的开头说明）。
# 不管走哪条，下面的 `C.get(...)` / `C.post(...)` 代码是同一套。
C = _api.client()
out = [f"传输方式 = {_api.MODE}", ""]


def add(s: str) -> None:
    out.append(s)


def post_file(name: str, mime: str, level: str, timeout: float = 300.0,
              translate: bool = False) -> None:
    path = ROOT / "samples" / name
    if not path.exists():
        add(f"POST /api/analyze [{name}]  跳过：样本不存在")
        return
    with open(path, "rb") as f:
        r = C.post(f"{BASE}/api/analyze", timeout=timeout,
                       files={"file": (name, f, mime)},
                       data={"level_id": level, "use_llm": "false", "no_save": "true",
                             "translate": "true" if translate else "false",
                             "trans_mode": "sentence"})
    if r.status_code != 200:
        add(f"POST /api/analyze [{name}]  {r.status_code}  {r.text[:400]}")
        return
    d = r.json()
    c = d["counters"]
    pi = d.get("parse_info") or {}
    add(f"POST /api/analyze [{name}]  200  区块={len(d['blocks'])} words={d['word_count']} "
        f"标={c['word_highlight']}/圈={c['word_circle']}/蓝={c['word_rare']} "
        f"语法={c['grammar']} 句型={c['patterns']}")
    add(f"    parse_info = {pi}")
    if translate:
        add(f"    译文 trans_mode={d.get('trans_mode')} 段数={len(d.get('translations') or {})}  "
            f"{d.get('trans_note')}")
        add(f"    HTML 含译文块 = {'是' if 'class=\"tr-zh' in d['html'] else '否'}")


# ---------------------------------------------------------------- 基础接口
r = C.get(f"{BASE}/api/levels", timeout=30)
lv = r.json()
add(f"GET /api/levels  {r.status_code}  levels={len(lv['levels'])}")
add(f"    wordlist = {lv['wordlist']}")
add(f"    formats  = {lv.get('formats')}")
add(f"    show_translation = "
    + ", ".join(f"{x['id']}={x.get('show_translation')}" for x in lv["levels"]))
_oc = lv.get("ocr") or {}
add(f"    ocr      = available={_oc.get('available')} engine={_oc.get('engine')} "
    f"python={_oc.get('python')} msg={_oc.get('message')}")

r = C.get(f"{BASE}/api/ocr/status", timeout=120)
add(f"GET /api/ocr/status  {r.status_code}  {r.json()}")

r = C.get(f"{BASE}/api/llm/presets", timeout=30)
add(f"GET /api/llm/presets  {r.status_code}  presets={len(r.json()['presets'])}")

# 只读检查：写操作会污染真实配置，留给 scripts/test_llm_config_api.py（用临时目录）
r = C.get(f"{BASE}/api/llm/config", timeout=30)
d = r.json()
add(f"GET /api/llm/config  {r.status_code}  has_key={d.get('has_key')} "
    f"provider={d.get('provider')!r} key_hint={d.get('key_hint')!r}")
add(f"    配置文件 = {d.get('path')}")
add(f"    响应是否泄漏明文 Key = {'是（有问题）' if 'api_key' in d else '否'}")

add("")

# ---------------------------------------------------------------- 进度上报
r = C.get(f"{BASE}/api/progress", timeout=30)
add(f"GET /api/progress  {r.status_code}  {r.json()}")

r = C.get(f"{BASE}/api/progress/never-existed", timeout=30)
d = r.json()
add(f"GET /api/progress/never-existed  {r.status_code}  found={d.get('found')}"
    f"（期望 200 + False：前端轮询未登记任务不该刷出错误）")

add("")

# ---------------------------------------------------------------- 文本标注（三档）
text = (ROOT / "samples" / "sample_article.md").read_text(encoding="utf-8")
for level in ["high_school", "cet4", "ielts"]:
    r = C.post(f"{BASE}/api/analyze-text", timeout=120, json={
        "text": text, "level_id": level, "title": "The Cost of Convenience",
        # 不存进知识库：见文件末尾「自检不许污染用户数据」的说明
        "no_save": True})
    if r.status_code != 200:
        add(f"POST /api/analyze-text [{level}]  {r.status_code}  {r.text[:300]}")
        continue
    d = r.json()
    c = d["counters"]
    add(f"POST /api/analyze-text [{level}]  200  words={d['word_count']}  "
        f"标={c['word_highlight']}/圈={c['word_circle']}/蓝={c['word_rare']}  "
        f"语法={c['grammar']}  句型={c['patterns']}  生词={len(d['vocab'])}  "
        f"html={len(d['html'])}字符")
    if level == "cet4":
        _base_c4 = d          # 给下面的「带 job_id 会不会改变返回内容」当基线
        add("    生词: " + "、".join(v["surface"] for v in d["vocab"]))
        add("    句型: " + "、".join(p["name"] for p in d["patterns"]))
        (ROOT / "out" / "handbook-api-cet4.html").write_text(d["html"], encoding="utf-8")

add("")

# ---------------------------------------------------------------- 带 job_id 的真实请求
# 进度是旁路：带上 job_id 之后，**返回内容必须逐字段一致** ——
# 否则前端拿到的手账会因为「顺手加了个进度」而悄悄变样。
job = "smoke" + uuid.uuid4().hex[:10]
r = C.post(f"{BASE}/api/analyze-text", timeout=120, json={
    "text": text, "level_id": "cet4", "title": "The Cost of Convenience",
    "job_id": job, "no_save": True})
add(f"POST /api/analyze-text [带 job_id]  {r.status_code}")
if r.status_code == 200:
    _with = r.json()
    s = C.get(f"{BASE}/api/progress/{job}", timeout=30).json()
    add(f"GET /api/progress/{job}  found={s.get('found')}  percent={s.get('percent')}  "
        f"done={s.get('done')}  stage={s.get('stage')}  detail={s.get('detail')!r}")
    add(f"    与不带 job_id 相比：标注计数"
        f"{'一致' if _with['counters'] == _base_c4['counters'] else '不一致（有问题）'}  "
        f"字段集合{'一致' if set(_with) == set(_base_c4) else '不一致（有问题）'}  "
        f"HTML 长度{'一致' if len(_with['html']) == len(_base_c4['html']) else '不一致（有问题）'}")
    add(f"    任务结束态是否正确 = "
        f"{'是' if (s.get('found') and s.get('done') and s.get('percent') == 100.0) else '否（有问题）'}")
else:
    add(f"    {r.text[:200]}")

add("")

# ---------------------------------------------------------------- 考点知识库
r = C.get(f"{BASE}/api/exam-points", timeout=30)
d = r.json()
add(f"GET /api/exam-points  {r.status_code}  阶段={len(d['levels'])}  "
    f"来源={d['stats']['sources']}（official "
    f"{sum(1 for s in d['sources'].values() if s['tier'] == 'official')}）  "
    f"语法条目={d['stats']['grammar_items']}  题型条目={d['stats']['question_types']}")
for lv_ in d["levels"]:
    add(f"    {lv_['id']:<12} {lv_['label']}  词 {lv_['vocab_target']}  "
        f"语法 {lv_['grammar_count']} 题型 {lv_['question_type_count']} 来源 {lv_['source_count']}"
        + ("  [含已失效旧制]" if lv_["has_legacy"] else ""))

for lid in ["high_school", "cet4", "cet6", "kaoyan", "ielts", "toefl"]:
    r = C.get(f"{BASE}/api/exam-points/{lid}", timeout=30)
    body = r.json()
    srcs = body["sources"]
    tiers = {}
    for s in srcs:
        tiers[s["tier"]] = tiers.get(s["tier"], 0) + 1
    add(f"GET /api/exam-points/{lid}  {r.status_code}  来源 {len(srcs)} {tiers}")

r = C.get(f"{BASE}/api/exam-points/nope", timeout=30)
add(f"GET /api/exam-points/nope  {r.status_code}（期望 404）")

r = C.post(f"{BASE}/api/exam-points/toefl/brief", timeout=30, json={"use_llm": False})
b = r.json()
add(f"POST /api/exam-points/toefl/brief  {r.status_code}  mode={b['mode']}  "
    f"长度={len(b['brief'])}  带来源={len(b['sources'])}")
add("    简报首行：" + b["brief"].split("\n")[0])

r = C.get(f"{BASE}/", timeout=30)
html = r.text
add(f"GET /  {r.status_code}  {len(html)} 字符  "
    f"含考点面板={'epBox' in html}  含考点JS={'loadExamPoints' in html}")
add(f"    含译文面板={'useTrans' in html}  含译文JS={'refreshTransStatus' in html}  "
    f"含译文状态条={'transNote' in html}")
add(f"    含进度面板={'progBox' in html}  含进度JS={'startProgress' in html}  "
    f"含等待文案={'等待模型应答' in html}")
add(f"    等待文案按阶段区分（OCR / 模型不能说成同一回事）="
    f"{'是' if 'waiting_label' in html else '否（有问题）'}")
# 这次要修的就是这句：「正在标注…」和「准备就绪，点击生成手账」并排出现，
# 用户根本不知道到底在跑还是没动。修完必须一个都不剩。
add(f"    残留矛盾文案「准备就绪，点击生成手账」= "
    f"{'是（有问题）' if '准备就绪，点击' in html else '否'}")
_has_job = (("append('job_id'" in html) or ("job_id: job" in html)
            or ('"job_id": job' in html))
add(f"    生成请求是否真的带上 job_id = {'是' if _has_job else '否（有问题）'}")

add("")

# ---------------------------------------------------------------- 中文译文
r = C.get(f"{BASE}/api/translate/status", timeout=60)
st = r.json()
add(f"GET /api/translate/status  {r.status_code}  available={st['available']}  "
    f"required={st['required']}  缓存={st['cache_entries']}  上限={st['max_chars']}字符 "
    f"批={st['batch_sentences']}句")
add(f"    provider/model = {st['provider']!r} / {st['model']!r}")
add(f"    message = {st['message']}")
add("    （DELETE /api/translate/cache 会清掉真实缓存，属写操作，"
    "改由 scripts/test_translate_api.py 在临时目录里验）")

_has_llm = bool(st.get("available"))
add(f"    → 本机 {'已' if _has_llm else '未'}配置可用模型，"
    f"以下译文检查按{'真实出译文' if _has_llm else '预期降级'}验证")

# 同一篇文章：不开译文 / 开译文（逐句对照）/ 开译文（整段附译）
_off = C.post(f"{BASE}/api/analyze-text", timeout=120, json={
    "text": text, "level_id": "cet4", "title": "The Cost of Convenience",
    "translate": False, "no_save": True}).json()

for mode in ["sentence", "paragraph"]:
    label = "逐句对照" if mode == "sentence" else "整段附译"
    r = C.post(f"{BASE}/api/analyze-text", timeout=600, json={
        "text": text, "level_id": "cet4", "title": "The Cost of Convenience",
        "translate": True, "trans_mode": mode, "no_save": True})
    if r.status_code != 200:
        add(f"POST /api/analyze-text [cet4 + {label}]  {r.status_code}  {r.text[:300]}")
        continue
    d = r.json()
    tr = d.get("translations") or {}
    pairs = [s for t in tr.values() for s in t["sentences"]]
    add(f"POST /api/analyze-text [cet4 + {label}]  200  trans_mode={d['trans_mode']}  "
        f"译文段数={len(tr)}  译文句数={len(pairs)}  html={len(d['html'])}字符")
    add(f"    trans_note = {d.get('trans_note')}")
    add(f"    HTML: 译文块={'是' if 'class=\"tr-zh' in d['html'] else '否'}  "
        f"逐句容器={'是' if 'class=\"tr-pair\"' in d['html'] else '否'}  "
        f"版式标签={'逐句对照' if '逐句对照' in d['html'] else ('整段附译' if '整段附译' in d['html'] else '无')}")
    # 开/关译文不能动标注
    same = d["counters"] == _off["counters"]
    add(f"    标注计数与不开译文时{'一致' if same else '不一致（有问题）'}  {d['counters']}")
    if pairs:
        ok_zh = all(any("\u4e00" <= ch <= "\u9fff" for ch in s["zh"]) for s in pairs)
        complete = all(s.get("en") and s.get("zh") for s in pairs)
        add(f"    每句译文都含中文={'是' if ok_zh else '否（有问题）'}  "
            f"无空译文={'是' if complete else '否（有问题）'}")
        for s in pairs[:2]:
            add(f"      EN: {s['en'][:76]}")
            add(f"      ZH: {s['zh'][:56]}")
    elif _has_llm:
        add("    （已配置模型却没有译文 —— 需要排查）")
    else:
        add("    [预期] 未配置模型 → 无译文，但已明确说明原因："
            f"{'是' if '大模型' in (d.get('trans_note') or '') else '否（有问题）'}")

add("")

# ---------------------------------------------------------------- 文件上传
post_file("sample_article.md", "text/markdown", "cet6", translate=True)
post_file("test_text.pdf", "application/pdf", "cet4")
post_file("test_scanned.pdf", "application/pdf", "cet4")
post_file("test_scan.png", "image/png", "cet4")

(ROOT / "out" / "_api_test.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
